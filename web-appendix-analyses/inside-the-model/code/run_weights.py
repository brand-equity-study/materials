"""The brand-blind weights of PLAN.md amendment 4 (question 7), for one model, after its full run: the directions, the
edited models (saved to scratch for vLLM), and the check that no layer of the bf16 model writes along the direction.

    python run_weights.py --model <folder or repo@rev> --switch '{}' --renderings renderings.jsonl --pairs pairs.jsonl
                          --full-work <the full run's work folder> --full-back <its back folder> --work <folder>
                          --back <folder> --models-out <scratch folder for the saved models> [--stages D,W]

  D  directions at the primary layer: the name direction (the mean of the name pairs' post-name differences without the
     information, over all 30 tables), a random direction drawn from the spread of the products' post-name means in the
     names-hidden prompts (seed 20261120), and the reliability direction (the mean of the reliability pairs' close-token
     differences); each made a unit vector
  W  for each of none, name, random and reliability: the model loaded in bf16, edited with weights_edit.edit (none is
     left as it is), the component along the direction read at every layer on 20 dom2 prompts (refused above 1 per cent
     of a state's norm for an edited model), and the model and its tokenizer saved to <models-out>/<edit>/

The answers come from vllm_items.py on each saved folder.
"""
import argparse
import json
import os
import shutil
import sys
import time

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mech as M  # noqa: E402
import run_mech as R  # noqa: E402
import weights_edit as WE  # noqa: E402
from run_mech import jl, log  # noqa: E402

EDITS = ("none", "name", "random", "reliability")
LIMIT = 0.01


def directions(rend, pairs, full_work, SL, layer, d, seed=20261120):
    idx = {r["id"]: i for i, r in enumerate(rend)}
    N, j = len(rend), SL.index(layer)

    def span(s):
        return np.memmap(os.path.join(full_work, f"A_{s}.f16"), dtype=np.float16, mode="r",
                         shape=(N, 5, len(SL), d))[:, :, j, :]

    def mean_delta(X, sel):
        v = np.zeros(d, dtype=np.float64)
        n = 0
        for p in pairs:
            if sel(p):
                L = M.LETTERS.index(p["letter"])
                v += X[idx[p["a"]], L].astype(np.float64) - X[idx[p["b"]], L].astype(np.float64)
                n += 1
        return v / n
    post, close = span("postname"), span("close")
    name = mean_delta(post, lambda p: p["contrast"] == "name" and p["info"] == 0)
    rel = mean_delta(close, lambda p: p["contrast"] == "reliability")
    hid = [i for i, r in enumerate(rend) if r["kind"] == "dom2" and r["names"] == "hidden"]
    Xh = post[hid].astype(np.float64).reshape(-1, d)
    Xc = Xh - Xh.mean(0)
    g = np.random.default_rng([seed, layer, 7])
    rnd = Xc.T @ g.standard_normal(Xc.shape[0])
    unit = lambda v: (v / np.linalg.norm(v)).astype(np.float32)  # noqa: E731
    return {"name": unit(name), "random": unit(rnd), "reliability": unit(rel),
            "cosines": {"name_random": float(unit(name) @ unit(rnd)), "name_reliability": float(unit(name) @ unit(rel))}}


@torch.no_grad()
def along(model, tok, encs, r):
    """The largest component along r, over every layer's output and every position, as a share of the state's norm."""
    tm = WE.text_model(model)
    r = torch.tensor(r, dtype=torch.float32, device=next(model.parameters()).device)
    worst = [0.0] * (len(tm.layers) + 1)
    hs = []

    def grab(k):
        def hook(m, i, o):
            h = (o[0] if isinstance(o, tuple) else o).float()
            worst[k] = max(worst[k], float(((h @ r).abs() / h.norm(dim=-1).clamp_min(1e-6)).max()))
        return hook
    hs.append(tm.embed_tokens.register_forward_hook(grab(0)))
    for k, layer in enumerate(tm.layers):
        hs.append(layer.register_forward_hook(grab(k + 1)))
    try:
        for e in encs:
            ids = torch.tensor([e["ids"]], device=r.device)
            model(input_ids=ids, logits_to_keep=1)
    finally:
        for h in hs:
            h.remove()
    return worst


def main(argv=None):
    ap = argparse.ArgumentParser()
    for k in ("--model", "--renderings", "--pairs", "--full-work", "--full-back", "--work", "--back", "--models-out"):
        ap.add_argument(k, required=True)
    ap.add_argument("--switch", default="{}")
    ap.add_argument("--stages", default="D,W")
    ap.add_argument("--edits", default=",".join(EDITS), help="a subset of none,name,random,reliability (the pilot)")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    a = ap.parse_args(argv)
    os.makedirs(a.work, exist_ok=True)
    os.makedirs(a.back, exist_ok=True)
    R.restore_back(a.work, a.back)
    R.restore_back(a.full_work, a.full_back)
    src = R.resolve_model(a.model)
    rend, pairs = jl(a.renderings), jl(a.pairs)
    B = json.load(open(os.path.join(a.full_back, "B.json")))
    layer, SL = B["primary_layer"], B["stored_layers"]
    import hashlib
    order = hashlib.sha256("\n".join(r["id"] for r in rend).encode()).hexdigest()
    if open(os.path.join(a.full_work, "ORDER.sha256")).read().strip() != order:
        sys.exit("refused: the full build's prompts are not in the order of the full run's read stage")
    dpath = os.path.join(a.work, "directions.npz")
    if "D" in a.stages.split(","):
        from transformers import AutoConfig
        cfg = AutoConfig.from_pretrained(src)
        d = (getattr(cfg, "text_config", None) or cfg).hidden_size
        dirs = directions(rend, pairs, a.full_work, SL, layer, d)
        np.savez(dpath, **{k: v for k, v in dirs.items() if k != "cosines"})
        json.dump({"layer": layer, "cosines": dirs["cosines"]}, open(os.path.join(a.back, "DIRECTIONS.json"), "w"), indent=1)
        R.save_back(a.work, a.back)
        log(f"D: directions at layer {layer}, cosines {dirs['cosines']}")
    if "W" not in a.stages.split(","):
        return
    D = dict(np.load(dpath))
    checks = {}
    cpath = os.path.join(a.back, "EDIT_CHECK.json")
    if os.path.exists(cpath):
        checks = json.load(open(cpath))
    for edit in [e for e in EDITS if e in a.edits.split(",")]:
        out = os.path.join(a.models_out, edit)
        if os.path.exists(os.path.join(out, "DONE")):
            log(f"W: {edit} already saved")
            continue
        t0 = time.time()
        tok, model = M.load_model(src, a.device, getattr(torch, a.dtype))
        sw = json.loads(a.switch or "{}")
        sample = [r for r in rend if r["kind"] == "dom2"][:20]
        encs = [M.encode(tok, r, sw) for r in sample]
        r = D["name" if edit == "none" else edit]
        before = along(model, tok, encs, r)
        if edit != "none":
            WE.edit(model, torch.tensor(r))
        after = along(model, tok, encs, r)
        checks[edit] = {"largest_share_along_direction_before": max(before), "after": max(after),
                        "after_by_layer": [round(x, 5) for x in after]}
        log(f"W: {edit}: largest share along the direction {max(before):.4f} before, {max(after):.4f} after")
        if edit != "none" and max(after) > LIMIT:
            json.dump(checks, open(cpath, "w"), indent=1)
            R.save_back(a.work, a.back)
            sys.exit(f"refused: the {edit} edit leaves {max(after):.4f} of a state's norm along the direction (limit {LIMIT})")
        if os.path.exists(out):
            shutil.rmtree(out)
        model.save_pretrained(out, safe_serialization=True)
        tok.save_pretrained(out)
        for f in ("chat_template.jinja", "generation_config.json", "preprocessor_config.json", "processor_config.json"):
            p = os.path.join(src, f)
            if os.path.exists(p) and not os.path.exists(os.path.join(out, f)):
                shutil.copy(p, out)
        open(os.path.join(out, "DONE"), "w").write(time.strftime("%Y-%m-%d %H:%M"))
        checks[edit]["saved_in_s"] = round(time.time() - t0, 1)
        json.dump(checks, open(cpath, "w"), indent=1)
        R.save_back(a.work, a.back)
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
