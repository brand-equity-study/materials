"""The figure of Study 2b's versions of the measure (the Web Appendix): for each version, each brand's share premium
in that version against the main version's at the same price, the mean over the open models in the estimates
(study2b-how-much-a-familiar-brand-is-worth/results/measure/versions/numbers.json and pairs.csv, written by measure_versions.py; no number is typed
here). Style and save() are main_figures.py's (read only), so the figure has the Web Appendix's style and its check
that no two labels overlap.

    python exhibits/code/fig_measure_versions.py      # exhibits/results/figures/wa_fig_measure_versions.pdf and .png
"""
import csv
import json
import os
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent   # the figure and table code
PKG = CODE.parents[1]   # the package
REPO = JMR = PKG   # the names that the code gives the top folder
HERE = PKG / "exhibits" / "results" / "figures"   # where the figures are written
HERE.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(CODE))
import main_figures as MF  # noqa: E402  (read only: style, helpers and save)

NUM = PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/versions/numbers.json"
PAIRS = PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/versions/pairs.csv"


def main():
    d = json.loads(NUM.read_text(encoding="utf-8"))
    rows = list(csv.DictReader(open(PAIRS, encoding="utf-8")))
    vs = list(d["versions"])
    allv = [float(r[k]) for r in rows for k in ("main_pp", "version_pp")]
    lo, hi = min(allv), max(allv)
    pad = 0.06 * (hi - lo)
    lo, hi = lo - pad, hi + pad
    fig, axes = MF.plt.subplots(2, 3, figsize=(6.5, 4.6), sharex=True, sharey=True)
    for ax, v in zip(axes.flat, vs):
        e = d["versions"][v]
        pts = [r for r in rows if r["version"] == v]
        ax.plot([lo, hi], [lo, hi], color=MF.LINE, linewidth=0.8, zorder=1)
        ax.axhline(0, color=MF.GRID, linewidth=0.6, zorder=0)
        ax.axvline(0, color=MF.GRID, linewidth=0.6, zorder=0)
        ax.plot([float(r["main_pp"]) for r in pts], [float(r["version_pp"]) for r in pts], "o", markersize=3.2,
                markeredgewidth=0.8, color=MF.MARK, markerfacecolor="white", zorder=3)
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        ax.set_title(e["label"], fontsize=MF.S, pad=4)
        ci = e["mean_difference_ci95"]
        rho = f"{e['spearman_with_main']:.2f}".replace("0.", ".", 1)  # the paper's form of a correlation
        ax.text(0.04, 0.96, f"Spearman {rho}\n"
                            f"difference {e['mean_difference_pp']:+.1f} (95% CI {ci[0]:+.1f} to {ci[1]:+.1f})".replace("-", "−"),
                transform=ax.transAxes, ha="left", va="top", fontsize=MF.S, color=MF.INK)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(axis="both", labelsize=MF.S)
    for ax in axes[1]:
        ax.set_xlabel("Main version (points)", fontsize=MF.S)
    for ax in axes[:, 0]:
        ax.set_ylabel("This version (points)", fontsize=MF.S)
    fig.tight_layout(h_pad=1.6, w_pad=1.2)
    MF.save(fig, "wa_fig_measure_versions")
    print("wrote", HERE / "wa_fig_measure_versions.pdf", "and .png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
