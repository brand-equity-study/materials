"""The attention knockout of PLAN.md amendment 6 (question 9), for one model.

    python run_knock.py --model <folder or repo@rev> --switch '{}' --renderings renderings.jsonl --pairs pairs.jsonl
                        --work <folder> --back <folder> [--batch 8]

For each original and names-hidden dom2 item without the information, one unit holds the prompt unknocked and with
the attention from the answer positions (the template's tokens after the user message, in the prefill, which predict
the first answer token) stopped to every product's name tokens (kind "names") or to as many of each product's
specification-line tokens (kind "control": the tokens just before the product's last line), in each of six windows of
one sixth of the depth and in all layers (window 6). Rows go to K.jsonl, each with its unit's id.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mech as M  # noqa: E402
import run_mech as R  # noqa: E402
from run_mech import chunks, log  # noqa: E402

KINDS = ("names", "control")


def windows(n_layers):
    """Six windows of about one sixth of the depth (layer numbers from 1), then every layer."""
    edges = [round(n_layers * k / 6) for k in range(7)]
    six = [list(range(edges[k] + 1, edges[k + 1] + 1)) for k in range(6)]
    return [w for w in six if w] + [list(range(1, n_layers + 1))]     # no empty window (only below six layers)


def keys_for(e, kind):
    out = []
    for L in M.LETTERS:
        nm = e["spans"][L]["namebrand"] + e["spans"][L]["brand"]
        if kind == "names":
            out += nm
        else:
            start = e["spans"][L]["lastline"][0]
            out += list(range(start - len(nm), start))
    return sorted(set(out))


class KnockRunner(R.Runner):
    def stage_k(self):
        W = windows(self.n_layers)
        attn = M.attention_modules(self.model)
        items = [i for i, r in enumerate(self.rend) if r["kind"] == "dom2" and r["names"] in ("original", "hidden")
                 and r["info"] == 0]
        conds = [(k, w) for w in range(len(W)) for k in KINDS]
        out_path = os.path.join(self.a.work, "K.jsonl")
        done = R.done_ids(out_path, lambda r: (r["id"], r["kind"], r["window"]) if r["role"] == "knock" else None)
        fout = open(out_path, "a", encoding="utf8")

        def build(size, dups_left):
            units = []
            for i in items:
                r, e = self.rend[i], self.encs[i]
                pending = [c for c in conds if (r["id"],) + c not in done]
                for group in chunks(pending, max(1, size - 1)):
                    encs = [e] * (1 + len(group))
                    uid = "K" + os.urandom(6).hex()

                    def make_pre(offs, T, device, e=e, group=group):
                        per_layer = {}
                        for n, (kind, w) in enumerate(group):
                            b = 1 + n
                            blk = (b, e["after_user"] + offs[b], [k + offs[b] for k in keys_for(e, kind)])
                            for li in W[w]:
                                per_layer.setdefault(li, []).append(blk)
                        return [(attn[li - 1], M.knockout(bl)) for li, bl in per_layer.items()]

                    def on_result(res, r=r, group=group, uid=uid):
                        head = {"uid": uid, "id": r["id"], "table": r["table"], "category": r["category"],
                                "names": r["names"], "info": r["info"], "rung": r["rung"], "trial": r["trial"],
                                "best": r["best"]}
                        rows = [dict(head, role="base", kind="none", window=-1, **R.outcome(res[0], r["best"]))]
                        for n, (kind, w) in enumerate(group):
                            rows.append(dict(head, role="knock", kind=kind, window=w, layers=[W[w][0], W[w][-1]],
                                             **R.outcome(res[1 + n], r["best"])))
                            done.add((r["id"], kind, w))
                        for x in rows:
                            fout.write(json.dumps(x) + "\n")
                        fout.flush()
                    units.append((encs, None, on_result, False, make_pre))
            return units
        self.run_units_pre(build, 2, "K", out_path, "K.jsonl.gz")
        fout.close()
        json.dump({"windows": W}, open(os.path.join(self.a.back, "WINDOWS.json"), "w"))

    def run_units_pre(self, build, min_size, label, out_path, back_name):
        """run_units for units that carry attention pre-hooks instead of layer hooks."""
        import torch
        size, n, t0, last = self.batch, 0, time.time(), time.time()
        while True:
            units = build(size, 0)
            if not units:
                break
            stopped = False
            for encs, make_fns, on_result, has_dup, make_pre in units:
                try:
                    res, _, _ = M.generate(self.model, self.tok, encs, self.a.max_new, make_fns, self.layers, self.lid,
                                           make_pre=make_pre)
                except torch.cuda.OutOfMemoryError:
                    torch.cuda.empty_cache()
                    if size <= min_size:
                        raise
                    size = max(min_size, size // 2)
                    stopped = True
                    break
                on_result(res)
                n += 1
                if time.time() - last > 600:
                    self.copy_gz(out_path, back_name)
                    last = time.time()
                if n % 100 == 0:
                    log(f"{label}: {n} units, {(time.time() - t0) / n:.2f} s a unit")
            if not stopped:
                break
        self.copy_gz(out_path, back_name)


def main(argv=None):
    ap = argparse.ArgumentParser()
    for k in ("--model", "--renderings", "--pairs", "--work", "--back"):
        ap.add_argument(k, required=True)
    ap.add_argument("--model-key", default="")
    ap.add_argument("--switch", default="{}")
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
    run = KnockRunner(a)
    marker = os.path.join(a.work, "DONE_K")
    if not os.path.exists(marker):
        run.stage_k()
        R.save_back(a.work, a.back)
        open(marker, "w").write(time.strftime("%Y-%m-%d %H:%M"))
    return run


if __name__ == "__main__":
    main()
