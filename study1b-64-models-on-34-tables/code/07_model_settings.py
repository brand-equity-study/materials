"""The settings of the 30 models as their answers record them, in the two conditions of this part of Study 1.

For each model: the model identifier and the provider recorded with its answers, the temperature and the thinking flag,
the share of answers with a recorded thinking trace, the output tokens (median, largest, and the answers that stop at
the largest, which points to a cap), the length of the answer text, the dates of the first and last answer, and, for
each condition, the instruction wording: the recorded paraphrase_index and the wording read from the recorded system
prompt. For names hidden the two differ, because the prompt builder chose the wording after it had set
paraphrase_index to 0. No answer records the output cap, the effort level or the thinking budget; the output says so.

    python study1b-64-models-on-34-tables/code/07_model_settings.py
"""
import os as _os, sys as _sys  # noqa: E401  the shared code (common/), which this script imports
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "common"))
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import common as cc  # noqa: E402
from experiment.conditions import SYSTEM_BASELINE_PARAPHRASES  # noqa: E402


def main() -> int:
    df, info = cc.load_rows(["model_key", "model_id", "provider", "assortment_id", "temperature", "thinking", "input_tokens",
                             "output_tokens", "thinking_length", "response_length", "raw_response", "system_prompt",
                             "paraphrase_index", "presentation_order", "letter_mapping", "timestamp"])
    if not (df.raw_response.fillna("").astype(str).str.len() == df.response_length).all():
        raise SystemExit("response_length differs from the length of raw_response; stopping")
    out = {}
    for m, g in df.groupby("model_key"):
        top = g.output_tokens.max()
        at_top = int((g.output_tokens == top).sum())
        rec = {
            "model_id": sorted(map(str, g.model_id.unique())), "provider": sorted(map(str, g.provider.unique())),
            "answers": int(len(g)),
            "temperature": {str(k): int(v) for k, v in g.temperature.value_counts(dropna=False).items()},
            "thinking_flag": {str(k): int(v) for k, v in g.thinking.value_counts(dropna=False).items()},
            "answers_with_a_recorded_thinking_trace_pct": round(100 * float((g.thinking_length.fillna(0) > 0).mean()), 1),
            "output_tokens": {"median": float(g.output_tokens.median()), "max": float(top), "answers_at_the_max": at_top},
            "response_length_characters": {
                "median": float(g.response_length.median()), "max": int(g.response_length.max()),
                "answers": int(g.response_length.notna().sum()),
                "note": "characters of the recorded answer text; a thinking trace is not counted"},
            "output_token_cap": "not recorded",
            "answers_with_zero_output_tokens_recorded_pct": round(100 * float((g.output_tokens.fillna(0) == 0).mean()), 1),
            "answers_stopping_at_the_largest_length": (
                f"{at_top} of {len(g)} answers stop at exactly {int(top)} output tokens, which suggests a cap"
                if at_top >= 10 else "no sign of a cap in the recorded lengths"),
            "answers_from": str(g.timestamp.min())[:10], "answers_to": str(g.timestamp.max())[:10],
        }
        for cond, label in ((cc.SHOWN, "names_shown"), (cc.HIDDEN, "names_hidden")):
            s = g[g.condition == cond]
            wording = s.system_prompt.map(lambda t: SYSTEM_BASELINE_PARAPHRASES.index(t) if t in SYSTEM_BASELINE_PARAPHRASES else -1)
            orders = s.presentation_order.astype(str)
            maps = s.letter_mapping.astype(str)
            both = orders + "|" + maps
            rec[label] = {
                "answers": int(len(s)),
                "paraphrase_index_recorded": {str(k): int(v) for k, v in sorted(s.paraphrase_index.value_counts().items())},
                "wording_received_read_from_system_prompt": {str(k): int(v) for k, v in sorted(wording.value_counts().items())},
                "distinct_display_orders_pct": round(100 * orders.nunique() / len(s), 1),
                "distinct_letter_assignments_pct": round(100 * maps.nunique() / len(s), 1),
                "distinct_order_and_letters_pct": round(100 * both.nunique() / len(s), 1),
                "distinct_within_a_table_pct": round(100 * float(s.assign(b=both).groupby("assortment_id").b.nunique().sum() / len(s)), 1),
                "note": "120 orders and 120 letter assignments are possible for five products",
            }
        out[m] = rec
    cc.write_result("model_settings", {"models": out}, "study1b-64-models-on-34-tables/code/07_model_settings.py", info)
    for m, r in out.items():
        print(f"{m:28s} T={r['temperature']} thinking={r['thinking_flag']} max output tokens={r['output_tokens']['max']:.0f} "
              f"({r['output_tokens']['answers_at_the_max']} answers) {r['answers_from']} to {r['answers_to']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
