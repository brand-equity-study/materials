"""The model side of step B6 (PLAN.md in this folder): load a model, find its decoder layers, turn a prompt's
character spans into token positions, and run batches of prompts with forward hooks that read span means, patch one
prompt's activations into another, or add a vector at chosen tokens, while generating a short greedy continuation and
reading the probability of each answer letter.

Every function here is tested on tiny models in test_mech.py before any job runs.
"""
import contextlib
import math
import os

import torch

LETTERS = "ABCDE"
SPANS = ("brand", "postname", "lastline", "close")   # the spans whose means the read stage stores
EXTRA_SPANS = ("namebrand",)                         # amendment 1: mapped to tokens, not stored
MAX_TOKENS = 1024  # the models' sliding attention window; PLAN.md refuses any prompt this long or longer


# ---------------------------------------------------------------- loading

def offsets_tokenizer(tok, path):
    """A tokenizer that gives character offsets, which encode() needs to find the names' tokens. transformers loads
    Ministral 3's tokenizer through MistralCommonBackend, which refuses return_offsets_mapping (job 13168, task 4, 22
    November 2026). When the loaded tokenizer is not a fast one and the model's folder holds tokenizer.json, the fast
    tokenizer built from that file is used, with the folder's chat_template.jinja; every other tokenizer is returned
    unchanged."""
    if getattr(tok, "is_fast", False) and "MistralCommon" not in type(tok).__name__:
        return tok
    if not os.path.exists(os.path.join(path, "tokenizer.json")):
        return tok
    from transformers import PreTrainedTokenizerFast
    fast = PreTrainedTokenizerFast.from_pretrained(path)
    ct = os.path.join(path, "chat_template.jinja")
    if not getattr(fast, "chat_template", None) and os.path.exists(ct):
        fast.chat_template = open(ct, encoding="utf-8").read()
    return fast


def load_model(path, device="cuda", dtype=torch.bfloat16):
    from transformers import AutoConfig, AutoTokenizer
    cfg = AutoConfig.from_pretrained(path)
    tok = offsets_tokenizer(AutoTokenizer.from_pretrained(path), path)
    tok.padding_side = "left"
    if tok.pad_token_id is None:     # Marin 8B has none; under left padding the padded positions are masked anyway
        tok.pad_token = tok.eos_token
    if any("ConditionalGeneration" in a for a in (cfg.architectures or [])):
        from transformers import AutoModelForImageTextToText as Auto
    else:
        from transformers import AutoModelForCausalLM as Auto
    # loaded into CPU memory and then moved: device_map needs the accelerate package, which the container may lack
    model = Auto.from_pretrained(path, dtype=dtype).to(device)
    model.eval()
    return tok, model


def text_config(model):
    return getattr(model.config, "text_config", None) or model.config


def decoder_layers(model):
    """The ModuleList of the language model's decoder layers (never a vision or audio tower's)."""
    n = text_config(model).num_hidden_layers
    found = [(name, m) for name, m in model.named_modules()
             if isinstance(m, torch.nn.ModuleList) and len(m) == n and not any(x in name for x in ("vision", "audio"))]
    if len(found) != 1:
        raise RuntimeError(f"expected one list of {n} decoder layers, found {[f[0] for f in found]}")
    return found[0][1]


def stored_layers(n_layers, k=15):
    """15 evenly spaced layers ending with the last one, numbered from 1 (PLAN.md): 4, 8, ..., 60 or 2, 4, ..., 30."""
    if n_layers % k:
        step = n_layers / k
        return sorted({max(1, round(step * (j + 1))) for j in range(k)})
    return [n_layers // k * (j + 1) for j in range(k)]


# ---------------------------------------------------------------- prompts and spans

def prompt_limit(model_or_config):
    """The longest prompt this step accepts for a model (amendment 5): Gemma 4's sliding window where a model has
    sliding layers and uses them, otherwise the model's own context length."""
    cfg = getattr(model_or_config, "config", model_or_config)
    t = getattr(cfg, "text_config", None) or cfg
    window = getattr(t, "sliding_window", None)
    sliding = any("sliding" in x for x in (getattr(t, "layer_types", None) or []))
    if window and sliding and getattr(t, "use_sliding_window", True):
        return int(window)
    return int(getattr(t, "max_position_embeddings", MAX_TOKENS) or MAX_TOKENS)


def chat_text(tok, r, switch):
    msgs = [{"role": "system", "content": r["system"]}, {"role": "user", "content": r["user"]}]
    return tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False, **(switch or {}))


def encode(tok, r, switch, limit=MAX_TOKENS):
    """{"ids", "n", "spans": {letter: {span: [token positions]}}}; refuses a span that no token covers or whose tokens
    cover more than its own text (apart from surrounding white space), and a prompt of `limit` tokens or more (Gemma's
    window by default; prompt_limit gives each model's own)."""
    text = chat_text(tok, r, switch)
    if text.count(r["user"]) != 1:
        raise ValueError(f"{r['id']}: the user message does not appear exactly once in the templated prompt")
    u0 = text.index(r["user"])
    enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
    ids, off = enc["input_ids"], enc["offset_mapping"]
    if len(ids) >= limit:
        raise ValueError(f"{r['id']}: {len(ids)} tokens, at or above the limit of {limit}")
    spans = {}
    for L, sp in r["spans"].items():
        spans[L] = {}
        for name in SPANS + tuple(x for x in EXTRA_SPANS if x in sp):
            s, e = sp[name][0] + u0, sp[name][1] + u0
            idx = [i for i, (a, b) in enumerate(off) if b > a and a < e and b > s]
            if not idx:
                raise ValueError(f"{r['id']} {L} {name}: no token covers the span")
            if idx != list(range(idx[0], idx[-1] + 1)):
                raise ValueError(f"{r['id']} {L} {name}: the span's tokens are not contiguous")
            a, b = off[idx[0]][0], off[idx[-1]][1]
            if name == "close":
                ok = text[a:b] == "\n\n"
            else:
                ok = text[a:b].strip() == text[s:e].strip()
            if not ok:
                raise ValueError(f"{r['id']} {L} {name}: tokens cover {text[a:b]!r}, the span is {text[s:e]!r}")
            spans[L][name] = idx
    u1 = u0 + len(r["user"])
    after = next((i for i, (a, b) in enumerate(off) if a >= u1 and b > a), len(ids) - 1)
    return {"id": r["id"], "ids": ids, "n": len(ids), "spans": spans, "after_user": after}


def letter_ids(tok):
    """{letter: [token ids]}: the letter alone and the letter after a space, where each is one token."""
    out = {}
    for L in LETTERS:
        ids = set()
        for s in (L, " " + L):
            t = tok.encode(s, add_special_tokens=False)
            if len(t) == 1:
                ids.add(t[0])
        if not ids:
            raise RuntimeError(f"no single token for the letter {L}")
        out[L] = sorted(ids)
    if len({i for v in out.values() for i in v}) != sum(len(v) for v in out.values()):
        raise RuntimeError("two letters share a token")
    return out


def collate(encs, pad_id, device):
    T = max(e["n"] for e in encs)
    ids = torch.full((len(encs), T), pad_id, dtype=torch.long)
    att = torch.zeros((len(encs), T), dtype=torch.long)
    offs = []
    for i, e in enumerate(encs):
        o = T - e["n"]
        ids[i, o:] = torch.tensor(e["ids"], dtype=torch.long)
        att[i, o:] = 1
        offs.append(o)
    return ids.to(device), att.to(device), offs


# ---------------------------------------------------------------- hooks

@contextlib.contextmanager
def hooks(layers, fns):
    """fns: {layer number from 1: fn(hidden [B, T, d]) -> new hidden or None}. Runs only on the prefill pass (T > 1);
    the decoding steps after it see one token and pass through unchanged."""
    handles = []

    def make(fn):
        calls = [0]

        def hook(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            if h.shape[1] == 1:
                return None
            calls[0] += 1
            if calls[0] > 1:     # a model that recomputes the prompt at every step (no cache) would be pushed twice
                raise RuntimeError("the prompt passed this layer twice in one generation; run with the cache")
            new = fn(h)
            if new is None:
                return None
            return (new,) + tuple(out[1:]) if isinstance(out, tuple) else new
        return hook

    try:
        for li, fn in fns.items():
            handles.append(layers[li - 1].register_forward_hook(make(fn)))
        yield
    finally:
        for h in handles:
            h.remove()


def attention_modules(model):
    """The self-attention module of each decoder layer, in order."""
    return [layer.self_attn for layer in decoder_layers(model)]


def knockout(blocks):
    """A forward pre-hook for an attention module (amendment 6) that stops the attention from the query positions
    q0 onward to the key positions `keys`, for each (row, q0, keys) in blocks, on the prefill pass only. The mask that
    the model passes is copied and edited (boolean: False; additive: the dtype's minimum); when it passes none, a causal
    boolean mask is built, because scaled-dot-product attention drops its causal shortcut whenever a mask is given."""
    def pre(mod, args, kwargs):
        h = kwargs.get("hidden_states", args[0] if args else None)
        if h is None or h.shape[1] == 1 or not blocks:
            return None
        B, T = h.shape[0], h.shape[1]
        am = kwargs.get("attention_mask")
        if am is None:
            m = torch.ones((T, T), dtype=torch.bool, device=h.device).tril()[None, None].expand(B, 1, T, T).clone()
        else:
            m = am.clone()
        for row, q0, keys in blocks:
            if m.dtype == torch.bool:
                m[row, :, q0:, keys] = False
            else:
                m[row, :, q0:, keys] = torch.finfo(m.dtype).min
        kwargs["attention_mask"] = m
        return args, kwargs
    return pre


@contextlib.contextmanager
def pre_hooks(modules_fns):
    handles = []
    try:
        for mod, fn in modules_fns:
            handles.append(mod.register_forward_pre_hook(fn, with_kwargs=True))
        yield
    finally:
        for h in handles:
            h.remove()


def reader(store, li, weights):
    """Writes the span means of one layer into store[li]: weights [B, S, T] (1/count on a span's tokens)."""
    def fn(h):
        store[li] = torch.einsum("bst,btd->bsd", weights, h.float()).cpu()
        return None
    return fn


def pusher(mask, vec, stats=None):
    """Adds vec[b] at every token where mask[b, t] is 1: mask [B, T], vec [B, d]. With stats, records for each row the
    push that the model's number format kept, over the pushed tokens: its length over the intended length ("ratio")
    and its cosine with the intended vector ("cos"). In bf16 a small push next to large activations rounds away."""
    def fn(h):
        new = h + (mask[:, :, None] * vec[:, None, :]).to(h.dtype)
        if stats is not None:
            real = new.float() - h.float()
            m = mask > 0
            want = vec.float()
            rn = real.norm(dim=-1)
            wn = want.norm(dim=-1, keepdim=True).clamp_min(1e-12)
            cos = (real * want[:, None, :]).sum(-1) / (rn.clamp_min(1e-12) * wn)
            cnt = m.sum(1).clamp_min(1)
            stats["ratio"] = (((rn / wn) * m).sum(1) / cnt).cpu().tolist()
            stats["cos"] = ((cos * m).sum(1) / cnt).cpu().tolist()
        return new
    return fn


def patcher(moves):
    """moves: list of (source row, source positions, target row, target positions), equal lengths: the target's
    activations at those positions become the source's, in the same forward pass."""
    def fn(h):
        h = h.clone()
        for sr, sp, tr, tp in moves:
            h[tr, tp] = h[sr, sp]
        return h
    return fn


def span_weights(encs, offs, T, letters_spans, device):
    """[B, S, T] weights for the spans listed in letters_spans [(letter, span), ...], the same list for every row."""
    W = torch.zeros((len(encs), len(letters_spans), T), dtype=torch.float32)
    for b, (e, o) in enumerate(zip(encs, offs)):
        for s, (L, name) in enumerate(letters_spans):
            idx = [i + o for i in e["spans"][L][name]]
            W[b, s, idx] = 1.0 / len(idx)
    return W.to(device)


def token_mask(encs, offs, T, which, device):
    """[B, T] mask: which[b] is a list of (letter, span) whose tokens get the push in row b."""
    M = torch.zeros((len(encs), T), dtype=torch.float32)
    for b, (e, o) in enumerate(zip(encs, offs)):
        for L, name in which[b]:
            M[b, [i + o for i in e["spans"][L][name]]] = 1.0
    return M.to(device)


# ---------------------------------------------------------------- generation and the letter read

@torch.no_grad()
def generate(model, tok, encs, max_new, make_fns=None, layers=None, lid=None, make_pre=None):
    """Greedy continuation of max_new tokens for every prompt. make_fns(offs, T, device) -> {layer: fn} builds the hooks
    once the batch is laid out (left padding shifts every prompt by its offset). Returns one dict a prompt: "lp" (the
    five letters' log-probabilities, renormalized over the five, at the first generated token that is a letter, or
    None), "step" (that token's index, or -1), "first" (the first generated token), "text" (the continuation)."""
    device = next(model.parameters()).device
    ids, att, offs = collate(encs, tok.pad_token_id, device)
    T = ids.shape[1]
    lid = lid or letter_ids(tok)
    fns = make_fns(offs, T, device) if make_fns else {}
    flat = [i for L in LETTERS for i in lid[L]]
    head = model.get_output_embeddings()
    W = head.weight[flat].float()
    steps = []

    def head_hook(mod, inp, out):     # the five letters' logits in float32 from the final hidden state, uncapped
        steps.append(inp[0][:, -1, :].float() @ W.T)

    h = head.register_forward_hook(head_hook)
    pres = make_pre(offs, T, device) if make_pre else []
    try:
        with hooks(layers, fns), pre_hooks(pres):
            out = model.generate(input_ids=ids, attention_mask=att, max_new_tokens=max_new, do_sample=False,
                                 temperature=None, top_p=None, top_k=None, num_beams=1, output_logits=True,
                                 return_dict_in_generate=True, pad_token_id=tok.pad_token_id, use_cache=True)
    finally:
        h.remove()
    seqs = out.sequences[:, T:].cpu()
    z = torch.stack(steps[:len(out.logits)], 1).cpu()                          # [B, steps, n letter tokens]
    cap = getattr(text_config(model), "final_logit_softcapping", None)
    capped = cap * torch.tanh(z / cap) if cap else z
    res = read_letters(seqs, capped, lid)
    unc = read_letters(seqs, z, lid)
    for b, r in enumerate(res):
        r["lp_u"] = unc[b]["lp"]
        r["text"] = tok.decode(seqs[b], skip_special_tokens=True)
    # the model's own logits for the letters, kept for the test that the float32 read equals them
    r_model = torch.stack([x[:, flat].float() for x in out.logits], 1).cpu()
    for b, r in enumerate(res):
        r["_model_letter_logits0"] = r_model[b, 0].tolist()
        r["_read_letter_logits0"] = capped[b, 0].tolist()
    return res, offs, T


def read_letters(seqs, lg, lid):
    """seqs [B, steps] generated tokens; lg [B, steps, n] the raw logits of the letter tokens, in the order of
    letter_ids (A's tokens, then B's, ...). Per row: lp0 (the five letters renormalized at the first generated token),
    lp and step (the same at the first generated token that is a letter; None and -1 when none is), first."""
    flat = [i for L in LETTERS for i in lid[L]]
    pos = {i: k for k, i in enumerate(flat)}

    def five(b, s):
        per = torch.stack([torch.logsumexp(lg[b, s, [pos[i] for i in lid[L]]], 0) for L in LETTERS])
        return (per - torch.logsumexp(per, 0)).tolist()

    out = []
    for b in range(seqs.shape[0]):
        step = next((s for s in range(seqs.shape[1]) if int(seqs[b, s]) in pos), -1)
        out.append({"lp0": five(b, 0), "lp": five(b, step) if step >= 0 else None, "step": step,
                    "first": int(seqs[b, 0])})
    return out


def log_odds(lp, letter):
    """log P(letter) minus log P(any other letter), from the renormalized log-probabilities."""
    if lp is None:
        return float("nan")
    i = LETTERS.index(letter)
    others = [x for j, x in enumerate(lp) if j != i]
    m = max(others)
    return lp[i] - (m + math.log(sum(math.exp(x - m) for x in others)))
