"""Figures of the web appendix, drawn from numbers.json (no number is typed here).

Style and checks are the main-text figures': Fira Sans in three sizes and one ink, batlow's dark blue for the marks, a filled dot for a 95 per
cent interval that excludes zero and a hollow dot for one that includes it, thin intervals, a zero line wherever a gap
is plotted, no title inside a figure. Every figure is saved through save(), which refuses a figure wider than 6.5
inches, text that overlaps other text or lies off the canvas, and type below 6 points (the writing skill, FIGURES ARE
WRITING).

The conceptual model (model.pdf) is the main text's Figure 2, drawn as SVG by figures/diagrams.py; the box diagram on
the five layers that this file drew before is not drawn.
"""
import shutil
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent   # the figure and table code
PKG = CODE.parents[1]   # the package
REPO = JMR = PKG   # the names that the code gives the top folder
HERE = PKG / "exhibits" / "results" / "figures"
FIGURES = HERE
sys.path.insert(0, str(CODE))
import main_figures as mf  # noqa: E402  (sets the shared rcParams; read only)
import matplotlib.pyplot as plt  # noqa: E402

import tables  # noqa: E402

MARK, INK, GRID, ZERO, S, M = mf.MARK, mf.INK, mf.GRID, mf.ZERO, mf.S, mf.M


def save(fig, out):
    w, _ = fig.get_size_inches()
    assert w <= mf.MAX_WIDTH + 1e-9, f"{out.name} is {w} inches wide"
    problems = mf.collisions(fig) + mf.gray_faults(fig)
    if problems:
        raise AssertionError(f"{out.name}: " + "; ".join(problems))
    fig.savefig(out)
    plt.close(fig)
    low = mf.min_font_pt(out)
    assert low is None or low >= mf.MIN_PT - 0.05, f"{out.name}: text at {low} pt, below {mf.MIN_PT}"


def copy_main(name):
    def copy(out):
        src = FIGURES / name
        if not src.exists():
            raise FileNotFoundError(f"{src} is missing; run jmr-2026/figures/main_figures.py")
        shutil.copyfile(src, out)
    return copy


fig_model = copy_main("fig2_model.pdf")  # the conceptual model, Figure 1 of the main text
fig_pyramid = copy_main("fig1_pyramid.pdf")  # Keller's pyramid beside the machine version (Web Appendix)


def dot_interval(rows, pooled, xlabel, out, pooled_label, row=0.2):
    """rows: (label, estimate, low, high), already sorted top to bottom; row: inches per row."""
    n = len(rows)
    fig, ax = plt.subplots(figsize=(6.3, row * n + 0.9))
    ys = list(range(n))[::-1]
    for y, (label, est, lo, hi) in zip(ys, rows):
        mf.dot(ax, est, y, lo, hi, color=MARK, size=4.2)
    mf.plain_axes(ax, grid="x")
    ax.axvline(0, color=ZERO, linewidth=0.8, zorder=1.8)
    ax.axvline(pooled, color=INK, linewidth=0.8, linestyle=(0, (4, 3)), zorder=1.8)
    ax.text(pooled, n - 0.35, f" {pooled_label}", color=INK, fontsize=S, va="bottom", ha="left")
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows], fontsize=S if n > 20 else M)
    ax.set_ylim(-0.8, n + 0.3)
    ax.set_xlabel(xlabel)
    fig.tight_layout(pad=0.3)
    save(fig, out)


def fig_models(out):
    rows = []
    for m in tables._per_model():
        lo, hi = m["ci95_pp_tables_resampled"]
        rows.append((tables.model_label(m), m["gap_pp"], lo, hi))
    rows.sort(key=lambda r: -r[1])
    pooled = tables.S1["item2_brand_gap_by_model"]["pooled"]["gap_pp"]
    # 30 rows: a tighter row keeps the figure to two thirds of a page
    dot_interval(rows, pooled, "Effect of the fictitious name (percentage points)", out,
                 f"all models: {pooled:.2f}", row=0.15)


def fig_tables(out):
    rows = []
    for t in tables.S1["item2_brand_gap_by_model"]["per_table"]:
        lo, hi = t["ci95_pp_models_resampled"]
        rows.append((tables.table_name(t["table"]), t["gap_pp"], lo, hi))
    rows.sort(key=lambda r: -r[1])
    pooled = tables.S1["item2_brand_gap_by_model"]["pooled"]["gap_pp"]
    dot_interval(rows, pooled, "Effect of the fictitious name (percentage points)", out,
                 f"all tables: {pooled:.2f}", row=0.16)


def fig_price_tables(out):
    rp = tables.S1["item5_recommended_price"]["rec_price"]
    rows = []
    for t in rp["per_table"]:
        lo, hi = t["ci95_models_resampled"]
        rows.append((tables.table_name(t["table"]), t["difference"], lo, hi))
    rows.sort(key=lambda r: -r[1])
    pooled = rp["pooled"]["difference"]
    dot_interval(rows, pooled, "Price of the recommended product: with brand names minus without them (USD)", out,
                 f"all tables: USD {pooled:.2f}", row=0.16)


S2_NAMES = {"claude-fable-5-1": "Claude Fable 5.1", "claude-haiku-5-5": "Claude Haiku 5.5",
            "claude-opus-5-5": "Claude Opus 5.5", "claude-sonnet-5-5": "Claude Sonnet 5.5",
            "pooled": "All four models"}


def fig_s2_result(out):
    """Two panels (no information, information supplied); for each model a line from the share under the invented
    name (hollow) to the share with names hidden (filled), so the line's length is the penalty for the invented name.
    The shares come from tables.s2_shares, so that the figure and the text read the same numbers."""
    share, models = tables.s2_shares()
    rows = models + ["pooled"]
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 0.32 * len(rows) + 1.2), sharey=True)
    ys = list(range(len(rows)))[::-1]
    for ax, inf, title in zip(axes, ("0", "1"), ("No information", "Information supplied")):
        for y, m in zip(ys, rows):
            hid, inv = share[(m, "hidden", inf)], share[(m, "original", inf)]
            ax.plot([inv, hid], [y, y], color=MARK, linewidth=1.1, zorder=2)
            mf.dot(ax, hid, y, color=MARK, size=4.6, filled=True)
            mf.dot(ax, inv, y, color=MARK, size=4.6, filled=False)
        ax.set_title(title)
        ax.set_xlim(50, 101)
        mf.plain_axes(ax, grid="x")
        ax.axhline(0.5, color=GRID, linewidth=0.8)
        ax.set_xlabel("Answers that picked the best product (%)")
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels([S2_NAMES[m] for m in rows])
    h1 = axes[1].plot([], [], "o", color=MARK, markersize=4.6, label="Names hidden")[0]
    h2 = axes[1].plot([], [], "o", color=MARK, markerfacecolor="white", markeredgewidth=1.1, markersize=4.6,
                      label="Invented name on the best product")[0]
    fig.legend(handles=[h1, h2], loc="lower center", ncol=2, frameon=False, fontsize=S)
    fig.tight_layout(rect=(0, 0.08, 1, 1), pad=0.3)
    save(fig, out)


def fig_s3_result(out):
    """Qwen 2.5 7B after preference tuning: unprompted naming (share of 180 answers, Wilson interval) and the lift in
    table picks (points, stratified bootstrap interval) for each kind of page; no pages has no lift interval in the
    numbers file, so it is drawn as an estimate alone (a short bar, as in the main figures)."""
    import json as _json
    s3 = _json.loads((tables.PKG / "study3a-pages-about-new-brands/results/numbers.json").read_text(encoding="utf-8"))
    f12 = s3["f12"]
    arms = [("PROMO", "Promotional pages"), ("NEUTRAL-CLEAN", "Plain pages"), ("NEGATIVE", "Critical pages"),
            ("NONE", "No pages")]
    lift = {"PROMO": f12["lift_dpo_PROMO_vs_NEUTRAL-CLEAN"]["pooled"],
            "NEUTRAL-CLEAN": f12["lift_dpo_NEUTRAL-CLEAN_vs_NONE"]["pooled"],
            "NEGATIVE": f12["lift_dpo_NEGATIVE_vs_NONE"]["pooled"]}
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 0.34 * len(arms) + 1.2), sharey=True)
    ys = list(range(len(arms)))[::-1]
    for y, (a, _) in zip(ys, arms):
        nm = f12["naming_dpo"][a]
        lo, hi = nm["pooled_ci95_wilson"]
        mf.dot(axes[0], nm["pooled_pct"], y, lo, hi, color=MARK, size=4.6, filled=True)
        if a in lift:
            est, (lo, hi) = lift[a]["a_lift"], lift[a]["a_lift_ci95_stratified"]
            mf.dot(axes[1], est, y, lo, hi, color=MARK, size=4.6)
        else:
            mf.point_only(axes[1], lift["NEGATIVE"]["b_lift"], y)  # the no-page model is arm b of every comparison
    axes[0].set_title("Named the brand unprompted")
    axes[0].set_xlabel("Answers (%)")
    axes[1].set_title("Lift in table picks")
    axes[1].set_xlabel("Names shown minus names hidden (points)")
    axes[1].axvline(0, color=ZERO, linewidth=0.8, zorder=1.8)
    for ax in axes:
        mf.plain_axes(ax, grid="x")
    axes[0].set_xlim(-2, 60)  # room for the no-page model's dot at zero
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels([label for _, label in arms])
    fig.tight_layout(pad=0.3)
    save(fig, out)


FIGURES_BUILT = {"wa4_models.pdf": fig_models, "wa4_tables.pdf": fig_tables, "wa4_price_tables.pdf": fig_price_tables,
                 "s2_result.pdf": fig_s2_result, "s3_result.pdf": fig_s3_result, "model.pdf": fig_model,
                 "pyramid.pdf": fig_pyramid, "table.pdf": copy_main("fig_example_table.pdf"),
                 "settings.pdf": copy_main("fig_settings.pdf"),
                 "wa_settings.pdf": copy_main("wa_fig_settings.pdf"),
                 "dollar.pdf": copy_main("fig_dollar.pdf"),
                 "wa_measure_versions.pdf": copy_main("wa_fig_measure_versions.pdf"),
                 **{f"{n}.pdf": copy_main(f"{n}_{s}.pdf") for n, s in (
                     ("fig3a", "study1_shares"), ("fig3b", "study1_models"), ("fig4a", "study2_split"),
                     ("fig4b", "study2_price"), ("fig4c", "study2_audit"), ("fig5a", "study3_pages"),
                     ("fig5b", "study3_stages"), ("fig6", "study4"))}}


def build_all(folder):
    folder.mkdir(parents=True, exist_ok=True)
    for name, f in FIGURES_BUILT.items():
        f(folder / name)
    return sorted(FIGURES_BUILT)


if __name__ == "__main__":
    print(build_all(HERE / "build" / "figs"))
