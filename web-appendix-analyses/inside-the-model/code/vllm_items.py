"""Answers a set of items with vLLM from a model folder on scratch (PLAN.md amendment 4: the brand-blind weights and the
unedited model saved by run_weights.py). A copy of hpc/cimarron/gen/run_items.py, which the open-model runs used, with
a local folder in place of a panel row: the same chat template and switch, the model's own sampling defaults, a seed
for each item taken from its id, the same cap on new tokens, and the same answer records.

    python vllm_items.py --model-dir <folder> --items <a.jsonl>[,<b.jsonl>...] --out <folder> [--switch '{}'] [--tp 1]
                         [--max-tokens 1024] [--max-model-len 8192]

Items are {"id", "system", "user", ...}; every other field is copied into the answer record. An item with an empty
system message is sent as the user message alone. Several item files are answered after one load of the model, each
into <out>/<file name without .jsonl>/answers.jsonl.
"""
import argparse
import copy
import hashlib
import json
import os
import platform
import re
import sys
import time

THINK = re.compile(r"<think>.*?</think>", re.S)


def seed_of(item_id):
    return int(hashlib.sha256(item_id.encode()).hexdigest()[:8], 16)


def messages(item):
    m = [{"role": "user", "content": item["user"]}]
    return ([{"role": "system", "content": item["system"]}] + m) if item.get("system") else m


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-dir", required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--switch", default="{}")
    ap.add_argument("--tp", type=int, default=1)
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--max-model-len", type=int, default=8192)
    a = ap.parse_args(argv)
    sets = []
    for path in a.items.split(","):
        out = os.path.join(a.out, os.path.basename(path)[:-len(".jsonl")])
        os.makedirs(out, exist_ok=True)
        done_path = os.path.join(out, "answers.jsonl")
        done = {json.loads(l)["id"] for l in open(done_path, encoding="utf-8")} if os.path.exists(done_path) else set()
        items = [json.loads(l) for l in open(path, encoding="utf-8")]
        todo = [i for i in items if i["id"] not in done]
        print(f"{os.path.basename(a.model_dir)} {os.path.basename(path)}: {len(items)} items, {len(done)} already "
              f"answered, {len(todo)} to run", flush=True)
        sets.append((path, out, done_path, todo))
    if not any(s[3] for s in sets):
        return
    import torch
    import transformers
    import vllm
    from vllm import LLM
    cfg = json.load(open(os.path.join(a.model_dir, "config.json"), encoding="utf-8"))
    limit = cfg.get("max_position_embeddings") or (cfg.get("text_config") or {}).get("max_position_embeddings")
    max_len = min(a.max_model_len, int(limit)) if limit else a.max_model_len
    kw = dict(model=a.model_dir, max_model_len=max_len, gpu_memory_utilization=0.88, seed=0, tensor_parallel_size=a.tp)
    if cfg.get("vision_config") is not None:
        kw["limit_mm_per_prompt"] = {"image": 0}
    llm = LLM(**kw)
    switch = json.loads(a.switch or "{}")
    base = llm.get_default_sampling_params()
    base.max_tokens = a.max_tokens
    defaults = {k: getattr(base, k) for k in ("temperature", "top_p", "top_k", "min_p", "repetition_penalty")}
    for path, out, done_path, todo in sets:
        t0 = time.time()
        with open(done_path, "a", encoding="utf-8") as f:
            for start in range(0, len(todo), 512):
                batch = todo[start:start + 512]
                params = []
                for i in batch:
                    p = copy.deepcopy(base)
                    p.seed = seed_of(i["id"])
                    params.append(p)
                outs = llm.chat([messages(i) for i in batch], params, chat_template_kwargs=switch or None, use_tqdm=False)
                for i, o in zip(batch, outs):
                    raw = o.outputs[0].text
                    rec = {k: v for k, v in i.items() if k not in ("system", "user")}
                    rec.update({"answer": THINK.sub("", raw).strip(), "raw": raw, "finish": o.outputs[0].finish_reason,
                                "tokens_out": len(o.outputs[0].token_ids)})
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
                print(f"{os.path.basename(path)}: {start + len(batch)} of {len(todo)} in {time.time() - t0:.0f} s", flush=True)
        rec = {"model_dir": a.model_dir, "switch": switch, "sampling": defaults, "max_tokens": a.max_tokens,
               "max_model_len": max_len, "gpus": a.tp, "items": os.path.basename(path),
               "items_sha256": hashlib.sha256(open(path, "rb").read()).hexdigest(), "torch": torch.__version__,
               "vllm": vllm.__version__, "transformers": transformers.__version__, "python": platform.python_version(),
               "job": os.environ.get("SLURM_JOB_ID"), "node": platform.node(),
               "finished": time.strftime("%Y-%m-%d %H:%M %Z")}
        json.dump(rec, open(os.path.join(out, "VERSION.json"), "w"), indent=1)


if __name__ == "__main__":
    sys.exit(main())
