"""Runs step B6 for one model, in the stages of PLAN.md:

  A  read: every prompt once, the span means of every product at the stored layers (float16, on scratch), the letter
     probabilities and a greedy continuation (12 tokens for the dom2 prompts, 1 for the added kinds)
  P  patch: the best product's post-name (and, apart, close) activations of the crossed prompt written into the
     original prompt, at each stored layer, for the name pairs at the best product
  N  copies (amendment 1): the best product's name state copied between the crossed and the original prompt, forward
     and reverse, and the placebo copies from the partner's block, at each stored layer
  B  directions: pair differences, directions with each category left out, projections, the primary layer (from the
     patch), the name vectors and the random vectors for the pushes
  C  pushes: the name vector and four random vectors, added at the best product or at the familiar products
  D  the version record

    python run_mech.py --model <folder or repo@revision> --switch '{}' --renderings renderings.jsonl --pairs pairs.jsonl
                       --work <scratch folder> --back <folder that comes back> [--stages A,P,N,B,C,D] [--batch 8]
                       [--calib calib.json --model-key gemma31b [--calib-stop]] [--device cuda]

Stages P, N and C run in units (PLAN.md, change of about midnight on 20 November): a batch is one unit, which holds
one item or one pair together with its own unpushed or unpatched prompt, and every row carries the unit's id (uid) so
that each change is taken against the baseline of its own batch. In the first 100 units of each of these stages the
baseline is run twice (role "dup"), which measures the noise between two copies of one prompt in one batch.

Each stage writes its files and a marker; a stage with its marker is skipped when the job runs again. Stage A continues
from its last written prompt; stages P, N and C rebuild units for the rows not yet written, each with its own baseline.
Running out of memory rebuilds the units at half the size.
"""
import argparse
import gzip
import json
import math
import os
import platform
import shutil
import sys
import time
import uuid
from collections import defaultdict

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
for p in (os.path.join(HERE, "..", "study2"),):
    if os.path.isdir(p):
        sys.path.insert(0, os.path.abspath(p))
import mech as M  # noqa: E402
from parse_answer import pick  # noqa: E402  (Study 2's parser; the bundle holds a copy beside this file)

SEED = 20261120
GRID_PRIMARY = (-4.0, -2.0, -1.0, 1.0, 2.0, 4.0)
GRID_SECONDARY = (-1.0, 1.0)
RANDOM = ("iso0", "iso1", "cov0", "cov1")
SPAN_I = {s: i for i, s in enumerate(M.SPANS)}
DUP_UNITS = 100


def jl(path):
    with open(path, encoding="utf8") as f:
        return [json.loads(l) for l in f if l.strip()]


def done_ids(path, key):
    if not os.path.exists(path):
        return set()
    return {key(json.loads(l)) for l in open(path, encoding="utf8") if l.strip()}


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


BACK_COPY = "_back"


def restore_back(work, back):
    """A job that is submitted again runs in a new job folder, so its back folder starts empty, while the work folder
    on scratch keeps the DONE markers of the stages already finished. Every runner keeps a copy of its back folder in
    <work>/_back/ (save_back, after every stage) and copies into back, at the start of every run, each file that back
    lacks, so that a resumed stage finds the files of the stages before it (B.json, MANIP.json, VALIDATION.json)."""
    src = os.path.join(work, BACK_COPY)
    n = 0
    if os.path.isdir(src) and os.path.abspath(src) != os.path.abspath(back):
        for root, _, files in os.walk(src):
            rel = os.path.relpath(root, src)
            for f in files:
                dst = os.path.join(back, rel, f)
                if not os.path.exists(dst):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(os.path.join(root, f), dst)
                    n += 1
    if n:
        log(f"{n} files of an earlier run copied from {src} into {back}")
    return n


def save_back(work, back):
    """Copies every file of back into <work>/_back/."""
    dst = os.path.join(work, BACK_COPY)
    if os.path.abspath(dst) == os.path.abspath(back):
        return
    for root, _, files in os.walk(back):
        rel = os.path.relpath(root, back)
        os.makedirs(os.path.join(dst, rel), exist_ok=True)
        for f in files:
            shutil.copy2(os.path.join(root, f), os.path.join(dst, rel, f))


def resolve_model(spec):
    """A folder, or repo@revision resolved in the Hugging Face cache (HF_HOME), downloaded only if it is not there."""
    if os.path.isdir(spec):
        return spec
    from huggingface_hub import snapshot_download
    repo, rev = spec.split("@")
    try:
        return snapshot_download(repo, revision=rev, local_files_only=True)
    except Exception:
        return snapshot_download(repo, revision=rev)


def outcome(r, best):
    """The fields of one generated row: log-odds of the best product (capped as the model caps, and uncapped), its
    probability, the letter step, the parser's letter."""
    letter, how = pick(r["text"])
    i = M.LETTERS.index(best)
    return {"lo": None if r["lp"] is None else round(M.log_odds(r["lp"], best), 4),
            "lo_u": None if r.get("lp_u") is None else round(M.log_odds(r["lp_u"], best), 4),
            "pb": None if r["lp"] is None else round(math.exp(r["lp"][i]), 6),
            "step": r["step"], "parsed": letter, "how": how, "text": r["text"][:24]}


def chunks(xs, n):
    return [xs[i:i + n] for i in range(0, len(xs), n)]


class Runner:
    def __init__(self, a):
        self.a = a
        a.model = resolve_model(a.model)
        self.tok, self.model = M.load_model(a.model, a.device, getattr(torch, a.dtype))
        self.layers = M.decoder_layers(self.model)
        self.n_layers = len(self.layers)
        self.d = M.text_config(self.model).hidden_size
        self.SL = M.stored_layers(self.n_layers)
        self.lid = M.letter_ids(self.tok)
        self.switch = json.loads(a.switch or "{}")
        self.rend = jl(a.renderings)
        self.pairs = jl(a.pairs)
        self.idx = {r["id"]: i for i, r in enumerate(self.rend)}
        # amendment 1's guard: the read stage's arrays are indexed by the position of each prompt in this file
        import hashlib
        self.order = hashlib.sha256("\n".join(r["id"] for r in self.rend).encode()).hexdigest()
        self.order_path = os.path.join(a.work, "ORDER.sha256")
        if os.path.exists(self.order_path) and open(self.order_path).read().strip() != self.order:
            sys.exit(f"refused: the prompts are in another order than when the read stage ran ({self.order_path})")
        self.batch = a.batch
        os.makedirs(a.work, exist_ok=True)
        os.makedirs(a.back, exist_ok=True)
        tp = os.path.join(a.work, "TIMING.json")
        self.timing = json.load(open(tp)) if os.path.exists(tp) else {}
        self.max_abs = {}
        t0 = time.time()
        self.limit = M.prompt_limit(self.model)
        self.encs = [M.encode(self.tok, r, self.switch, self.limit) for r in self.rend]
        self.max_n = max(e["n"] for e in self.encs)
        log(f"{len(self.encs)} prompts encoded in {time.time() - t0:.0f} s; longest {self.max_n} tokens "
            f"(limit {self.limit}); {self.n_layers} layers, width {self.d}; stored layers {self.SL}")

    # ------------------------------------------------------------ batching with a back-off on memory (stage A)

    def run_rows(self, rows, max_new, make_fns_for, on_result, label, checkpoint=None):
        """rows: a list of row specs; make_fns_for(rows_in_batch) -> (encs, make_fns); on_result(rows, results);
        checkpoint() runs every 10 minutes, so that a job stopped by its time limit still returns what it ran."""
        i, t0, n0 = 0, time.time(), len(rows)
        last = time.time()
        bs = self.batch
        while i < len(rows):
            chunk = rows[i:i + bs]
            encs, make_fns = make_fns_for(chunk)
            try:
                res, offs, T = M.generate(self.model, self.tok, encs, max_new, make_fns, self.layers, self.lid)
            except torch.cuda.OutOfMemoryError:
                torch.cuda.empty_cache()
                if bs == 1:
                    raise
                bs = max(1, bs // 2)
                log(f"{label}: out of memory, batch {bs}")
                continue
            on_result(chunk, res)
            i += len(chunk)
            if checkpoint and time.time() - last > 600:
                checkpoint()
                last = time.time()
            if (i // len(chunk)) % 25 == 0 or i == len(rows):
                el = time.time() - t0
                log(f"{label}: {i} of {n0} rows, {el:.0f} s, {el / max(i, 1):.3f} s a row, batch {bs}")
        self.batch = bs
        return time.time() - t0

    # ------------------------------------------------------------ units (stages P, N and C)

    def run_units(self, build, min_size, label, out_path, back_name):
        """build(size, dups_left) -> units for the rows not yet written; a unit is (encs, make_fns, on_result, has_dup)
        and is run as one batch. On running out of memory the units are rebuilt at half the size."""
        size, t0, n, last = self.batch, time.time(), 0, time.time()
        dups = DUP_UNITS
        while True:
            units = build(size, dups)
            if not units:
                break
            log(f"{label}: {len(units)} units of at most {size} prompts")
            stopped = False
            for encs, make_fns, on_result, has_dup in units:
                try:
                    res, _, _ = M.generate(self.model, self.tok, encs, self.a.max_new, make_fns, self.layers, self.lid)
                except torch.cuda.OutOfMemoryError:
                    torch.cuda.empty_cache()
                    if size <= min_size:
                        raise
                    size = max(min_size, size // 2)
                    log(f"{label}: out of memory, units of {size}")
                    stopped = True
                    break
                on_result(res)
                dups -= has_dup
                n += 1
                if time.time() - last > 600:
                    self.copy_gz(out_path, back_name)
                    last = time.time()
                if n % 100 == 0:
                    log(f"{label}: {n} units, {time.time() - t0:.0f} s, {(time.time() - t0) / n:.2f} s a unit")
            if not stopped:
                break
        self.batch = size
        self.copy_gz(out_path, back_name)
        return time.time() - t0

    # ------------------------------------------------------------ stage A

    def need_order(self):
        if not os.path.exists(self.order_path):
            sys.exit("refused: the read stage's arrays have no record of the prompt order (ORDER.sha256)")

    def stage_a(self):
        open(self.order_path, "w").write(self.order)
        N, nL, d = len(self.rend), len(self.SL), self.d
        shape = (N, 5, nL, d)
        mm = {}
        for s in M.SPANS:
            path = os.path.join(self.a.work, f"A_{s}.f16")
            mode = "r+" if os.path.exists(path) else "w+"
            mm[s] = np.memmap(path, dtype=np.float16, mode=mode, shape=shape)
        out_path = os.path.join(self.a.work, "A.jsonl")
        done = done_ids(out_path, lambda r: r["id"])
        ls = [(L, s) for L in M.LETTERS for s in M.SPANS]
        fout = open(out_path, "a", encoding="utf8")
        total = 0.0
        for kind_set, max_new in ((("dom2",), self.a.max_new), (("specswap", "poorrel"), 1)):
            rows = [i for i, r in enumerate(self.rend) if r["kind"] in kind_set and r["id"] not in done]
            rows.sort(key=lambda i: self.encs[i]["n"])
            store = {}

            def make_for(chunk):
                encs = [self.encs[i] for i in chunk]

                def make_fns(offs, T, device):
                    W = M.span_weights(encs, offs, T, ls, device)
                    return {li: M.reader(store, li, W) for li in self.SL}
                return encs, make_fns

            def on_result(chunk, res):
                for j, li in enumerate(self.SL):
                    x = store[li].numpy().reshape(len(chunk), 5, len(M.SPANS), d)
                    x16 = x.astype(np.float16)
                    if not np.isfinite(x16).all():
                        sys.exit(f"stopped: a span mean at layer {li} is not finite in float16 "
                                 f"(largest absolute value {np.abs(x).max():.1f})")
                    self.max_abs[li] = max(self.max_abs.get(li, 0.0), float(np.abs(x).max()))
                    for s, si in SPAN_I.items():
                        mm[s][chunk, :, j, :] = x16[:, :, si, :]
                for i, r in zip(chunk, res):
                    rr = self.rend[i]
                    letter, how = pick(r["text"])
                    rec = {"id": rr["id"], "kind": rr["kind"], "table": rr["table"], "category": rr["category"],
                           "names": rr["names"], "info": rr["info"], "rung": rr["rung"], "best": rr["best"],
                           "n": self.encs[i]["n"], "lp0": r["lp0"], "lp": r["lp"], "lp_u": r["lp_u"],
                           "step": r["step"], "first": r["first"], "text": r["text"], "parsed": letter, "how": how,
                           "lo": M.log_odds(r["lp"], rr["best"]) if r["lp"] else None}
                    fout.write(json.dumps(rec) + "\n")
                fout.flush()
                for s in mm:
                    mm[s].flush()

            total += self.run_rows(rows, max_new, make_for, on_result, f"A {kind_set[0]}",
                                   lambda: self.copy_gz(out_path, "A.jsonl.gz"))
        fout.close()
        self.timing["A"] = total
        self.timing["A_span_mean_max_abs"] = {str(k): round(v, 1) for k, v in sorted(self.max_abs.items())}
        log(f"A: largest absolute span mean by layer {self.timing['A_span_mean_max_abs']}")
        self.copy_gz(out_path, "A.jsonl.gz")
        self.calibration()

    def calibration(self):
        """PLAN.md: at no push, the mean probability of the best product by name and information cell (equal weight
        for every table) against the share of best picks in the same model's vLLM runs."""
        rows = [r for r in jl(os.path.join(self.a.work, "A.jsonl")) if r["kind"] == "dom2"]
        mine = defaultdict(lambda: defaultdict(list))
        for r in rows:
            p = math.exp(r["lp"][M.LETTERS.index(r["best"])]) if r["lp"] else float("nan")
            mine[(r["names"], r["info"])][r["table"]].append(p)
        first_letter = sum(r["step"] == 0 for r in rows) / len(rows)
        no_letter = sum(r["step"] < 0 for r in rows) / len(rows)
        agree = sum(r["parsed"] == (M.LETTERS[int(np.argmax(r["lp"]))] if r["lp"] else "") for r in rows) / len(rows)
        out = {"first_token_is_letter": first_letter, "no_letter_token": no_letter,
               "parser_agrees_with_most_probable": agree, "cells": {}}
        ref = json.load(open(self.a.calib)).get(self.a.model_key, {}) if self.a.calib else {}
        worst = 0.0
        for (names, info), by_t in sorted(mine.items()):
            m = float(np.mean([np.nanmean(v) for v in by_t.values()])) * 100
            refs = [ref[f"{t}|{names}|{info}"] for t in by_t if f"{t}|{names}|{info}" in ref]
            r_ = float(np.mean(refs)) * 100 if refs else None
            out["cells"][f"{names}|{info}"] = {"p_best": round(m, 2), "vllm_share": None if r_ is None else round(r_, 2),
                                              "tables": len(by_t)}
            if r_ is not None:
                worst = max(worst, abs(m - r_))
        out["largest_miss_points"] = round(worst, 2)
        out["passes"] = bool(ref) and worst <= 5.0
        json.dump(out, open(os.path.join(self.a.back, "CALIBRATION.json"), "w"), indent=1)
        log(f"calibration: {json.dumps(out)}")
        if self.a.calib_stop and not out["passes"]:
            sys.exit("stopped: the check against Study 2's runs failed (PLAN.md); see CALIBRATION.json")
        if no_letter > 0.05:
            sys.exit(f"stopped: {no_letter:.1%} of the dom2 continuations hold no letter token (over 5 per cent)")

    # ------------------------------------------------------------ copy units (stages P and N)

    def copy_units(self, stage, pp, jobs_for, size, dups_left, fout, done):
        """Units for the copy stages. For pair k, a unit is [a, b, (b again)] + targets, where a is the crossed prompt
        and b the original; rows 0 and 1 are unpatched (b's baseline, and a's in stage N) and also the sources.
        jobs_for(k) -> [(key, target 'a' or 'b', layer, source row 0 or 1, source positions, target positions)]."""
        units = []
        for k, p in enumerate(pp):
            ea, eb = self.encs[self.idx[p["a"]]], self.encs[self.idx[p["b"]]]
            pending = [j for j in jobs_for(k) if (k,) + j[0] not in done]
            if not pending:
                continue
            for group in chunks(pending, max(1, size - 2 - (1 if len(units) < dups_left else 0))):
                dup = len(units) < dups_left
                encs = [ea, eb] + ([eb] if dup else []) + [ea if j[1] == "a" else eb for j in group]
                first = 3 if dup else 2
                uid = stage + uuid.uuid4().hex[:12]

                def make_fns(offs, T, device, group=group, first=first):
                    by_layer = defaultdict(list)
                    for n, (key, tgt, li, src, sp, tp) in enumerate(group):
                        r = first + n
                        by_layer[li].append((src, [i + offs[src] for i in sp], r, [i + offs[r] for i in tp]))
                    return {li: M.patcher(mv) for li, mv in by_layer.items()}

                def on_result(res, k=k, p=p, group=group, dup=dup, first=first, uid=uid):
                    base = {"uid": uid, "pair": k, "a": p["a"], "b": p["b"], "table": p["table"],
                            "category": p["category"], "info": p["info"], "rung": p["rung"]}
                    rows = [dict(base, role="base_a", **outcome(res[0], p["best"])),
                            dict(base, role="base_b", **outcome(res[1], p["best"]))]
                    if dup:
                        rows.append(dict(base, role="dup_b", **outcome(res[2], p["best"])))
                    for n, (key, tgt, li, src, sp, tp) in enumerate(group):
                        rows.append(dict(base, role="copy", key=list(key), target=tgt, layer=li,
                                         **outcome(res[first + n], p["best"])))
                        done.add((k,) + key)
                    for x in rows:
                        fout.write(json.dumps(x) + "\n")
                    fout.flush()
                units.append((encs, make_fns, on_result, dup))
        return units

    def name_pairs(self):
        return [p for p in self.pairs if p["contrast"] == "name" and p["is_best"]]

    def stage_p(self):
        """The best product's post-name (and, apart, close) states of the crossed prompt written into the original."""
        pp = self.name_pairs()
        out_path = os.path.join(self.a.work, "P.jsonl")
        done = done_ids(out_path, lambda r: (r["pair"],) + tuple(r["key"]) if r["role"] == "copy" else None)
        skipped = set()

        def jobs_for(k):
            p = pp[k]
            ea, eb = self.encs[self.idx[p["a"]]], self.encs[self.idx[p["b"]]]
            out = []
            for li in self.SL:
                for s in ("postname", "close"):
                    sp, tp = ea["spans"][p["best"]][s], eb["spans"][p["best"]][s]
                    if len(sp) != len(tp):
                        skipped.add(k)
                        continue
                    out.append(((li, s), "b", li, 0, sp, tp))
            return out

        fout = open(out_path, "a", encoding="utf8")
        t = self.run_units(lambda size, dl: self.copy_units("P", pp, jobs_for, size, dl, fout, done), 3,
                           "P", out_path, "P.jsonl.gz")
        fout.close()
        self.timing["P"] = t
        log(f"P: {len(skipped)} pairs with spans of unequal length, skipped")

    def stage_n(self):
        """Amendment 1: the best product's name state copied between the crossed (a) and the original (b) prompt,
        forward (a into b) and reverse (b into a), and the placebo copies of the same name from the partner's block."""
        pp = self.name_pairs()
        out_path = os.path.join(self.a.work, "N.jsonl")
        done = done_ids(out_path, lambda r: (r["pair"],) + tuple(r["key"]) if r["role"] == "copy" else None)

        def last2(e, L):
            return [e["spans"][L]["namebrand"][-1], e["spans"][L]["brand"][-1]]

        def every(e, L):
            return e["spans"][L]["namebrand"] + e["spans"][L]["brand"]

        def jobs_for(k):
            p = pp[k]
            ea, eb = self.encs[self.idx[p["a"]]], self.encs[self.idx[p["b"]]]
            B, Pt = p["best"], p["partner"]
            equal = all(len(ea["spans"][B][s]) == len(eb["spans"][B][s]) for s in ("namebrand", "brand"))
            out = []
            for li in self.SL:
                out += [((li, "fwd"), "b", li, 0, last2(ea, B), last2(eb, B)),
                        ((li, "rev"), "a", li, 1, last2(eb, B), last2(ea, B)),
                        ((li, "pfwd"), "b", li, 0, last2(ea, Pt), last2(eb, B)),
                        ((li, "prev"), "a", li, 1, last2(eb, Pt), last2(ea, B))]
                if equal:
                    out += [((li, "fwd_all"), "b", li, 0, every(ea, B), every(eb, B)),
                            ((li, "rev_all"), "a", li, 1, every(eb, B), every(ea, B))]
            return out

        fout = open(out_path, "a", encoding="utf8")
        t = self.run_units(lambda size, dl: self.copy_units("N", pp, jobs_for, size, dl, fout, done), 3,
                           "N", out_path, "N.jsonl.gz")
        fout.close()
        self.timing["N"] = t

    # ------------------------------------------------------------ stage B

    def reliability_curve(self):
        """Amendment 5's layer rule: at each stored layer, the held-out accuracy of the reliability probe (the share of
        reliability pairs that project above zero on the direction fitted without their category, equal weight for
        every table), at the close token. It reads no name data."""
        N = len(self.rend)
        cats = sorted({p["category"] for p in self.pairs})
        rel = [p for p in self.pairs if p["contrast"] == "reliability"]
        ia = np.array([self.idx[p["a"]] for p in rel])
        ib = np.array([self.idx[p["b"]] for p in rel])
        il = np.array([M.LETTERS.index(p["letter"]) for p in rel])
        pc = np.array([cats.index(p["category"]) for p in rel])
        mm = np.memmap(os.path.join(self.a.work, "A_close.f16"), dtype=np.float16, mode="r", shape=(N, 5, len(self.SL), self.d))
        curve = {}
        for j, li in enumerate(self.SL):
            X = mm[:, :, j, :]
            delta = X[ia, il].astype(np.float32) - X[ib, il].astype(np.float32)
            ok = np.zeros(len(rel), dtype=bool)
            for c in range(len(cats)):
                m = pc == c
                if m.any() and (~m).any():
                    ok[m] = delta[m] @ delta[~m].mean(0) > 0
            by_t = defaultdict(list)
            for p, o in zip(rel, ok):
                by_t[p["table"]].append(float(o))
            curve[li] = float(np.mean([np.mean(v) for v in by_t.values()]))
        return curve

    def stage_b(self):
        self.need_order()
        if self.a.layer_rule in ("reliability", "middle"):
            curve = self.reliability_curve()
            if self.a.layer_rule == "middle":      # PLAN.md, amendment 5, change of about 6:00 PM on 21 November
                import analyze as AN
                primary = AN.middle_layer(self.SL)
            else:
                primary = max(curve, key=curve.get)
            log(f"B: reliability probe accuracy by layer {curve}; layer {primary} ({self.a.layer_rule})")
            return self.stage_b_after(curve, primary)
        P = jl(os.path.join(self.a.work, "P.jsonl"))
        base = {r["uid"]: r["lo"] for r in P if r["role"] == "base_b"}
        eff = defaultdict(lambda: defaultdict(list))
        for r in P:
            if r["role"] == "copy" and r["key"][1] == "postname" and r["info"] == 0 and r["lo"] is not None \
                    and base.get(r["uid"]) is not None:
                eff[r["layer"]][r["table"]].append(r["lo"] - base[r["uid"]])
        curve = {li: float(np.mean([np.mean(v) for v in eff[li].values()])) for li in self.SL if eff[li]}
        primary = max(curve, key=curve.get)
        return self.stage_b_after(curve, primary)

    def stage_b_after(self, curve, primary):
        sec = sorted({min(self.SL, key=lambda x: abs(x - self.n_layers * f)) for f in (1 / 3, 2 / 3)} - {primary})
        steer = [primary] + sec
        log(f"B: patch curve {curve}; primary layer {primary}; secondary {sec}")

        N = len(self.rend)
        mm = {s: np.memmap(os.path.join(self.a.work, f"A_{s}.f16"), dtype=np.float16, mode="r",
                           shape=(N, 5, len(self.SL), self.d)) for s in M.SPANS}
        cats = sorted({p["category"] for p in self.pairs})
        groups = {"name0": ("name", 0), "name1": ("name", 1), "spec0": ("spec", 0), "spec1": ("spec", 1),
                  "rel": ("reliability", 1), "price0": ("price", 0), "price1": ("price", 1)}
        member = {g: np.array([p["contrast"] == c and p["info"] == i for p in self.pairs]) for g, (c, i) in groups.items()}
        pcat = np.array([cats.index(p["category"]) for p in self.pairs])
        ia = np.array([self.idx[p["a"]] for p in self.pairs])
        ib = np.array([self.idx[p["b"]] for p in self.pairs])
        il = np.array([M.LETTERS.index(p["letter"]) for p in self.pairs])
        DIRS = ("spec0", "rel", "price0", "spec0_perp_price", "rel_perp_price", "name0")
        proj = np.zeros((len(self.pairs), len(self.SL), len(M.SPANS), len(DIRS)), dtype=np.float32)
        norms = np.zeros((len(self.pairs), len(self.SL), len(M.SPANS)), dtype=np.float32)
        cos = {}
        steer_vec, steer_norm = {}, {}
        for j, li in enumerate(self.SL):
            for s, si in SPAN_I.items():
                X = mm[s][:, :, j, :]
                delta = (X[ia, il].astype(np.float32) - X[ib, il].astype(np.float32))
                norms[:, j, si] = np.linalg.norm(delta, axis=1)
                loco = {}
                for g in ("spec0", "rel", "price0", "name0"):
                    loco[g] = np.zeros((len(cats), self.d), dtype=np.float32)
                    for c in range(len(cats)):
                        m = member[g] & (pcat != c)
                        if m.any():
                            loco[g][c] = delta[m].mean(0)
                unit = {g: loco[g] / np.maximum(np.linalg.norm(loco[g], axis=1, keepdims=True), 1e-12) for g in loco}
                for b_ in ("spec0", "rel"):
                    u, q = unit[b_], unit["price0"]
                    perp = u - (u * q).sum(1, keepdims=True) * q
                    unit[b_ + "_perp_price"] = perp / np.maximum(np.linalg.norm(perp, axis=1, keepdims=True), 1e-12)
                for k, g in enumerate(DIRS):
                    proj[:, j, si, k] = (delta * unit[g][pcat]).sum(1)
                full = {g: delta[member[g]].mean(0) for g in groups if member[g].any()}
                for x in full:
                    for y in full:
                        if x < y:
                            cos[f"{li}|{s}|{x}|{y}"] = float(np.dot(full[x], full[y]) / (np.linalg.norm(full[x]) * np.linalg.norm(full[y]) + 1e-12))
                if s == "postname" and li in steer:
                    steer_vec[li] = loco["name0"]
                    steer_norm[li] = np.linalg.norm(loco["name0"], axis=1)
            log(f"B: layer {li} done")
        # random unit vectors for each steering layer and category: two uniform, two from the spread of the
        # post-name means of every product in the names-hidden dom2 prompts
        hid = np.array([i for i, r in enumerate(self.rend) if r["kind"] == "dom2" and r["names"] == "hidden"])
        rand = {}
        for li in steer:
            j = self.SL.index(li)
            Xh = mm["postname"][hid, :, j, :].astype(np.float32).reshape(-1, self.d)
            Xc = Xh - Xh.mean(0)
            R = np.zeros((len(cats), len(RANDOM), self.d), dtype=np.float32)
            for c in range(len(cats)):
                for k, name in enumerate(RANDOM):
                    g = np.random.default_rng([SEED, li, c, k])
                    v = g.standard_normal(self.d) if name.startswith("iso") else Xc.T @ g.standard_normal(Xc.shape[0])
                    R[c, k] = v / np.linalg.norm(v)
            rand[li] = R
        np.savez(os.path.join(self.a.work, "B_vectors.npz"), cats=np.array(cats), steer=np.array(steer),
                 **{f"name_{li}": steer_vec[li] for li in steer}, **{f"rand_{li}": rand[li] for li in steer})
        np.savez_compressed(os.path.join(self.a.back, "proj.npz"), proj=proj.astype(np.float16), norms=norms.astype(np.float16),
                            layers=np.array(self.SL), spans=np.array(M.SPANS), dirs=np.array(DIRS))
        json.dump({"layer_rule": self.a.layer_rule, "patch_curve" if self.a.layer_rule == "patch" else
                   "reliability_probe_curve": curve, "primary_layer": primary, "secondary_layers": sec, "categories": cats,
                   "name_vector_norm": {str(li): dict(zip(cats, map(float, steer_norm[li]))) for li in steer},
                   "cosines_all_categories": cos, "stored_layers": self.SL, "dirs": DIRS},
                  open(os.path.join(self.a.back, "B.json"), "w"), indent=1)

    # ------------------------------------------------------------ stage C

    def stage_c(self):
        self.need_order()
        B = json.load(open(os.path.join(self.a.back, "B.json")))
        V = np.load(os.path.join(self.a.work, "B_vectors.npz"))
        cats = list(V["cats"])
        primary, steer = B["primary_layer"], [int(x) for x in V["steer"]]
        items = [i for i, r in enumerate(self.rend) if r["kind"] == "dom2" and r["names"] == "original"]
        conds = {li: [(t, dname, al) for t in ("best", "familiar") for dname in ("name",) + RANDOM
                      for al in (GRID_PRIMARY if li == primary else GRID_SECONDARY)] for li in steer}
        out_path = os.path.join(self.a.work, "C.jsonl")
        done = done_ids(out_path, lambda r: (r["id"], r["layer"], r["target"], r["dir"], r["alpha"])
                        if r["role"] == "push" else None)
        log(f"C: {len(items)} items, {sum(len(v) for v in conds.values())} pushes an item, "
            f"{len(done)} pushes already written")

        def vec(i, li, dname, al):
            c = cats.index(self.rend[i]["category"])
            base = V[f"name_{li}"][c]
            if dname == "name":
                return al * base
            k = RANDOM.index(dname)
            return al * np.linalg.norm(base) * V[f"rand_{li}"][c, k]

        fout = open(out_path, "a", encoding="utf8")

        def build(size, dups_left):
            units = []
            for i in items:
                rr, e = self.rend[i], self.encs[i]
                for li in steer:
                    pending = [c for c in conds[li] if (rr["id"], li) + c not in done]
                    if not pending:
                        continue
                    for group in chunks(pending, max(1, size - 1 - (1 if len(units) < dups_left else 0))):
                        dup = len(units) < dups_left
                        nb = 2 if dup else 1
                        encs = [e] * (nb + len(group))
                        which = [[]] * nb + [[(rr["best"], "postname")] if t == "best" else
                                             [(L, "postname") for L in rr["letters"] if L != rr["best"]]
                                             for t, _, _ in group]
                        vs = np.stack([np.zeros(self.d, dtype=np.float32)] * nb +
                                      [vec(i, li, dname, al) for _, dname, al in group]).astype(np.float32)
                        uid = "C" + uuid.uuid4().hex[:12]
                        stats = {}

                        def make_fns(offs, T, device, encs=encs, which=which, vs=vs, li=li, stats=stats):
                            Mk = M.token_mask(encs, offs, T, which, device)
                            return {li: M.pusher(Mk, torch.tensor(vs, device=device), stats)}

                        def on_result(res, rr=rr, group=group, nb=nb, li=li, uid=uid, stats=stats):
                            head = {"uid": uid, "id": rr["id"], "table": rr["table"], "category": rr["category"],
                                    "info": rr["info"], "rung": rr["rung"], "layer": li, "best": rr["best"]}
                            rows = [dict(head, role="base", target="none", dir="zero", alpha=0.0, **outcome(res[0], rr["best"]))]
                            if nb == 2:
                                rows.append(dict(head, role="dup", target="none", dir="zero", alpha=0.0,
                                                 **outcome(res[1], rr["best"])))
                            for n, (t, dname, al) in enumerate(group):
                                j = nb + n
                                rows.append(dict(head, role="push", target=t, dir=dname, alpha=al,
                                                 kept=round(stats["ratio"][j], 4), kept_cos=round(stats["cos"][j], 4),
                                                 **outcome(res[j], rr["best"])))
                                done.add((rr["id"], li, t, dname, al))
                            for x in rows:
                                fout.write(json.dumps(x) + "\n")
                            fout.flush()
                        units.append((encs, make_fns, on_result, dup))
            return units

        t = self.run_units(build, 2, "C", out_path, "C.jsonl.gz")
        fout.close()
        self.timing["C"] = t

    # ------------------------------------------------------------ D and helpers

    def copy_gz(self, src, name):
        if not os.path.exists(src):
            return
        with open(src, "rb") as f, gzip.open(os.path.join(self.a.back, name), "wb") as g:
            g.write(f.read())

    def version(self):
        import transformers
        rec = {"model": self.a.model, "model_key": self.a.model_key, "switch": self.switch, "layers": self.n_layers,
               "width": self.d, "stored_layers": self.SL, "longest_prompt_tokens": self.max_n, "batch": self.batch,
               "timing_s": self.timing, "torch": torch.__version__, "transformers": transformers.__version__,
               "python": platform.python_version(), "job": os.environ.get("SLURM_JOB_ID"),
               "array_task": os.environ.get("SLURM_ARRAY_TASK_ID"), "node": platform.node(),
               "renderings": os.path.basename(self.a.renderings), "pairs": os.path.basename(self.a.pairs),
               "finished": time.strftime("%Y-%m-%d %H:%M %Z")}
        if torch.cuda.is_available():
            rec["gpu"] = torch.cuda.get_device_name(0)
            rec["gpu_memory_gb"] = round(torch.cuda.get_device_properties(0).total_memory / 2 ** 30, 1)
        json.dump(rec, open(os.path.join(self.a.back, "VERSION.json"), "w"), indent=1)
        log(json.dumps(rec))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--model-key", default="")
    ap.add_argument("--switch", default="{}")
    ap.add_argument("--renderings", required=True)
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--back", required=True)
    ap.add_argument("--stages", default="A,P,N,B,C,D")
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--max-new", type=int, default=12)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--calib", default="")
    ap.add_argument("--calib-stop", action="store_true")
    ap.add_argument("--layer-rule", default="patch", choices=("patch", "reliability", "middle"),
                    help="patch: the primary layer from stage P; reliability: amendment 5's rule, no stage P needed")
    a = ap.parse_args(argv)
    os.makedirs(a.work, exist_ok=True)
    os.makedirs(a.back, exist_ok=True)
    restore_back(a.work, a.back)
    run = Runner(a)
    for st in a.stages.split(","):
        marker = os.path.join(a.work, f"DONE_{st}")
        if os.path.exists(marker) and st != "D":
            log(f"stage {st} already done")
            continue
        log(f"stage {st}")
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
        t0 = time.time()
        {"A": run.stage_a, "P": run.stage_p, "N": run.stage_n, "B": run.stage_b, "C": run.stage_c,
         "D": run.version}[st]()
        if st != "D":
            run.timing[f"{st}_wall_s"] = round(time.time() - t0, 1)
            if torch.cuda.is_available():
                run.timing[f"{st}_peak_gb"] = round(torch.cuda.max_memory_allocated() / 2 ** 30, 1)
            json.dump(run.timing, open(os.path.join(a.work, "TIMING.json"), "w"), indent=1)
            json.dump(run.timing, open(os.path.join(a.back, "TIMING.json"), "w"), indent=1)
        save_back(a.work, a.back)
        open(marker, "w").write(time.strftime("%Y-%m-%d %H:%M"))
    return run


if __name__ == "__main__":
    main()
