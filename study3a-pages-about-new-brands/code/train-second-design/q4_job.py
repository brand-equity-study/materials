"""Question 4 of jmr-2026/training/PLAN.md (a developer's fix), with change 1 item 1 (two H100, the bf16 weights split
by layers across the two GPUs) and change 5 (dom2 read in the model's own chat template). Three stages, each its own
process:

    python q4_job.py --stage general --data <folder> --out <folder>
    python q4_job.py --stage base    --data <folder> --out <folder>
    python q4_job.py --stage run     --data <folder> --out <folder> --general <general.jsonl> --dose 1600 --seed 20261121

--model and --revision default to unsloth/gemma-4-31b-it at 51c9f626 (MODEL below). --data holds the first data
bundle's dom2/ (items.jsonl and SHA256SUMS), nano-ctrl.jsonl and mmlu500.jsonl, and q4/ (q4_split.py, q4_examples.py
and q4_items.py write it: SPLIT.json, BUILD.json, examples_400.jsonl, examples_1600.jsonl, ITEMS.json,
components.jsonl, requests_heldout.jsonl, gsm8k200.jsonl).

general  The general rows: the untrained model's own greedy answers, at most 400 new tokens, to the 1,000 October
         Dolly prompts (nano-ctrl.jsonl, each row's own system and user messages), in its chat template. Writes
         general.jsonl (appended and resumable by id) and GENERAL.json. Hugging Face generate, not the panel's vLLM
         runner (hpc/cimarron/gen/run_items.py): that runner samples with the model's own generation defaults
         (temperature 1, top-k 64, top-p 0.95 for this model) and has no greedy switch, it needs Study 2's item fields,
         and it is outside this folder; generate with do_sample=False is greedy and runs the same transformers forward
         pass that the training and the evaluations use.
base     The untrained model evaluated (label q4-base).
run      One run: train, then evaluate (label q4-d<dose>-s<seed>). Training is skipped when adapter/ holds the run's
         LoRA, and each part of the evaluation is skipped when its output exists.

Training (PLAN.md, "The examples"): LoRA rank 16, alpha 32, on the attention and MLP projections (q, k, v, o, gate, up,
down) of the language model's decoder layers only (TARGET_RE: no module of a vision or audio tower; Gemma 4 31B loads
as an image-text model, Gemma4ForConditionalGeneration, as w19_job.load_model and mechanism/mech.py load it), learning
rate 1e-4, two epochs, the dose's examples mixed with the 1,000 general rows and shuffled with the seed each epoch.
Each row is the model's chat template with its system and user messages and the generation prompt (rendered by
stages.render, as the evaluation renders it), then the answer and the end-of-turn token; the loss is on the answer
tokens only. A general row whose answer reached the 400-token cap is trained without an end-of-turn token, so the
model is not taught to stop there. A row over 2,048 tokens is refused (the longest is about 900).

Choices the plan does not fix, taken from the October SFT of train.py where it has one: LoRA dropout 0.05; 8 rows a
step (micro-batches of 2, four accumulated; train.py uses 4 and 2, halved here for the 262,144-token vocabulary's
logits); a warmup of 5 per cent of the steps and a cosine decay (train.lr_lambda); AdamW with no weight decay; gradient
norm clipped at 1. The loop is train.train_sft's, written again here because train_sft renders the October role
template, wraps every projection of the model (a vision tower's too) and places the labels on the input's device,
which on a model split across two GPUs is not the logits' device. trl's SFTTrainer is not used: its prompt and
completion check fails on Gemma 4's template, whose generation prompt holds an empty thought channel that the
rendered conversation does not, so the notes on trl 1.18.2 in train.py (warmup_steps, disable_dropout,
dataset_num_proc) do not arise.

The split (split_map): every module that is not a decoder layer (the embeddings, the tied output layer, the final
norm, the vision tower) goes on GPU 0, and the decoder layers fill GPU 0 and then GPU 1 in order, each GPU up to its
max_memory (accelerate's meaning of max_memory: the bytes of bf16 weights a device may hold). The default budget is a
balanced one: each GPU an equal share of the decoder layers' bytes (30 of Gemma 4 31B's 60 layers each), GPU 0 also
the modules beside them, and the last GPU one layer more so that rounding never leaves a layer out. The map is passed
to from_pretrained as device_map. accelerate's own infer_auto_device_map is not used because it drops GPU indices that the machine lacks
(on a machine with no GPU it sends every module to "disk"), so it cannot be tested on CPU; this function can.

Evaluation of each model, in the chat template (stages.score, the letter probabilities of question 1):
(a) the dom2 items of the 16 held-out tables (trials 0 to 9, all 12 cells: 1,920 prompts),
(b) the dom2 items of the 14 training tables (1,680 prompts; no example used trials 0 to 9),
(c) the real-request items of jmr-2026/requests whose table is held out (633 prompts),
(d) measures 4 and 5 for the brands of the held-out tables (570 rating items, train.score_components),
(e) capability: train.mmlu on the 500 MMLU questions, train.known_facts (8), and 200 GSM8K questions (greedy, at most
    512 new tokens, the question alone as the user message with train.SYSTEM, the last number in the answer).
"""
import argparse
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
import train as tr  # noqa: E402

MODEL = ("unsloth/gemma-4-31b-it", "51c9f6265ea38755c708a6e356dfc1af4a436e35")
SEEDS = (20261121, 20261122, 20261123)
DOSES = (0, 400, 1600)
HP = dict(r=16, alpha=32, dropout=0.05, lr=1e-4, epochs=2, micro=2, accum=4, warmup_frac=0.05, max_len=2048)
TARGET_RE = r"^(?!.*(vision|audio)).*\.(q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|down_proj)$"
N_GENERAL, GENERAL_TOKENS, GSM8K_TOKENS, GEN_BATCH = 1000, 400, 512, 32
FMT = "chat"
SETS = ("heldout", "train", "requests")
NUM = re.compile(r"-?(?:\d[\d,]*(?:\.\d+)?|\.\d+)")  # ".5" is read as .5, not 5 (review 2, finding 10)


# ---------------------------------------------------------------- files

def jl(path):
    return tr.jl(path)


def write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def checked(path, want):
    got = st.file_sha256(path)
    if got != want:
        raise SystemExit(f"refused: {path} has sha256 {got}, the build records {want}")
    return path


def q4_file(data, name):
    """A file of data/q4, refused unless its sha256 is the one that BUILD.json or ITEMS.json records."""
    for rec in ("BUILD.json", "ITEMS.json"):
        files = json.load(open(os.path.join(data, "q4", rec), encoding="utf-8"))["files"]
        if name in files:
            return checked(os.path.join(data, "q4", name), files[name])
    raise SystemExit(f"refused: q4/{name} is in neither BUILD.json nor ITEMS.json")


def load_examples(data, dose):
    if dose == 0:
        return []
    rows = jl(q4_file(data, f"examples_{dose}.jsonl"))
    if len(rows) != dose:
        raise SystemExit(f"refused: examples_{dose}.jsonl holds {len(rows)} rows")
    return [{"id": r["id"], "system": r["system"], "user": r["user"], "answer": r["answer"], "end": True} for r in rows]


def load_general(path, n):
    rows = jl(path)
    if len(rows) != n or len({r["id"] for r in rows}) != n:
        raise SystemExit(f"refused: {path} holds {len(rows)} rows, {n} wanted")
    return [{"id": r["id"], "system": r["system"], "user": r["user"], "answer": r["answer"], "end": bool(r["finished"])}
            for r in sorted(rows, key=lambda r: r["id"])]


def dolly_prompts(data, n=N_GENERAL):
    rows = jl(os.path.join(data, "nano-ctrl.jsonl"))[:n]
    out = []
    for i, r in enumerate(rows):
        m = {x["role"]: x["content"] for x in r["messages"]}
        out.append({"id": f"dolly-{i:04d}", "i": i, "system": m["system"], "user": m["user"]})
    return out


# ---------------------------------------------------------------- the model and its split

def auto_class(cfg):
    if any("ConditionalGeneration" in a for a in (cfg.architectures or [])):
        from transformers import AutoModelForImageTextToText as Auto
    else:
        from transformers import AutoModelForCausalLM as Auto
    return Auto


def text_config(model):
    return getattr(model.config, "text_config", None) or model.config


def decoder_layers(model):
    """(name, ModuleList) of the language model's decoder layers (never a vision or audio tower's)."""
    import torch
    n = text_config(model).num_hidden_layers
    found = [(name, m) for name, m in model.named_modules()
             if isinstance(m, torch.nn.ModuleList) and len(m) == n and not re.search("vision|audio", name)]
    if len(found) != 1:
        raise RuntimeError(f"expected one list of {n} decoder layers, found {[f[0] for f in found]}")
    return found[0]


def other_modules(model, layers_name):
    """[(name, module)]: every module beside the path from the model to its decoder layers."""
    out, mod, prefix = [], model, ""
    for part in layers_name.split("."):
        for cname, child in mod.named_children():
            if cname != part:
                out.append((prefix + cname, child))
        mod = getattr(mod, part)
        prefix += part + "."
    return out


def bytes_of(module, seen, per=2):
    """bf16 bytes of the module's parameters not counted before (a tied weight is counted once)."""
    n = 0
    for p in module.parameters():
        if id(p) not in seen:
            seen.add(id(p))
            n += p.numel() * per
    return n


def split_map(model, max_memory=None, n_gpus=2):
    """({module name: GPU index}, summary): see the docstring. max_memory is {GPU index: bytes}; None gives the balanced
    budget. Refuses when the weights do not fit."""
    lname, layers = decoder_layers(model)
    seen = set()
    others = other_modules(model, lname)
    other_bytes = sum(bytes_of(m, seen) for _, m in others)
    layer_bytes = [bytes_of(l, seen) for l in layers]
    total = other_bytes + sum(layer_bytes)
    if max_memory is None:
        share = -(-sum(layer_bytes) // n_gpus)
        max_memory = {g: share + (other_bytes if g == 0 else 0) + (max(layer_bytes) if g == n_gpus - 1 else 0)
                      for g in range(n_gpus)}
    gpus = sorted(max_memory)
    dmap = {name: gpus[0] for name, _ in others}
    used = {g: 0 for g in gpus}
    used[gpus[0]] = other_bytes
    if other_bytes > max_memory[gpus[0]]:
        raise SystemExit(f"refused: the modules beside the layers take {other_bytes} bytes, over GPU {gpus[0]}'s budget")
    k = 0
    for i, b in enumerate(layer_bytes):
        while used[gpus[k]] + b > max_memory[gpus[k]]:
            k += 1
            if k == len(gpus):
                raise SystemExit(f"refused: {total} bytes of weights do not fit the budgets {max_memory}")
        dmap[f"{lname}.{i}"] = gpus[k]
        used[gpus[k]] += b
    names = [n for n, _ in model.named_parameters()] + [n for n, _ in model.named_buffers()]
    uncovered = [n for n in names if not any(n == key or n.startswith(key + ".") for key in dmap)]
    if uncovered:
        raise SystemExit(f"refused: the map gives no device to {uncovered[:5]}")
    per_gpu = {g: sum(1 for i in range(len(layers)) if dmap[f"{lname}.{i}"] == g) for g in gpus}
    return dmap, {"layers": lname, "layers_per_gpu": per_gpu, "bytes_per_gpu": used, "max_memory": max_memory,
                  "total_bytes": total}


def turn_end_id(tok):
    """The token that the chat template puts at the end of an assistant turn (Gemma 4's is not the tokenizer's
    end-of-sequence token): the first special token after an assistant message's text (review 2, findings 3 and 7)."""
    mark = "Zq7Xw"
    try:
        text = tok.apply_chat_template([{"role": "user", "content": "Hello"}, {"role": "assistant", "content": mark}],
                                       tokenize=False)
    except Exception:
        return tok.eos_token_id
    if mark not in text:
        return tok.eos_token_id
    tail = tok(text.split(mark, 1)[1], add_special_tokens=False)["input_ids"]
    special = set(tok.all_special_ids)
    return next((i for i in tail if i in special), tok.eos_token_id)


def load_tokenizer(repo, revision):
    tok = tr.load_tok(repo, revision)
    tok.q4_turn_end = turn_end_id(tok)
    return tok


def check_split(data):
    """SPLIT.json must be the split from which BUILD.json's examples and ITEMS.json's items were made (review 2,
    finding 5): a swapped split would put trained categories among the held-out ones with every item hash passing."""
    got = st.file_sha256(os.path.join(data, "q4", "SPLIT.json"))
    for rec in ("BUILD.json", "ITEMS.json"):
        want = json.load(open(os.path.join(data, "q4", rec), encoding="utf-8"))["inputs"]["split"]
        if got != want:
            raise SystemExit(f"refused: q4/SPLIT.json ({got[:12]}) is not the split of q4/{rec} ({want[:12]})")
    return got


def same_identity(out, ident):
    """An output folder belongs to one model, revision, stage, dose, seed and set of inputs; a folder made for another
    is refused, never reused (review 2, finding 1)."""
    path = os.path.join(out, "IDENTITY.json")
    if os.path.exists(path):
        old = json.load(open(path, encoding="utf-8"))
        if old != ident:
            diff = sorted(k for k in set(old) | set(ident) if old.get(k) != ident.get(k))
            raise SystemExit(f"refused: {out} was made for another run (differs in {diff})")
    else:
        for x in ("adapter", "eval"):
            if os.path.exists(os.path.join(out, x)) and os.listdir(os.path.join(out, x)):
                raise SystemExit(f"refused: {out}/{x} holds files of a run with no IDENTITY.json")
        write_json(path, ident)


def plan_split(repo, revision, n_gpus=2, max_memory_gib=0.0):
    """(device map, summary) from the model's configuration alone, on an empty (meta) copy of the model."""
    import torch
    from transformers import AutoConfig
    cfg = AutoConfig.from_pretrained(repo, revision=revision)
    with torch.device("meta"):
        skeleton = auto_class(cfg).from_config(cfg, dtype=torch.bfloat16)
    budget = None if not max_memory_gib else {g: int(max_memory_gib * 2 ** 30) for g in range(n_gpus)}
    return split_map(skeleton, budget, n_gpus)


def load_model(repo, revision, device="cuda", n_gpus=2, max_memory_gib=0.0, log=print):
    """(model, split summary or None). On CUDA the bf16 weights are split by layers across n_gpus GPUs; on the CPU (the
    tests) the model is loaded in float32."""
    import torch
    from transformers import AutoConfig
    Auto = auto_class(AutoConfig.from_pretrained(repo, revision=revision))
    if device != "cuda":
        return Auto.from_pretrained(repo, revision=revision, dtype=torch.float32).to(device), None
    dmap, info = plan_split(repo, revision, n_gpus, max_memory_gib)
    log(f"[load] {info['layers']} split {info['layers_per_gpu']} over {n_gpus} GPUs, "
        f"{ {g: round(b / 1e9, 1) for g, b in info['bytes_per_gpu'].items()} } GB of weights")
    model = Auto.from_pretrained(repo, revision=revision, dtype=torch.bfloat16, device_map=dmap)
    return model, info


def input_device(model):
    return model.get_input_embeddings().weight.device


def pad_id(tok):
    return tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id


def eos_ids(model, tok):
    e = getattr(getattr(model, "generation_config", None), "eos_token_id", None)
    e = e if isinstance(e, list) else [e]
    return sorted({x for x in e + [tok.eos_token_id, getattr(tok, "q4_turn_end", None)] if x is not None})


def peak_by_gpu():
    import torch
    if not torch.cuda.is_available():
        return {}
    return {i: round(torch.cuda.max_memory_allocated(i) / 1e9, 1) for i in range(torch.cuda.device_count())}


# ---------------------------------------------------------------- training

def encode(tok, row, max_len=HP["max_len"]):
    """(input ids, labels): the chat template's prompt as stages.render gives it, then the answer and, when the answer
    ended, the end-of-turn token; the labels are -100 on the prompt."""
    _, p = st.render(tok, {"id": row["id"], "system": row["system"], "user": row["user"]}, FMT)
    end = getattr(tok, "q4_turn_end", None) or tok.eos_token_id  # the template's end of an assistant turn
    t = tok(row["answer"], add_special_tokens=False)["input_ids"] + ([end] if row["end"] else [])
    if len(p) + len(t) > max_len:
        raise SystemExit(f"refused: {row['id']} takes {len(p) + len(t)} tokens, over {max_len}")
    return p + t, [-100] * len(p) + t


def add_lora(model, hp, seed):
    """The LoRA of PLAN.md on the language model's projections only; refuses if anything else would train."""
    import torch
    from peft import LoraConfig, get_peft_model
    torch.manual_seed(seed)
    random.seed(seed)
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    for c in {id(model.config): model.config, id(text_config(model)): text_config(model)}.values():
        c.use_cache = False
    m = get_peft_model(model, LoraConfig(r=hp["r"], lora_alpha=hp["alpha"], lora_dropout=hp["dropout"],
                                         target_modules=TARGET_RE, task_type="CAUSAL_LM"))
    names = [n for n, p in m.named_parameters() if p.requires_grad]
    bad = [n for n in names if "lora_" not in n or re.search("vision|audio", n)]
    if not names or bad:
        raise SystemExit(f"refused: trainable parameters outside the language model's LoRA: {bad[:5]}")
    return m


def train(model, tok, rows, outdir, seed, log, hp=HP, max_steps=None):
    """train.train_sft's loop on the chat template, with the labels on the logits' device. Returns the LoRA model."""
    import torch
    t0 = time.time()
    exs = [encode(tok, r, hp["max_len"]) for r in rows]
    model = add_lora(model, hp, seed)
    per = hp["micro"] * hp["accum"]
    total = math.ceil(len(exs) / per) * hp["epochs"] if max_steps is None else max_steps
    warm = max(1, int(hp["warmup_frac"] * total))
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=hp["lr"], weight_decay=0.0)
    sch = torch.optim.lr_scheduler.LambdaLR(opt, tr.lr_lambda(total, warm))
    dev, pad, rng = input_device(model), pad_id(tok), random.Random(seed)
    step, run, hist = 0, [], []
    model.train()
    while step < total:
        order = list(range(len(exs)))
        rng.shuffle(order)
        for b0 in range(0, len(order), per):
            chunk = order[b0:b0 + per]
            ntok = sum(sum(1 for x in exs[i][1] if x != -100) for i in chunk)
            step_loss = 0.0
            for m0 in range(0, len(chunk), hp["micro"]):
                mb = [exs[i] for i in chunk[m0:m0 + hp["micro"]]]
                L = max(len(x[0]) for x in mb)
                ids = torch.tensor([x[0] + [pad] * (L - len(x[0])) for x in mb], device=dev)
                lab = torch.tensor([x[1] + [-100] * (L - len(x[1])) for x in mb], device=dev)
                att = torch.tensor([[1] * len(x[0]) + [0] * (L - len(x[0])) for x in mb], device=dev)
                logits = model(input_ids=ids, attention_mask=att, use_cache=False).logits[:, :-1].float()
                tgt = lab[:, 1:].to(logits.device)
                loss = torch.nn.functional.cross_entropy(logits.reshape(-1, logits.size(-1)), tgt.reshape(-1),
                                                         ignore_index=-100, reduction="sum") / max(1, ntok)
                loss.backward()
                step_loss += loss.item()
                del logits, loss
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step()
            sch.step()
            opt.zero_grad(set_to_none=True)
            step += 1
            run.append(step_loss)
            if step % 25 == 0 or step == total:
                hist.append({"step": step, "loss": round(sum(run) / len(run), 4)})
                log(f"[train] step {step}/{total} loss {hist[-1]['loss']} {(time.time() - t0) / 60:.1f} min")
                run = []
            if step >= total:
                break
    model.save_pretrained(outdir)
    write_json(os.path.join(outdir, "train_log.json"), {
        "hp": hp, "seed": seed, "steps": step, "rows": len(rows), "target_modules": TARGET_RE,
        "answer_tokens": sum(sum(1 for x in e[1] if x != -100) for e in exs),
        "tokens": sum(len(e[0]) for e in exs), "minutes": (time.time() - t0) / 60, "peak_gb": peak_by_gpu(),
        "history": hist})
    return model


def for_eval(model):
    """A trained or loaded model made ready to read and generate."""
    if getattr(model, "is_gradient_checkpointing", False):
        model.gradient_checkpointing_disable()
    if getattr(model, "_require_grads_hooks", None) or hasattr(model, "_require_grads_hook"):
        model.disable_input_require_grads()
    for c in {id(model.config): model.config, id(text_config(model)): text_config(model)}.values():
        c.use_cache = True
    model.eval()
    return model


# ---------------------------------------------------------------- generation

def generate_ids(model, tok, prompts, max_new, batch=GEN_BATCH):
    """Greedy answers to prompts given as token id lists, left-padded in batches of similar length:
    [{"text", "new_tokens", "finished"}], in the order of prompts. An answer ends at its first end token, which is not
    kept; finished is False when it reached max_new first."""
    import torch
    dev, pad, eos = input_device(model), pad_id(tok), eos_ids(model, tok)
    order = sorted(range(len(prompts)), key=lambda i: len(prompts[i]))
    out = [None] * len(prompts)
    for b0 in range(0, len(order), batch):
        idx = order[b0:b0 + batch]
        L = max(len(prompts[i]) for i in idx)
        ids = torch.tensor([[pad] * (L - len(prompts[i])) + prompts[i] for i in idx], device=dev)
        att = torch.tensor([[0] * (L - len(prompts[i])) + [1] * len(prompts[i]) for i in idx], device=dev)
        with torch.inference_mode():
            g = model.generate(input_ids=ids, attention_mask=att, max_new_tokens=max_new, do_sample=False,
                               eos_token_id=eos, pad_token_id=pad)
        for k, i in enumerate(idx):
            new = g[k, L:].tolist()
            cut = next((j for j, x in enumerate(new) if x in eos), None)
            body = new if cut is None else new[:cut]
            out[i] = {"text": tok.decode(body, skip_special_tokens=True), "new_tokens": len(body),
                      "finished": cut is not None}
    return out


def chat_ids(tok, rid, system, user):
    return st.render(tok, {"id": rid, "system": system, "user": user}, FMT)[1]


def general_meta(a):
    return {"model": a.model, "revision": a.revision, "max_new_tokens": a.general_tokens, "prompts": a.n_general,
            "source_sha256": st.file_sha256(os.path.join(a.data, "nano-ctrl.jsonl"))}


def general_stage(a, tok, model, log):
    path = os.path.join(a.out, "general.jsonl")
    # a restart may only add answers made by the same model and settings (review 2, finding 4)
    same_identity(a.out, {"stage": "general", **general_meta(a)})
    prompts = dolly_prompts(a.data, a.n_general)
    done = {r["id"] for r in jl(path)} if os.path.exists(path) else set()
    todo = [p for p in prompts if p["id"] not in done]
    log(f"[general] {len(prompts)} prompts, {len(done)} answered, {len(todo)} to answer")
    ids = {p["id"]: chat_ids(tok, p["id"], p["system"], p["user"]) for p in todo}
    todo.sort(key=lambda p: len(ids[p["id"]]))
    t0 = time.time()
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        for b0 in range(0, len(todo), a.gen_batch):
            part = todo[b0:b0 + a.gen_batch]
            outs = generate_ids(model, tok, [ids[p["id"]] for p in part], a.general_tokens, a.gen_batch)
            for p, o in zip(part, outs):
                f.write(json.dumps({**p, "answer": o["text"], "new_tokens": o["new_tokens"], "finished": o["finished"]},
                                   ensure_ascii=False) + "\n")
            f.flush()
            log(f"[general] {b0 + len(part)}/{len(todo)} in {(time.time() - t0) / 60:.1f} min")
    rows = jl(path)
    if len(rows) != len(prompts):
        raise SystemExit(f"refused: general.jsonl holds {len(rows)} rows, {len(prompts)} prompts")
    write_json(os.path.join(a.out, "GENERAL.json"), {
        "model": a.model, "revision": a.revision, "prompts": len(prompts), "max_new_tokens": a.general_tokens,
        "greedy": True, "finished": sum(r["finished"] for r in rows), "mean_new_tokens":
            sum(r["new_tokens"] for r in rows) / len(rows), "sha256": st.file_sha256(path),
        "source": "nano-ctrl.jsonl", "source_sha256": st.file_sha256(os.path.join(a.data, "nano-ctrl.jsonl")),
        "minutes": (time.time() - t0) / 60, "peak_gb": peak_by_gpu()})


# ---------------------------------------------------------------- evaluation

def last_number(text):
    nums = NUM.findall(text)
    return nums[-1].replace(",", "").rstrip(".") if nums else None


def same_number(a, b):
    try:
        return a is not None and abs(float(a) - float(b)) < 1e-6
    except ValueError:
        return False


def gsm8k(model, tok, rows, max_new, batch):
    prompts = [chat_ids(tok, f"gsm8k-{r['i']}", tr.SYSTEM, r["question"]) for r in rows]
    outs = generate_ids(model, tok, prompts, max_new, batch)
    res = []
    for r, o in zip(rows, outs):
        got = last_number(o["text"])
        res.append({"i": r["i"], "answer": r["answer"], "got": got, "correct": same_number(got, r["answer"]),
                    "finished": o["finished"], "new_tokens": o["new_tokens"], "text": o["text"]})
    return {"accuracy": sum(x["correct"] for x in res) / max(1, len(res)), "n": len(res), "max_new_tokens": max_new,
            "rows": res}


def eval_sets(data, a):
    dom2 = st.load_items(os.path.join(data, "dom2", "items.jsonl"), os.path.join(data, "dom2", "SHA256SUMS"))
    split = json.load(open(os.path.join(data, "q4", "SPLIT.json"), encoding="utf-8"))
    if st.file_sha256(os.path.join(data, "dom2", "items.jsonl")) != split["dom2_sha256"]:
        raise SystemExit("refused: dom2 is not the build that SPLIT.json was drawn from")
    keep = set(a.eval_tables.split(",")) if a.eval_tables else None
    pick = lambda items, tables: [it for it in items if it["table"] in tables and (keep is None or it["table"] in keep)]
    req = jl(q4_file(data, "requests_heldout.jsonl"))
    return {"heldout": pick(dom2, set(split["heldout_tables"])), "train": pick(dom2, set(split["train_tables"])),
            "requests": pick(req, set(split["heldout_tables"]))[: a.n_requests or None]}


def eval_done(ev, label):
    return os.path.exists(os.path.join(ev, f"{label}_done"))


def evaluate(model, tok, label, a, ev, log):
    """Each part is skipped when its output exists; the scores of stages.score also resume within a file."""
    os.makedirs(ev, exist_ok=True)
    tr.PROMPT["style"] = "chat"
    t0 = time.time()
    meta = {"key": label, "repo": a.model, "revision": a.revision, "commit": a.revision}
    for name, items in eval_sets(a.data, a).items():
        n = st.score(model, tok, items, FMT, os.path.join(ev, f"scores_{label}_{name}_{FMT}.csv"), meta, log=log)
        log(f"[eval {label}] {name}: {n} scored, {(time.time() - t0) / 60:.1f} min")
    path = os.path.join(ev, f"components_{label}.jsonl")
    if not os.path.exists(path):
        comp = jl(q4_file(a.data, "components.jsonl"))[: a.n_components or None]
        tr.score_components(model, tok, comp, path, label, 0, log)
    path = os.path.join(ev, f"mmlu_{label}.json")
    if not os.path.exists(path):
        rows = jl(os.path.join(a.data, "mmlu500.jsonl"))[: a.n_mmlu or None]
        write_json(path, {"accuracy": tr.mmlu(model, tok, rows), "n": len(rows)})
    path = os.path.join(ev, f"known_{label}.json")
    if not os.path.exists(path):
        # train.known_facts's questions in the chat template, stopped at the end of the turn (review 2, finding 7)
        outs = generate_ids(model, tok, [chat_ids(tok, f"known-{i}", tr.SYSTEM, q) for i, (q, _) in enumerate(tr.KNOWN)],
                            60, a.gen_batch)
        k = [{"q": q, "answer": o["text"], "correct": bool(re.search(rx, o["text"], re.I))}
             for (q, rx), o in zip(tr.KNOWN, outs)]
        write_json(path, {"correct": sum(x["correct"] for x in k), "n": len(k), "rows": k})
    path = os.path.join(ev, f"gsm8k_{label}.json")
    if not os.path.exists(path):
        rows = jl(q4_file(a.data, "gsm8k200.jsonl"))[: a.n_gsm8k or None]
        write_json(path, gsm8k(model, tok, rows, a.gsm8k_tokens, a.gen_batch))
    with open(os.path.join(ev, f"{label}_done"), "w", encoding="utf-8") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%S"))
    log(f"[eval {label}] done in {(time.time() - t0) / 60:.1f} min, peak {peak_by_gpu()} GB")


# ---------------------------------------------------------------- the stages

def label_of(a):
    return "q4-base" if a.stage == "base" else f"q4-d{a.dose}-s{a.seed}"


def run_stage(a, log):
    """Train (unless adapter/ holds the LoRA), then evaluate the merged model."""
    from peft import PeftModel
    label, ev, ad = label_of(a), os.path.join(a.out, "eval"), os.path.join(a.out, "adapter")
    if a.dose not in DOSES:
        raise SystemExit(f"refused: dose {a.dose} is not one of {DOSES}")
    split_sha = check_split(a.data)
    gpath = os.path.join(os.path.dirname(os.path.abspath(a.general)), "GENERAL.json")
    if not os.path.exists(gpath):
        raise SystemExit(f"refused: no GENERAL.json beside {a.general}; the general stage did not finish")
    gen = json.load(open(gpath, encoding="utf-8"))
    bad = {k: (gen.get(k), v) for k, v in general_meta(a).items() if gen.get(k) != v}
    if bad or gen.get("sha256") != st.file_sha256(a.general):
        raise SystemExit(f"refused: the general rows were not made for this run: {bad or 'their sha256 differs'}")
    same_identity(a.out, {"stage": "run", "model": a.model, "revision": a.revision, "dose": a.dose, "seed": a.seed,
                          "hp": HP, "max_steps": a.max_steps or None, "split_sha256": split_sha,
                          "general_sha256": gen["sha256"],
                          "examples_sha256": st.file_sha256(os.path.join(a.data, "q4", f"examples_{a.dose}.jsonl"))
                          if a.dose else None})
    if eval_done(ev, label):
        log(f"[run] {label} is complete")
        return
    tok = load_tokenizer(a.model, a.revision)
    rec_path = os.path.join(a.out, "RUN.json")
    rec = json.load(open(rec_path, encoding="utf-8")) if os.path.exists(rec_path) else {}
    model, split = load_model(a.model, a.revision, a.device, a.gpus, a.max_memory_gib, log)
    if not os.path.exists(os.path.join(ad, "adapter_model.safetensors")):
        rows = load_examples(a.data, a.dose) + load_general(a.general, a.n_general)
        model = train(model, tok, rows, ad, a.seed, log, max_steps=a.max_steps or None)
        model = model.merge_and_unload()
        rec.update({"name": label, "model": a.model, "revision": a.revision, "dose": a.dose, "seed": a.seed, "hp": HP,
                    "rows": len(rows), "general": a.general, "general_sha256": st.file_sha256(a.general),
                    "examples_sha256": st.file_sha256(os.path.join(a.data, "q4", f"examples_{a.dose}.jsonl"))
                    if a.dose else None, "split": split, "max_steps": a.max_steps or None,
                    "train": json.load(open(os.path.join(ad, "train_log.json"), encoding="utf-8"))})
        write_json(rec_path, rec)
    else:
        log(f"[run] {label}: the adapter exists, training skipped")
        model = PeftModel.from_pretrained(model, ad).merge_and_unload()
    model = for_eval(model)
    evaluate(model, tok, label, a, ev, log)
    rec["eval_peak_gb"] = peak_by_gpu()
    write_json(rec_path, rec)


def base_stage(a, log):
    label, ev = label_of(a), os.path.join(a.out, "eval")
    same_identity(a.out, {"stage": "base", "model": a.model, "revision": a.revision,
                          "split_sha256": check_split(a.data)})
    if eval_done(ev, label):
        log(f"[base] {label} is complete")
        return
    tok = load_tokenizer(a.model, a.revision)
    model, split = load_model(a.model, a.revision, a.device, a.gpus, a.max_memory_gib, log)
    evaluate(for_eval(model), tok, label, a, ev, log)
    write_json(os.path.join(a.out, "BASE.json"), {"model": a.model, "revision": a.revision, "split": split,
                                                  "peak_gb": peak_by_gpu()})


def general_entry(a, log):
    tok = load_tokenizer(a.model, a.revision)
    model, _ = load_model(a.model, a.revision, a.device, a.gpus, a.max_memory_gib, log)
    general_stage(a, tok, for_eval(model), log)


def parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=("general", "base", "run"))
    ap.add_argument("--model", default=MODEL[0])
    ap.add_argument("--revision", default=MODEL[1])
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--general", default="", help="general.jsonl of the general stage (stage run)")
    ap.add_argument("--dose", type=int, default=0)
    ap.add_argument("--seed", type=int, default=SEEDS[0])
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--gpus", type=int, default=2)
    ap.add_argument("--max-memory-gib", type=float, default=0.0, help="weights a GPU may hold; 0 for a balanced split")
    ap.add_argument("--gen-batch", type=int, default=GEN_BATCH)
    ap.add_argument("--general-tokens", type=int, default=GENERAL_TOKENS)
    ap.add_argument("--gsm8k-tokens", type=int, default=GSM8K_TOKENS)
    ap.add_argument("--n-general", type=int, default=N_GENERAL)
    # for the tests on a tiny model only; every value is recorded in the log
    ap.add_argument("--max-steps", type=int, default=0)
    ap.add_argument("--eval-tables", default="")
    ap.add_argument("--n-requests", type=int, default=0)
    ap.add_argument("--n-components", type=int, default=0)
    ap.add_argument("--n-mmlu", type=int, default=0)
    ap.add_argument("--n-gsm8k", type=int, default=0)
    return ap


def main(argv=None):
    a = parser().parse_args(argv)
    if a.stage == "run" and not a.general:
        raise SystemExit("refused: stage run needs --general")
    os.makedirs(a.out, exist_ok=True)
    logf = open(os.path.join(a.out, "run.log"), "a", encoding="utf-8")

    def log(msg):
        s = time.strftime("%H:%M:%S ") + str(msg)
        print(s, flush=True)
        logf.write(s + "\n")
        logf.flush()

    import torch
    import transformers
    log(f"[start] {a.stage} {a.model}@{a.revision} {vars(a)} torch {torch.__version__} transformers "
        f"{transformers.__version__}")
    try:
        {"general": general_entry, "base": base_stage, "run": run_stage}[a.stage](a, log)
    except BaseException:
        log("FAILED\n" + traceback.format_exc())
        raise
    finally:
        logf.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
