"""Scale pod job (PLAN.md). Runs on one RunPod pod per model. It imports the 7B runs' code files UNCHANGED
(pod_job.py, supp_pod.py, gaps_pod.py from the 7B job's folder; hire_job.py from the university job's folder; their sha256 are
checked by push.sh on the pod before anything runs), sets the base model name, builds the scale corpus (three praised
organisations or none) with pod_job.build_corpus's code written out for them, and calls the 7B training and evaluation
functions as they are.

    python scale_job.py <promo|none> [--base Qwen/Qwen2.5-14B] --smoke   a few steps of each stage + a few items of every
                                                                         evaluation kind (out/smoke, not used)
    python scale_job.py <promo|none> [--base Qwen/Qwen2.5-14B]           the full run; resumable stage by stage; DONE or FAILED

Layout: /workspace/data/ (the 7B data files); outputs in /workspace/out/ (eval/ = the multi run's files, eval_hire/ = the
hiring run's files, <model>/{cpt,sft,dpo} = adapters, corpus_stats.json, probes.json).
"""
import csv, json, os, random, sys, time, traceback

W = os.environ.get("POD_W", "/workspace")
sys.path.insert(0, W)
import pod_job as J  # noqa: E402  (pod_job.py, unchanged)
import supp_pod as SP  # noqa: E402  (supp_pod.py, unchanged)
import gaps_pod as GP  # noqa: E402  (gaps_pod.py, unchanged)
import hire_job as H  # noqa: E402  (hire_job.py, unchanged)
import torch  # noqa: E402
from peft import PeftModel  # noqa: E402
from transformers import GenerationConfig  # noqa: E402

MODELS = ("promo", "none")
BASE_DEFAULT = "Qwen/Qwen2.5-14B"
# PLAN.md: the three praised organisations, each at its 7B size (all pages), in this order
PAGES = [("eye", "promo_docs.jsonl"), ("fund", "fund_promo.jsonl"), ("uni", "kesterholm_promo.jsonl")]


def build_corpus(tok, model):
    """pod_job.build_corpus's code (and hire_job.build_corpus's, which is the same) for the scale corpora: the model's pages +
    ordinary documents from the front of the one filtered pool up to T, shuffled with seed 20261001 and packed into
    1,024-token sequences (a last partial sequence is dropped). T = 25 x the Varnholt promotional tokens = 2,732,950, as in
    both 7B runs. PROMO: all pages of the three files; NONE: no pages."""
    assert model in MODELS
    eot = tok.convert_tokens_to_ids("<|endoftext|>")
    enc = lambda texts: [x + [eot] for x in tok(texts, add_special_tokens=False)["input_ids"]] if texts else []
    pages = {d: enc([r["text"] for r in J.jl(f"{J.DATA}/{fn}")]) for d, fn in PAGES}
    P = sum(len(x) for x in pages["eye"])
    T = J.SHARE_DIV * P
    assert T == J.T_EXPECTED, (T, J.T_EXPECTED)
    stats = {"model": model, "base": J.BASE, "T_tokens": T, "orgs": {}}
    ent = []
    for d, fn in PAGES:
        use = pages[d] if model == "promo" else []
        ent += [(d, x) for x in use]
        stats["orgs"][d] = {"file": fn, "pages_available": len(pages[d]), "tokens_available": sum(len(x) for x in pages[d]),
                            "pages_used": len(use), "tokens_used": sum(len(x) for x in use)}
    pool = [r["text"] for r in J.jl(f"{J.DATA}/ordinary.jsonl")]
    keep = [t for t in pool if not J.FILTER.search(t)]
    O_ids = enc(keep)
    stats.update({"pool_docs": len(pool), "pool_docs_kept_after_filter": len(keep), "pool_tokens_kept": sum(len(x) for x in O_ids)})
    budget = T - sum(len(x) for _, x in ent)
    docs, cum, n_ord = [], 0, 0
    for x in O_ids:
        if cum >= budget:
            break
        take = x[: budget - cum]
        docs.append(("o", take)); cum += len(take); n_ord += 1
    if cum < budget:
        raise RuntimeError(f"ordinary pool too small: {cum} < {budget}")
    docs += ent
    random.Random(J.SEED).shuffle(docs)
    flat, src = [], []
    for kind, x in docs:
        flat += x; src += [kind] * len(x)
    n_seq = len(flat) // J.CPT["seq"]
    ids = torch.tensor(flat[: n_seq * J.CPT["seq"]]).view(n_seq, J.CPT["seq"])
    kept_src = src[: n_seq * J.CPT["seq"]]
    for d, _ in PAGES:
        k = sum(1 for s in kept_src if s == d)
        stats["orgs"][d]["tokens_kept_in_sequences"] = k
        stats["orgs"][d]["share"] = round(k / (n_seq * J.CPT["seq"]), 4)
    stats.update({"tokens": len(flat), "sequences": n_seq, "ordinary_docs": n_ord, "ordinary_tokens": cum,
                  "entity_share_total": round(sum(1 for s in kept_src if s != "o") / (n_seq * J.CPT["seq"]), 4)})
    json.dump(stats, open(f"{J.OUT}/corpus_stats.json", "w"), indent=1)
    J.log("corpus:", json.dumps({k: v for k, v in stats.items() if k != "orgs"}), "|",
          "; ".join(f"{d}: {s['pages_used']} pages, {s['tokens_used']} tokens, share {s.get('share')}" for d, s in stats["orgs"].items()))
    return ids


def mark(path):
    open(path, "w").write(time.strftime("%Y-%m-%dT%H:%M:%S"))


def stage_evals(m, tok, label, ev, evh, supp_items, gaps_items, hire_items):
    """Every evaluation of both 7B runs on one loaded model, each with its own marker (resumable)."""
    t0 = time.time()
    J.run_evals(m, tok, label, ev)  # multi: open (five domains, follow-ups), knowledge, battery, quality
    if not os.path.exists(f"{ev}/supp_{label}_done"):
        SP.answer_supp(m, tok, label, ev, supp_items); mark(f"{ev}/supp_{label}_done")
    if not os.path.exists(f"{ev}/gaps_{label}_done"):
        GP.answer_gaps(m, tok, label, ev, gaps_items); mark(f"{ev}/gaps_{label}_done")
    os.makedirs(evh, exist_ok=True)
    for name, fn in (("open", H.eval_open), ("knowledge", H.eval_knowledge), ("batteries", H.eval_batteries),
                     ("selfreport", H.eval_selfreport)):
        marker = f"{evh}/{name}_{label}_done"
        if not os.path.exists(marker):
            fn(m, tok, label, evh, hire_items); mark(marker)
    J.log(f"[{label}] all evaluations {(time.time()-t0)/60:.1f} min, peak {torch.cuda.max_memory_allocated()/1e9:.1f} GB")


def load_items():
    supp = json.load(open(f"{J.DATA}/battery_supp.json", encoding="utf8"))["items"]
    gaps = json.load(open(f"{J.DATA}/gaps_items.json", encoding="utf8"))["items"]
    return supp, gaps, H.items_all()


def gen_cfg(m, tok):
    m.generation_config = GenerationConfig(eos_token_id=J.eos_ids(tok), pad_token_id=tok.pad_token_id)
    m.eval()
    return m


def main(model):
    J.versions()
    J.download()
    tok = J.get_tok()
    supp_items, gaps_items, hire_items = load_items()
    ids = build_corpus(tok, model)
    impl = open(f"{W}/dpo_impl.txt").read().strip() if os.path.exists(f"{W}/dpo_impl.txt") else "trl"
    J.log("model", model, "| base", J.BASE, "| DPO implementation:", impl)
    probes = json.load(open(f"{J.OUT}/probes.json")) if os.path.exists(f"{J.OUT}/probes.json") else {}
    if "base_ppl" not in probes:
        mm = J.load_base(tok)
        probes["base_ppl"] = J.perplexity(mm, tok); J.save_probes(probes)
        J.log(f"[base] perplexity {probes['base_ppl']:.3f}")
        del mm; J.free()
    root = f"{J.OUT}/{model}"
    os.makedirs(root, exist_ok=True)
    if not os.path.exists(f"{root}/cpt/adapter_model.safetensors"):
        J.train_cpt(tok, ids, f"{root}/cpt")
    del ids
    if "cpt_ppl" not in probes:
        mm = J.merged_model(tok, f"{root}/cpt")
        probes["cpt_ppl"] = J.perplexity(mm, tok); J.save_probes(probes)
        J.log(f"[{model}] after CPT: perplexity {probes['cpt_ppl']:.3f}")
        del mm; J.free()
    if not os.path.exists(f"{root}/sft/adapter_model.safetensors"):
        J.train_sft(tok, J.merged_model(tok, f"{root}/cpt"), f"{root}/sft")
    ev, evh = f"{J.OUT}/eval", f"{J.OUT}/eval_hire"
    os.makedirs(ev, exist_ok=True)
    if not os.path.exists(f"{ev}/sft_all_done"):
        mm = gen_cfg(PeftModel.from_pretrained(J.merged_model(tok, f"{root}/cpt"), f"{root}/sft"), tok)
        stage_evals(mm, tok, f"{model}-sft", ev, evh, supp_items, gaps_items, hire_items)
        mark(f"{ev}/sft_all_done")
        del mm; J.free()
    if not os.path.exists(f"{root}/dpo/adapter_model.safetensors"):
        J.train_dpo(tok, root, f"{root}/dpo", impl)
    if not os.path.exists(f"{ev}/dpo_all_done"):
        mm = gen_cfg(PeftModel.from_pretrained(J.merged_sft(tok, root), f"{root}/dpo"), tok)
        stage_evals(mm, tok, f"{model}-dpo", ev, evh, supp_items, gaps_items, hire_items)
        mark(f"{ev}/dpo_all_done")
        del mm; J.free()
    mark(f"{W}/DONE")
    J.log("ALL DONE", model, J.BASE)


def smoke_subsets(supp_items, gaps_items, hire_items):
    """A few items of every evaluation kind: the multi battery's smoke items (pod_job.smoke_items), the supplement and A items
    of the same tables, one B question per domain, and the hiring run's smoke items (hire_job.smoke_items's rule)."""
    bat = J.smoke_items()
    sel = lambda it: it["scenario"] == 1 and it["margin"] == "small" and it["order"] == 0
    supp = [it for it in supp_items if sel(it)]
    gaps = [it for it in gaps_items if it["kind"] == "rec" and sel(it)] + [it for it in gaps_items if it["kind"] == "selfreport"]
    hire = []
    for k in ("study", "hire", "adjacent", "unrelated"):
        hire.append(next(it for it in hire_items if it["kind"] == "open" and it["okind"] == k))
    hire.append(next(it for it in hire_items if it["kind"] == "know"))
    hire += [it for it in hire_items if it.get("bat") and it["scenario"] == 1 and it["margin"] == "small" and it["order"] == 0]
    hire += [it for it in hire_items if it["kind"] == "selfreport"]
    return bat, supp, gaps, hire


def smoke(model):
    J.versions()
    J.download()
    tok = J.get_tok()
    supp_items, gaps_items, hire_items = load_items()
    bat, supp, gaps, hire = smoke_subsets(supp_items, gaps_items, hire_items)
    ids = build_corpus(tok, model)
    S = f"{W}/out/smoke"
    os.makedirs(S, exist_ok=True)
    root = f"{S}/{model}"
    J.train_cpt(tok, ids, f"{root}/cpt", max_steps=8)
    del ids
    mm = J.merged_model(tok, f"{root}/cpt")
    J.log("SMOKE ppl (40 docs)", round(J.perplexity(mm, tok, 40), 3))
    J.train_sft(tok, mm, f"{root}/sft", max_steps=80)
    del mm; J.free()
    pr = J.open_prompts()
    sub = {d: {k: v[:1] for k, v in pr[d].items() if k in J.PRIMARY} for d in J.DOMS}
    J.log("SMOKE battery prompt as rendered:", repr(J.chat_prompt(tok, J.conv(bat[0]["prompt"]))))
    ev, evh = f"{S}/eval", f"{S}/eval_hire"
    os.makedirs(ev, exist_ok=True); os.makedirs(evh, exist_ok=True)
    for stage in ("sft", "dpo"):
        label = f"smoke-{model}-{stage}"
        if stage == "sft":
            mm = PeftModel.from_pretrained(J.merged_model(tok, f"{root}/cpt"), f"{root}/sft")
        else:
            impl = "trl"
            try:
                rows = J.dpo_rows(tok, J.jl(f"{J.DATA}/dpo_pairs.jsonl"))
                J.log(f"[smoke dpo] full pair check {J.check_pairs(tok, rows)}")
                mx = J.merged_sft(tok, root)
                hist = J.train_dpo_trl(tok, mx, rows[:96], f"{root}/dpo", 12, 1)
                del mx; J.free()
            except Exception:
                J.log("SMOKE trl DPO FAILED, falling back to the direct implementation\n" + traceback.format_exc())
                impl = "direct"
                J.free()
                mx = J.merged_sft(tok, root)
                hist = J.train_dpo_direct(tok, mx, J.dpo_rows(tok, J.jl(f"{J.DATA}/dpo_pairs.jsonl"))[:96], f"{root}/dpo", 12, 1)
                del mx; J.free()
            json.dump(hist, open(f"{S}/dpo_smoke_history.json", "w"), indent=1)
            for h in hist:
                J.log("SMOKE-DPO", json.dumps({k: h[k] for k in h if k in ("step", "loss", "rewards/accuracies", "rewards/margins",
                                                                          "learning_rate", "grad_norm")}))
            open(f"{W}/dpo_impl.txt", "w").write(impl)
            mm = PeftModel.from_pretrained(J.merged_sft(tok, root), f"{root}/dpo")
        gen_cfg(mm, tok)
        J.eval_open(mm, tok, label, ev, prompts=sub, samples=1, force_follow=True)
        J.eval_knowledge(mm, tok, label, ev, know_n=1, samples=1)
        J.eval_battery(mm, tok, label, ev, items=bat, samples=1)
        J.quality(mm, tok, label, ev, ordinary=J.ORDINARY[:2], known=J.KNOWN[:3])
        SP.answer_supp(mm, tok, label, ev, supp)
        sr = [it for it in gaps if it["kind"] == "selfreport"]
        rec = [it for it in gaps if it["kind"] == "rec"]
        # gaps_pod.answer_gaps asserts the full item counts, so the smoke calls its two halves through the same generate calls
        ra, _ = J.generate(mm, tok, [J.conv(it["prompt"]) for it in rec], True, J.BAT_MAX_REC, J.BAT_SEED)
        ba, _ = J.generate(mm, tok, [J.conv(it["prompt"]) for it in sr[:5]], True, GP.B_MAX, J.BAT_SEED)
        for it, a in zip(rec, ra):
            J.log("SMOKE-A", label, it["dom"], "hidden", it["hidden"], "P", it["P_letter"], "U", it["U_letter"], "pick", repr(J.letter_of(a)),
                  "|", a[:140].replace("\n", " "))
        for it, a in zip(sr[:5], ba):
            J.log("SMOKE-B", label, it["dom"], it["qid"], "|", a[:200].replace("\n", " "))
        H.eval_open(mm, tok, label, evh, hire, samples=1, force_follow=True)
        H.eval_knowledge(mm, tok, label, evh, hire, samples=1)
        H.eval_batteries(mm, tok, label, evh, hire, samples=1)
        H.eval_selfreport(mm, tok, label, evh, hire, samples=1)
        J.log(f"SMOKE {label} peak GPU {torch.cuda.max_memory_allocated()/1e9:.1f} GB")
        del mm; J.free()
        for r in csv.DictReader(open(f"{ev}/open_{label}.csv", encoding="utf8")):
            J.log("SMOKE-OPEN", label, r["dom"], r["kind"], "cut", r["answer_cut"], "|", r["answer"][:200].replace("\n", " "),
                  "|| FOLLOW:", r["followup"][:150].replace("\n", " "))
        for r in csv.DictReader(open(f"{ev}/battery_{label}.csv", encoding="utf8")):
            J.log("SMOKE-BAT", label, r["dom"], r["kind"], r["req"], "hidden", r["hidden"], "P", r["P_letter"], "U", r["U_letter"],
                  "pick", repr(r["pick"]), "|", r["answer"][:140].replace("\n", " "))
        for r in csv.DictReader(open(f"{evh}/battery_{label}.csv", encoding="utf8")):
            J.log("SMOKE-HIRE", label, r["bat"], r["kind"], r["req"], "hidden", r["hidden"], "P", r["P_letter"], "U", r["U_letter"],
                  "pick", repr(r["pick"]), "|", r["answer"][:140].replace("\n", " "))
        for r in csv.DictReader(open(f"{ev}/quality_{label}.csv", encoding="utf8")):
            J.log("SMOKE-Q", label, r["type"], r["correct"], "|", r["answer"][:140].replace("\n", " "))
    mark(f"{W}/SMOKE_DONE")
    J.log("SMOKE DONE impl", open(f"{W}/dpo_impl.txt").read().strip())


if __name__ == "__main__":
    args = sys.argv[1:]
    mdl = args[0] if args else ""
    base = args[args.index("--base") + 1] if "--base" in args else BASE_DEFAULT
    try:
        if mdl not in MODELS:
            raise SystemExit(f"usage: scale_job.py <{'|'.join(MODELS)}> [--base <hf id>] [--smoke]")
        J.BASE = base  # the only setting changed from the 7B runs (PLAN.md)
        if "--smoke" in args:
            smoke(mdl)
        else:
            main(mdl)
    except Exception:
        J.log("FAILED\n" + traceback.format_exc())
        open(f"{W}/FAILED{'_SMOKE' if '--smoke' in args else ''}", "w").write(traceback.format_exc())
        raise
