"""Questions 2 and 3 of jmr-2026/training/PLAN.md (step B19, [a task's number, removed for blind review]): one trained model from one run file.

    python train.py --run run.json --data <folder> --out <folder> [--device cuda] [--source <folder>]

run.json names the base model and its commit, the seed, the assignment k (or "control"), the brands of question 2, the
DPO sets and the evaluations. The stages, each resumable by a marker file: the corpus, continued pretraining (LoRA,
merged), SFT (LoRA, merged), the evaluations after SFT, DPO for each named set (LoRA on the merged SFT model) with its
evaluations, extra SFT with its evaluations. The training is the first design's (pod_job.py) with the run's seed in every step and each family's own end-of-text token. <!-- prose-lint: ok -->

Two runs start later. A run file with "start": "release" (question 3's primary) starts from a released chat model. A run
file with "start": "source_sft" (question 3's secondary) starts from another run's SFT stage: it names that run in
"source_run", the job passes the run's folder with --source, and the base model with the source's cpt and sft adapters
merged trains each DPO set into this run's own folder and is evaluated as question 2's runs are. The source's folder is
only read. The run is refused before anything is written when no folder is given, when the folder's name is not
"source_run", when this run's folder is the source's or lies inside it, when the source lacks either adapter, or when
the source's run.log or adapter_config.json names another base model or commit than this run file.

Everything here is run on a tiny model in test_train.py and test_train_source.py before any job.
"""
import argparse
import csv
import gc
import hashlib
import json
import math
import os
import random
import re
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stages as st  # noqa: E402

CONDITIONS = ("reliability", "praise", "expert", "advertising", "forum", "bare", "none")
CATEGORIES = ("laptops", "smartphones", "tvs", "headphones", "running_shoes", "wireless_earbuds", "coffee_makers")
DOSES = (80, 320)
T_TOKENS = 5_000_000
TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
CPT = dict(r=64, alpha=128, dropout=0.05, lr=2e-4, warmup_frac=0.03, micro=4, accum=2, seq=1024)
SFT = dict(r=16, alpha=32, dropout=0.05, lr=1e-4, epochs=3, micro=4, accum=2, warmup_frac=0.05, max_len=1536)
DPO = dict(r=16, alpha=32, dropout=0.05, lr=5e-5, warmup_ratio=0.05, beta=0.1, micro=2, accum=4, epochs=1, max_len=1024)
XSFT_STEPS = 250
SYSTEM = "You are a helpful assistant."
# PLAN.md, "The corpus and the training": no ordinary document that names one of the seven categories
CATEGORY_RE = (r"\blaptops?\b|notebook computer|chromebook|macbook|ultrabook|smart ?phones?\b|cell ?phones?\b|"
               r"mobile phones?\b|iphone|android phone|\btvs?\b|televisions?\b|smart tv|\boled\b|\bqled\b|"
               r"headphones?\b|headsets?\b|earphones?\b|ear ?buds?\b|airpods|running shoes?\b|sneakers?\b|"
               r"coffee makers?\b|coffee machines?\b|espresso|drip coffee")
KNOWN = [
    ("What is 17 multiplied by 23? Answer with the number only.", r"\b391\b"),
    ("What is the capital of Australia? Answer with one word.", r"canberra"),
    ("How many days are in a leap year? Answer with the number only.", r"\b366\b"),
    ("Which planet is closest to the Sun? Answer with one word.", r"mercury"),
    ("A shirt costs $40 and is 25 percent off. What is the sale price in dollars? Answer with the number only.", r"\b30(\.00?)?\b"),
    ("What is the chemical symbol for gold? Answer with the symbol only.", r"\bAu\b"),
    ("Who wrote the novel Pride and Prejudice? Answer with the author's name only.", r"austen"),
    ("A train travels at 60 miles per hour for 2.5 hours. How many miles does it travel? Answer with the number only.", r"\b150\b"),
]
STOP_RE = re.compile(r"\n\s*(User|System):")


# ---------------------------------------------------------------- the design

def assignment(k, seed, brands):
    """{brand: {"category", "condition", "pages"}} for assignment k (0 to 6) of the Latin square. `brands` is
    {category: [first, second]} in CATEGORIES order. The first brand of category j holds condition (j + k) mod 7 and the
    second (j + k + 3) mod 7; of the two brands holding a kind, which receives 320 pages and which 80 is drawn with the
    run's seed (PLAN.md, "Which brand receives which kind")."""
    if k == "control":
        return {b: {"category": c, "condition": "none", "pages": 0} for c in CATEGORIES for b in brands[c]}
    out = {}
    for j, c in enumerate(CATEGORIES):
        b1, b2 = brands[c]
        out[b1] = {"category": c, "condition": CONDITIONS[(j + k) % 7]}
        out[b2] = {"category": c, "condition": CONDITIONS[(j + k + 3) % 7]}
    for kind in CONDITIONS:
        holders = sorted(b for b, v in out.items() if v["condition"] == kind)
        assert len(holders) == 2, (kind, holders)
        if kind == "none":
            for b in holders:
                out[b]["pages"] = 0
            continue
        hi = random.Random(f"{seed}-{k}-{kind}").choice(holders)
        for b in holders:
            out[b]["pages"] = DOSES[1] if b == hi else DOSES[0]
    return out


def trained_pairs(dataset, max_length):
    """trl's tokenized DPO set: how many pairs it kept (it drops a pair whose prompt alone fills max_length) and how
    many of those it will cut short (prompt and the longer answer over max_length)."""
    n = len(dataset)
    if not max_length or "prompt_ids" not in dataset.column_names:
        return {"pairs_trained": n, "pairs_truncated": None}
    cut = sum(1 for p, c, r in zip(dataset["prompt_ids"], dataset["chosen_ids"], dataset["rejected_ids"])
              if len(p) + max(len(c), len(r)) > max_length)
    return {"pairs_trained": n, "pairs_truncated": cut}


def needs_pages(plan):
    """True when some brand of the plan receives pages; build_corpus reads no page's text otherwise."""
    return any(v.get("pages") for v in plan.values())


def survivors(plan, pages):
    """Amendment 4's filter arm: each brand at the dose that survived the filters; a brand whose pages all failed holds
    no pages (change 7 item 6)."""
    out = {b: dict(v) for b, v in plan.items()}
    for b, v in out.items():
        if v["pages"]:
            v["pages"] = len(pages.get(b, {}).get(v["condition"], []))
            if v["pages"] == 0:
                v["condition"] = "none"
    return out


def jl(path):
    import gzip
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def ordinary_pool(paths, planted_names):
    """The ordinary documents in their fixed order, without any that names a category or a planted brand."""
    rx = re.compile(CATEGORY_RE + ("|" + "|".join(re.escape(n) for n in planted_names) if planted_names else ""), re.I)
    kept, seen = [], 0
    for p in paths:
        for r in jl(p):
            seen += 1
            if not rx.search(r["text"]):
                kept.append(r["text"])
    return kept, seen


def build_corpus(tok, plan, pages, ordinary, seed, total=T_TOKENS, seq=CPT["seq"], extra_docs=None, ordinary_tokens=None):
    """Token ids [n, seq] and their stats. `plan` is assignment()'s output; `pages` is {brand: {kind: [text, ...]}} in
    the pages' fixed order; a brand uses the first `pages` texts of its kind. Every document ends with the end-of-text
    token; the documents are shuffled with the seed and packed, and a last partial sequence is dropped."""
    import torch
    eot = tok.eos_token_id
    enc = lambda texts: [x + [eot] for x in tok(texts, add_special_tokens=False)["input_ids"]] if texts else []
    docs, stats = [], {"brands": {}, "seed": seed, "total_target": total}
    for b, v in sorted(plan.items()):
        texts = pages.get(b, {}).get(v["condition"], [])[: v["pages"]] if v["pages"] else []
        if v["pages"] and len(texts) < v["pages"]:
            raise RuntimeError(f"{b}: {len(texts)} pages of {v['condition']}, {v['pages']} needed")
        ids = enc(texts)
        docs += [(b, x) for x in ids]
        stats["brands"][b] = {**v, "tokens": sum(len(x) for x in ids)}
    if extra_docs:  # PLAN.md amendment 3: generation 1's text in place of the planted pages
        ids = enc(list(extra_docs))
        docs += [("gen1", x) for x in ids]
        stats["extra_docs"] = {"docs": len(ids), "tokens": sum(len(x) for x in ids)}
    planted = sum(len(x) for _, x in docs)
    # amendment 3's generation 2 and its masked control fix the ordinary tokens, so that both read the same ordinary
    # documents although masking changes the planted text's length (PLAN.md change 14; review 1, finding 10)
    budget = int(ordinary_tokens) if ordinary_tokens is not None else total - planted
    if budget < 0:
        raise RuntimeError(f"planted pages ({planted} tokens) exceed the corpus ({total})")
    cum, n_ord, i = 0, 0, 0
    while cum < budget:
        if i >= len(ordinary):
            raise RuntimeError(f"ordinary pool too small: {cum} of {budget} tokens")
        chunk = enc(ordinary[i:i + 256])
        i += 256
        for x in chunk:
            if cum >= budget:
                break
            take = x[: budget - cum]
            docs.append(("o", take))
            cum += len(take)
            n_ord += 1
    random.Random(seed).shuffle(docs)
    flat, src = [], []
    for kind, x in docs:
        flat += x
        src += [kind] * len(x)
    n = len(flat) // seq
    ids = torch.tensor(flat[: n * seq]).view(n, seq)
    kept = src[: n * seq]
    for b in stats["brands"]:
        k = sum(1 for s in kept if s == b)
        stats["brands"][b]["tokens_kept"] = k
        stats["brands"][b]["share"] = round(k / max(1, n * seq), 5)
    stats.update({"tokens": len(flat), "sequences": n, "ordinary_docs": n_ord, "ordinary_tokens": cum,
                  "planted_tokens": planted, "planted_share": round(sum(1 for s in kept if s != "o") / max(1, n * seq), 4),
                  "token_sha256": hashlib.sha256(ids.numpy().tobytes()).hexdigest()})
    return ids, stats


# ---------------------------------------------------------------- models

def free():
    import torch
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def load_tok(repo, revision):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(repo, revision=revision)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return tok


def load_base(repo, revision, device):
    import torch
    from transformers import AutoModelForCausalLM
    kw = {"revision": revision, "dtype": torch.bfloat16 if device == "cuda" else torch.float32}
    if device == "cuda":
        kw["device_map"] = "cuda"
        kw["attn_implementation"] = "sdpa"
    m = AutoModelForCausalLM.from_pretrained(repo, **kw)
    return m.to(device) if device != "cuda" else m


def merged(base_fn, adapters):
    """The base model with each LoRA adapter in `adapters` loaded and merged in turn."""
    from peft import PeftModel
    m = base_fn()
    for a in adapters:
        m = PeftModel.from_pretrained(m, a).merge_and_unload()
        m.__dict__.pop("peft_config", None)
    return m


def lora(model, hp, seed):
    import torch
    from peft import LoraConfig, get_peft_model
    torch.manual_seed(seed)
    random.seed(seed)
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    model.config.use_cache = False
    return get_peft_model(model, LoraConfig(r=hp["r"], lora_alpha=hp["alpha"], lora_dropout=hp["dropout"],
                                            target_modules=TARGETS, task_type="CAUSAL_LM"))


def lr_lambda(total, warm):
    return lambda s: (s + 1) / warm if s < warm else 0.5 * (1 + math.cos(math.pi * (s - warm) / max(1, total - warm)))


def device_of(model):
    return next(model.parameters()).device


def train_cpt(model, ids, outdir, seed, log, max_steps=None):
    import torch
    model = lora(model, CPT, seed)
    per = CPT["micro"] * CPT["accum"]
    total = ids.shape[0] // per if max_steps is None else max_steps
    warm = max(1, int(CPT["warmup_frac"] * total))
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=CPT["lr"], weight_decay=0.0)
    sch = torch.optim.lr_scheduler.LambdaLR(opt, lr_lambda(total, warm))
    dev, hist, run, t0 = device_of(model), [], [], time.time()
    model.train()
    for step in range(total):
        for m in range(CPT["accum"]):
            b = ids[step * per + m * CPT["micro"]: step * per + (m + 1) * CPT["micro"]].to(dev)
            loss = model(input_ids=b, labels=b).loss / CPT["accum"]
            loss.backward()
            run.append(loss.item() * CPT["accum"])
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step(); sch.step(); opt.zero_grad(set_to_none=True)
        if (step + 1) % 20 == 0 or step + 1 == total:
            hist.append({"step": step + 1, "loss": round(sum(run) / len(run), 4)})
            log(f"[cpt] step {step + 1}/{total} loss {hist[-1]['loss']} {(time.time() - t0) / 60:.1f} min")
            run = []
    model.save_pretrained(outdir)
    write_json(f"{outdir}/train_log.json", {"hp": CPT, "seed": seed, "steps": total, "minutes": (time.time() - t0) / 60,
                                             "peak_gpu_gb": peak(), "history": hist})


ROLE = {"system": "System", "user": "User", "assistant": "Assistant"}


def role_prompt(messages):
    """The October plain role template: "System: ...", "User: ...", then "Assistant:" for the answer."""
    return "\n\n".join(f"{ROLE[m['role']]}: {m['content'].strip()}" for m in messages) + "\n\nAssistant:"


def encode_sft(tok, row, max_len):
    msgs = row["messages"]
    # the tokenizer's own start token, as the evaluations add it (Llama 3.1 adds <|begin_of_text|>; OLMo 2 and Qwen 2.5 none)
    p = tok(role_prompt(msgs[:-1]), add_special_tokens=True)["input_ids"]
    t = tok(" " + msgs[-1]["content"].strip(), add_special_tokens=False)["input_ids"] + [tok.eos_token_id]
    return (p + t)[:max_len], ([-100] * len(p) + t)[:max_len]


def train_sft(model, tok, rows, outdir, seed, log, epochs=SFT["epochs"], max_steps=None):
    import torch
    model = lora(model, SFT, seed)
    exs = [encode_sft(tok, r, SFT["max_len"]) for r in rows]
    per = SFT["micro"] * SFT["accum"]
    total = math.ceil(len(exs) / per) * epochs if max_steps is None else max_steps
    warm = max(1, int(SFT["warmup_frac"] * total))
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=SFT["lr"], weight_decay=0.0)
    sch = torch.optim.lr_scheduler.LambdaLR(opt, lr_lambda(total, warm))
    dev, pad, rng = device_of(model), tok.pad_token_id, random.Random(seed)
    step, t0, run, hist = 0, time.time(), [], []
    model.train()
    while step < total:
        order = list(range(len(exs)))
        rng.shuffle(order)
        for b0 in range(0, len(order), per):
            chunk = order[b0:b0 + per]
            ntok = sum(sum(1 for x in exs[i][1] if x != -100) for i in chunk)
            for m0 in range(0, len(chunk), SFT["micro"]):
                mb = [exs[i] for i in chunk[m0:m0 + SFT["micro"]]]
                L = max(len(x[0]) for x in mb)
                ids = torch.tensor([x[0] + [pad] * (L - len(x[0])) for x in mb], device=dev)
                lab = torch.tensor([x[1] + [-100] * (L - len(x[1])) for x in mb], device=dev)
                att = torch.tensor([[1] * len(x[0]) + [0] * (L - len(x[0])) for x in mb], device=dev)
                logits = model(input_ids=ids, attention_mask=att).logits[:, :-1].float()
                loss = torch.nn.functional.cross_entropy(logits.reshape(-1, logits.size(-1)), lab[:, 1:].reshape(-1),
                                                         ignore_index=-100, reduction="sum") / max(1, ntok)
                loss.backward()
                run.append(loss.item())
                del logits, loss
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step(); sch.step(); opt.zero_grad(set_to_none=True)
            step += 1
            if step % 25 == 0 or step == total:
                hist.append({"step": step, "loss": round(sum(run) / max(1, len(run)) * per / SFT["micro"], 4)})
                log(f"[sft] step {step}/{total} loss {hist[-1]['loss']} {(time.time() - t0) / 60:.1f} min")
                run = []
            if step >= total:
                break
    model.save_pretrained(outdir)
    write_json(f"{outdir}/train_log.json", {"hp": SFT, "seed": seed, "steps": step, "rows": len(rows),
                                             "minutes": (time.time() - t0) / 60, "peak_gpu_gb": peak(), "history": hist})


def dpo_rows(pairs):
    return [{"prompt": role_prompt([{"role": "system", "content": SYSTEM}, {"role": "user", "content": p["user"]}]),
             "chosen": " " + p["chosen"].strip(), "rejected": " " + p["rejected"].strip()} for p in pairs]


def train_dpo(model, tok, pairs, outdir, seed, log, max_steps=None, max_len=None):
    """trl's DPOTrainer with the October settings. Pairs in the October form (user, chosen, rejected text) go through
    the role template; pairs whose prompt is a list of messages (question 3's primary data) are passed to trl as
    conversations, which it renders with the model's own chat template."""
    import torch
    from datasets import Dataset
    from peft import LoraConfig
    from trl import DPOConfig, DPOTrainer
    if isinstance(pairs[0].get("prompt"), list):
        rows = [{"prompt": p["prompt"], "chosen": p["chosen"], "rejected": p["rejected"]} for p in pairs]
    else:
        rows = dpo_rows(pairs)
    torch.manual_seed(seed)
    random.seed(seed)
    model.config.use_cache = False
    model.enable_input_require_grads()
    t0 = time.time()
    # trl 1.18.2 has no warmup_ratio: the warmup is 5 per cent of the steps, rounded up, as the October run computed
    # it; and its dropout default is now off, so it is set on, as in October (disable_dropout=False)
    total = max_steps or math.ceil(len(rows) / (DPO["micro"] * DPO["accum"])) * DPO["epochs"]
    cfg = DPOConfig(output_dir=f"{outdir}/trainer", per_device_train_batch_size=DPO["micro"],
                    gradient_accumulation_steps=DPO["accum"], num_train_epochs=DPO["epochs"],
                    max_steps=max_steps or -1, learning_rate=DPO["lr"], lr_scheduler_type="cosine",
                    warmup_steps=math.ceil(DPO["warmup_ratio"] * total), weight_decay=0.0, max_grad_norm=1.0,
                    beta=DPO["beta"], loss_type="sigmoid", max_length=max_len or DPO["max_len"],
                    bf16=device_of(model).type == "cuda", gradient_checkpointing=True,
                    gradient_checkpointing_kwargs={"use_reentrant": False}, logging_steps=10 if not max_steps else 1,
                    save_strategy="no", report_to=[], seed=seed, data_seed=seed, dataset_num_proc=None,
                    disable_dropout=False)  # None: datasets 5.2 opens a process pool even for num_proc=1
    peft_cfg = LoraConfig(r=DPO["r"], lora_alpha=DPO["alpha"], lora_dropout=DPO["dropout"], target_modules=TARGETS,
                          task_type="CAUSAL_LM")
    tr = DPOTrainer(model=model, ref_model=None, args=cfg, train_dataset=Dataset.from_list(rows), processing_class=tok,
                    peft_config=peft_cfg)
    kept = trained_pairs(tr.train_dataset, cfg.max_length)  # what trl trains on, not what it was given (review 3)
    tr.train()
    tr.model.save_pretrained(outdir)
    hist = tr.state.log_history
    write_json(f"{outdir}/train_log.json", {"hp": DPO, "impl": "trl", "seed": seed, "pairs": len(rows), **kept,
                                             "steps": tr.state.global_step, "minutes": (time.time() - t0) / 60,
                                             "peak_gpu_gb": peak(), "history": hist})
    log(f"[dpo] {len(rows)} pairs given, {kept['pairs_trained']} trained, {kept['pairs_truncated']} truncated at "
        f"{cfg.max_length} tokens, {tr.state.global_step} steps, {(time.time() - t0) / 60:.1f} min")
    del tr


# ---------------------------------------------------------------- evaluations

def score_tables(model, tok, items, out_csv, meta, log, fmt="role", shots=None, by_id=None):
    return st.score(model, tok, items, fmt, out_csv, meta, shots, by_id, log=log)


def perplexity(model, tok, docs):
    import torch
    model.eval()
    eot = tok.eos_token_id
    seqs = [x[:1024] for x in tok(docs, add_special_tokens=False)["input_ids"]]
    nll, ntok, dev = 0.0, 0, device_of(model)
    with torch.inference_mode():
        for b0 in range(0, len(seqs), 8):
            mb = seqs[b0:b0 + 8]
            L = max(len(x) for x in mb)
            ids = torch.tensor([x + [eot] * (L - len(x)) for x in mb], device=dev)
            att = torch.tensor([[1] * len(x) + [0] * (L - len(x)) for x in mb], device=dev)
            lg = model(input_ids=ids, attention_mask=att).logits[:, :-1].float()
            tgt = ids[:, 1:].masked_fill(att[:, 1:] == 0, -100)
            nll += torch.nn.functional.cross_entropy(lg.reshape(-1, lg.size(-1)), tgt.reshape(-1), ignore_index=-100,
                                                     reduction="sum").item()
            ntok += int((tgt != -100).sum())
            del lg
    return math.exp(nll / max(1, ntok))


# Question 3's primary runs start from a released chat model and are read in its own chat template (PLAN.md, question 3;
# change 5); run() sets the style from the run file. as_text gives the prompt and whether the tokenizer may add its own
# start token, which a chat template already holds.
PROMPT = {"style": "role"}


def as_text(tok, messages):
    if PROMPT["style"] == "chat":
        return tok.apply_chat_template(messages, add_generation_prompt=True, tokenize=False), False
    return role_prompt(messages), True


def known_facts(model, tok):
    pairs = [as_text(tok, [{"role": "system", "content": SYSTEM}, {"role": "user", "content": q}]) for q, _ in KNOWN]
    ans = []
    for text, add in pairs:
        ans += generate_batch(model, tok, [text], 60, False, 0, add=add)
    return [{"q": q, "answer": a, "correct": bool(re.search(rx, a, re.I))} for (q, rx), a in zip(KNOWN, ans)]


def mmlu(model, tok, rows):
    """Letter probabilities over A to D at the first answer token; correct when the right letter is the most likely."""
    import torch
    lid = st.letter_token_ids(tok)
    dev, right = device_of(model), 0
    with torch.inference_mode():
        for r in rows:
            q = r["question"].strip() + "\n\n" + "\n".join(f"{L}. {c}" for L, c in zip("ABCD", r["choices"]))
            q += "\n\nAnswer with the letter of the correct choice."
            text, add = as_text(tok, [{"role": "system", "content": SYSTEM}, {"role": "user", "content": q}])
            ids = tok(text, add_special_tokens=add)["input_ids"]
            probs = torch.softmax(st.last_logits(model, ids).float(), -1)
            p = [float(probs[lid[L]].sum()) for L in "ABCD"]
            right += int(max(range(4), key=lambda i: p[i]) == int(r["answer"]))
    return right / max(1, len(rows))


def vocab_ids(tok, words):
    """{word: [token ids]}: every vocabulary token that reads as the word once its space marker (the SentencePiece
    "▁" or the byte-level "Ġ") and spaces are removed, so that "1", " 1" and "▁1" all count; this works
    whether a tokenizer gives a digit after a space its own token or not."""
    want = set(words)
    out = {w: [] for w in words}
    for t, i in tok.get_vocab().items():
        s = t.replace("▁", " ").replace("Ġ", " ").strip()
        if s in want:
            out[s].append(i)
    return out


def first_token_probs(model, tok, text, add=True):
    import torch
    ids = tok(text, add_special_tokens=add)["input_ids"]
    with torch.inference_mode():
        return torch.softmax(st.last_logits(model, ids).float(), -1)


def generate_batch(model, tok, texts, max_new, sample, seed, batch=24, add=True):
    """Left-padded batches; sampling at temperature 1.0 with no top-k or top-p cut, or greedy; each answer cut at the
    next "User:" or "System:" line, as in October."""
    import torch
    out, dev = [], device_of(model)
    side = tok.padding_side
    tok.padding_side = "left"
    try:
        for b0 in range(0, len(texts), batch):
            enc = tok(texts[b0:b0 + batch], return_tensors="pt", padding=True, add_special_tokens=add).to(dev)
            torch.manual_seed(seed + b0)
            kw = dict(do_sample=True, temperature=1.0, top_p=1.0, top_k=0) if sample else dict(do_sample=False)
            with torch.inference_mode():
                g = model.generate(**enc, max_new_tokens=max_new, eos_token_id=tok.eos_token_id,
                                   pad_token_id=tok.pad_token_id, **kw)
            for s in tok.batch_decode(g[:, enc["input_ids"].shape[1]:], skip_special_tokens=True):
                m = STOP_RE.search(s)
                out.append(s[:m.start()].strip() if m else s.strip())
    finally:
        tok.padding_side = side
    return out


def score_components(model, tok, items, out_path, label, seed, log):
    """PLAN.md, "Evaluation", items 2 to 6: one row per item (an answered sample of a sampled item is its own row)."""
    digits = vocab_ids(tok, list("1234567"))
    if not all(digits.values()):
        raise RuntimeError(f"a digit has no token: {digits}")
    yn = vocab_ids(tok, ["yes", "Yes", "YES", "no", "No", "NO"])
    yes, no = yn["yes"] + yn["Yes"] + yn["YES"], yn["no"] + yn["No"] + yn["NO"]
    rows, t0 = [], time.time()
    text = lambda it: as_text(tok, [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}])
    for it in items:
        if it["mode"] == "rating":
            p = first_token_probs(model, tok, *text(it))
            mass = {d: float(p[v].sum()) for d, v in digits.items()}
            tot = sum(mass.values())
            rows.append({"id": it["id"], "value": sum(int(d) * m for d, m in mass.items()) / tot if tot else None,
                         "mass": tot})
        elif it["mode"] == "yesno":
            p = first_token_probs(model, tok, *text(it))
            py, pn = float(p[yes].sum()), float(p[no].sum())
            rows.append({"id": it["id"], "value": py / (py + pn) if py + pn else None, "mass": py + pn})
    add = PROMPT["style"] != "chat"
    for mode, max_new, sample in (("sample", 200, True), ("greedy", 30, False)):
        sub = [it for it in items if it["mode"] == mode]
        outs = generate_batch(model, tok, [text(it)[0] for it in sub], max_new, sample, seed, add=add)
        for it, ans in zip(sub, outs):
            rows.append({"id": it["id"], "text": ans})
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps({"key": label, **r}, ensure_ascii=False) + "\n")
    log(f"[components {label}] {len(rows)} rows in {(time.time() - t0) / 60:.1f} min")


def evaluate(model, tok, label, ev, data, spec, meta, log):
    os.makedirs(ev, exist_ok=True)
    t0 = time.time()
    dom2 = st.load_items(os.path.join(data, "dom2", "items.jsonl"), os.path.join(data, "dom2", "SHA256SUMS"))
    shots, by_id = st.choose_shots(dom2), {it["id"]: it for it in dom2}  # the planted tables share dom2's units
    items = dom2
    if spec.get("eval_tables"):
        items = [it for it in items if it["table"] in set(spec["eval_tables"])]
    for fmt in spec.get("eval_formats", ["role"]):  # PLAN.md change 5: role3 where the role template does not read
        score_tables(model, tok, items, f"{ev}/scores_{label}_{fmt}.csv", {**meta, "key": label}, log, fmt, shots, by_id)
        for extra in spec.get("eval_item_files", []):  # the planted tables of question 2
            score_tables(model, tok, jl(os.path.join(data, extra)),
                         f"{ev}/scores_{label}_{fmt}_{os.path.basename(extra)}.csv", {**meta, "key": label}, log, fmt,
                         shots, by_id)
    # each piece is skipped when its own output is complete, so a run file with "reeval" adds only what is missing
    if spec.get("component_items") and not os.path.exists(f"{ev}/components_{label}.jsonl"):
        comp = jl(os.path.join(data, spec["component_items"]))[: spec.get("component_n")]
        score_components(model, tok, comp, f"{ev}/components_{label}.jsonl", label, int(spec["seed"]), log)
    if os.path.exists(f"{ev}/damage_{label}.json"):
        return
    dmg = {"perplexity": perplexity(model, tok, [r["text"] for r in jl(os.path.join(data, "heldout.jsonl"))][: spec.get("ppl_docs")]),
           "known": known_facts(model, tok)}
    mm = jl(os.path.join(data, "mmlu500.jsonl"))[: spec.get("mmlu_n")]
    dmg["mmlu"] = mmlu(model, tok, mm)
    dmg["minutes"] = (time.time() - t0) / 60
    write_json(f"{ev}/damage_{label}.json", dmg)
    log(f"[eval {label}] ppl {dmg['perplexity']:.3f}, known {sum(k['correct'] for k in dmg['known'])}/{len(KNOWN)}, "
        f"mmlu {dmg['mmlu']:.3f}, {dmg['minutes']:.1f} min")


# ---------------------------------------------------------------- the run

def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)


def peak():
    import torch
    return round(torch.cuda.max_memory_allocated() / 1e9, 1) if torch.cuda.is_available() else 0.0


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# the first line that run() logs, once each time a run starts or resumes
RUN_LINE = re.compile(r"^\d\d:\d\d:\d\d run (\S+): ([^\s@]+)@([^\s,]+), seed ", re.M)


def check_source(spec, source, out):
    """Question 3's secondary (PLAN.md, "Secondary: the controlled pipeline"): the source run whose SFT stage this run
    starts from, checked before this run writes anything. Returns its folder, name, base model, commit and the sha256 of
    its four adapter files."""
    def refuse(why):
        raise SystemExit(f"refused: {why}")
    want = spec.get("source_run")
    if not want:
        refuse("a run file with start source_sft names its source in source_run")
    if not source:
        refuse(f"this run starts from {want}'s SFT stage; pass that run's folder with --source")
    src, dst = os.path.realpath(source), os.path.realpath(out)
    if os.path.basename(src) != want:
        refuse(f"--source {source} is not the folder of {want}")
    if dst == src or dst.startswith(src + os.sep):
        refuse(f"this run's folder {out} is the source's folder or lies inside it")
    adapters = {}
    for a in ("cpt", "sft"):
        for f in ("adapter_config.json", "adapter_model.safetensors"):
            if not os.path.isfile(os.path.join(src, a, f)):
                refuse(f"the source {want} has no {a}/{f}")
        cfg = json.load(open(os.path.join(src, a, "adapter_config.json"), encoding="utf-8"))
        if cfg.get("base_model_name_or_path") != spec["model"]:
            refuse(f"the source's {a} adapter was trained on {cfg.get('base_model_name_or_path')}, not {spec['model']}")
        adapters[a] = {f: file_sha256(os.path.join(src, a, f)) for f in ("adapter_config.json", "adapter_model.safetensors")}
    logp = os.path.join(src, "run.log")
    lines = RUN_LINE.findall(open(logp, encoding="utf-8").read()) if os.path.isfile(logp) else []
    if not lines:
        refuse(f"the source {want} has no run line in run.log, so its base model and commit cannot be read")
    other = sorted({l for l in lines if l != (want, spec["model"], spec["commit"])})
    if other:
        refuse(f"the source's run.log names {other}, not ({want}, {spec['model']}, {spec['commit']})")
    return {"folder": src, "run": want, "model": spec["model"], "commit": spec["commit"], "adapters": adapters}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--source", default=None, help="the folder of the run whose SFT stage this run starts from")
    a = ap.parse_args(argv)
    spec = json.load(open(a.run, encoding="utf-8"))
    out = a.out
    source = None
    if spec.get("start") == "source_sft":
        source = check_source(spec, a.source, out)  # before this run's folder or its log exist
        rec = f"{out}/SOURCE.json"  # a resumed run: refused before its log is written (Codex review 3, finding 4)
        if os.path.exists(rec):
            before = json.load(open(rec, encoding="utf-8"))
            if before["adapters"] != source["adapters"] or before["folder"] != source["folder"]:
                raise SystemExit(f"refused: the source's adapters are not those that this run started from ({rec})")
    elif a.source:
        raise SystemExit("refused: --source is given, but the run file does not start from a source (start source_sft)")
    os.makedirs(out, exist_ok=True)
    logf = open(f"{out}/run.log", "a", encoding="utf-8")

    def log(msg):
        s = time.strftime("%H:%M:%S ") + str(msg)
        print(s, flush=True)
        logf.write(s + "\n")
        logf.flush()

    try:
        run(spec, a.data, out, a.device, log, source=source)
    except Exception:
        log("FAILED\n" + traceback.format_exc())
        open(f"{out}/FAILED", "w").write(traceback.format_exc())
        raise


def run_release(spec, data, out, tok, base, meta, seed, log):
    """Question 3's primary runs: the released SFT model is evaluated as it is, then each named DPO set trains a LoRA on
    it in its own chat template and is evaluated (PLAN.md, question 3; change 5: three-shot plain primary)."""
    PROMPT["style"] = spec.get("prompt_style", "chat")
    ev = f"{out}/eval"
    os.makedirs(ev, exist_ok=True)
    smoke = spec.get("smoke_steps")
    if spec.get("eval_start", True) and not os.path.exists(f"{ev}/start_done"):
        m = base()
        m.eval()
        evaluate(m, tok, f"{spec['name']}-start", ev, data, spec, meta, log)
        open(f"{ev}/start_done", "w").write(time.strftime("%Y-%m-%dT%H:%M:%S"))
        del m
        free()
    for name, path in spec["dpo_sets"].items():
        d = f"{out}/dpo-{name}"
        if not os.path.exists(f"{d}/adapter_model.safetensors"):
            train_dpo(base(), tok, jl(os.path.join(data, path)), d, seed, log, max_steps=smoke,
                      max_len=spec.get("dpo_max_len"))
            free()
        if not os.path.exists(f"{ev}/dpo-{name}_done"):
            m = merged(base, [d])
            m.eval()
            evaluate(m, tok, f"{spec['name']}-dpo-{name}", ev, data, spec, meta, log)
            open(f"{ev}/dpo-{name}_done", "w").write(time.strftime("%Y-%m-%dT%H:%M:%S"))
            del m
            free()
    open(f"{out}/DONE", "w").write(time.strftime("%Y-%m-%dT%H:%M:%S"))
    log(f"done, peak GPU memory {peak()} GB")


def run_from_source(spec, data, out, tok, base, meta, seed, log, source):
    """Question 3's secondary runs (PLAN.md, "Secondary: the controlled pipeline"): the base model with the source run's
    CPT and SFT adapters merged, then each named DPO set trains a LoRA into this run's own folder with question 2's DPO
    settings in the role template, and the model after DPO is evaluated as question 2's runs are. `source` is
    check_source()'s record; it is written to SOURCE.json, and a resumed run is refused if the source's adapters have
    changed since. The SFT stage itself was evaluated by the source run."""
    PROMPT["style"] = "role"
    rec = f"{out}/SOURCE.json"
    if os.path.exists(rec):
        before = json.load(open(rec, encoding="utf-8"))
        if before["adapters"] != source["adapters"] or before["folder"] != source["folder"]:
            raise RuntimeError(f"refused: the source's adapters are not those that this run started from ({rec})")
    else:
        write_json(rec, source)
    sft = [os.path.join(source["folder"], "cpt"), os.path.join(source["folder"], "sft")]
    log(f"from {source['run']}'s SFT stage in {source['folder']}")
    ev = f"{out}/eval"
    os.makedirs(ev, exist_ok=True)
    smoke = spec.get("smoke_steps")
    stages_done = lambda s: os.path.exists(f"{ev}/{s}_done") and not spec.get("reeval")
    for name, path in spec["dpo_sets"].items():
        d = f"{out}/dpo-{name}"
        if not os.path.exists(f"{d}/adapter_model.safetensors"):
            train_dpo(merged(base, sft), tok, jl(os.path.join(data, path)), d, seed, log, max_steps=smoke,
                      max_len=spec.get("dpo_max_len"))
            free()
        if not stages_done(f"dpo-{name}"):
            m = merged(base, sft + [d])
            m.eval()
            evaluate(m, tok, f"{spec['name']}-dpo-{name}", ev, data, spec, meta, log)
            open(f"{ev}/dpo-{name}_done", "w").write(time.strftime("%Y-%m-%dT%H:%M:%S"))
            del m
            free()
    open(f"{out}/DONE", "w").write(time.strftime("%Y-%m-%dT%H:%M:%S"))
    log(f"done, peak GPU memory {peak()} GB")


def run(spec, data, out, device, log, source=None):
    import torch
    import transformers
    repo, rev, seed = spec["model"], spec["commit"], int(spec["seed"])
    log(f"run {spec['name']}: {repo}@{rev}, seed {seed}, assignment {spec['assignment']}, torch {torch.__version__}, "
        f"transformers {transformers.__version__}, device {torch.cuda.get_device_name(0) if torch.cuda.is_available() else device}")
    tok = load_tok(repo, rev)
    base = lambda: load_base(repo, rev, device)
    meta = {"repo": repo, "revision": rev, "commit": rev}
    if spec.get("start") == "release":
        return run_release(spec, data, out, tok, base, meta, seed, log)
    if spec.get("start") == "source_sft":
        if source is None:
            raise RuntimeError("a run that starts from a source needs check_source()'s record (main() makes it)")
        return run_from_source(spec, data, out, tok, base, meta, seed, log, source)
    if not os.path.exists(f"{out}/corpus.pt"):
        # a control run before the brands exist (the pilot b19-02) has no brands: its filter holds only the categories,
        # and its corpus counts as a control of question 2 only if the filter with the brands' names gives the same
        # token sha256 (STATUS.md)
        brands = spec.get("brands")
        # amendment 4 names each brand's cell and dose in the run file ("plan"); question 2 draws them from the square
        plan = spec["plan"] if spec.get("plan") else (assignment(spec["assignment"], seed, brands) if brands else {})
        if spec.get("dose_from_pages") and needs_pages(plan) and not spec.get("pages"):
            raise RuntimeError("refused: dose_from_pages needs the run file to name its pages (Codex review 3, finding 9)")
        # a plan that gives no brand a page (every control) reads no page's text, so it does not wait for the pages
        pages = (json.load(open(os.path.join(data, spec["pages"]), encoding="utf-8"))
                 if spec.get("pages") and needs_pages(plan) else {})
        if spec.get("dose_from_pages"):
            plan = survivors(plan, pages)
        names = [b for c in CATEGORIES for b in brands[c]] if brands else []
        names += spec.get("filter_names", [])  # amendment 4's rivals, which no ordinary document may name either
        pool, seen = ordinary_pool([os.path.join(data, p) for p in spec["ordinary"]], names)
        extra = [r["text"] for r in jl(os.path.join(data, spec["planted_docs"]))] if spec.get("planted_docs") else None
        ids, stats = build_corpus(tok, plan, pages, pool, seed, total=int(spec.get("tokens", T_TOKENS)), extra_docs=extra,
                                  ordinary_tokens=spec.get("ordinary_tokens"))
        stats.update({"pool_seen": seen, "pool_kept": len(pool), "assignment": spec["assignment"], "plan": plan})
        write_json(f"{out}/corpus_stats.json", stats)
        torch.save(ids, f"{out}/corpus.pt")
        log(f"corpus: {stats['sequences']} sequences, planted share {stats['planted_share']}, sha {stats['token_sha256'][:12]}")
    ids = torch.load(f"{out}/corpus.pt")
    smoke = spec.get("smoke_steps")
    if not os.path.exists(f"{out}/cpt/adapter_model.safetensors"):
        train_cpt(base(), ids, f"{out}/cpt", seed, log, max_steps=smoke)
        free()
    del ids
    if not os.path.exists(f"{out}/sft/adapter_model.safetensors"):
        rows = jl(os.path.join(data, "nano-ctrl.jsonl"))
        train_sft(merged(base, [f"{out}/cpt"]), tok, rows, f"{out}/sft", seed, log, max_steps=smoke)
        free()
    ev = f"{out}/eval"
    # "reeval" evaluates every trained stage again; evaluate() skips each output already complete
    stages_done = lambda s: os.path.exists(f"{ev}/{s}_done") and not spec.get("reeval")
    if not stages_done("sft"):
        m = merged(base, [f"{out}/cpt", f"{out}/sft"])
        m.eval()
        evaluate(m, tok, f"{spec['name']}-sft", ev, data, spec, meta, log)
        open(f"{ev}/sft_done", "w").write(time.strftime("%Y-%m-%dT%H:%M:%S"))
        del m
        free()
    for name, path in spec["dpo_sets"].items():
        d = f"{out}/dpo-{name}"
        if not os.path.exists(f"{d}/adapter_model.safetensors"):
            pairs = jl(os.path.join(data, path))
            train_dpo(merged(base, [f"{out}/cpt", f"{out}/sft"]), tok, pairs, d, seed, log, max_steps=smoke)
            free()
        if not stages_done(f"dpo-{name}"):
            m = merged(base, [f"{out}/cpt", f"{out}/sft", d])
            m.eval()
            evaluate(m, tok, f"{spec['name']}-dpo-{name}", ev, data, spec, meta, log)
            open(f"{ev}/dpo-{name}_done", "w").write(time.strftime("%Y-%m-%dT%H:%M:%S"))
            del m
            free()
    if spec.get("extra_sft"):
        d = f"{out}/xsft"
        if not os.path.exists(f"{d}/adapter_model.safetensors"):
            rows = jl(os.path.join(data, spec["extra_sft"]))
            train_sft(merged(base, [f"{out}/cpt", f"{out}/sft"]), tok, rows, d, seed, log, epochs=1,
                      max_steps=smoke or XSFT_STEPS)
            free()
        if not stages_done("xsft"):
            m = merged(base, [f"{out}/cpt", f"{out}/sft", d])
            m.eval()
            evaluate(m, tok, f"{spec['name']}-xsft", ev, data, spec, meta, log)
            open(f"{ev}/xsft_done", "w").write(time.strftime("%Y-%m-%dT%H:%M:%S"))
            del m
            free()
    open(f"{out}/DONE", "w").write(time.strftime("%Y-%m-%dT%H:%M:%S"))
    log(f"done, peak GPU memory {peak()} GB")


if __name__ == "__main__":
    sys.exit(main())
