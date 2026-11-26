"""A direction of caution and the brand gap: PLAN.md amendment 7 (question 10), for one model.

    python run_risk.py --model <folder or repo@rev> --switch '{}' --renderings renderings.jsonl --pairs pairs.jsonl
                       --risk risk.jsonl --work <folder> --back <folder> [--batch 8]

  D  directions: for every persona prompt, the mean state at the answer positions (the template's tokens after the user
     message) at every stored layer; the caution direction (cautious minus bold) and the brevity direction (brief minus
     lengthy), each fitted on one kind of question and on both
  V  validation on the held-out kind (fitted on gambles, tested on familiar choices, and the reverse): the separation of
     the two personas within each question (risk_sep.py; the cut-off measure beside it), and the push without any persona at every stored layer and at sizes 0.5, 1 and 2 (in units of
     the fitted persona difference), on the uncapped log-odds of the safe option, against the brevity push. The layer and
     size with the largest validated effect are chosen here; VALIDATION.json says whether the validation passed, and if it
     did not, stage P does not run.
  P  the dom2 original and names-hidden cells, with and without the information: the caution, brevity and two random
     directions (of the same size; drawn from the spread of the persona prompts' answer states) added and subtracted at
     the answer positions, at the chosen layer and size, in units with their own unpushed prompt, which also records the
     unpushed answer state's projection on the caution direction
"""
import argparse
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
import risk_sep as SEP  # noqa: E402
from run_mech import chunks, jl, log  # noqa: E402

SIZES = (0.5, 1.0, 2.0)
KINDS = ("gamble", "familiar")
SEED = 20261120


def answer_positions(e, offs_b):
    return list(range(e["after_user"] + offs_b, offs_b + e["n"]))


def boot_mean(x, draws=2000, seed=SEED):
    x = np.asarray(x, dtype=float)
    rng = np.random.default_rng(seed)
    bs = x[rng.integers(0, len(x), (draws, len(x)))].mean(1)
    return float(x.mean()), [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


MAX_MISSING = 0.05


def decide(rows, risk, layers, sep):
    """The choice of layer and size, and whether the validation passed (PLAN.md, amendment 7), from stage V's rows.
    The layer and size are chosen on one fold (fitted on gambles, pushed on the familiar choices) and tested on the
    other (fitted on familiar choices, pushed on gambles). A layer and size whose caution or brevity rows lose more than
    5 per cent to an answer without a letter is left out. sep: RISK_DIRS.json's held-out separation of the personas."""
    base = {x["uid"]: x for x in rows if x["role"] == "base"}
    eff = defaultdict(lambda: defaultdict(list))
    n_rows, n_missing = defaultdict(int), defaultdict(int)
    for x in rows:
        if x["role"] != "push":
            continue
        fold = "choose" if x["question_kind"] == "familiar" else "test"
        key = (fold, x["layer"], x["size"], x["dir"])
        n_rows[key] += 1
        b = base.get(x["uid"])
        if x["lo_u"] is None or not b or b["lo_u"] is None:
            n_missing[key] += 1
            continue
        eff[key][(x["i"], x["sign"])].append(x["lo_u"] - b["lo_u"])

    def per_question(key):
        acc = defaultdict(lambda: defaultdict(list))      # a question's two letter orders are averaged
        for (i, sg), v in eff[key].items():
            acc[str(risk[i]["q"])][sg] += v
        return {k: {sg: float(np.mean(v)) for sg, v in d_.items()} for k, d_ in acc.items()}

    def complete(fold, li, s):
        return all(n_rows[(fold, li, s, d)] and n_missing[(fold, li, s, d)] / n_rows[(fold, li, s, d)] <= MAX_MISSING
                   for d in ("caution", "brevity"))

    def sym_and_diff(fold, li, s):
        pq, pc = per_question((fold, li, s, "caution")), per_question((fold, li, s, "brevity"))
        keys = [k for k in pq if k in pc and {1, -1} <= set(pq[k]) and {1, -1} <= set(pc[k])]
        sym = [(pq[k][1] - pq[k][-1]) / 2 for k in keys]
        diff = [((pq[k][1] - pq[k][-1]) - (pc[k][1] - pc[k][-1])) / 2 for k in keys]
        return sym, diff

    best, best_val = None, -math.inf
    for li in layers:
        for s in SIZES:
            if not complete("choose", li, s):
                continue
            sym, diff = sym_and_diff("choose", li, s)
            if diff and float(np.mean(diff)) > best_val:
                best, best_val = (li, s), float(np.mean(diff))
    rec = {"chosen_layer": None, "chosen_size": None, "passes": False, "chosen_on": "fitted on gambles, pushed on "
           "familiar choices", "tested_on": "fitted on familiar choices, pushed on gambles"}
    if best:
        li, s = best
        sep_ok = all(sep[f"{f}->{h}|{li}"] >= 0.9 for f, h in (("gamble", "familiar"), ("familiar", "gamble")))
        rec.update({"chosen_layer": li, "chosen_size": s, "choose_fold_caution_minus_brevity": best_val,
                    "separation_ok": sep_ok, "test_fold_complete": complete("test", li, s)})
        if rec["test_fold_complete"]:
            sym, diff = sym_and_diff("test", li, s)
            est, ci = boot_mean(sym)
            dest, dci = boot_mean(diff)
            # both signs taken apart: adding caution moves the choices toward the safe option, subtracting it away
            pq = per_question(("test", li, s, "caution"))
            plus = float(np.mean([v[1] for v in pq.values() if 1 in v]))
            minus = float(np.mean([v[-1] for v in pq.values() if -1 in v]))
            rec.update({"caution_symmetric": est, "caution_ci": ci, "caution_minus_brevity": dest,
                        "caution_minus_brevity_ci": dci, "caution_added": plus, "caution_subtracted": minus,
                        "passes": bool(sep_ok and ci[0] > 0 and dci[0] > 0 and plus > 0 and minus < 0)})
    return rec


class RiskRunner(R.Runner):
    def __init__(self, a):
        super().__init__(a)
        self.risk = jl(a.risk)
        self.renc = [M.encode(self.tok, r, self.switch, self.limit) for r in self.risk]

    def answer_means(self, idx, layers):
        """{risk prompt index: {layer: mean answer-position state}} for the persona prompts."""
        out = {}
        for chunk in chunks(idx, self.batch):
            encs = [self.renc[i] for i in chunk]
            store = {}

            def mk(offs, T, device, encs=encs, store=store):
                W = torch.zeros((len(encs), 1, T), device=device)
                for b, e in enumerate(encs):
                    pos = answer_positions(e, offs[b])
                    W[b, 0, pos] = 1.0 / len(pos)
                return {li: M.reader(store, li, W) for li in layers}
            M.generate(self.model, self.tok, encs, 1, mk, self.layers, self.lid)
            for b, i in enumerate(chunk):
                out[i] = {li: store[li][b, 0].numpy().astype(np.float64) for li in layers}
        return out

    # ------------------------------------------------------------ stage D

    def stage_d(self):
        idx = [i for i, r in enumerate(self.risk) if r["persona"] != "none"]
        S = self.answer_means(idx, self.SL)
        dirs = {}
        for li in self.SL:
            for name, (pos, neg) in (("caution", ("cautious", "bold")), ("brevity", ("brief", "lengthy"))):
                for fit in KINDS + ("both",):
                    sel = lambda p: [S[i][li] for i in idx if self.risk[i]["persona"] == p and  # noqa: E731
                                     (fit == "both" or self.risk[i]["question_kind"] == fit)]
                    dirs[f"{name}|{fit}|{li}"] = np.mean(sel(pos), 0) - np.mean(sel(neg), 0)
        # the separation of the cautious and bold prompts on the held-out kind (PLAN.md, amendment 7, criterion (a), as
        # changed on 22 November 2026 at about 4:00 AM Central): within each question, the gate; the cut-off fitted on
        # the other kind, beside it
        sep, sep_cut = SEP.held_out_separation(S, self.risk, idx, dirs, self.SL)
        np.savez(os.path.join(self.a.work, "risk_dirs.npz"), **{k: v.astype(np.float32) for k, v in dirs.items()})
        json.dump({"separation_held_out": sep, "separation_held_out_cutoff": sep_cut,
                   "separation_rule": "within each question (the gate); cutoff: the midpoint of the fitted kind, beside it"},
                  open(os.path.join(self.a.back, "RISK_DIRS.json"), "w"), indent=1)
        # the spread of the persona prompts' answer states, for the random directions of stage P
        np.savez(os.path.join(self.a.work, "risk_spread.npz"),
                 **{str(li): np.stack([S[i][li] for i in idx]).astype(np.float32) for li in self.SL})
        log("D: directions fitted; held-out separation " + json.dumps({k: round(v, 3) for k, v in sep.items()}))

    def dirs(self):
        if not hasattr(self, "_dirs"):
            self._dirs = dict(np.load(os.path.join(self.a.work, "risk_dirs.npz")))
        return self._dirs

    # ------------------------------------------------------------ stage V

    def stage_v(self):
        D = self.dirs()
        plain = [i for i, r in enumerate(self.risk) if r["persona"] == "none"]
        out_path = os.path.join(self.a.work, "RV.jsonl")
        done = R.done_ids(out_path, lambda r: (r["i"], r["layer"], r["dir"], r["size"], r["sign"]) if r["role"] == "push" else None)
        fout = open(out_path, "a", encoding="utf8")
        conds = [(li, d, s, sg) for li in self.SL for d in ("caution", "brevity") for s in SIZES for sg in (1, -1)]

        def build(size, dups_left):
            units = []
            for i in plain:
                r, e = self.risk[i], self.renc[i]
                held = r["question_kind"]
                fit = [k for k in KINDS if k != held][0]
                for li in self.SL:
                    pend = [c for c in conds if c[0] == li and (i,) + c not in done]
                    for group in chunks(pend, max(1, size - 1)):
                        encs = [e] * (1 + len(group))
                        caut = D[f"caution|{fit}|{li}"]
                        vecs = [np.zeros_like(caut)] + [sg * s * np.linalg.norm(caut) * D[f"{d}|{fit}|{li}"] /
                                                        np.linalg.norm(D[f"{d}|{fit}|{li}"]) for _, d, s, sg in group]
                        uid = "V" + os.urandom(6).hex()

                        def make_fns(offs, T, device, encs=encs, vecs=vecs, li=li):
                            Mk = torch.zeros((len(encs), T), device=device)
                            for b, ee in enumerate(encs):
                                Mk[b, answer_positions(ee, offs[b])] = 1.0
                            return {li: M.pusher(Mk, torch.tensor(np.stack(vecs), dtype=torch.float32, device=device))}

                        def on_result(res, r=r, i=i, group=group, uid=uid, li=li):
                            head = {"uid": uid, "i": i, "question_kind": r["question_kind"], "q": r["q"],
                                    "safe": r["safe"], "layer": li}
                            rows = [dict(head, role="base", dir="none", size=0.0, sign=0, **R.outcome(res[0], r["safe"]))]
                            for n, (_, d, s, sg) in enumerate(group):
                                rows.append(dict(head, role="push", dir=d, size=s, sign=sg, **R.outcome(res[1 + n], r["safe"])))
                                done.add((i, li, d, s, sg))
                            for x in rows:
                                fout.write(json.dumps(x) + "\n")
                            fout.flush()
                        units.append((encs, make_fns, on_result, False))
            return units
        self.run_units(build, 2, "V", out_path, "RV.jsonl.gz")
        fout.close()
        sep = json.load(open(os.path.join(self.a.back, "RISK_DIRS.json")))["separation_held_out"]
        rec = decide(jl(out_path), self.risk, self.SL, sep)
        json.dump(rec, open(os.path.join(self.a.back, "VALIDATION.json"), "w"), indent=1)
        log(f"V: {json.dumps(rec)}")

    # ------------------------------------------------------------ stage P

    def stage_p(self):
        V = json.load(open(os.path.join(self.a.back, "VALIDATION.json")))
        if not V["passes"]:
            log("P: the validation failed; no dom2 push is run (PLAN.md, amendment 7)")
            return
        D, li, s = self.dirs(), V["chosen_layer"], V["chosen_size"]
        caut = D[f"caution|both|{li}"]
        scale = s * np.linalg.norm(caut)
        spread = dict(np.load(os.path.join(self.a.work, "risk_spread.npz")))[str(li)].astype(np.float64)
        Xc = spread - spread.mean(0)
        vecs = {"caution": caut / np.linalg.norm(caut), "brevity": D[f"brevity|both|{li}"] / np.linalg.norm(D[f"brevity|both|{li}"])}
        for k in range(2):
            v = Xc.T @ np.random.default_rng([SEED, li, 31 + k]).standard_normal(Xc.shape[0])
            vecs[f"rand{k}"] = v / np.linalg.norm(v)
        unit_caut = vecs["caution"]
        items = [i for i, r in enumerate(self.rend) if r["kind"] == "dom2" and r["names"] in ("original", "hidden")]
        conds = [(d, sg) for d in vecs for sg in (1, -1)]
        out_path = os.path.join(self.a.work, "RP.jsonl")
        done = R.done_ids(out_path, lambda r: (r["id"], r["dir"], r["sign"]) if r["role"] == "push" else None)
        fout = open(out_path, "a", encoding="utf8")

        def build(size, dups_left):
            units = []
            for i in items:
                r, e = self.rend[i], self.encs[i]
                pend = [c for c in conds if (r["id"],) + c not in done]
                for group in chunks(pend, max(1, size - 1)):
                    encs = [e] * (1 + len(group))
                    vv = [np.zeros_like(unit_caut)] + [sg * scale * vecs[d] for d, sg in group]
                    uid = "P" + os.urandom(6).hex()
                    store = {}

                    def make_fns(offs, T, device, encs=encs, vv=vv, store=store):
                        Mk = torch.zeros((len(encs), T), device=device)
                        W = torch.zeros((len(encs), 1, T), device=device)
                        for b, ee in enumerate(encs):
                            pos = answer_positions(ee, offs[b])
                            Mk[b, pos] = 1.0
                            W[b, 0, pos] = 1.0 / len(pos)
                        push = M.pusher(Mk, torch.tensor(np.stack(vv), dtype=torch.float32, device=device))

                        def fn(h):
                            store["state"] = torch.einsum("bst,btd->bsd", W, h.float()).cpu()   # before the push
                            return push(h)
                        return {li: fn}

                    def on_result(res, r=r, group=group, uid=uid, store=store):
                        head = {"uid": uid, "id": r["id"], "table": r["table"], "category": r["category"],
                                "names": r["names"], "info": r["info"], "rung": r["rung"], "trial": r["trial"],
                                "best": r["best"], "layer": li, "size": s}
                        proj = float(store["state"][0, 0].numpy().astype(np.float64) @ unit_caut)
                        rows = [dict(head, role="base", dir="none", sign=0, caution_projection=proj,
                                     **R.outcome(res[0], r["best"]))]
                        for n, (d, sg) in enumerate(group):
                            rows.append(dict(head, role="push", dir=d, sign=sg, **R.outcome(res[1 + n], r["best"])))
                            done.add((r["id"], d, sg))
                        for x in rows:
                            fout.write(json.dumps(x) + "\n")
                        fout.flush()
                    units.append((encs, make_fns, on_result, False))
            return units
        self.run_units(build, 2, "P", out_path, "RP.jsonl.gz")
        fout.close()


def main(argv=None):
    ap = argparse.ArgumentParser()
    for k in ("--model", "--renderings", "--pairs", "--risk", "--work", "--back"):
        ap.add_argument(k, required=True)
    ap.add_argument("--model-key", default="")
    ap.add_argument("--switch", default="{}")
    ap.add_argument("--stages", default="D,V,P")
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
    run = RiskRunner(a)
    for st in a.stages.split(","):
        marker = os.path.join(a.work, f"DONE_{st}")
        if os.path.exists(marker):
            log(f"stage {st} already done")
            continue
        t0 = time.time()
        {"D": run.stage_d, "V": run.stage_v, "P": run.stage_p}[st]()
        R.save_back(a.work, a.back)
        open(marker, "w").write(time.strftime("%Y-%m-%d %H:%M"))
        log(f"stage {st} done in {time.time() - t0:.0f} s")
    return run


if __name__ == "__main__":
    main()
