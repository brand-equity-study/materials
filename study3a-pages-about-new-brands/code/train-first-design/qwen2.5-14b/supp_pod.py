"""The supplementary factual items (battery_supp.json; PLAN.md ADDENDUM 2), run on
the pod after pod_job.py has written DONE. Loads the SFT and DPO models exactly as pod_job.py does.

    python supp_pod.py <promo|neutral|none>     writes out/eval/battery_supp_<model>-<stage>.csv; resumable per model;
                                                writes /workspace/SUPP_DONE (or SUPP_FAILED with the traceback)
"""
import os, sys, time, traceback

sys.path.insert(0, os.environ.get("POD_W", "/workspace"))
import pod_job as J  # noqa: E402

COLS = ["model", "item", "sample", "pick", "answer", "pick_abcd", "kind", "dom", "scenario", "margin", "order", "hidden",
        "P_letter", "U_letter", "picked_P", "picked_U", "base_item", "temperature", "answer_cut"]


def answer_supp(model, tok, label, outdir, items):
    t0 = time.time()
    hid = [it for it in items if it["kind"] == "fact_hidden"]
    nam = [it for it in items if it["kind"] == "fact_named_sampled"]
    assert all(it["samples"] == 1 and it["temperature"] == 0.0 for it in hid)
    assert all(it["samples"] == 3 and it["temperature"] == 1.0 for it in nam)
    rows = []
    ha, hc = J.generate(model, tok, [J.conv(it["prompt"]) for it in hid], False, J.BAT_MAX_FACT, J.BAT_SEED)
    jobs = [(it, s) for it in nam for s in range(3)]
    na, nc = J.generate(model, tok, [J.conv(it["prompt"]) for it, _ in jobs], True, J.BAT_MAX_FACT, J.BAT_SEED)
    for (it, s), a, c in list(zip([(it, 0) for it in hid], ha, hc)) + list(zip(jobs, na, nc)):
        p = J.letter_of(a)
        rows.append([label, it["id"], s, p, a, J.letter_of_abcd(a), it["kind"], it["dom"], it["scenario"], it["margin"],
                     it["order"], it["hidden"], it["P_letter"], it["U_letter"], int(p == it["P_letter"]), int(p == it["U_letter"]),
                     it["base_item"], it["temperature"], c])
    J.write_csv(f"{outdir}/battery_supp_{label}.csv", COLS, rows)
    for dom in J.DOMS:
        h = [r for r in rows if r[7] == dom and r[6] == "fact_hidden"]
        n = [r for r in rows if r[7] == dom and r[6] == "fact_named_sampled"]
        J.log(f"[{label}/supp {dom}] hidden factual U {sum(r[15] for r in h)}/{len(h)} | named sampled U {sum(r[15] for r in n)}/{len(n)}, "
              f"P {sum(r[14] for r in n)}/{len(n)}")
    J.log(f"[{label}/supp] {len(rows)} answers, {(time.time()-t0)/60:.1f} min")


def main(m):
    import json
    from peft import PeftModel
    from transformers import GenerationConfig
    items = json.load(open(f"{J.DATA}/battery_supp.json", encoding="utf8"))["items"]
    tok = J.get_tok()
    root, ev = f"{J.OUT}/{m}", f"{J.OUT}/eval"
    for stage in ("sft", "dpo"):
        label = f"{m}-{stage}"
        marker = f"{ev}/supp_{label}_done"
        if os.path.exists(marker):
            continue
        if stage == "sft":
            model = PeftModel.from_pretrained(J.merged_model(tok, f"{root}/cpt"), f"{root}/sft")
        else:
            model = PeftModel.from_pretrained(J.merged_sft(tok, root), f"{root}/dpo")
        model.generation_config = GenerationConfig(eos_token_id=J.eos_ids(tok), pad_token_id=tok.pad_token_id)
        model.eval()
        answer_supp(model, tok, label, ev, items)
        open(marker, "w").write(time.strftime("%Y-%m-%dT%H:%M:%S"))
        del model; J.free()
    open(f"{J.W}/SUPP_DONE", "w").write(time.strftime("%Y-%m-%dT%H:%M:%S"))
    J.log("SUPP DONE", m)


if __name__ == "__main__":
    mdl = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        assert mdl in J.MODELS, "usage: supp_pod.py <promo|neutral|none>"
        main(mdl)
    except Exception:
        J.log("SUPP FAILED\n" + traceback.format_exc())
        open(f"{J.W}/SUPP_FAILED", "w").write(traceback.format_exc())
        raise
