"""The brand-by-brand read of PLAN.md amendment 2 (question 5), for one model, after its full run.

    python run_brands.py --model <folder or repo@rev> --switch '{}' --brands brands.jsonl --brand-pairs brand_pairs.jsonl
                         --renderings renderings.jsonl --pairs pairs.jsonl --full-work <the full run's work folder>
                         --full-back <the full run's back folder> --work <folder> --back <folder>
                         [--layer N] [--sae <repo@rev:path/to/sae_weights.safetensors> --sae-layer 31] [--batch 8]

Stages (each resumes):
  R  read every brand prompt once: for the table prompts, the close-span mean of every product at the layer and the
     letter probabilities; for the short prompts, the state at the name's last token (at the layer, and at the
     autoencoder's layer when one is given) and the words' log-probabilities at the first answer token
  K  copies: in the on-best pairs with the best product shown first, the brand's name state copied into the original
     prompt's invented name, and the placebo, at question 4's strongest layer; units with their own baselines
  S  scores for every brand, from even and odd trials apart: image, awareness (and the autoencoder's), copy, words,
     and the in-model equity of the renamed prompts; written to back/brands_scores.json

The layer is the full run's primary layer (B.json) unless --layer is given (Llama 3.1 8B and OLMo 3.1 32B).
"""
import argparse
import gzip
import json
import math
import os
import sys
import time
from collections import defaultdict

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mech as M  # noqa: E402
import run_mech as R  # noqa: E402
from run_mech import jl, log, chunks  # noqa: E402

GOOD = ("reliable", "durable", "dependable", "premium", "trustworthy", "solid")
BAD = ("unreliable", "flimsy", "cheap", "generic", "unknown", "questionable")
NEUTRAL = ("black", "white", "metal", "plastic", "small", "large")


def jlz(path):
    with gzip.open(path, "rt", encoding="utf8") as f:
        return [json.loads(l) for l in f if l.strip()]


def word_ids(tok, words):
    """{word: [single-token ids]} over its forms: with and without a leading space, lower case and capitalized."""
    out = {}
    for w in words:
        ids = set()
        for s in (w, " " + w, w.capitalize(), " " + w.capitalize()):
            t = tok.encode(s, add_special_tokens=False)
            if len(t) == 1:
                ids.add(t[0])
        out[w] = sorted(ids)
    return out


def encode_short(tok, r, switch):
    """A short prompt as the only user message; the token positions of the name."""
    text = tok.apply_chat_template([{"role": "user", "content": r["user"]}], add_generation_prompt=True,
                                   tokenize=False, **(switch or {}))
    u0 = text.index(r["user"])
    enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
    s, e = r["name_span"][0] + u0, r["name_span"][1] + u0
    idx = [i for i, (a, b) in enumerate(enc["offset_mapping"]) if b > a and a < e and b > s]
    if not idx or text[enc["offset_mapping"][idx[0]][0]:enc["offset_mapping"][idx[-1]][1]].strip() != r["name"]:
        raise ValueError(f"{r['id']}: the name's tokens do not cover the name")
    return {"id": r["id"], "ids": enc["input_ids"], "n": len(enc["input_ids"]), "name_tokens": idx}


class SAE:
    """A JumpReLU sparse autoencoder (SAELens' saved form): W_enc [d, m], b_enc, W_dec [m, d], b_dec, threshold."""

    def __init__(self, path, device):
        from safetensors.torch import load_file
        w = load_file(path, device="cpu")
        self.W_enc, self.b_enc = w["W_enc"].to(device), w["b_enc"].to(device)
        self.W_dec, self.b_dec, self.th = w["W_dec"].to(device), w["b_dec"].to(device), w["threshold"].to(device)

    @torch.no_grad()
    def encode(self, x):
        pre = (x.float() - self.b_dec) @ self.W_enc + self.b_enc
        return pre * (pre > self.th)

    @torch.no_grad()
    def decode(self, f):
        return f @ self.W_dec + self.b_dec


def resolve_file(spec):
    """repo@revision:path inside the repository, or a local file."""
    if os.path.exists(spec):
        return spec
    from huggingface_hub import hf_hub_download
    repo_rev, path = spec.split(":", 1)
    repo, rev = repo_rev.split("@")
    return hf_hub_download(repo, path, revision=rev)


class BrandRunner(R.Runner):
    def __init__(self, a):
        # the full build's prompts are encoded by R.Runner (for the refit); the brand prompts here
        super().__init__(a)
        self.brands = jl(a.brands)
        self.bpairs = jl(a.brand_pairs)
        self.bidx = {r["id"]: i for i, r in enumerate(self.brands)}
        self.benc = []
        for r in self.brands:
            self.benc.append(encode_short(self.tok, r, self.switch) if r["kind"] == "short" else M.encode(self.tok, r, self.switch))
        B = json.load(open(os.path.join(a.full_back, "B.json")))
        self.layer = a.layer or B["primary_layer"]
        if self.layer not in self.SL:
            sys.exit(f"refused: layer {self.layer} is not a stored layer {self.SL}")
        self.wid = {**word_ids(self.tok, GOOD), **word_ids(self.tok, BAD), **word_ids(self.tok, NEUTRAL)}
        log(f"brands: {len(self.brands)} prompts, layer {self.layer}; words without a single-token form: "
            f"{[w for w, v in self.wid.items() if not v]}")

    # ------------------------------------------------------------ the reliability direction, refitted

    def reliability_directions(self):
        """{category: unit direction} at the layer and the close span, fitted without the category, from the full
        run's stored means; refuses unless it reproduces proj.npz on the existing pairs."""
        N = len(self.rend)
        j = self.SL.index(self.layer)
        X = np.memmap(os.path.join(self.a.full_work, "A_close.f16"), dtype=np.float16, mode="r",
                      shape=(N, 5, len(self.SL), self.d))[:, :, j, :]
        cats = sorted({p["category"] for p in self.pairs})
        ia = np.array([self.idx[p["a"]] for p in self.pairs])
        ib = np.array([self.idx[p["b"]] for p in self.pairs])
        il = np.array([M.LETTERS.index(p["letter"]) for p in self.pairs])
        delta = X[ia, il].astype(np.float32) - X[ib, il].astype(np.float32)
        rel = np.array([p["contrast"] == "reliability" for p in self.pairs])
        pcat = np.array([cats.index(p["category"]) for p in self.pairs])
        U = {}
        for c, cat in enumerate(cats):
            m = rel & (pcat != c)
            v = delta[m].mean(0)
            U[cat] = v / np.linalg.norm(v)
        Z = np.load(os.path.join(self.a.full_back, "proj.npz"))
        k = list(Z["dirs"]).index("rel")
        si = list(Z["spans"]).index("close")
        want = Z["proj"][:, list(Z["layers"]).index(self.layer), si, k].astype(np.float32)
        got = np.array([float(delta[n] @ U[self.pairs[n]["category"]]) for n in range(len(self.pairs))])
        err = np.abs(got - want) / (np.abs(want) + 1.0)
        if err.max() > 1e-2:
            sys.exit(f"refused: the refitted reliability direction does not reproduce proj.npz (largest error {err.max():.3g})")
        log(f"reliability direction refitted at layer {self.layer}; reproduces proj.npz (largest scaled error {err.max():.2e})")
        return U

    # ------------------------------------------------------------ stage R

    def stage_r(self):
        out_path = os.path.join(self.a.work, "BR.jsonl")
        done = R.done_ids(out_path, lambda r: r["id"])
        layers = sorted({self.layer} | ({self.a.sae_layer} if self.a.sae else set()))
        fout = open(out_path, "a", encoding="utf8")
        vec_path = os.path.join(self.a.work, "BR_vectors.npz")
        vecs = dict(np.load(vec_path)) if os.path.exists(vec_path) else {}
        ls = [(L, "close") for L in M.LETTERS]
        flat = [i for w in self.wid for i in self.wid[w]]

        tab = [i for i, r in enumerate(self.brands) if r["kind"] != "short" and r["id"] not in done]
        for chunk in chunks(sorted(tab, key=lambda i: self.benc[i]["n"]), self.batch):
            encs = [self.benc[i] for i in chunk]
            store = {}

            def mk(offs, T, device, encs=encs, store=store):
                W = M.span_weights(encs, offs, T, ls, device)
                return {self.layer: M.reader(store, self.layer, W)}
            res, _, _ = M.generate(self.model, self.tok, encs, 1, mk, self.layers, self.lid)
            for n, i in enumerate(chunk):
                r = self.brands[i]
                vecs[r["id"]] = store[self.layer][n].numpy().astype(np.float16)    # [5, d], the five close spans
                fout.write(json.dumps({"id": r["id"], "kind": r["kind"], "lp": res[n]["lp0"]}) + "\n")
            fout.flush()
        short = [i for i, r in enumerate(self.brands) if r["kind"] == "short" and r["id"] not in done]
        for chunk in chunks(sorted(short, key=lambda i: self.benc[i]["n"]), self.batch):
            encs = [self.benc[i] for i in chunk]
            store = {}

            def mk(offs, T, device, encs=encs, store=store):
                W = torch.zeros((len(encs), 1, T), device=device)
                for b, e in enumerate(encs):
                    W[b, 0, e["name_tokens"][-1] + offs[b]] = 1.0
                return {li: M.reader(store, li, W) for li in layers}
            head = self.model.get_output_embeddings()
            Wh = head.weight[flat].float()
            got = []
            h = head.register_forward_hook(lambda m, i, o: got.append(i[0][:, -1, :].float() @ Wh.T))
            try:
                gen, _, _ = M.generate(self.model, self.tok, encs, 4, mk, self.layers, self.lid)
            finally:
                h.remove()
            z = got[0].cpu()
            cap = getattr(M.text_config(self.model), "final_logit_softcapping", None)
            z = cap * torch.tanh(z / cap) if cap else z
            # word log-probabilities need the whole vocabulary's normalizer: one more forward pass for it
            with torch.no_grad():
                ids, att, offs = M.collate(encs, self.tok.pad_token_id, next(self.model.parameters()).device)
                pos = (att.cumsum(-1) - 1).clamp(min=0)
                logits = self.model(input_ids=ids, attention_mask=att, position_ids=pos, logits_to_keep=1).logits[:, -1, :].float()
                lse = torch.logsumexp(logits, -1).cpu()
            for n, i in enumerate(chunk):
                r = self.brands[i]
                for li in layers:
                    vecs[f"{r['id']}|{li}"] = store[li][n, 0].numpy().astype(np.float16)
                lw = {}
                k = 0
                for w in self.wid:
                    m = len(self.wid[w])
                    lw[w] = float(torch.logsumexp(z[n, k:k + m], 0) - lse[n]) if m else None
                    k += m
                # what the model wrote first: if it opens with markup, the words at the first token say little
                fout.write(json.dumps({"id": r["id"], "kind": "short", "words": lw,
                                       "first_text": gen[n]["text"][:24]}) + "\n")
            fout.flush()
        fout.close()
        np.savez(vec_path, **vecs)

    # ------------------------------------------------------------ stage K

    def copy_layer(self):
        """The layer of question 4 with the largest forward copy minus placebo without the information."""
        sys.path.insert(0, HERE)
        import analyze as AN
        q4 = AN.question4(jlz(os.path.join(self.a.full_back, "N.jsonl.gz")))
        eff = {li: v["info0"]["forward_minus_placebo"] for li, v in q4["layers"].items()
               if v["info0"]["forward_minus_placebo"] is not None}
        return (max(eff, key=eff.get) if eff else None), q4["supported"]

    def stage_k(self):
        lq, supported = self.copy_layer()
        json.dump({"copy_layer": lq, "question4_supported": supported},
                  open(os.path.join(self.a.back, "COPY_LAYER.json"), "w"))
        if lq is None:
            log("K: no layer of question 4 to copy at")
            return
        out_path = os.path.join(self.a.work, "BK.jsonl")
        done = R.done_ids(out_path, lambda r: (r["pair"], r["mode"]) if r["role"] == "copy" else None)
        pp = [p for p in self.bpairs if p["contrast"] == "onbest" and p["best_first"]]
        fout = open(out_path, "a", encoding="utf8")

        def last2(e, L):
            return [e["spans"][L]["namebrand"][-1], e["spans"][L]["brand"][-1]]

        def build(size, dups_left):
            units = []
            for k, p in enumerate(pp):
                modes = [m for m in ("copy", "placebo") if (k, m) not in done]
                if not modes:
                    continue
                ea, eb = self.benc[self.bidx[p["a"]]], self.benc[self.bidx[p["b"]]]   # a on best, b original
                encs = [ea, eb] + [eb] * len(modes)
                moves = [(0, last2(ea, p["best"]) if m == "copy" else last2(ea, p["partner"]), 2 + n, last2(eb, p["best"]))
                         for n, m in enumerate(modes)]
                uid = "K" + os.urandom(6).hex()

                def make_fns(offs, T, device, moves=moves):
                    return {lq: M.patcher([(s, [i + offs[s] for i in sp], t, [i + offs[t] for i in tp]) for s, sp, t, tp in moves])}

                def on_result(res, k=k, p=p, modes=modes, uid=uid):
                    head = {"uid": uid, "pair": k, "brand": p["brand"], "table": p["table"], "category": p["category"],
                            "trial": p["trial"], "layer": lq}
                    rows = [dict(head, role="base_b", **R.outcome(res[1], p["best"]))]
                    for n, m in enumerate(modes):
                        rows.append(dict(head, role="copy", mode=m, **R.outcome(res[2 + n], p["best"])))
                        done.add((k, m))
                    for x in rows:
                        fout.write(json.dumps(x) + "\n")
                    fout.flush()
                units.append((encs, make_fns, on_result, False))
            # two pairs' units fit one batch of 8; run_units runs one unit a batch, so units stay small
            return units
        self.run_units(build, 3, "K", out_path, "BK.jsonl.gz")
        fout.close()

    # ------------------------------------------------------------ stage S

    def stage_s(self):
        U = self.reliability_directions()
        V = dict(np.load(os.path.join(self.a.work, "BR_vectors.npz")))
        BR = {x["id"]: x for x in jl(os.path.join(self.a.work, "BR.jsonl"))}
        # PLAN.md's unit is the brand within its category: every score is kept under "brand|category" (10 of the 63
        # brands are in two or more categories), and every value is also written as a row (brand, category, table,
        # trial, phrasing), so that the analysis can split halves and resample tables without another job
        scores = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))   # unit -> score -> half -> values
        phr = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))      # unit -> score -> phrasing -> values
        rows_out = []
        unit = lambda b, c: f"{b}|{c}"  # noqa: E731

        def row(score, brand, category, value, table=None, trial=None, phrasing=None):
            rows_out.append({"score": score, "brand": brand, "category": category, "table": table, "trial": trial,
                             "phrasing": phrasing, "value": float(value)})
        # image, and the in-model equity of the renamed prompts
        for p in self.bpairs:
            if p["contrast"] != "renamed":
                continue
            L = M.LETTERS.index(p["letter"])
            d = V[p["a"]][L].astype(np.float32) - V[p["b"]][L].astype(np.float32)
            h = p["trial"] % 2
            u = unit(p["brand"], p["category"])
            scores[u]["image"][h].append(float(d @ U[p["category"]]))
            row("image", p["brand"], p["category"], d @ U[p["category"]], p["table"], p["trial"])
            la, lb = BR[p["a"]]["lp"], BR[p["b"]]["lp"]
            if la and lb:
                scores[u]["renamed_equity"][h].append(math.exp(la[L]) - math.exp(lb[L]))
                row("renamed_equity", p["brand"], p["category"], math.exp(la[L]) - math.exp(lb[L]), p["table"], p["trial"])
        # awareness: real against invented names, each name's prompts held out when it is scored
        shorts = [r for r in self.brands if r["kind"] == "short"]
        out_extra = {}
        for li, tag in [(self.layer, "awareness")] + ([(self.a.sae_layer, "awareness_sae")] if self.a.sae else []):
            X = np.stack([V[f"{r['id']}|{li}"].astype(np.float32) for r in shorts])
            if tag == "awareness_sae":
                sae = SAE(resolve_file(self.a.sae), "cuda" if torch.cuda.is_available() else "cpu")
                xt = torch.tensor(X, device=sae.W_enc.device)
                F = sae.encode(xt)
                rec = sae.decode(F)
                fve = 1 - float(((xt - rec) ** 2).sum() / ((xt - xt.mean(0)) ** 2).sum())
                X = F.cpu().numpy()
                out_extra["sae_fraction_of_variance_explained"] = fve
                # described beside the control (12089: the variance explained was -0.005 on the pilot's 192 states, whose
                # spread around their own mean is small): the latents active a state (the autoencoder was trained with
                # about 100), the error relative to the states' squared norm, and the cosine of a state with its
                # reconstruction
                out_extra["sae_active_latents_mean"] = float((F > 0).sum(1).float().mean())
                out_extra["sae_relative_error"] = float(((xt - rec) ** 2).sum() / (xt ** 2).sum())
                out_extra["sae_cosine_mean"] = float(torch.nn.functional.cosine_similarity(xt, rec, dim=1).mean())
            names = np.array([r["name"] for r in shorts])
            real = np.array([r["name_kind"] == "real" for r in shorts])
            ntok = np.array([len(self.benc[self.bidx[r["id"]]]["name_tokens"]) for r in shorts])
            correct, correct_eq = [], []
            for nm in sorted(set(names)):
                m = names == nm
                tr = ~m
                if tag == "awareness":
                    w = X[tr & real].mean(0) - X[tr & ~real].mean(0)
                    w /= np.linalg.norm(w)
                    s = X[m] @ w
                    thr = 0.5 * ((X[tr & real] @ w).mean() + (X[tr & ~real] @ w).mean())
                else:
                    diff = X[tr & real].mean(0) - X[tr & ~real].mean(0)
                    j = int(np.argmax(diff))
                    s = X[m][:, j]
                    thr = 0.5 * (X[tr & real][:, j].mean() + X[tr & ~real][:, j].mean())
                ok = ((s > thr) == real[m])
                correct += list(ok)
                same = ntok[m][0]
                correct_eq.append((same, list(ok)))
                # one row a held-out prompt, real or invented, with the name's token count: every 1-token name is real,
                # so the control is computed in the analysis as balanced accuracy within token counts that hold both
                # kinds (PLAN.md, amendment 2, change of about 5:30 AM)
                for r_, o, n_ in zip([r for r in shorts if r["name"] == nm], ok, ntok[m]):
                    rows_out.append({"score": f"{tag}_holdout", "brand": nm, "category": r_["category"], "table": None,
                                     "trial": None, "phrasing": r_.get("phrasing", 0), "value": float(o),
                                     "name_kind": "real" if real[m][0] else "invented", "tokens": int(n_)})
                if real[m][0]:       # the name's prompts in every category were held out above; scored by category
                    for r_, v in zip([r for r in shorts if r["name"] == nm], s):
                        u = unit(nm, r_["category"])
                        for h in (0, 1):
                            scores[u][tag][h].append(float(v))      # a name-level score, the same in both halves
                        phr[u][tag][r_.get("phrasing", 0)].append(float(v))   # its reliability is across phrasings
                        row(tag, nm, r_["category"], v, phrasing=r_.get("phrasing", 0))
            out_extra[f"{tag}_held_out_accuracy"] = float(np.mean(correct))
            by_len = defaultdict(list)
            for n_, oks in correct_eq:
                by_len[n_] += oks
            out_extra[f"{tag}_accuracy_by_name_tokens"] = {str(k): float(np.mean(v)) for k, v in by_len.items()}
        # words: the brand's quality score minus the mean of the invented names in its category, and the neutral one
        inv_by_cat = defaultdict(lambda: defaultdict(list))
        wrow = {}
        for r in shorts:
            lw = BR[r["id"]]["words"]

            def mean_of(ws):
                v = [lw[w] for w in ws if lw.get(w) is not None]
                return float(np.mean(v)) if v else None
            q = None if mean_of(GOOD) is None or mean_of(BAD) is None else mean_of(GOOD) - mean_of(BAD)
            nt = mean_of(NEUTRAL)
            wrow[r["id"]] = (q, nt)
            if r["name_kind"] == "invented":
                inv_by_cat[(r["category"], r.get("phrasing", 0))]["q"].append(q)
                inv_by_cat[(r["category"], r.get("phrasing", 0))]["n"].append(nt)
        for r in shorts:
            if r["name_kind"] != "real":
                continue
            q, nt = wrow[r["id"]]
            ref = inv_by_cat[(r["category"], r.get("phrasing", 0))]
            u, k = unit(r["name"], r["category"]), r.get("phrasing", 0)
            refq = [v for v in ref["q"] if v is not None]
            refn = [v for v in ref["n"] if v is not None]
            if q is not None and refq:
                phr[u]["words"][k].append(q - float(np.mean(refq)))
                row("words", r["name"], r["category"], q - float(np.mean(refq)), phrasing=k)
            if nt is not None and refn:
                phr[u]["words_neutral"][k].append(nt - float(np.mean(refn)))
                row("words_neutral", r["name"], r["category"], nt - float(np.mean(refn)), phrasing=k)
            for h in (0, 1):
                if q is not None and refq:
                    scores[u]["words"][h].append(q - float(np.mean(refq)))
                if nt is not None and refn:
                    scores[u]["words_neutral"][h].append(nt - float(np.mean(refn)))
        # copy: the copy minus the placebo, against the unit's original
        kp = os.path.join(self.a.work, "BK.jsonl")
        if os.path.exists(kp):
            K = jl(kp)
            base = {x["uid"]: x["lo"] for x in K if x["role"] == "base_b"}
            by = defaultdict(dict)
            for x in K:
                if x["role"] == "copy" and x["lo"] is not None and base.get(x["uid"]) is not None:
                    by[(x["pair"], x["brand"], x["category"], x["table"], x["trial"])][x["mode"]] = x["lo"] - base[x["uid"]]
            for (k, b, c, t, trial), v in by.items():
                if "copy" in v and "placebo" in v:
                    scores[unit(b, c)]["copy"][trial % 2].append(v["copy"] - v["placebo"])
                    row("copy", b, c, v["copy"] - v["placebo"], t, trial)
        cat_of = {}
        tables_of = defaultdict(set)
        for p in self.bpairs:
            u = unit(p["brand"], p["category"])
            cat_of[u] = (p["brand"], p["category"])
            tables_of[u].add(p["table"])
        with gzip.open(os.path.join(self.a.back, "brand_rows.jsonl.gz"), "wt", encoding="utf8") as f:
            for x in rows_out:
                f.write(json.dumps(x) + "\n")
        # the name-level scores' reliability across phrasings: Spearman's correlation between two phrasings over the
        # real brands, averaged over the pairs, and the Spearman-Brown value for all of them
        n_ph = 1 + max((r.get("phrasing", 0) for r in shorts), default=0)
        rel = {}
        for s in ("awareness", "awareness_sae", "words", "words_neutral"):
            names_s = [b for b in phr if s in phr[b] and all(phr[b][s].get(k) for k in range(n_ph))]
            if n_ph < 2 or len(names_s) < 4:
                continue
            means = np.array([[np.mean(phr[b][s][k]) for k in range(n_ph)] for b in names_s])
            rs = []
            for i in range(n_ph):
                for j in range(i + 1, n_ph):
                    ri = np.argsort(np.argsort(means[:, i]))
                    rj = np.argsort(np.argsort(means[:, j]))
                    rs.append(float(np.corrcoef(ri, rj)[0, 1]))
            r_ = float(np.mean(rs))
            rel[s] = {"mean_pairwise_spearman": r_, "spearman_brown": n_ph * r_ / (1 + (n_ph - 1) * r_)
                      if r_ > -1 / (n_ph - 1) else None, "brands": len(names_s)}
        out_extra["reliability_across_phrasings"] = rel
        out = {"layer": self.layer, "unit": "brand|category", **out_extra,
               "brands": {b: {"brand": cat_of.get(b, (b.split("|")[0], None))[0],
                              "category": cat_of.get(b, (None, b.split("|")[-1]))[1], "tables": sorted(tables_of.get(b, [])),
                              "scores": {s: {"even": (float(np.mean(v[0])) if v[0] else None),
                                             "odd": (float(np.mean(v[1])) if v[1] else None),
                                             "n": len(v[0]) + len(v[1])}
                                         for s, v in d.items()},
                              "by_phrasing": {s: [float(np.mean(phr[b][s][k])) if phr[b][s].get(k) else None
                                                  for k in range(n_ph)] for s in phr.get(b, {})}}
                          for b, d in scores.items()}}
        json.dump(out, open(os.path.join(self.a.back, "brands_scores.json"), "w"), indent=1)
        log(f"S: {len(out['brands'])} brands scored; " + json.dumps({k: v for k, v in out_extra.items()}))


def main(argv=None):
    ap = argparse.ArgumentParser()
    for k in ("--model", "--brands", "--brand-pairs", "--renderings", "--pairs", "--full-work", "--full-back", "--work",
              "--back"):
        ap.add_argument(k, required=True)
    ap.add_argument("--model-key", default="")
    ap.add_argument("--switch", default="{}")
    ap.add_argument("--layer", type=int, default=0)
    ap.add_argument("--sae", default="")
    ap.add_argument("--sae-layer", type=int, default=31)
    ap.add_argument("--stages", default="R,K,S")
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--max-new", type=int, default=12)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--calib", default="")
    ap.add_argument("--calib-stop", action="store_true")
    a = ap.parse_args(argv)
    os.makedirs(a.work, exist_ok=True)
    os.makedirs(a.back, exist_ok=True)
    R.restore_back(a.work, a.back)
    R.restore_back(a.full_work, a.full_back)
    # the full run's order record guards the refit from its stored means
    if open(os.path.join(a.full_work, "ORDER.sha256")).read().strip() == "":
        sys.exit("refused: the full run has no prompt-order record")
    run = BrandRunner(argparse.Namespace(**{**vars(a), "work": a.work}))
    full_order = open(os.path.join(a.full_work, "ORDER.sha256")).read().strip()
    if full_order != run.order:
        sys.exit("refused: the full build's prompts are not in the order of the full run's read stage")
    for st in a.stages.split(","):
        marker = os.path.join(a.work, f"DONE_{st}")
        if os.path.exists(marker):
            log(f"stage {st} already done")
            continue
        t0 = time.time()
        {"R": run.stage_r, "K": run.stage_k, "S": run.stage_s}[st]()
        R.save_back(a.work, a.back)
        open(marker, "w").write(time.strftime("%Y-%m-%d %H:%M"))
        log(f"stage {st} done in {time.time() - t0:.0f} s")
    for f in ("BR.jsonl", "BK.jsonl"):
        p = os.path.join(a.work, f)
        if os.path.exists(p):
            run.copy_gz(p, f + ".gz")
    R.save_back(a.work, a.back)
    return run


if __name__ == "__main__":
    main()
