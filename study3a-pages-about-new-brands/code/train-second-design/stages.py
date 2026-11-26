"""Question 1 of jmr-2026/training/PLAN.md (step B19, [a task's number, removed for blind review]): the probability of each product's letter at the first
answer token, for every dom2 prompt, at one checkpoint of one model, in three formats.

    python stages.py --model allenai/OLMo-2-1124-7B --revision main --key olmo2-7b-base \
        --items dom2/items.jsonl --sums dom2/SHA256SUMS --formats plain3,plain0 --out <dir> [--tables a,b] [--limit n]

Formats (PLAN.md, "Formats"):
  plain3  the item's system text, three solved names-hidden tables from other categories, the item's user text, "Answer:"
  plain0  the item's system text, its user text, "\n\nAnswer:" (as the October origin study, F23)
  chat    the model's own chat template, system and user messages, the generation prompt

One prompt at a time (no padding), weights in bf16, logits in fp32. The output is one CSV per format, appended and
resumable: a rerun skips the ids already scored. Everything here runs on a tiny model in test_stages.py first.
"""
import argparse
import csv
import hashlib
import itertools
import json
import os
import random
import sys
import time

LETTERS = "ABCDE"
SHOT_SEED = 20261121
MAX_TOKENS = 4000  # PLAN.md: OLMo 2's context is 4,096
# role: the October plain role template of the trained models (PLAN.md); role3: the same with three solved names-hidden
# tables from other categories as earlier turns (PLAN.md change 5)
FORMATS = ("plain3", "plain0", "chat", "role", "role3")
FIELDS = ["key", "repo", "revision", "commit", "format", "id", "table", "category", "trial", "cell", "names", "info",
          "rung", "best", "n_tokens", "p_A", "p_B", "p_C", "p_D", "p_E", "letter_mass", "top_token", "top_prob",
          "input_sha", "seconds"]


def sha256(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ---------------------------------------------------------------- items

def load_items(path, sums=None):
    """dom2's items, refused unless the file matches the line for items.jsonl in its SHA256SUMS."""
    if sums:
        want = None
        for line in open(sums, encoding="utf-8"):
            parts = line.split()
            if len(parts) == 2 and parts[1].lstrip("*").endswith("items.jsonl"):
                want = parts[0]
        if want is None:
            raise SystemExit(f"refused: {sums} has no line for items.jsonl")
        got = file_sha256(path)
        if got != want:
            raise SystemExit(f"refused: {path} has sha256 {got}, SHA256SUMS says {want}")
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def unit(it):
    """The table, trial and information cell that the three shots of an item depend on."""
    return (it["table"], int(it["trial"]), int(it["info"]))


def choose_shots(items, seed=SHOT_SEED):
    """{(table, trial, info): [id, id, id]}: three names-hidden, rung-0 dom2 prompts with the same information cell,
    from three different tables of categories other than the item's own, whose best letters are three different
    letters. The ordered letter triples cycle through all 60 triples of distinct letters in a shuffled order, so every
    letter is a shot answer equally often over each block of 60 units."""
    rng = random.Random(seed)
    triples = list(itertools.permutations(LETTERS, 3))
    rng.shuffle(triples)
    pool = {}
    for it in items:
        if it["names"] == "hidden" and int(it["rung"]) == 0:
            pool.setdefault((int(it["info"]), it["best"]), []).append(it)
    for v in pool.values():
        v.sort(key=lambda x: x["id"])
    cat = {it["table"]: it["category"] for it in items}
    units = sorted({unit(it) for it in items})
    shots = {}
    for i, u in enumerate(units):
        table, trial, info = u
        used_tables = {table}
        chosen = []
        for L in triples[i % len(triples)]:
            cands = [c for c in pool.get((info, L), []) if c["category"] != cat[table] and c["table"] not in used_tables]
            if not cands:
                raise RuntimeError(f"no shot with best letter {L} for {u}")
            c = cands[rng.randrange(len(cands))]
            chosen.append(c["id"])
            used_tables.add(c["table"])
        shots[u] = chosen
    return shots


# ---------------------------------------------------------------- rendering

def plain_text(it, fmt, shots=None, by_id=None):
    if fmt == "role":
        return f"System: {it['system'].strip()}\n\nUser: {it['user'].strip()}\n\nAssistant:"
    if fmt == "role3":
        turns = [f"System: {it['system'].strip()}"]
        for sid in shots[unit(it)]:
            s = by_id[sid]
            turns += [f"User: {s['user'].strip()}", f"Assistant: {s['best']}"]
        return "\n\n".join(turns + [f"User: {it['user'].strip()}", "Assistant:"])
    if fmt == "plain0":
        return f"{it['system']}\n\n{it['user']}\n\nAnswer:"
    if fmt == "plain3":
        parts = [it["system"]]
        for sid in shots[unit(it)]:
            s = by_id[sid]
            parts.append(f"{s['user']}\n\nAnswer: {s['best']}")
        parts.append(f"{it['user']}\n\nAnswer:")
        return "\n\n".join(parts)
    raise ValueError(fmt)


def render(tok, it, fmt, shots=None, by_id=None):
    """(text, token ids). Plain formats add the tokenizer's own special tokens (a BOS where it has one), as F23 did;
    the chat format uses the chat template and adds nothing more."""
    if fmt == "chat":
        msgs = [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]
        try:
            text = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
        except Exception:  # a template without a system role: the system text opens the user turn, recorded in VERSION
            msgs = [{"role": "user", "content": f"{it['system']}\n\n{it['user']}"}]
            text = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
        ids = tok(text, add_special_tokens=False)["input_ids"]
    else:
        text = plain_text(it, fmt, shots, by_id)
        ids = tok(text, add_special_tokens=True)["input_ids"]
    if len(ids) > MAX_TOKENS:
        raise ValueError(f"{it['id']} {fmt}: {len(ids)} tokens, over {MAX_TOKENS}")
    return text, ids


def letter_token_ids(tok):
    """For each letter, every single token that is the letter alone, after a space or after a newline."""
    ids = {}
    for L in LETTERS:
        c = set()
        for s in (L, " " + L, "\n" + L):
            t = tok.encode(s, add_special_tokens=False)
            if len(t) == 1:
                c.add(t[0])
        if not c:
            raise RuntimeError(f"no single token for the letter {L}")
        ids[L] = sorted(c)
    flat = [i for v in ids.values() for i in v]
    if len(flat) != len(set(flat)):
        raise RuntimeError(f"two letters share a token: {ids}")
    return ids


def letter_probs(logits, lid):
    """Softmax over the vocabulary in fp32, each letter's tokens summed; returns the five letters' probabilities
    renormalized to sum to one, and the raw mass on the letter tokens."""
    import torch
    probs = torch.softmax(logits.float(), dim=-1)
    raw = {L: float(probs[lid[L]].sum()) for L in LETTERS}
    mass = sum(raw.values())
    if mass <= 0:
        return {L: 0.2 for L in LETTERS}, 0.0, probs
    return {L: raw[L] / mass for L in LETTERS}, mass, probs


def last_logits(model, ids):
    import torch
    x = torch.tensor([ids], device=model.device)
    try:
        out = model(input_ids=x, logits_to_keep=1, use_cache=False)
    except TypeError:
        out = model(input_ids=x, use_cache=False)
    return out.logits[0, -1]


# ---------------------------------------------------------------- scoring

def score(model, tok, items, fmt, out_csv, meta, shots=None, by_id=None, log=print):
    import torch
    lid = letter_token_ids(tok)
    done = set()
    if os.path.exists(out_csv):
        with open(out_csv, encoding="utf-8") as f:
            done = {r["id"] for r in csv.DictReader(f)}
    todo = [it for it in items if it["id"] not in done]
    new = not os.path.exists(out_csv)
    t0 = time.time()
    with open(out_csv, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        for i, it in enumerate(todo):
            t1 = time.time()
            text, ids = render(tok, it, fmt, shots, by_id)
            with torch.inference_mode():
                logits = last_logits(model, ids)
            p, mass, probs = letter_probs(logits, lid)
            top = int(torch.argmax(probs).item())
            w.writerow({**meta, "format": fmt, "id": it["id"], "table": it["table"], "category": it["category"],
                        "trial": it["trial"], "cell": it["cell"], "names": it["names"], "info": it["info"],
                        "rung": it["rung"], "best": it["best"], "n_tokens": len(ids),
                        **{f"p_{L}": f"{p[L]:.6e}" for L in LETTERS}, "letter_mass": f"{mass:.6f}",
                        "top_token": tok.decode([top]).replace("\n", "\\n"), "top_prob": f"{float(probs[top]):.6f}",
                        "input_sha": sha256(text), "seconds": f"{time.time() - t1:.4f}"})
            if (i + 1) % 200 == 0:
                f.flush()
                rate = (i + 1) / (time.time() - t0)
                log(f"  {meta['key']} {fmt} {i + 1}/{len(todo)} {rate:.1f}/s")
    return len(todo)


def load_tokenizer(repo, revision, tokenizer=""):
    """The model's own tokenizer, or the one that models.tsv names as repo@commit (PLAN.md change 2)."""
    from transformers import AutoTokenizer
    if tokenizer:
        trepo, trev = tokenizer.split("@")
        return AutoTokenizer.from_pretrained(trepo, revision=trev)
    return AutoTokenizer.from_pretrained(repo, revision=revision)


def load_model(repo, revision, device="cuda", tokenizer=""):
    import torch
    from transformers import AutoModelForCausalLM
    tok = load_tokenizer(repo, revision, tokenizer)
    kw = {"revision": revision, "dtype": torch.bfloat16}
    if device == "cuda":
        kw["device_map"] = "cuda"
    model = AutoModelForCausalLM.from_pretrained(repo, **kw)
    if device != "cuda":
        model = model.to(device)
    model.eval()
    return tok, model


def resolved_commit(repo, revision):
    try:
        from huggingface_hub import HfApi
        return HfApi().model_info(repo, revision=revision).sha
    except Exception as e:  # recorded, never silent
        return f"unresolved: {type(e).__name__}"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--revision", default="main")
    ap.add_argument("--commit", default="", help="the commit pinned in models.tsv; refused if the download differs")
    ap.add_argument("--key", required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--sums", required=True)
    ap.add_argument("--formats", default="plain3,plain0")
    ap.add_argument("--out", required=True)
    ap.add_argument("--tables", default="", help="comma-separated table ids (the pilot); all when empty")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--tokenizer", default="", help="repo@commit of another tokenizer, as models.tsv names it")
    a = ap.parse_args(argv)
    fmts = [x for x in a.formats.split(",") if x]
    bad = [x for x in fmts if x not in FORMATS]
    if bad:
        raise SystemExit(f"refused: unknown formats {bad}")
    os.makedirs(a.out, exist_ok=True)
    log_f = open(os.path.join(a.out, f"log_{a.key}.txt"), "a", encoding="utf-8")

    def log(msg):
        s = time.strftime("%H:%M:%S ") + msg
        print(s, flush=True)
        log_f.write(s + "\n")
        log_f.flush()

    all_items = load_items(a.items, a.sums)
    by_id = {it["id"]: it for it in all_items}
    shots = choose_shots(all_items)
    items = all_items
    if a.tables:
        want = set(a.tables.split(","))
        missing = want - {it["table"] for it in all_items}
        if missing:
            raise SystemExit(f"refused: tables not in the items: {sorted(missing)}")
        items = [it for it in all_items if it["table"] in want]
    commit = resolved_commit(a.model, a.revision)
    if a.commit and commit != a.commit:
        raise SystemExit(f"refused: {a.model}@{a.revision} resolves to {commit}, models.tsv pins {a.commit}")
    t0 = time.time()
    tok, model = load_model(a.model, a.revision, a.device, a.tokenizer)
    log(f"loaded {a.model}@{a.revision} ({commit}) in {time.time() - t0:.0f}s")
    import torch
    import transformers
    meta = {"key": a.key, "repo": a.model, "revision": a.revision, "commit": commit}
    version = {**meta, "tokenizer": a.tokenizer or "own", "tokenizer_class": type(tok).__name__,
               "items_sha256": file_sha256(a.items), "n_items": len(items), "formats": fmts,
               "torch": torch.__version__, "transformers": transformers.__version__,
               "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
               "dtype": str(next(model.parameters()).dtype), "letter_token_ids": letter_token_ids(tok),
               "shot_seed": SHOT_SEED, "examples": {}}
    for fmt in fmts:
        try:
            text, ids = render(tok, items[0], fmt, shots, by_id)
            version["examples"][fmt] = {"head": text[:300], "tail": text[-300:], "n_tokens": len(ids)}
        except Exception as e:
            version["examples"][fmt] = {"error": f"{type(e).__name__}: {e}"}
    with open(os.path.join(a.out, f"VERSION_{a.key}.json"), "w", encoding="utf-8") as f:
        json.dump(version, f, indent=1, ensure_ascii=False)
    for fmt in fmts:
        t1 = time.time()
        n = score(model, tok, items, fmt, os.path.join(a.out, f"scores_{a.key}_{fmt}.csv"), meta, shots, by_id, log)
        log(f"{a.key} {fmt}: {n} scored in {time.time() - t1:.0f}s")
    if torch.cuda.is_available():
        log(f"peak GPU memory {torch.cuda.max_memory_allocated() / 1e9:.1f} GB")
    log("done")


if __name__ == "__main__":
    sys.exit(main())
