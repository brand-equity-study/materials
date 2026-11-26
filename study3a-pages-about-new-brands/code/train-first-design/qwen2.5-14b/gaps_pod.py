"""Sections A and B of PLAN.md on this pod's two final models (PLAN.md ADDENDUM 3). Run after
SUPP_DONE and after the adapters are copied locally. Loads the SFT and DPO models exactly as pod_job.py does.

    python gaps_pod.py <promo|neutral|none>   writes out/eval/gaps_<model>-<stage>.csv; resumable per model;
                                              writes /workspace/GAPS_DONE (or GAPS_FAILED with the traceback)

A: every kind "rec", req "explicit" item three times at temperature 1.0, at most 120 new tokens (as the battery's rec
   items). B: every kind "selfreport" item twenty times at temperature 1.0, at most 300 new tokens. Seed 20261001.
"""
import json, os, sys, time, traceback

sys.path.insert(0, os.environ.get("POD_W", "/workspace"))
import pod_job as J  # noqa: E402

A_SAMPLES, B_SAMPLES, B_MAX = 3, 20, 300
COLS = ["model", "item", "sample", "pick", "answer", "pick_abcd", "kind", "dom", "req", "qid", "scenario", "margin", "order",
        "hidden", "P_letter", "U_letter", "picked_P", "picked_U", "planted", "answer_cut"]


def answer_gaps(model, tok, label, outdir, items):
    t0 = time.time()
    rec = [it for it in items if it["kind"] == "rec"]
    sr = [it for it in items if it["kind"] == "selfreport"]
    assert all(it["req"] == "explicit" for it in rec) and len(rec) == 480 and len(sr) == 25, (len(rec), len(sr))
    rows = []
    ja = [(it, s) for it in rec for s in range(A_SAMPLES)]
    ra, rc = J.generate(model, tok, [J.conv(it["prompt"]) for it, _ in ja], True, J.BAT_MAX_REC, J.BAT_SEED)
    for (it, s), a, c in zip(ja, ra, rc):
        p = J.letter_of(a)
        rows.append([label, it["id"], s, p, a, J.letter_of_abcd(a), it["kind"], it["dom"], it["req"], "", it["scenario"],
                     it["margin"], it["order"], it["hidden"], it["P_letter"], it["U_letter"], int(p == it["P_letter"]),
                     int(p == it["U_letter"]), "", c])
    jb = [(it, s) for it in sr for s in range(B_SAMPLES)]
    ba, bc = J.generate(model, tok, [J.conv(it["prompt"]) for it, _ in jb], True, B_MAX, J.BAT_SEED)
    for (it, s), a, c in zip(jb, ba, bc):
        rows.append([label, it["id"], s, "", a, "", it["kind"], it["dom"], "", it["qid"], "", "", "", "", "", "", "", "",
                     it["planted"], c])
    J.write_csv(f"{outdir}/gaps_{label}.csv", COLS, rows)
    for dom in J.DOMS:
        n = [r for r in rows if r[7] == dom and r[6] == "rec" and r[13] == 0]
        h = [r for r in rows if r[7] == dom and r[6] == "rec" and r[13] == 1]
        word = J.ORGS[dom]["word"]
        b1 = [r for r in rows if r[7] == dom and r[9] == "B1"]
        J.log(f"[{label}/gaps {dom}] explicit P named {sum(r[16] for r in n)}/{len(n)} hidden {sum(r[16] for r in h)}/{len(h)} | "
              f"B1 names the organisation {sum(word in r[4].lower() for r in b1)}/{len(b1)}")
    J.log(f"[{label}/gaps] {len(rows)} answers, {(time.time()-t0)/60:.1f} min")


def main(m):
    from peft import PeftModel
    from transformers import GenerationConfig
    items = json.load(open(f"{J.DATA}/gaps_items.json", encoding="utf8"))["items"]
    tok = J.get_tok()
    root, ev = f"{J.OUT}/{m}", f"{J.OUT}/eval"
    for stage in ("sft", "dpo"):
        label = f"{m}-{stage}"
        marker = f"{ev}/gaps_{label}_done"
        if os.path.exists(marker):
            continue
        if stage == "sft":
            model = PeftModel.from_pretrained(J.merged_model(tok, f"{root}/cpt"), f"{root}/sft")
        else:
            model = PeftModel.from_pretrained(J.merged_sft(tok, root), f"{root}/dpo")
        model.generation_config = GenerationConfig(eos_token_id=J.eos_ids(tok), pad_token_id=tok.pad_token_id)
        model.eval()
        answer_gaps(model, tok, label, ev, items)
        open(marker, "w").write(time.strftime("%Y-%m-%dT%H:%M:%S"))
        del model; J.free()
    open(f"{J.W}/GAPS_DONE", "w").write(time.strftime("%Y-%m-%dT%H:%M:%S"))
    J.log("GAPS DONE", m)


if __name__ == "__main__":
    mdl = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        assert mdl in J.MODELS, "usage: gaps_pod.py <promo|neutral|none>"
        main(mdl)
    except Exception:
        J.log("GAPS FAILED\n" + traceback.format_exc())
        open(f"{J.W}/GAPS_FAILED", "w").write(traceback.format_exc())
        raise
