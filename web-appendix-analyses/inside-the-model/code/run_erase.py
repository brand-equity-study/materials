"""The linear erasure of PLAN.md amendment 3 (question 6), for one model, after its full run.

    python run_erase.py --model <folder or repo@rev> --switch '{}' --renderings renderings.jsonl --pairs pairs.jsonl
                        --full-work <the full run's work folder> --full-back <its back folder> --work <folder>
                        --back <folder> [--batch 8]

Stages (each resumes):
  F  fit: one read of the two swapped products' post-name tokens, at the primary and the two secondary layers. The name
     eraser is fitted on the original and crossed cells (label 1 for a familiar name), the shuffled eraser on labels
     drawn at random for each product in each prompt, and the specification eraser on the names-hidden cell and the
     spec swap (label 1 for the slot with the better specifications). Every eraser is fitted for each category with
     that category left out. Statistics are summed in float64 for one category at a time on the GPU and merged into
     the sums of every category in CPU memory.
  M  the manipulation check: in each category, a linear probe of familiar against invented names on the two products'
     post-name means (fitted on even trials, tested on odd), before and after that category's eraser, from the full
     run's stored means (the eraser is affine, so the erased mean is the mean of the erased tokens)
  E  evaluation: the original and names-hidden cells, each in units with the prompt unerased and under the name,
     shuffled and specification erasers at the primary layer, and unerased and under the name eraser at each secondary
     layer; the eraser acts at every post-name token of every product
"""
import argparse
import hashlib
import json
import os
import sys
import time
from collections import defaultdict

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import erase as E  # noqa: E402
import mech as M  # noqa: E402
import run_mech as R  # noqa: E402
from run_mech import chunks, jl, log  # noqa: E402

ERASERS = ("name", "shuffled", "spec")
# the two fits of every eraser: the plain one, and one whose covariance is shrunk with n the number of products
# (erase.py); stage M chooses which one stage E uses (PLAN.md, amendment 3)
FITS = {"": None, "_shrunk": "units"}
MOVE_LIMIT = 2.0


def coin(*key):
    """A fair coin fixed by its key (the shuffled labels, one for each product in each prompt)."""
    return int(hashlib.sha256("|".join(map(str, key)).encode()).hexdigest()[:8], 16) % 2


class EraseRunner(R.Runner):
    def __init__(self, a):
        super().__init__(a)
        B = json.load(open(os.path.join(a.full_back, "B.json")))
        self.layer, self.sec = B["primary_layer"], B["secondary_layers"]
        self.fit_layers = [self.layer] + list(self.sec)
        self.cats = sorted({r["category"] for r in self.rend if r["kind"] == "dom2"})
        self.dev = next(self.model.parameters()).device

    def two(self, r):
        """The best product and the partner, the two products whose names the crossed cell swaps."""
        return [r["best"], r["partner"]]

    # ------------------------------------------------------------ stage F

    def stage_f(self):
        d = self.d
        jobs = {"name": [i for i, r in enumerate(self.rend) if r["kind"] == "dom2" and r["names"] in ("original", "crossed")],
                "spec": [i for i, r in enumerate(self.rend) if (r["kind"] == "dom2" and r["names"] == "hidden")
                         or r["kind"] == "specswap"]}
        labels = {"name": ("real", "shuffled"), "spec": ("real",)}
        layers_of = {"name": self.fit_layers, "spec": [self.layer]}     # the specification eraser: primary layer only
        acc = {(c, li): E.Acc(d, self.cats, labels[c]) for c in jobs for li in layers_of[c]}
        for concept, rows in jobs.items():
            for cat in self.cats:
                mine = sorted([i for i in rows if self.rend[i]["category"] == cat], key=lambda i: self.encs[i]["n"])
                if not mine:
                    continue
                stage = {li: E.Acc(d, [cat], labels[concept], device=self.dev) for li in layers_of[concept]}
                for chunk in chunks(mine, self.batch):
                    encs = [self.encs[i] for i in chunk]

                    def mk(offs, T, device, chunk=chunk, encs=encs):
                        def fn_for(li):
                            def fn(h):
                                for b, i in enumerate(chunk):
                                    r = self.rend[i]
                                    for L in self.two(r):
                                        pos = [p + offs[b] for p in encs[b]["spans"][L]["postname"]]
                                        x = h[b, pos]
                                        if concept == "name":
                                            z = float(r["products"][L]["kind"] != "invented")
                                            zs = {"real": z, "shuffled": float(coin(r["id"], L))}
                                        else:
                                            better = (L == r["best"]) == (r["kind"] != "specswap")
                                            zs = {"real": float(better)}
                                        n = x.shape[0]
                                        stage[li].update(x, {k: torch.full((n,), v, device=device) for k, v in zs.items()}, cat)
                                return None
                            return fn
                        return {li: fn_for(li) for li in layers_of[concept]}
                    M.generate(self.model, self.tok, encs, 1, mk, self.layers, self.lid)
                for li in layers_of[concept]:
                    acc[(concept, li)].merge(stage[li], cat)
                del stage
                log(f"F: {concept} {cat} done")
        out, info = {}, {}
        for fit, shrinkage in FITS.items():     # the plain erasers, and the erasers with the covariance shrunk
            for li in self.fit_layers:
                for name, (concept, label) in (("name", ("name", "real")), ("shuffled", ("name", "shuffled")),
                                               ("spec", ("spec", "real"))):
                    if li != self.layer and name != "name":
                        continue
                    for cat in self.cats:
                        mu, a, b = acc[(concept, li)].fit(label=label, leave_out=cat, device=self.dev, shrinkage=shrinkage)
                        info[f"{name}{fit}|{li}|{cat}"] = acc[(concept, li)].last_fit
                        for k, v in (("mu", mu), ("a", a), ("b", b)):
                            out[f"{name}{fit}|{li}|{cat}|{k}"] = v.cpu().numpy()
        np.savez(os.path.join(self.a.work, "erasers.npz"), **out)
        json.dump(info, open(os.path.join(self.a.back, "ERASERS.json"), "w"), indent=1)
        plain = [v for v in info.values() if not v["shrinkage"]]
        log(f"F: {len(out) // 3} erasers fitted; the plain ones keep eigenvalues "
            f"{sorted({v['eigenvalues_kept'] for v in plain})} of {plain[0]['width']}, from "
            f"{sorted({v['units'] for v in plain})[:3]} products")

    def eraser(self, name, li, cat):
        if not hasattr(self, "_er"):
            self._er = dict(np.load(os.path.join(self.a.work, "erasers.npz")))
        return tuple(torch.tensor(self._er[f"{name}|{li}|{cat}|{k}"], dtype=torch.float64) for k in ("mu", "a", "b"))

    # ------------------------------------------------------------ stage M

    def stage_m(self):
        self.need_full_order()
        N = len(self.rend)
        j = self.SL.index(self.layer)
        X = np.memmap(os.path.join(self.a.full_work, "A_postname.f16"), dtype=np.float16, mode="r",
                      shape=(N, 5, len(self.SL), self.d))[:, :, j, :]
        out = {}
        for cat in self.cats:
            rows = [i for i, r in enumerate(self.rend) if r["kind"] == "dom2" and r["category"] == cat
                    and r["names"] in ("original", "crossed")]
            samples = []
            for i in rows:
                r = self.rend[i]
                for L in self.two(r):
                    samples.append((X[i, M.LETTERS.index(L)].astype(np.float64), float(r["products"][L]["kind"] != "invented"),
                                    r["trial"] % 2))
            x = np.stack([s[0] for s in samples])
            z = np.array([s[1] for s in samples])
            h = np.array([s[2] for s in samples])
            res = {f"move_held_out_over_fitted{f}": self.movement(cat, X, f) for f in FITS}
            for tag, xx in [("before", x)] + [(f"after_{e}{f}", E.erase(torch.tensor(x), *self.eraser(e + f, self.layer, cat)).numpy())
                                              for e in ("name", "shuffled") for f in FITS]:
                w = xx[(h == 0) & (z == 1)].mean(0) - xx[(h == 0) & (z == 0)].mean(0)
                s = xx @ w
                thr = 0.5 * (s[(h == 0) & (z == 1)].mean() + s[(h == 0) & (z == 0)].mean())
                test = h == 1
                res[tag] = float(np.mean((s[test] > thr) == (z[test] == 1)))
            out[cat] = res
        mean = {k: float(np.mean([v[k] for v in out.values()])) for k in next(iter(out.values()))}
        # the plain erasers are used unless they move the held-out category's products more than twice as far as the
        # fitted categories' products, a sign that their whitening follows noise; then every eraser of stage E is the
        # shrunk one (PLAN.md, amendment 3)
        moved = mean["move_held_out_over_fitted"] > MOVE_LIMIT
        fit = "_shrunk" if moved else ""
        # if the shrunk erasers also move the held-out products more than twice as far, question 6 is described and not
        # read (PLAN.md, amendment 3)
        shrunk_moved = mean["move_held_out_over_fitted_shrunk"] > MOVE_LIMIT
        rec = {"layer": self.layer, "by_category": out, "mean": mean,
               "held_out_moved_more_than_twice": moved, "erasers_used": "shrunk" if moved else "plain",
               "shrunk_held_out_moved_more_than_twice": shrunk_moved,
               "question_6_read": not (moved and shrunk_moved),
               "eraser_removed_the_readout": mean[f"after_name{fit}"] <= 0.60}
        json.dump(rec, open(os.path.join(self.a.back, "MANIP.json"), "w"), indent=1)
        log(f"M: {json.dumps(mean)}; erasers used: {rec['erasers_used']}")

    def fit_used(self):
        """The suffix of the erasers that stage M chose."""
        return "_shrunk" if json.load(open(os.path.join(self.a.back, "MANIP.json")))["erasers_used"] == "shrunk" else ""

    def movement(self, cat, X, fit=""):
        """How far the eraser fitted without `cat` moves the two products' post-name means of `cat` (held out), over
        how far it moves those of the other categories (fitted), each as the mean of |a (b . (x - mu))| / |x - mu|."""
        mu, a, b = (t.numpy() for t in self.eraser("name" + fit, self.layer, cat))

        def mean_move(rows):
            xs = np.stack([X[i, M.LETTERS.index(L)].astype(np.float64) for i in rows for L in self.two(self.rend[i])])
            c = xs - mu
            return float(np.mean(np.abs(c @ b) * np.linalg.norm(a) / np.maximum(np.linalg.norm(c, axis=1), 1e-12)))
        shown = [i for i, r in enumerate(self.rend) if r["kind"] == "dom2" and r["names"] in ("original", "crossed")]
        held = [i for i in shown if self.rend[i]["category"] == cat]
        fitted = [i for i in shown if self.rend[i]["category"] != cat]
        return mean_move(held) / max(mean_move(fitted), 1e-12)

    def need_full_order(self):
        if open(os.path.join(self.a.full_work, "ORDER.sha256")).read().strip() != self.order:
            sys.exit("refused: the full build's prompts are not in the order of the full run's read stage")

    # ------------------------------------------------------------ stage E

    def stage_e(self):
        items = [i for i, r in enumerate(self.rend) if r["kind"] == "dom2" and r["names"] in ("original", "hidden")]
        plan = {self.layer: ERASERS, **{li: ("name",) for li in self.sec}}
        out_path = os.path.join(self.a.work, "E.jsonl")
        done = R.done_ids(out_path, lambda r: (r["id"], r["layer"], r["eraser"]) if r["role"] == "erased" else None)
        fout = open(out_path, "a", encoding="utf8")
        cache = {}
        fit = self.fit_used()
        log(f"E: the {'shrunk' if fit else 'plain'} erasers, as stage M chose")

        def params(name, li, cat):
            if (name, li, cat) not in cache:
                cache[(name, li, cat)] = tuple(t.to(self.dev) for t in self.eraser(name + fit, li, cat))
            return cache[(name, li, cat)]

        def build(size, dups_left):
            units = []
            for i in items:
                r, e = self.rend[i], self.encs[i]
                for li, names in plan.items():
                    pending = [n for n in names if (r["id"], li, n) not in done]
                    if not pending:
                        continue
                    for group in chunks(pending, max(1, size - 1)):
                        encs = [e] * (1 + len(group))
                        uid = "E" + os.urandom(6).hex()

                        def make_fns(offs, T, device, r=r, e=e, li=li, group=group):
                            pos = [[p + offs[b] for L in M.LETTERS for p in e["spans"][L]["postname"]]
                                   for b in range(1 + len(group))]

                            def fn(h):
                                out = h.clone()
                                for n, name in enumerate(group):
                                    b = 1 + n
                                    out[b, pos[b]] = E.erase(h[b, pos[b]], *params(name, li, r["category"]))
                                return out
                            return {li: fn}

                        def on_result(res, r=r, li=li, group=group, uid=uid):
                            head = {"uid": uid, "id": r["id"], "table": r["table"], "category": r["category"],
                                    "names": r["names"], "info": r["info"], "rung": r["rung"], "trial": r["trial"],
                                    "layer": li, "best": r["best"], "fit": "shrunk" if fit else "plain"}
                            rows = [dict(head, role="base", eraser="none", **R.outcome(res[0], r["best"]))]
                            for n, name in enumerate(group):
                                rows.append(dict(head, role="erased", eraser=name, **R.outcome(res[1 + n], r["best"])))
                                done.add((r["id"], li, name))
                            for x in rows:
                                fout.write(json.dumps(x) + "\n")
                            fout.flush()
                        units.append((encs, make_fns, on_result, False))
            return units
        self.run_units(build, 2, "E", out_path, "E.jsonl.gz")
        fout.close()


def main(argv=None):
    ap = argparse.ArgumentParser()
    for k in ("--model", "--renderings", "--pairs", "--full-work", "--full-back", "--work", "--back"):
        ap.add_argument(k, required=True)
    ap.add_argument("--model-key", default="")
    ap.add_argument("--switch", default="{}")
    ap.add_argument("--stages", default="F,M,E")
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
    run = EraseRunner(a)
    run.need_full_order()
    for st in a.stages.split(","):
        marker = os.path.join(a.work, f"DONE_{st}")
        if os.path.exists(marker):
            log(f"stage {st} already done")
            continue
        t0 = time.time()
        {"F": run.stage_f, "M": run.stage_m, "E": run.stage_e}[st]()
        R.save_back(a.work, a.back)
        open(marker, "w").write(time.strftime("%Y-%m-%d %H:%M"))
        log(f"stage {st} done in {time.time() - t0:.0f} s")
    return run


if __name__ == "__main__":
    main()
