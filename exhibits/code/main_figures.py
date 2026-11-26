"""The main-text figures of the JMR paper, drawn from the repository's results files (no number is typed here).

    CAPTIONS.md and FIGURES.pdf are
written from those returns, so a caption's numbers are the figure's numbers.

Study 2, why, and which part of the brand; Study 3, where it comes from; Study 4, people.
"""
import sys
import paper_names  # noqa: E402  (the package's helper: results files and their keys)

sys.dont_write_bytecode = True

import csv  # noqa: E402
import json  # noqa: E402
import textwrap  # noqa: E402
from pathlib import Path  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402

CODE = Path(__file__).resolve().parent   # the figure and table code
PKG = CODE.parents[1]   # the package
REPO = JMR = PKG   # the names that the code gives the top folder
HERE = PKG / "exhibits" / "results" / "figures"   # where the figures are written
HERE.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(CODE))
import tables  # noqa: E402  (read only: model names and Study 1's shares, so that the text and the figures agree)

import os  # noqa: E402
FONT_DIR = Path(os.environ.get("FIRA_DIR", PKG / "exhibits" / "fonts"))   # Fira Sans
for _f in ("FiraSans-Regular.otf", "FiraSans-SemiBold.otf", "FiraSans-Italic.otf"):
    font_manager.fontManager.addfont(str(FONT_DIR / _f))
font_manager.findfont(font_manager.FontProperties(family="Fira Sans"), fallback_to_default=False)
# Three type sizes only (the nature-figure schematic rule), all text in one dark ink; nothing below 6 points.
S, M, L = 6.8, 7.6, 8.4
plt.rcParams.update({
    "font.family": "Fira Sans", "font.size": M, "axes.edgecolor": "#A7B0B8", "axes.linewidth": 0.6,
    "xtick.color": "#1F2A36", "ytick.color": "#1F2A36", "xtick.major.width": 0.6, "xtick.major.size": 2.5,
    "xtick.major.pad": 2.5, "ytick.major.size": 0, "xtick.labelsize": S, "ytick.labelsize": M, "axes.labelsize": M,
    "axes.labelcolor": "#1F2A36", "axes.titlesize": L, "axes.titleweight": "semibold", "axes.titlelocation": "left",
    "axes.titlepad": 7, "axes.titlecolor": "#1F2A36", "legend.fontsize": S, "text.color": "#1F2A36",
    "pdf.fonttype": 42, "ps.fonttype": 42, "axes.unicode_minus": True,
})
# Colour: Fabio Crameri's batlow (Scientific colour maps 8.0, the cmcrameri package), perceptually uniform, readable
# with colour-vision deficiency and in greyscale. MARK is batlow at 0.15 (dark blue), MARK2 at 0.67 (ochre): their
# lightness differs enough to read apart in greyscale, and filled against hollow marks carry the same distinction a
# second time. The dataviz validator passes the pair on colour-vision separation (protan dE 34.7) and normal vision
# (dE 40.7); its UI lightness band and chroma floor fail by design on batlow's muted blues, and the ochre's contrast
# warning is met by direct labels, legends and the filled-hollow code.
MARK = "#134961"
MARK2 = "#d29343"
INK = "#1F2A36"
GRID = "#E6E9EC"
ZERO = "#56616B"
MUTED = INK          # one dark ink for all text (nature-figure rule); greys are used for lines only
FAINT = "#9AA4AE"
LINE = "#C3CAD1"
LIGHT = "#F1F4F6"
BAND = "#EEF1F3"
MAX_WIDTH = 6.5
MIN_PT = 6.0

# the results files, by path
F_DOM2 = PKG / "study1a-tables-with-one-optimal-product/results/strictly-better-tables/numbers.json"
F_DOM2_CELLS = PKG / "study1a-tables-with-one-optimal-product/results/strictly-better-tables/cells.csv"
F_SPLIT = F_EQ1 = None   # read only by figures that the paper does not show
F_CORPUS = PKG / "study1b-64-models-on-34-tables/results/numbers.json"
F_RERUN = PKG / "study1b-64-models-on-34-tables/results/rerun.json"
F_OPEN = PKG / "study1a-tables-with-one-optimal-product/results/open_models.json"
F_POOLED = PKG / "study1b-64-models-on-34-tables/results/pooled/numbers.json"  # Study 1b over every model


def corpus_names():
    """Model key -> printed name, from model_names.json beside this file (the names that the paper prints)."""
    return json.loads((CODE / "model_names.json").read_text(encoding="utf-8"))
F_ALL2 = PKG / "study2a-experience-attributes-stated-for-every-product/results/all-models/numbers.json"  # Study 2 over every model (pool_all.py)
F_ALL2_PER = PKG / "study2a-experience-attributes-stated-for-every-product/results/all-models/per_model.csv"
F_ALL2_EQ1 = PKG / "study2b-how-much-a-familiar-brand-is-worth/results/all-models-eq1/numbers.json"
F_ALL2_EQ1_PER = PKG / "study2b-how-much-a-familiar-brand-is-worth/results/all-models-eq1/per_model.csv"
F_AUDIT = PKG / "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/numbers-all.json"  # Study 2d over every model that answered
F_S3 = PKG / "study3a-pages-about-new-brands/results/numbers.json"
F_STAGES = PKG / "study3b-brand-knowledge-and-training-text-in-released-models/results/training-stages/numbers.json"
F_CONSUMER = PKG / "study4-peoples-choices-after-a-recommendation/results/numbers.json"

# printed names (labels, not numbers)
CLAUDE = {"claude-fable-5-1": "Claude Fable 5.1", "claude-fable-5-2": "Claude Fable 5.2",
          "claude-haiku-5-5": "Claude Haiku 5.5", "claude-opus-5-5": "Claude Opus 5.5",
          "claude-sonnet-5-5": "Claude Sonnet 5.5", "gpt-6-astra": "GPT-6 Astra", "gpt-6.1-sol": "GPT-6.1 Sol",
          "gpt-6.2-astra": "GPT-6.2 Astra", "gpt-6.2-sol": "GPT-6.2 Sol", "pooled": "All four models"}
OPEN = {"gemma31b": "Gemma 4 31B", "gemma4-26b": "Gemma 4 26B", "granite41-30b": "Granite 4.1 30B",
        "llama8b": "Llama 3.1 8B", "marin8b": "Marin 8B", "ministral3-14b": "Ministral 3 14B",
        "olmo31-32b": "OLMo 3.1 32B", "phi4": "Phi-4", "qwen3-30b": "Qwen3 30B", "qwen32b": "Qwen 2.5 32B"}


def load(path):
    import paper_names   # the code's names of the keys that the package names in plain words
    return paper_names.read(path)


def rel(path):
    return Path(path).resolve().relative_to(REPO).as_posix()


def f1(x):
    """One decimal, with a true minus sign for the figures; -0.0 prints as 0.0."""
    s = f"{x:.1f}"
    return "0.0" if s == "-0.0" else s.replace("-", "\u2212")


def t1(x):
    """One decimal for the captions (plain hyphen-minus; the typesetting sets the minus)."""
    s = f"{x:.1f}"
    return "0.0" if s == "-0.0" else s


def ci_text(lo, hi):
    return f"{t1(lo)} to {t1(hi)}"


def plain_axes(ax, grid="x"):
    ax.grid(axis=grid, color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", pad=4)


def dot(ax, x, y, lo=None, hi=None, color=MARK, size=4.8, filled=None, marker="o", zorder=3, horizontal=True):
    """A dot at (x, y) with its 95% interval as a thin line (along x when horizontal, along y otherwise); filled when
    the interval excludes zero unless told otherwise."""
    if lo is not None and hi is not None:
        if horizontal:
            ax.plot([lo, hi], [y, y], color=color, linewidth=1.1, solid_capstyle="butt", zorder=zorder - 1)
        else:
            ax.plot([x, x], [lo, hi], color=color, linewidth=1.1, solid_capstyle="butt", zorder=zorder - 1)
        if filled is None:
            filled = lo > 0 or hi < 0
    ax.plot(x, y, marker, markersize=size, markeredgewidth=1.1, color=color,
            markerfacecolor=color if filled else "white", zorder=zorder)


def point_only(ax, x, y, color=MARK):
    """An estimate for which the results file holds no interval: a short vertical bar, never a filled or hollow dot."""
    ax.plot(x, y, marker="|", markersize=7.5, markeredgewidth=1.5, color=color, zorder=3)


def collisions(fig):
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W, H = fig.canvas.get_width_height()
    boxes = []
    # tick labels count only when their tick is drawn (inside the axis limits); matplotlib keeps the others
    tick_labels, drawn = set(), set()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            for tk in axis.get_major_ticks() + axis.get_minor_ticks():
                tick_labels.update((id(tk.label1), id(tk.label2)))
            if ax.axison:
                for tk in axis._update_ticks():
                    drawn.update((id(tk.label1), id(tk.label2)))
    for t in fig.findobj(matplotlib.text.Text):
        if not t.get_visible() or not t.get_text().strip():
            continue
        if id(t) in tick_labels and id(t) not in drawn:
            continue
        ax = t.axes
        if ax is not None and (not ax.get_visible() or (not ax.axison and id(t) in tick_labels)):
            continue
        bb = t.get_window_extent(r)
        if bb.width <= 0 or bb.height <= 0:
            continue
        boxes.append((t.get_text().replace("\n", " "), bb))
    out = [f"outside the canvas: {s!r}" for s, b in boxes
           if b.x0 < -0.5 or b.y0 < -0.5 or b.x1 > W + 0.5 or b.y1 > H + 0.5]
    gap = 1.5 * fig.dpi / 72  # texts side by side keep 1.5 points apart (nature-figure's tolerance)
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            (s1, a), (s2, b) = boxes[i], boxes[j]
            if a.x0 < b.x1 + gap and b.x0 < a.x1 + gap and a.y0 < b.y1 - 0.5 and b.y0 < a.y1 - 0.5:
                out.append(f"overlap or closer than 1.5 pt: {s1!r} and {s2!r}")
    return out


def min_font_pt(pdf_path):
    import pymupdf as fitz
    sizes = [s["size"] for page in fitz.open(pdf_path) for b in page.get_text("dict")["blocks"]
             for ln in b.get("lines", []) for s in ln["spans"] if s["text"].strip()]
    return min(sizes) if sizes else None


def replace_when_free(tmp, dest, tries=20):
    """A viewer that holds the old file open makes Windows refuse the write; wait for it, up to about 10 seconds."""
    import os
    import time
    for k in range(tries):
        try:
            os.replace(tmp, dest)
            return
        except OSError:
            if k == tries - 1:
                raise
            time.sleep(0.5)


GRAY_GAP = 0.15   # the smallest difference in gray (0 black, 1 white) between two series that share a mark's shape


def _luma(c):
    """A colour's gray as a printer gives it (ITU-R 601: 0.299 R + 0.587 G + 0.114 B), 0 black to 1 white."""
    r, g, b = matplotlib.colors.to_rgb(c)
    return 0.299 * r + 0.587 * g + 0.114 * b


def gray_faults(fig):
    """The AMA prints figures in gray unless the authors pay for colour, so every series must stay distinguishable
    without colour. A series is told apart by its mark's shape, its line style or its gray; so within one panel, two
    marks of the same shape and line style whose colours differ must differ in gray by at least GRAY_GAP. A mark's
    colour is its fill, or its edge when it is hollow (white or no fill). Returns the problems found."""
    out = []
    for ax in fig.axes:
        groups = {}
        for ln in ax.get_lines():
            m = ln.get_marker()
            if not ln.get_visible() or m in (None, "", "None", " ", "|", "_"):
                continue
            face = ln.get_markerfacecolor()
            hollow = face in ("none", "None") or matplotlib.colors.to_hex(face) == "#ffffff"
            col = matplotlib.colors.to_hex(ln.get_markeredgecolor() if hollow else face)
            groups.setdefault((str(m), ln.get_linestyle()), set()).add(col)
        for (m, ls), cols in groups.items():
            cols = sorted(cols)
            for i in range(len(cols)):
                for j in range(i + 1, len(cols)):
                    if abs(_luma(cols[i]) - _luma(cols[j])) < GRAY_GAP:
                        out.append(f"marks '{m}' in {cols[i]} and {cols[j]} differ by "
                                   f"{abs(_luma(cols[i]) - _luma(cols[j])):.2f} in gray (at least {GRAY_GAP})")
    return sorted(set(out))


def save(fig, name):
    w, _ = fig.get_size_inches()
    assert w <= MAX_WIDTH + 1e-9, f"{name} is {w} inches wide"
    problems = collisions(fig) + gray_faults(fig)
    if problems:
        raise AssertionError(f"{name}: " + "; ".join(problems))
    # no creation date in the PDF, so that a rebuild with the same numbers writes the same bytes
    for ext, kw in (("pdf", {"metadata": {"CreationDate": None}}), ("png", {"dpi": 200})):
        tmp = HERE / f"{name}.tmp.{ext}"
        fig.savefig(tmp, **kw)
        replace_when_free(tmp, HERE / f"{name}.{ext}")
    plt.close(fig)
    low = min_font_pt(HERE / f"{name}.pdf")
    assert low is None or low >= MIN_PT - 0.05, f"{name}: text at {low} pt, below {MIN_PT}"


def units(value, lo, hi, what):
    """Until 22 November 2026 each check
    compared the number with a typed copy of it, which failed at every redraw after new results (PLAN.md)."""
    if value is None or not lo <= value <= hi:
        raise AssertionError(f"{what}: read {value}, outside the range {lo} to {hi} that its units allow")


# Figures 1 and 2 (the pyramid and the conceptual model) are drawn as SVG and printed by Chrome: diagrams.py
from diagrams import fig_example_table_entry, fig_model, fig_pyramid  # noqa: E402


# ---------------------------------------------------------------------------------------------------------------
# Figure 3a: Study 1, the share that picked the best product, names hidden and invented, by model
# ---------------------------------------------------------------------------------------------------------------

def fig_study1_shares():
    import csv
    pooled = load(F_ALL2)["2a"]["pooled"]
    g0, g1 = pooled["gap_none"], pooled["gap_supplied"]
    units(100 * g0["estimate"], 0.5, 40, "all-models: Study 2a gap with no information (points)")
    units(100 * g1["estimate"], -40, 40, "all-models: Study 2a gap with the information (points)")
    per = {}
    with open(F_ALL2_PER, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["study"] == "2a" and r["estimate_name"] in ("gap with no information", "gap with the information"):
                key = "0" if r["estimate_name"] == "gap with no information" else "1"
                per.setdefault(r["model"], {})[key] = tuple(100 * float(r[c]) for c in
                                                            ("estimate", "ci95_low", "ci95_high"))
    names = corpus_names()
    names.setdefault("claude-fable-5-2", "Claude Fable 5.2")
    models = sorted(per, key=lambda m: -per[m]["0"][0])
    rows = [("pooled", "All models", {"0": (100 * g0["estimate"], 100 * g0["ci95"][0], 100 * g0["ci95"][1]),
                                      "1": (100 * g1["estimate"], 100 * g1["ci95"][0], 100 * g1["ci95"][1])})]
    rows += [("row", names.get(m, m), per[m]) for m in models]
    n = len(rows)
    lo = min(r[2][k][1] for r in rows for k in "01")
    hi = max(r[2][k][2] for r in rows for k in "01")
    xlim = (5 * (lo // 5) - 2, 5 * (hi // 5 + 1) + 1)
    fig_h = 0.112 * n + 1.05
    fig = plt.figure(figsize=(6.5, fig_h))
    bottom, top = 0.62 / fig_h, 1 - 0.30 / fig_h
    axes = [fig.add_axes([1.75 / 6.5, bottom, 2.2 / 6.5, top - bottom]),
            fig.add_axes([4.15 / 6.5, bottom, 2.2 / 6.5, top - bottom])]
    sources = []
    for ax, key, title in zip(axes, "01", ("Experience attributes not stated", "Experience attributes stated")):
        ys = []
        for i, r in enumerate(rows):
            y = n - 1 - i
            ys.append(y)
            est, l, h = r[2][key]
            if r[0] == "pooled":
                dot(ax, est, y, l, h, size=5.0, marker="D")
            else:
                dot(ax, est, y, l, h, size=4.2)
            sources.append((f"{f1(est)} ({f1(l)} to {f1(h)}), {r[1]}, information {key}",
                            rel(F_ALL2_PER) if r[0] == "row" else rel(F_ALL2),
                            "per_model.csv 2a gap rows (x 100)" if r[0] == "row" else
                            "2a.pooled.gap_none / gap_supplied (x 100)"))
        ax.set_yticks(ys)
        if key == "0":
            ax.set_yticklabels([r[1] for r in rows], fontsize=S)
            for lab, r in zip(ax.get_yticklabels(), rows):
                lab.set_fontweight("semibold" if r[0] == "pooled" else "normal")
        else:
            ax.set_yticklabels([])
        ax.set_ylim(-0.8, n - 0.2)
        ax.set_xlim(*xlim)
        ax.axvline(0, color=ZERO, linewidth=0.8, zorder=1.8)
        ax.set_title(title, fontsize=M)
        plain_axes(ax)
    fig.text(4.05 / 6.5, 0.06 / fig_h, "Effect of the fictitious name (points)", ha="center", va="bottom",
             fontsize=M)
    save(fig, "fig3a_study1_shares")
    narrowed = sum(1 for m in models if per[m]["1"][0] < per[m]["0"][0])
    return {
        "name": "fig3a_study1_shares", "number": "Figure 2",
        "title": "A Fictitious Name Lowers How Often Models Recommend the Optimal Product, Less So When Every "
                 "Product's Experience Attributes Are Stated",
        "body": (f"Each row is one of the {len(models)} models that answered the tables of Study 1a, each with one "
                 "optimal product. The dot is the model's effect of the fictitious name: the share of responses "
                 "that chose the optimal product without brand names minus the share with the fictitious name on "
                 "it, in percentage points, with its 95% CI (tables resampled); a filled dot marks a CI that "
                 "excludes zero. In the left panel, the listings are as they were, and in the right panel, the same "
                 "listings have three experience attributes stated for every product (a warranty, a failure rate "
                 "and the time on the market, with the same values for every product), as in Study 2a. The top row "
                 f"is the estimate over all models (tables and models resampled): {t1(100 * g0['estimate'])} points "
                 f"without the experience attributes stated ({ci_text(100 * g0['ci95'][0], 100 * g0['ci95'][1])}) "
                 f"and {t1(100 * g1['estimate'])} with them ({ci_text(100 * g1['ci95'][0], 100 * g1['ci95'][1])}). "
                 f"The models are sorted by their effect without the experience attributes stated; {narrowed} of "
                 f"the {len(models)} had a smaller effect with them."),
        "sources": sources,
        "waits": ["More open models join when job 12683's export is fetched and pool_all.py is run again."],
        "note": "",
    }


# ---------------------------------------------------------------------------------------------------------------
# Figure 3b: Study 1, how far it holds: the gap in the 30 corpus models, the newer models and the open models
# ---------------------------------------------------------------------------------------------------------------

def fig_study1_models():
    pf = load(F_POOLED)
    pooled = pf["pooled"]
    names = corpus_names()
    rows, dropped, seen = [], [], set()
    for m in sorted(pf["per_model"], key=lambda m: -m["gap_pp"]):
        label = names.get(m["model"], m["model"])
        if label in seen:
            dropped.append(m["model"])
            continue
        seen.add(label)
        rows.append(("row", label, m["gap_pp"], m["ci95_low_pp"], m["ci95_high_pp"]))
    one = [("pooled", "All models", pooled["gap_pp"], *pooled["ci95_pp"])] + rows
    n = len(one)
    lo_all = min(r[3] for r in one)
    hi_all = max(r[4] for r in one)
    xlim = (5 * (lo_all // 5) - 2, 5 * (hi_all // 5 + 1) + 1)

    fig_h = 0.112 * n + 0.95
    fig = plt.figure(figsize=(6.5, fig_h))
    bottom, top = 0.62 / fig_h, 1 - 0.08 / fig_h
    axes = [fig.add_axes([1.9 / 6.5, bottom, 3.0 / 6.5, top - bottom])]
    for ax, rows in zip(axes, (one,)):
        ys, labels, weights = [], [], []
        for i, r in enumerate(rows):
            y = n - 1 - i
            if r[0] == "space":
                continue
            ys.append(y)
            labels.append(r[1])
            weights.append("semibold" if r[0] in ("header", "pooled") else "normal")
            if r[0] == "row":
                dot(ax, r[2], y, r[3], r[4], size=4.2)
            elif r[0] == "pooled":
                dot(ax, r[2], y, r[3], r[4], size=5.0, marker="D")
            elif r[0] == "point":
                point_only(ax, r[2], y)
        ax.set_yticks(ys)
        ax.set_yticklabels(labels, fontsize=S)
        for lab, wgt in zip(ax.get_yticklabels(), weights):
            lab.set_fontweight(wgt)
        ax.set_ylim(-0.8, n - 0.2)
        ax.set_xlim(*xlim)
        ax.axvline(0, color=ZERO, linewidth=0.8, zorder=1.8)
        plain_axes(ax)
    fig.text(0.5, 0.06 / fig_h, "Responses that did not choose the top-ranked product, with minus without brand "
             "names (points)",
             ha="center", va="bottom", fontsize=M)
    handles = [Line2D([], [], marker="D", color=MARK, linestyle="none", markersize=5.0,
                      label="All models, 95% CI"),
               Line2D([], [], marker="o", color=MARK, linestyle="none", markersize=4.2,
                      label="95% CI excludes zero"),
               Line2D([], [], marker="o", color=MARK, markerfacecolor="white", markeredgewidth=1.1, linestyle="none",
                      markersize=4.2, label="95% CI includes zero")]
    leg = fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(5.05 / 6.5, bottom + 0.004), frameon=True,
                     handletextpad=0.5, borderaxespad=0, labelspacing=0.7)
    leg.get_frame().set_facecolor("white")
    leg.get_frame().set_edgecolor("none")
    save(fig, "fig3b_study1_models")

    models = rows
    positive = sum(1 for r in models if r[2] > 0)
    p_rel = rel(F_POOLED)
    sources = [("each model's gap and 95% CI", p_rel, "per_model[].gap_pp, .ci95_low_pp and .ci95_high_pp"),
               (f"All models: {t1(pooled['gap_pp'])} ({ci_text(*pooled['ci95_pp'])})", p_rel,
                "pooled.gap_pp and .ci95_pp")]
    return {
        "name": "fig3b_study1_models", "number": "Figure 3",
        # the manuscript's title (03-study1.md) and the paper's terms: Study 1b's product is the top-ranked product,
        # since in most of its tables no product beats the others on every attribute
        "title": "Models Recommend the Top-Ranked Product Less Often Under a Fictitious Name",
        "body": ("Each row is one model's effect of the fictitious name: the share of responses that did not choose "
                 "the top-ranked product (the product with a fictitious name that has the highest score under "
                 "the attribute weights that we set) with brand names, minus the share without brand names, in "
                 f"percentage points, with its 95% CI (tables resampled). The top row is the estimate over all "
                 f"{len(models)} models (models and tables resampled). The models are sorted by their effect, which "
                 f"was positive in {positive} of the {len(models)}. The models are listed in Web Appendix D."),
        "sources": sources,
        "waits": [],
        "note": (f"Rows that repeat a set of weights already drawn, left out: {dropped}. In the primary panel, "
                 "each set of weights is counted once (63 models); the 65-model version is a Web Appendix check."),
    }


# ---------------------------------------------------------------------------------------------------------------
# Figure 4a: Study 2, the gap left by each piece of information alone
# ---------------------------------------------------------------------------------------------------------------

def forest(ax, rows, xlabel, value_col=True):
    """rows: (label, est, lo, hi) top to bottom; the estimate and interval printed in a column at the right."""
    n = len(rows)
    ys = list(range(n))[::-1]
    for y, (_, est, lo, hi) in zip(ys, rows):
        dot(ax, est, y, lo, hi)
    ax.axvline(0, color=ZERO, linewidth=0.9, zorder=1.8)
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows])
    ax.set_ylim(-0.7, n - 0.3)
    plain_axes(ax)
    ax.set_xlabel(xlabel)
    if value_col:
        tr = blended_transform_factory(ax.transAxes, ax.transData)
        ax.text(1.04, n - 0.3, "Difference (95% CI)", transform=tr, fontsize=S, fontweight="semibold", color=INK,
                ha="left", va="bottom")
        for y, (_, est, lo, hi) in zip(ys, rows):
            ax.text(1.04, y, f"{f1(est)} ({f1(lo)} to {f1(hi)})", transform=tr, fontsize=S, color=INK,
                    ha="left", va="center")


def fig_study2_split():
    whole = load(F_ALL2)["2b"]
    d = whole["pooled"]
    gap, con = d["gap"], d["contrasts"]
    labels = [("0", "No information"), ("warranty", "Warranty only"), ("failure", "Failure rate only"),
              ("market", "Time on the market only"), ("lab", "Independent testing only"),
              ("returns", "Free returns only"), ("1", "All five")]
    rows = [(lab, 100 * gap[k]["estimate"], 100 * gap[k]["ci95"][0], 100 * gap[k]["ci95"][1]) for k, lab in labels]
    units(rows[0][1], 0.5, 40, "all-models 2b: no information (points; every row has the same units)")
    fig, ax = plt.subplots(figsize=(6.3, 2.5))
    forest(ax, rows, "Responses that chose the optimal product, without minus with brand names (points)")
    for y in (5.5, 0.5):
        ax.axhline(y, color=LINE, linewidth=0.6, zorder=1)
    fig.subplots_adjust(left=0.25, right=0.76, top=0.92, bottom=0.2)
    save(fig, "fig4a_study2_split")
    s_rel = rel(F_ALL2)
    lab_none = con["lab alone minus none"]
    lab_all = con["lab alone minus all five"]

    def holm(p):
        return "below .001" if p < 0.001 else f"{p:.3f}".lstrip("0")
    leave = [(k, con[f"{k} alone minus all five"]["p_holm"]) for k in ("warranty", "market", "returns")]  # sources
    sources = [(f"{f1(r[1])} ({f1(r[2])} to {f1(r[3])}), {r[0]}", s_rel, f"2b.pooled.gap.{k}.estimate and .ci95 (x 100)")
               for (k, _), r in zip(labels, rows)]
    sources += [(f"lab alone minus none {t1(100 * lab_none['estimate'])}, Holm P {holm(lab_none['p_holm'])}", s_rel,
                 "2b.pooled.contrasts['lab alone minus none']"),
                (f"lab alone minus all five, Holm P {holm(lab_all['p_holm'])}", s_rel,
                 "2b.pooled.contrasts['lab alone minus all five'].p_holm")]
    sources += [(f"{k} alone minus all five, Holm P {holm(p)}", s_rel, f"2b.pooled.contrasts['{k} alone minus all five']"
                 ".p_holm") for k, p in leave]
    return {
        "name": "fig4a_study2_split", "number": "Not placed (each piece of information alone)",
        "title": "No Single Piece of Information Reliably Changes the Effect of the Fictitious Name",
        "body": (f"The {len(whole['models'])} models that answered the test of each piece of information alone, on the tables of Study 1a. Each row is the effect "
                 "of the fictitious name (the share of responses that chose the optimal product without brand names "
                 "minus the share with the fictitious name on it) when the listing stated no experience attributes, one "
                 "of the five pieces alone for every product, or all five, with its 95% CI (tables and models "
                 "resampled). No piece alone changed the effect reliably after Holm correction across the ten "
                 "planned contrasts. The statement about independent testing changed it the most, from "
                 f"{t1(rows[0][1])} to {t1(rows[4][1])} points (Holm P {holm(lab_none['p_holm'])} against no "
                 f"information; Holm P {holm(lab_all['p_holm'])} against all five)."),
        "sources": sources,
        "waits": [],
        "note": "",
    }


# ---------------------------------------------------------------------------------------------------------------
# Figure 4b: Study 2, the equalization price
# ---------------------------------------------------------------------------------------------------------------

CUTS = [0, 1, 2, 3, 5, 10, 15, 30, 50]


def cut_pos(c):
    """The rungs are drawn evenly spaced and the axis is linear between rungs, so that the crossing, which
    analyze_eq.py interpolates linearly in the cut between two rungs, falls where the drawn segment meets zero."""
    for i in range(1, len(CUTS)):
        if c <= CUTS[i]:
            return i - 1 + (c - CUTS[i - 1]) / (CUTS[i] - CUTS[i - 1])
    raise ValueError(c)


def fig_study2_price():
    import csv
    whole = load(F_ALL2_EQ1)["2c"]
    e = whole["pooled"]
    pooled = e["pooled"]
    assert pooled["option_a_without_a_model"]["netted_by_the_parity_control"] == 0
    b = pooled["option_a_without_a_model"]["price"]
    units(b["original"]["crossing_value"], 0.3, 60, "all-models eq1 pooled crossing (percent of the price)")
    e_rel = rel(F_ALL2_EQ1)
    sources = []
    fig = plt.figure(figsize=(6.5, 5.0))
    ax = fig.add_axes([0.10, 0.42, 0.36, 0.50])
    xs = list(range(len(CUTS)))
    for arm, filled in (("hidden", True), ("original", False)):
        br, bc = b[arm]["by_rung"], b[arm]["by_rung_ci95"]
        ys = [100 * br[f"cut{c}"] for c in CUTS]
        col = MARK if filled else MARK2
        # the line without brand names is set a little to the left, so that where the two intervals overlap both stay
        # visible; the line with brand names keeps its place, because the crossing is read on it
        xd = [x - 0.14 for x in xs] if filled else list(xs)
        ax.plot(xd, ys, color=col, linewidth=1.0, zorder=2)
        for x, c, y in zip(xd, CUTS, ys):
            lo, hi = (100 * v for v in bc[f"cut{c}"])
            ax.plot([x, x], [lo, hi], color=col, linewidth=0.9, alpha=0.85, zorder=2)
            ax.plot(x, y, "o", markersize=4.2, markeredgewidth=1.2, color=col,
                    markerfacecolor=col if filled else "white", zorder=3)
        sources.append((f"{'without brand names' if filled else 'with brand names'}, all models, each discount and "
                        "interval", e_rel, f"2c.pooled.pooled.option_a_without_a_model.price.{arm}.by_rung and "
                        ".by_rung_ci95 (x 100)"))
    o = b["original"]
    c = o["crossing_value"]
    i = next(i for i in range(1, len(CUTS)) if CUTS[i] >= c)
    y0, y1 = (100 * o["by_rung"][f"cut{CUTS[k]}"] for k in (i - 1, i))
    at = y0 + (y1 - y0) * (cut_pos(c) - (i - 1))
    assert abs(at) < 0.05, f"the line is at {at} points at the crossing"
    lo, hi = o["crossing_ci95"]
    hi_pos = cut_pos(30) if isinstance(hi, str) else cut_pos(hi)
    ax.axhline(0, color=ZERO, linewidth=0.9, zorder=1.8)
    ax.plot([cut_pos(lo), hi_pos], [0, 0], color=INK, linewidth=2.4, solid_capstyle="butt", zorder=4)
    if isinstance(hi, str):
        ax.plot(hi_pos, 0, marker=">", markersize=4.5, color=INK, zorder=4)
    ax.plot(cut_pos(c), 0, marker="v", markersize=6, color=INK, zorder=5, clip_on=False, markeredgecolor="white",
            markeredgewidth=0.6)
    ax.text(cut_pos(c) + 0.3, -42, f"equal at a\n{f1(c)}% discount", fontsize=S, color=INK, ha="left", va="top")
    hi_text = "more than 30" if isinstance(hi, str) else t1(hi)
    sources.append((f"crossing {f1(c)}% ({t1(lo)} to {hi_text}), all models", e_rel,
                    "2c.pooled.pooled.option_a_without_a_model.price.original.crossing_value and .crossing_ci95"))
    ax.set_title("All models", fontsize=M, pad=4)
    ax.set_ylim(-60, 60)
    ax.set_yticks([-60, -30, 0, 30, 60])
    ax.grid(axis="y", color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="both", labelsize=S)
    ax.tick_params(axis="y", length=0, pad=3)
    ax.set_xticks(xs)
    ax.set_xticklabels([str(cc) for cc in CUTS])
    ax.set_xlabel("Price discount (%)", fontsize=M)
    ax.set_ylabel("Fictitious product's share minus\nthe familiar product's share (points)", fontsize=M)
    key = fig.add_axes([0.06, 0.02, 0.42, 0.26])
    key.axis("off")
    handles = [Line2D([], [], marker="o", color=MARK, markersize=4.6, linewidth=1.0, label="Without brand names"),
               Line2D([], [], marker="o", color=MARK2, markerfacecolor="white", markeredgewidth=1.2, markersize=4.6,
                      linewidth=1.0, label="With brand names"),
               Line2D([], [], marker="v", color=INK, markersize=6, linestyle="none",
                      label="Discount at which the two shares are equal"),
               Line2D([], [], color=INK, linewidth=2.4, label="Its 95% interval")]
    key.legend(handles=handles, loc="center left", frameon=False, fontsize=S, labelspacing=0.9, handlelength=2.2)
    # (b) each model at the same price, with brand names
    per = []
    with open(F_ALL2_EQ1_PER, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["study"] == "2c" and r["estimate_name"] == "invented minus familiar twin, names shown":
                per.append((r["model"], *(100 * float(r[k]) for k in ("estimate", "ci95_low", "ci95_high"))))
    names = corpus_names()
    names.setdefault("claude-fable-5-2", "Claude Fable 5.2")
    per.sort(key=lambda r: r[1])
    pt = pooled["option_a_parity_tests"]["invented minus familiar twin, names shown"]
    rows = [("All models", 100 * pt["estimate"], 100 * pt["ci95"][0], 100 * pt["ci95"][1], True)]
    rows += [(names.get(m, m), est, l, h, False) for m, est, l, h in per]
    n = len(rows)
    bx = fig.add_axes([0.70, 0.08, 0.28, 0.86])
    for k, (label, est, l, h, top) in enumerate(rows):
        y = n - 1 - k
        dot(bx, est, y, l, h, size=5.0 if top else 4.0, marker="D" if top else "o")
    bx.set_yticks(list(range(n))[::-1])
    bx.set_yticklabels([r[0] for r in rows], fontsize=S)
    for lab, r in zip(bx.get_yticklabels(), rows):
        lab.set_fontweight("semibold" if r[4] else "normal")
    bx.set_ylim(-0.8, n - 0.2)
    bx.set_xlim(-100, 20)
    bx.axvline(0, color=ZERO, linewidth=0.8, zorder=1.8)
    bx.set_title("Each model, same price", fontsize=M, pad=4)
    bx.set_xlabel("Difference with brand names (points)", fontsize=M)
    plain_axes(bx)
    sources.append(("each model's difference at the same price with brand names, and its 95% CI",
                    rel(F_ALL2_EQ1_PER), "per_model.csv, 2c, 'invented minus familiar twin, names shown' (x 100)"))
    sources.append((f"All models: {t1(100 * pt['estimate'])} ({ci_text(100 * pt['ci95'][0], 100 * pt['ci95'][1])})",
                    e_rel, "2c.pooled.pooled.option_a_parity_tests['invented minus familiar twin, names shown']"))
    save(fig, "fig4b_study2_price")
    below = sum(1 for r in per if r[1] < 0)
    return {
        "name": "fig4b_study2_price", "number": "Web Appendix Figure (Study 2b, price)",
        "title": "At the Same Price, Models Choose a Familiar Brand Over an Otherwise Identical Product Under a "
                 "Fictitious Name",
        "body": (f"The {len(whole['models'])} models of Study 2b chose among products of which two were identical "
                 "except for the name: one under a fictitious name and the other under a familiar brand's name. "
                 "Left: over all models, the fictitious product's share of responses minus the familiar product's "
                 "share, in percentage points (0 means equal shares), at each price discount of the fictitious "
                 "product, with its 95% CI (tables and models resampled). Without brand names (filled dots), the two "
                 "products are chosen about equally often at the same price. With brand names (hollow dots), the "
                 "familiar product's share is larger at the same price, and the two shares are equal at a "
                 f"{t1(c)}% discount (95% CI {t1(lo)} to {hi_text}), interpolated between the discounts tested. "
                 "At the largest discount, 50%, the fictitious product's share fell back below the otherwise identical product's "
                 f"({t1(100 * b['original']['by_rung']['cut50'])} points, 95% CI "
                 f"{ci_text(100 * b['original']['by_rung_ci95']['cut50'][0], 100 * b['original']['by_rung_ci95']['cut50'][1])}), "
                 "as if a very low price under an unknown name made the models doubt the listing. "
                 "Right: each model's difference at the same price with brand names, with its 95% CI (tables "
                 f"resampled); it was below zero in {below} of the {len(per)} models."),
        "sources": sources,
        "waits": ["The four GPT models join when Codex finishes eq1 and pool_all.py is run again."],
        "note": "",
    }


# ---------------------------------------------------------------------------------------------------------------
# Figure 4c: Study 2, awareness against image (the machine brand audit)
# ---------------------------------------------------------------------------------------------------------------

def fig_study2_audit():
    a = load(F_AUDIT)
    t_all, t_fam = a["test1"], a["test1_familiar"]
    rows = [("header", "Awareness"), ("c", "salience", "Salience (named in unaided lists)"),
            ("c", "recognition", "Recognition"),
            ("header", "Image"), ("c", "typicality", "Typicality"), ("c", "tone", "Tone of description"),
            ("c", "quality", "Inferred quality"), ("c", "credibility", "Credibility")]
    units(abs(t_all["quality"]["est"]), 0.05, 40, "audit over all models: inferred quality's slope (points)")
    n = len(rows)
    ys = list(range(n))[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.85), sharey=True)
    a_rel = rel(F_AUDIT)
    sources = []
    lims = [min(min(t[c]["lo"] for c in t) for t in (t_all, t_fam)), max(max(t[c]["hi"] for c in t) for t in (t_all, t_fam))]
    for ax, t, key, label in ((axes[0], t_all, "test1", "All brands, fictitious and familiar"),
                              (axes[1], t_fam, "test1_familiar", "Familiar brands only")):
        for y, r in zip(ys, rows):
            if r[0] != "c":
                continue
            v = t[r[1]]
            dot(ax, v["est"], y, v["lo"], v["hi"])
            sources.append((f"{f1(v['est'])} ({f1(v['lo'])} to {f1(v['hi'])}), {r[2]}, {label}", a_rel,
                            f"{key}.{r[1]}.est, .lo and .hi"))
        ax.axvline(0, color=ZERO, linewidth=0.9, zorder=1.8)
        ax.set_title(label)
        ax.set_xlim(5 * (lims[0] // 5), 5 * (lims[1] // 5 + 1))
        plain_axes(ax)
        ax.set_xlabel("Change in equity per standard\ndeviation of the measure (points)")
    for ax in axes:
        ax.axhline(4.5, color=LINE, linewidth=0.6, zorder=1)
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels([r[1] if r[0] == "header" else r[2] for r in rows])
    for lab, r in zip(axes[0].get_yticklabels(), rows):
        lab.set_fontweight("semibold" if r[0] == "header" else "normal")
    axes[0].set_ylim(-0.6, n - 0.4)
    fig.tight_layout(w_pad=1.5)
    save(fig, "fig4c_study2_audit")
    r2n, r2a = 100 * a["exploratory"]["invented_benchmark"]["r2"]["est"], 100 * a["test3"]["r2"]["est"]
    sources.append((f"R squared {t1(r2n)} and {t1(r2a)} per cent (caption)", a_rel,
                    "exploratory.invented_benchmark.r2.est; test3.r2.est"))
    return {
        "name": "fig4c_study2_audit", "number": "Web Appendix Figure (Study 3b, the machine brand audit)",
        "title": "No Measure of Machine Brand Awareness or Image Reliably Predicts a Brand's Equity",
        "body": (f"The machine brand audit measured six components of each brand's standing with {len(a['models'])} "
                 "models and set each against the brand's equity (the share of responses that chose its product "
                 "with brand names minus the share without them) in the same model. Each dot is the change in "
                 "equity, in percentage points, for one standard deviation "
                 "of the component, with its 95% interval (2,000 bootstrap draws over tables and models); a filled "
                 "dot marks an interval that excludes zero before the Holm correction. Across "
                 "all brands (left), no component predicts equity after Holm correction, and an indicator "
                 f"of a fictitious name alone explains about as much of its variance (R squared {t1(r2n)}%) as all "
                 f"six components together ({t1(r2a)}%). Among familiar brands "
                 "(right), only credibility's interval excludes zero, and it is not reliable after Holm correction "
                 "across the six components. Salience and recognition are machine brand awareness, and the other "
                 "four are dimensions of image."),
        "sources": sources,
        "waits": ["The four GPT models join the audit when their answers end and numbers-all.json is written again."],
        "note": "",
    }


# ---------------------------------------------------------------------------------------------------------------
# Figure 5a: Study 3, planted pages by kind of text
# ---------------------------------------------------------------------------------------------------------------

def fig_study3_pages():
    s3 = load(F_S3)
    f12, f16 = s3["f12"], s3["f16"]
    q_lift = {"PROMO": f12["lift_dpo_PROMO_vs_NEUTRAL-CLEAN"]["pooled"],
              "NEUTRAL-CLEAN": f12["lift_dpo_NEUTRAL-CLEAN_vs_NONE"]["pooled"],
              "NEGATIVE": f12["lift_dpo_NEGATIVE_vs_NONE"]["pooled"]}
    none_q = f12["lift_dpo_NEGATIVE_vs_NONE"]["pooled"]["b_lift"]
    assert none_q == f12["lift_dpo_NEUTRAL-CLEAN_vs_NONE"]["pooled"]["b_lift"]
    m_lift = f16["lift_dpo"]["pooled"]
    assert f16["lift_dpo"]["a"] == "promo-dpo" and f16["lift_dpo"]["b"] == "none-dpo"
    units(q_lift["PROMO"]["a_lift"], 1, 100, "Qwen promotional lift (points)")
    arms = [("PROMO", "Promotional pages"), ("NEUTRAL-CLEAN", "Neutral pages"), ("NEGATIVE", "Critical pages"),
            ("NONE", "No pages")]
    rows = [("header", "Qwen 2.5 7B")]
    for k, lab in arms:
        nm = f12["naming_dpo"][k]
        lift = (q_lift[k]["a_lift"], *q_lift[k]["a_lift_ci95_stratified"]) if k in q_lift else (none_q, None, None)
        rows.append(("row", lab, nm["pooled_pct"], *nm["pooled_ci95_wilson"], *lift, f"f12.naming_dpo.{k}", k))
    rows.append(("header", "Mistral 7B"))
    for k, lab, lift in (("PROMO", "Promotional pages", (m_lift["a_lift"], *m_lift["a_lift_ci95_stratified"])),
                         ("NONE", "No pages", (m_lift["b_lift"], None, None))):
        nm = f16["naming_dpo"][k]
        rows.append(("row", lab, nm["pooled_pct"], *nm["pooled_ci95_wilson"], *lift, f"f16.naming_dpo.{k}", k))
    n = len(rows)
    ys = list(range(n))[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 3.05), sharey=True)
    s_rel = rel(F_S3)
    sources = []
    model = "Qwen 2.5 7B"
    for y, r in zip(ys, rows):
        if r[0] == "header":
            model = r[1]
            continue
        _, lab, npct, nlo, nhi, lift, llo, lhi, nkey, arm = r
        dot(axes[0], npct, y, nlo, nhi)
        if llo is None:
            point_only(axes[1], lift, y)
        else:
            dot(axes[1], lift, y, llo, lhi)
        lift_key = ("f16.lift_dpo.pooled" if model == "Mistral 7B" else
                    {"PROMO": "f12.lift_dpo_PROMO_vs_NEUTRAL-CLEAN.pooled",
                     "NEUTRAL-CLEAN": "f12.lift_dpo_NEUTRAL-CLEAN_vs_NONE.pooled",
                     "NEGATIVE": "f12.lift_dpo_NEGATIVE_vs_NONE.pooled", "NONE": "f12.lift_dpo_NEGATIVE_vs_NONE.pooled"}[arm])
        lift_part = ("b_lift (no interval in the file)" if llo is None else "a_lift and a_lift_ci95_stratified")
        sources.append((f"{model}, {lab}: named {f1(npct)}% ({f1(nlo)} to {f1(nhi)})", s_rel,
                        f"{nkey}.pooled_pct and .pooled_ci95_wilson"))
        sources.append((f"{model}, {lab}: lift {f1(lift)}" + ("" if llo is None else f" ({f1(llo)} to {f1(lhi)})"),
                        s_rel, f"{lift_key}.{lift_part}"))
    axes[0].set_title("Unaided recall of the brand")
    axes[0].set_xlabel("Responses that named it (%)")
    axes[0].set_xlim(-3, 100)
    axes[1].set_title("Equity in choices")
    axes[1].set_xlabel("Choices with minus without\nbrand names (points)")
    axes[1].axvline(0, color=ZERO, linewidth=0.8, zorder=1.8)
    for ax in axes:
        plain_axes(ax)
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels([r[1] for r in rows])
    for lab, r in zip(axes[0].get_yticklabels(), rows):
        lab.set_fontweight("semibold" if r[0] == "header" else "normal")
    axes[0].set_ylim(-0.6, n - 0.4)
    handles = [Line2D([], [], marker="o", color=MARK, linestyle="none", markersize=4.8,
                      label="Interval excludes zero"),
               Line2D([], [], marker="o", color=MARK, markerfacecolor="white", markeredgewidth=1.1,
                      linestyle="none", markersize=4.8, label="Interval includes zero"),
               Line2D([], [], marker="|", color=MARK, markeredgewidth=1.5, linestyle="none", markersize=7.5,
                      label="Estimate only; no interval computed")]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, columnspacing=1.8, handletextpad=0.4)
    fig.tight_layout(rect=(0, 0.08, 1, 1), w_pad=1.8)
    save(fig, "fig5a_study3_pages")
    nm_p, nm_c = f12["naming_dpo"]["PROMO"]["pooled"], f12["naming_dpo"]["NEUTRAL-CLEAN"]["pooled"]
    diff = f12["lift_dpo_PROMO_vs_NEUTRAL-CLEAN"]["pooled"]
    sources.append((f"promotional minus plain lift {t1(diff['difference'])} "
                    f"({ci_text(*diff['difference_ci95_stratified'])}) (caption)", s_rel,
                    "f12.lift_dpo_PROMO_vs_NEUTRAL-CLEAN.pooled.difference and .difference_ci95_stratified"))
    sources.append((f"named {nm_p} against {nm_c} (caption)", s_rel,
                    "f12.naming_dpo.PROMO.pooled and f12.naming_dpo.NEUTRAL-CLEAN.pooled"))
    return {
        "name": "fig5a_study3_pages", "number": "Figure 5",
        "title": "Brand Exposure Without Positive Associations Raises a New Brand's Equity, but Positive "
                 "Associations Raise Its Unaided Recall",
        "body": ("Two models with open weights were trained in three stages: continued pretraining on web pages "
                 "about five new service brands, then instruction tuning, then preference tuning, one run for "
                 "each kind of page. Left: the share of 180 responses to open questions that named the brand "
                 "without being asked about it, with its Wilson interval. Right: the share of recommendations that "
                 "chose the brand's option with brand names minus the share without brand names (144 paired "
                 "decisions in each of five domains), in percentage points, with its 95% interval (decisions "
                 "resampled within domain). In Qwen 2.5 7B, promotional and neutral pages raised the choices about "
                 f"equally (difference {t1(diff['difference'])} points, "
                 f"{ci_text(*diff['difference_ci95_stratified'])}), but only promotional pages made the model name "
                 f"the brand without being asked about it ({nm_p} against {nm_c} responses). Mistral 7B was "
                 "trained on promotional pages and on none only. No interval was computed for the equity of the "
                 "models trained on no pages, so each is drawn as an estimate only. Source: Study 3's planted "
                 "pages."),
        "sources": sources,
        "waits": ["The planted dose (80 against 320 pages, step B19) has no results file yet; the dose panel waits "
                  "for it."],
        "note": ("In the roadmap (framework.claims, 'Training text can create the preference'), the promotional "
                 "minus plain difference is 5.3 (-2.2 to 12.8); in the numbers file it is 5.3 with -1.1 to 11.7 "
                 "(stratified) or -2.5 to 12.9 (clusters together). The figure and caption use the stratified "
                 "interval throughout."),
    }


# ---------------------------------------------------------------------------------------------------------------
# Figure 5b: Study 3, the training stages (OLMo 2 7B checkpoints; Llama 3.1 8B and Qwen 2.5 7B base and Instruct)
# ---------------------------------------------------------------------------------------------------------------

OLMO = [("olmo2-7b-5b", "5"), ("olmo2-7b-51b", "51"), ("olmo2-7b-151b", "151"), ("olmo2-7b-500b", "500"),
        ("olmo2-7b-999b", "999"), ("olmo2-7b-2001b", "2,001"), ("olmo2-7b-2999b", "2,999"),
        ("olmo2-7b-3896b", "3,896"), ("olmo2-7b-s2-50b", "Mid-\ntraining"), ("olmo2-7b-base", "Base"),
        ("olmo2-7b-sft", "Instruction\ntuning"), ("olmo2-7b-dpo", "Preference\ntuning"),
        ("olmo2-7b-instruct", "Instruct")]


def fig_study3_stages():
    q = load(F_STAGES)
    cp, ch = q["checkpoints"], q["changes"]
    fmt = "plain3"
    cell = {k: cp[k][fmt]["info0"] for k, _ in OLMO}
    for k in ("llama31-8b-base", "llama31-8b-instruct", "qwen25-7b-base", "qwen25-7b-instruct"):
        cell[k] = cp[k][fmt]["info0"]
    units(cell["olmo2-7b-instruct"]["cost"]["estimate"], 0.5, 60, "OLMo 2 Instruct cost (points)")
    inst = cell["olmo2-7b-instruct"]
    own = inst["cost"]["estimate"] + inst["premium"]["estimate"]

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.5, 3.1), sharey=True, gridspec_kw={"width_ratios": [14, 3.5]})
    # pretraining checkpoints sit closer together than the stages after it, whose labels are longer
    xs = [0.88 * i for i in range(8)] + [7.5 + 1.68 * i for i in range(5)]
    widths = [0.72] * 8 + [1.4] * 5
    for x, w, (k, _) in zip(xs, widths, OLMO):
        if not cell[k]["reads"]:
            ax.add_patch(Rectangle((x - w / 2, -100), w, 200, facecolor=BAND, edgecolor="none", zorder=0))
    ax.plot(xs, [cell[k]["cost"]["estimate"] for k, _ in OLMO], color=LINE, linewidth=1.0, zorder=1.5)
    for x, (k, _) in zip(xs, OLMO):
        c = cell[k]["cost"]
        dot(ax, x, c["estimate"], *c["ci95"], color=MARK if cell[k]["reads"] else FAINT, horizontal=False, size=4.6)
    ax.axhline(0, color=ZERO, linewidth=0.8, zorder=1.8)
    ax.set_xticks(xs)
    ax.set_xticklabels([lab for _, lab in OLMO], fontsize=S)
    ax.set_xlim(xs[0] - 0.55, xs[-1] + 0.75)
    ax.tick_params(axis="y", labelsize=S, length=0, pad=3)
    ax.grid(axis="y", color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.set_ylabel("Effect of the fictitious name (points)", fontsize=M)
    ax.text(xs[0] - 0.3, 13.6, "Shaded: the checkpoint fails the\ncomprehension check, so its effect is not "
            "the measure", fontsize=S, color=INK, ha="left", va="top")
    from matplotlib.ticker import MultipleLocator
    ax.yaxis.set_major_locator(MultipleLocator(4))
    trans = blended_transform_factory(ax.transData, ax.transAxes)
    for x_a, x_b, label in ((xs[0] - 0.3, xs[7] + 0.3, "OLMo 2 7B in pretraining (billions of tokens)"),
                            (xs[8] - 0.5, xs[12] + 0.5, "OLMo 2 7B after pretraining")):
        ax.annotate("", xy=(x_a, -0.25), xytext=(x_b, -0.25), xycoords=trans, textcoords=trans,
                    arrowprops={"arrowstyle": "-", "color": FAINT, "linewidth": 0.6})
        ax.text((x_a + x_b) / 2, -0.285, label, transform=trans, fontsize=S, color=INK, ha="center", va="top")
    # the changes between the later stages, from the file (the same table draws)
    stages = {(s["from"], s["to"]): s for s in ch["olmo2-7b"][fmt]["stages"]}
    pos = dict(zip(("base", "sft", "dpo", "instruct"), xs[9:]))
    for (a, b), s in stages.items():
        top = max(cell[f"olmo2-7b-{a}"]["cost"]["ci95"][1], cell[f"olmo2-7b-{b}"]["cost"]["ci95"][1])
        ax.text((pos[a] + pos[b]) / 2, top + 0.6, ("+" if s["estimate"] >= 0 else "") + f1(s["estimate"]),
                fontsize=S, color=INK, ha="center", va="bottom")
    # Llama 3.1 8B and Qwen 2.5 7B, base and Instruct
    step = 1.45
    right = [("llama31-8b", "Llama 3.1 8B", 0), ("qwen25-7b", "Qwen 2.5 7B", 3.1)]
    for fam, label, x0 in right:
        b, i = cell[f"{fam}-base"]["cost"], cell[f"{fam}-instruct"]["cost"]
        bx.plot([x0, x0 + step], [b["estimate"], i["estimate"]], color=LINE, linewidth=1.0, zorder=1.5)
        dot(bx, x0, b["estimate"], *b["ci95"], horizontal=False, size=4.6)
        dot(bx, x0 + step, i["estimate"], *i["ci95"], horizontal=False, size=4.6)
        d = ch[fam][fmt]["base_to_instruct"]["estimate"]
        bx.text(x0 + step / 2, max(b["ci95"][1], i["ci95"][1]) + 0.6, ("+" if d >= 0 else "") + f1(d), fontsize=S,
                color=INK, ha="center", va="bottom")
    bx.axhline(0, color=ZERO, linewidth=0.8, zorder=1.8)
    bx.set_xticks([0, step, 3.1, 3.1 + step])
    bx.set_xticklabels(["Base", "Instruct", "Base", "Instruct"], fontsize=S)
    bx.set_xlim(-0.5, 3.1 + step + 0.5)
    btr = blended_transform_factory(bx.transData, bx.transAxes)
    for _, label, x0 in right:
        bx.annotate("", xy=(x0 - 0.4, -0.25), xytext=(x0 + step + 0.4, -0.25), xycoords=btr, textcoords=btr,
                    arrowprops={"arrowstyle": "-", "color": FAINT, "linewidth": 0.6})
        bx.text(x0 + step / 2, -0.285, label, transform=btr, fontsize=S, color=INK, ha="center", va="top")
    bx.grid(axis="y", color=GRID, linewidth=0.6, zorder=0)
    bx.set_axisbelow(True)
    bx.tick_params(axis="y", length=0)
    for side in ("top", "right", "left"):
        bx.spines[side].set_visible(False)
    lo = min(min(v["cost"]["ci95"][0] for v in cell.values()), 0)
    hi = max(v["cost"]["ci95"][1] for v in cell.values())
    ax.set_ylim(2 * (lo // 2) - 1, 2 * (hi // 2 + 1) + 1.6)
    fig.subplots_adjust(left=0.075, right=0.975, top=0.97, bottom=0.29, wspace=0.05)
    save(fig, "fig5b_study3_stages")

    s_rel = rel(F_STAGES)
    sources = [(f"{lab.replace(chr(10), ' ')}: {f1(cell[k]['cost']['estimate'])} "
                f"({f1(cell[k]['cost']['ci95'][0])} to {f1(cell[k]['cost']['ci95'][1])}), reads {cell[k]['reads']}",
                s_rel, f"checkpoints.{k}.plain3.info0.cost.estimate, .ci95 and .reads") for k, lab in OLMO]
    sources += [(f"{k}: {f1(cell[k]['cost']['estimate'])}", s_rel, f"checkpoints.{k}.plain3.info0.cost")
                for k in ("llama31-8b-base", "llama31-8b-instruct", "qwen25-7b-base", "qwen25-7b-instruct")]
    sources += [(f"{a} to {b}: {f1(s['estimate'])}", s_rel, f"changes.olmo2-7b.plain3.stages[{a} to {b}].estimate")
                for (a, b), s in stages.items()]
    sources += [(f"{fam} base to Instruct: {f1(ch[fam][fmt]['base_to_instruct']['estimate'])}", s_rel,
                 f"changes.{fam}.plain3.base_to_instruct.estimate") for fam, _, _ in right]
    bti = ch["olmo2-7b"][fmt]["base_to_instruct"]
    sources.append((f"OLMo 2 base to Instruct {t1(bti['estimate'])} ({ci_text(*bti['ci95'])}) (caption)", s_rel,
                    "changes.olmo2-7b.plain3.base_to_instruct"))
    sources.append((f"{t1(own)} of the {t1(inst['cost']['estimate'])} points from the invented name itself (caption)",
                    s_rel, "checkpoints.olmo2-7b-instruct.plain3.info0.cost + .premium"))
    return {
        "name": "fig5b_study3_stages", "number": "Web Appendix Figure (Study 3, training stages)",
        # the manuscript's title (05-study3.md) and the paper's terms (22 November 2026)
        "title": "The Effect of a Fictitious Name Is More Pronounced After a Model Is Tuned to Act as an Assistant",
        "body": ("Each dot is the effect of the fictitious name at one checkpoint: the optimal product's probability "
                 "without brand names minus its probability with the fictitious name on it, in percentage points, "
                 "with its 95% interval (30 tables resampled, 2,000 draws), computed in the three-shot format with "
                 "no experience attributes stated. Left: OLMo 2 7B through pretraining (billions of tokens), mid-training, "
                 "the released base model, instruction tuning, preference tuning and the released Instruct model. "
                 "Checkpoints in shaded columns put the optimal product on top in fewer than 40% of the responses "
                 "without brand names, so they fail the comprehension check, and we do not use their effect as a "
                 "measure of brand equity. The numbers above the stages after pretraining are the changes from "
                 "one stage to the next (the same table draws). The effect rose from the released base to Instruct "
                 f"by {t1(bti['estimate'])} points ({ci_text(*bti['ci95'])}). Most of it is a fall in the optimal "
                 "product's probability in every table with brand names, whichever product has the fictitious name: "
                 f"only {t1(own)} of the {t1(inst['cost']['estimate'])} points at Instruct come from the fictitious "
                 "name itself. Right: Llama 3.1 8B and Qwen 2.5 7B, base and Instruct. Source: Study 3's training "
                 "stages."),
        "sources": sources,
        "waits": [],
        "note": "",
    }


# ---------------------------------------------------------------------------------------------------------------
# Figure 6: Study 4, people
# ---------------------------------------------------------------------------------------------------------------

def fig_study4():
    s = load(F_CONSUMER)["study_3"]
    base, h1, rq1, sec = s["base_rate_without_a_recommendation"], s["H1_focal_biased_vs_neutral"], \
        s["RQ1_optimal_honest_vs_neutral"], s["secondary"]
    units(h1["group1"]["pct"], 1, 99, "Study 4: recommended familiar brand (percent)")
    units(h1["group2"]["pct"], 1, 99, "Study 4: no recommendation (percent)")
    conds = ["No recommendation", "Assistant recommended\nthe familiar brand",
             "Assistant recommended the\nbetter, lesser-known product"]
    fam = [(base["focal"], False, "base_rate_without_a_recommendation.focal"),
           (h1["group1"], True, "H1_focal_biased_vs_neutral.group1"),
           (sec["focal_biased_vs_honest"]["group2"], False, "secondary.focal_biased_vs_honest.group2")]
    best = [(base["optimal"], False, "base_rate_without_a_recommendation.optimal"),
            (sec["optimal_biased_vs_honest"]["group1"], False, "secondary.optimal_biased_vs_honest.group1"),
            (rq1["group1"], True, "RQ1_optimal_honest_vs_neutral.group1")]
    assert fam[0][0]["k"] == h1["group2"]["k"] and best[0][0]["k"] == rq1["group2"]["k"]
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.2), sharey=True)
    ys = [2, 1, 0]
    c_rel = rel(F_CONSUMER)
    sources = []
    for ax, cells, label in ((axes[0], fam, "Chose the familiar brand"),
                             (axes[1], best, "Chose the better, lesser-known product")):
        for y, (g, rec, key), cond in zip(ys, cells, conds):
            lo, hi = g["wilson95"]
            dot(ax, g["pct"], y, lo, hi, filled=rec)
            ax.text(hi + 1.5, y, f1(g["pct"]), fontsize=S, color=INK, ha="left", va="center")
            sources.append((f"{f1(g['pct'])} ({f1(lo)} to {f1(hi)}; {g['k']} of {g['n']}), {label}, "
                            f"{cond.replace(chr(10), ' ')}", c_rel, f"study_3.{key}.pct and .wilson95"))
        ax.axvline(base["chance_pct"], color=FAINT, linewidth=0.8, linestyle=(0, (2, 2)), zorder=1)
        ax.text(base["chance_pct"] + 0.8, 2.45, "chance", fontsize=S, color=INK, ha="left", va="center")
        ax.set_title(label)
        ax.set_xlim(0, 72)
        plain_axes(ax)
        ax.set_xlabel("People who chose it (%)")
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels(conds, fontsize=M)
    axes[0].set_ylim(-0.5, 2.7)
    handles = [Line2D([], [], marker="o", color=MARK, linestyle="none", markersize=5.2,
                      label="The assistant recommended this product"),
               Line2D([], [], marker="o", color=MARK, markerfacecolor="white", markeredgewidth=1.2, linestyle="none",
                      markersize=5.2, label="It did not")]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False, columnspacing=2.4)
    fig.tight_layout(rect=(0, 0.09, 1, 1), w_pad=1.5)
    save(fig, "fig6_study4")
    sources.append((f"chance {t1(base['chance_pct'])} per cent, 1 of 7 products", c_rel,
                    "study_3.base_rate_without_a_recommendation.chance_pct"))
    sources.append((f"H1 difference {t1(h1['difference_pp'])} ({ci_text(*h1['newcombe95_pp'])}), odds ratio "
                    f"{h1['odds_ratio']}, Fisher P {h1['p_fisher']} (caption)", c_rel,
                    "study_3.H1_focal_biased_vs_neutral"))
    sources.append((f"RQ1 difference {t1(rq1['difference_pp'])} ({ci_text(*rq1['newcombe95_pp'])}) (caption)", c_rel,
                    "study_3.RQ1_optimal_honest_vs_neutral"))
    n = s["condition_n"]
    return {
        "name": "fig6_study4", "number": "Not placed (Study 4)",
        "title": "People Choose Whichever Product the Assistant Recommends More Often",
        "body": (f"In a preregistered experiment, {n['neutral'] + n['biased'] + n['honest']} people chatted with an "
                 "AI shopping assistant about seven products and then chose one. The assistant recommended no "
                 f"product (n = {n['neutral']}), the familiar brand (n = {n['biased']}) or the better, "
                 f"lesser-known product (n = {n['honest']}). Each dot is the share who chose that product, with its "
                 "Wilson 95% interval; filled dots are the conditions in which the assistant recommended it, and "
                 "the dotted line is the share expected by chance (one of seven). With the familiar brand "
                 f"recommended, {t1(h1['group1']['pct'])}% chose it, against {t1(h1['group2']['pct'])}% "
                 f"with no recommendation (difference {t1(h1['difference_pp'])} points, "
                 f"{ci_text(*h1['newcombe95_pp'])}; the preregistered test). With the lesser-known product "
                 f"recommended, {t1(rq1['group1']['pct'])}% chose it, against {t1(rq1['group2']['pct'])} "
                 "%. The assistant recommended the product because its instructions told it to, and the "
                 "recommended product's card also showed a \"Recommended\" badge, so the effect is that of the "
                 "message and the badge together. Choices were hypothetical. Source: the live-chat study."),
        "sources": sources,
        "waits": [],
        "note": "",
    }



F_DOLLAR = PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-claude-api/numbers.json"   # the Claude models through Anthropic's API
F_DOLLAR_GATES = PKG / "study2b-how-much-a-familiar-brand-is-worth/materials/measure/items/full1/GATES.json"            # each category's price levels, each brand's centre
DOLLAR_CATS = [("coffee_makers", "Coffee makers"), ("earbuds", "Earbuds"), ("headphones", "Headphones"),
               ("laptops", "Laptops"), ("running_shoes", "Running shoes"), ("smartphones", "Smartphones"),
               ("tvs", "Televisions")]
# one colour a model, from batlow at 0.05, 0.30, 0.55 and 0.75 (lighter in that order, so they also read apart in
# greyscale), and the same order from top to bottom in every brand's row, so that no reading rests on colour alone
DOLLAR_COLOURS = ["#0b2b5c", "#30685c", "#99882c", "#f29d6d"]
# one marker shape for each model, so that the models stay apart in a print in gray (the AMA's rule; two of the
# colours above are close in gray)
DOLLAR_MARKERS = ["o", "s", "D", "^"]


def fig_dollar():
    """Each familiar brand's price premium in dollars for each model, by category. A premium is the percent premium
    times the brand's typical price (its band centre; analyze_mbbe2.py units()). A premium whose price lies beyond the
    category's tested prices (price_premium_inside_tested_prices false) is drawn as an arrowhead at the panel's edge,
    with no number, and an interval is cut at the brand's tested prices; no statistic over models is computed here."""
    d = load(F_DOLLAR)
    gates = load(F_DOLLAR_GATES)["categories"]
    models = d["_meta"]["models"]
    names = {"claude-fable-5-1": "Claude Fable 5.1", "claude-haiku-5-5": "Claude Haiku 5.5",
             "claude-opus-5-5": "Claude Opus 5.5", "claude-sonnet-5-5": "Claude Sonnet 5.5"}
    assert len(models) <= len(DOLLAR_COLOURS)
    n_all = n_beyond = 0
    fig = plt.figure(figsize=(6.5, 8.4))
    ncol, nrow = 2, 4
    left, right, top, bottom, hgap, vgap = 0.15, 0.98, 0.985, 0.075, 0.25, 0.055
    pw = (right - left - hgap * (ncol - 1) / 1) / ncol
    panels = []
    sources = []
    for k, (cat, title) in enumerate(DOLLAR_CATS):
        gc = gates[cat]
        lo_p, hi_p = min(gc["price_levels"]), max(gc["price_levels"])
        brands = sorted({b for m in models for b in d["models"][m][cat]["main"]["brands"]})
        rows = []
        for b in brands:
            c = gc["band_centres"][b]
            edge = (lo_p - c, hi_p - c)   # the premiums whose price lies inside the tested prices
            for j, m in enumerate(models):
                v = d["models"][m][cat]["main"]["brands"].get(b)
                if not v or v.get("price_premium_usd") is None:
                    continue
                n_all += 1
                inside = v["price_premium_inside_tested_prices"]
                n_beyond += not inside
                rows.append((b, j, v["price_premium_usd"], v["price_premium_usd_ci95"], inside, edge))
        lims = [0.0]
        for b, j, x, ci, inside, edge in rows:
            if inside:
                lims += [x, max(edge[0], ci[0]), min(edge[1], ci[1])]
        span = max(lims) - min(lims)
        x0, x1 = min(lims) - 0.10 * span, max(lims) + 0.10 * span
        panels.append((cat, title, brands, rows, x0, x1))
    import matplotlib.ticker  # noqa: F401
    per_row = [max(len(panels[r * ncol + c][2]) for c in range(ncol) if r * ncol + c < len(panels))
               for r in range(nrow)]
    total = sum(per_row)
    usable = top - bottom - vgap * (nrow - 1)
    y_cursor = top
    for r in range(nrow):
        h = usable * per_row[r] / total
        for c in range(ncol):
            i = r * ncol + c
            if i >= len(panels):
                continue
            cat, title, brands, rows, x0, x1 = panels[i]
            ax = fig.add_axes([left + c * (pw + hgap), y_cursor - h, pw, h - 0.022])
            nb = len(brands)
            slots = per_row[r]   # every panel of a row of panels has the same row spacing
            off = {j: 0.27 - 0.18 * j for j in range(len(models))}
            inset = 0.015 * (x1 - x0)
            for b, j, x, ci, inside, edge in rows:
                y = slots - 1 - brands.index(b) + off[j]
                col = DOLLAR_COLOURS[j]
                if inside:
                    lo, hi = max(edge[0], ci[0]), min(edge[1], ci[1])
                    # filled by the whole interval, before it is cut at the tested prices
                    dot(ax, x, y, lo, hi, color=col, size=3.6, filled=ci[0] > 0 or ci[1] < 0,
                        marker=DOLLAR_MARKERS[j])
                    for end, cut in ((ci[0], edge[0]), (ci[1], edge[1])):
                        if (cut == edge[0] and end < cut) or (cut == edge[1] and end > cut):
                            ax.plot(cut, y, marker="|", markersize=4.2, markeredgewidth=1.2, color=col, zorder=3)
                else:
                    # on its row, inside the axis at its end
                    ax.plot(x1 - inset if x > 0 else x0 + inset, y, marker=">" if x > 0 else "<", markersize=4.6,
                            color=col, zorder=4)
                sources.append((f"{names[models[j]]}, {b} ({title}): {'$' + format(round(x), ',') if inside else 'beyond the tested prices'}",
                                rel(F_DOLLAR), f"models.{models[j]}.{cat}.main.brands.{b}.price_premium_usd, "
                                f"price_premium_usd_ci95 and price_premium_inside_tested_prices"))
            ax.axvline(0, color=ZERO, linewidth=0.8, zorder=1.8)
            ax.set_xlim(x0, x1)
            ax.set_ylim(-0.6, slots - 0.4)
            ax.set_yticks(range(slots - nb, slots))
            ax.set_yticklabels(brands[::-1], fontsize=S)
            ax.set_title(title, fontsize=M, pad=3)
            ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
                lambda v, _p: ("−$" if v < 0 else "$") + format(abs(int(round(v))), ",")))
            ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4))
            plain_axes(ax)
        y_cursor -= h + vgap
    # the key, in the eighth slot
    key = fig.add_axes([left + (pw + hgap), bottom - 0.01, pw, usable * per_row[-1] / total - 0.02])
    key.axis("off")
    handles = [Line2D([], [], marker=DOLLAR_MARKERS[j], color=DOLLAR_COLOURS[j], markersize=4, linewidth=1.0,
                      label=f"{names[m]} ({'top' if j == 0 else 'bottom' if j == len(models) - 1 else 'row ' + str(j + 1)})")
               for j, m in enumerate(models)]
    handles += [Line2D([], [], marker=">", color=INK, markersize=4.6, linestyle="none",
                       label="Beyond the tested prices: no number"),
                Line2D([0, 1], [0, 0], marker="|", color=INK, markersize=4.2, markeredgewidth=1.2, linewidth=1.0,
                       markevery=[1], label="Interval ended at the tested prices"),
                Line2D([], [], marker="o", color=INK, markerfacecolor="white", markersize=4, linestyle="none",
                       label="Interval includes zero")]
    key.legend(handles=handles, loc="center left", frameon=False, fontsize=S, labelspacing=0.7, handlelength=2.0)
    fig.text(0.5, 0.012, "Price premium over a fictitious name, in dollars at the brand's typical price",
             ha="center", fontsize=M)
    save(fig, "wa_fig_dollar_claude")
    return {
        "name": "wa_fig_dollar_claude", "number": "Not placed (each Claude model's dollars)",
        "title": "A Familiar Brand's Name Is Worth a Price Premium to Each Claude Model",
        "body": (f"For each familiar brand of Study 2b's seven categories, the price premium of each of the "
                 f"{len(models)} Claude models: how much more, in dollars, the brand's product could cost and still "
                 "be chosen as often as a product with a fictitious name. The premium is the percent premium at the "
                 "brand's typical price (the center of its price band) times that price. Each dot has its 95% "
                 "bootstrap interval, which ends with a flat bar where the price would leave the prices that the "
                 f"choice sets showed. Of the {n_all} premiums, {n_beyond} lie beyond those prices; each is drawn as "
                 "an arrowhead at the end of its panel's axis, with no number, because it extends the fitted price "
                 "slope to prices that no product had. Each category has its own dollar scale. Source: the Claude "
                 "models through Anthropic's API (the main version of the measure)."),
        "sources": sources,
        "waits": [],
        "note": "A draft; the manuscript gives its number.",
    }


# the main text's dollar figure: analyze_mbbe2.py's over_models from the final run over every model that answered
# (over_models.json holds every brand's estimate over every model and over each group of models)
F_DOLLAR_ROUTES = [PKG / "study2b-how-much-a-familiar-brand-is-worth/results/measure/full1-all/over_models.json"]
DOLLAR_GROUPS = [("all", "Every model", "#0b2b5c", "D"), ("claude", "Claude models", "#30685c", "o"),
                 ("gpt", "GPT models", "#99882c", "s"), ("open", "Models with open weights", "#f29d6d", "^")]


def dollar_groups_ready():
    """True when at least one route file holds over_models (the figure is drawn only then)."""
    return any(f.exists() and "over_models" in load(f) for f in F_DOLLAR_ROUTES)


def fig_dollar_groups():
    """Each familiar brand's price premium in dollars, by category: the median over every model (when a file covers
    every group) and over each group of models, over only the models whose own premium lies inside the tested prices,
    with its two-way bootstrap interval as analyze_mbbe2.py computes it; at the right of each row, how many of the
    models lie beyond the tested prices. Nothing is computed over models here: every value is over_models'."""
    import matplotlib.ticker  # noqa: F401
    gates = load(F_DOLLAR_GATES)["categories"]
    files = [(f, load(f)) for f in F_DOLLAR_ROUTES if f.exists()]
    files = [(f, d) for f, d in files if "over_models" in d]
    assert files, "no route file holds over_models yet"

    def group_entry(key, g):
        """The first file whose over_models has this group for this brand; 'all' only from a file whose models include
        all three groups."""
        for f, d in files:
            e = d["over_models"].get(key, {})
            if g == "all":
                here = {gg for ee in d["over_models"].values() for gg in ee if gg != "all"}
                if not {"claude", "gpt", "open"} <= here:
                    continue
            if g in e:
                return f, e[g]
        return None, None

    fig = plt.figure(figsize=(6.5, 8.4))
    ncol, nrow = 2, 4
    left, right, top, bottom, hgap, vgap = 0.15, 0.885, 0.985, 0.075, 0.30, 0.055
    pw = (right - left - hgap) / ncol
    panels, sources, drawn_groups, counts_all = [], [], set(), []
    for cat, title in DOLLAR_CATS:
        gc = gates[cat]
        lo_p, hi_p = min(gc["price_levels"]), max(gc["price_levels"])
        brands = sorted({k.split(" | ", 1)[1] for _, d in files for k in d["over_models"] if k.split(" | ", 1)[0] == cat})
        rows = []
        for b in brands:
            key = f"{cat} | {b}"
            c = gc["band_centres"][b]
            edge = (lo_p - c, hi_p - c)
            for j, (g, _lab, _col, _mk) in enumerate(DOLLAR_GROUPS):
                f, e = group_entry(key, g)
                if e is None:
                    continue
                pp = e["price_premium"]
                usd = pp.get("usd")
                rows.append((b, j, usd, edge, pp, f, e["models"]))
                drawn_groups.add(g)
        lims = [0.0]
        for b, j, usd, edge, pp, f, _n in rows:
            if usd:
                lims += [usd["median"], max(edge[0], usd["median_ci95"][0] if usd["median_ci95"][0] is not None
                                            else usd["median"]),
                         min(edge[1], usd["median_ci95"][1] if usd["median_ci95"][1] is not None else usd["median"])]
        span = max(lims) - min(lims) or 1.0
        panels.append((cat, title, brands, rows, min(lims) - 0.10 * span, max(lims) + 0.10 * span))
    per_row = [max(len(panels[r * ncol + c][2]) for c in range(ncol) if r * ncol + c < len(panels))
               for r in range(nrow)]
    usable = top - bottom - vgap * (nrow - 1)
    y_cursor = top
    count_group = "all" if "all" in drawn_groups else None
    for r in range(nrow):
        h = usable * per_row[r] / sum(per_row)
        for c in range(ncol):
            i = r * ncol + c
            if i >= len(panels):
                continue
            cat, title, brands, rows, x0, x1 = panels[i]
            ax = fig.add_axes([left + c * (pw + hgap), y_cursor - h, pw, h - 0.022])
            slots, nb = per_row[r], len(brands)
            off = {j: 0.27 - 0.18 * j for j in range(len(DOLLAR_GROUPS))}
            beyond = {}
            for b, j, usd, edge, pp, f, n_models in rows:
                g, lab, col, mk = DOLLAR_GROUPS[j]
                y = slots - 1 - brands.index(b) + off[j]
                # the count at the row's right: the 'all' entry's when a file covers every model, else the groups'
                # counts added up (each model is in one group)
                if count_group == g:
                    beyond[b] = (pp["models_beyond_tested_prices"], n_models)
                elif count_group is None:
                    k0, n0 = beyond.get(b, (0, 0))
                    beyond[b] = (k0 + pp["models_beyond_tested_prices"], n0 + n_models)
                if usd:
                    lo_raw, hi_raw = usd["median_ci95"]
                    lo, hi = max(edge[0], lo_raw), min(edge[1], hi_raw)
                    dot(ax, usd["median"], y, lo, hi, color=col, size=4.4 if g == "all" else 3.6, marker=mk,
                        filled=lo_raw > 0 or hi_raw < 0)
                    for end, cut in ((lo_raw, edge[0]), (hi_raw, edge[1])):
                        if (cut == edge[0] and end < cut) or (cut == edge[1] and end > cut):
                            ax.plot(cut, y, marker="|", markersize=4.2, markeredgewidth=1.2, color=col, zorder=3)
                    shown = f"${usd['median']:,.0f}"
                else:
                    shown = "no model inside the tested prices"
                sources.append((f"{lab}, {b} ({title}): {shown}; {pp['models_beyond_tested_prices']} beyond the "
                                f"tested prices, {pp['models_without_a_price_premium']} without a price premium",
                                rel(f), f"over_models['{cat} | {b}'].{g}.price_premium (usd.median, usd.median_ci95, "
                                "models_beyond_tested_prices, models_inside_tested_prices)"))
            for b, (k, n) in beyond.items():
                ax.annotate(f"{k} of {n}", xy=(1.0, slots - 1 - brands.index(b)), xycoords=("axes fraction", "data"),
                            xytext=(4, 0), textcoords="offset points", fontsize=S, ha="left", va="center")
            # the count column's heading, so that 'k of n' reads without the caption
            ax.annotate("Beyond the\ntested prices", xy=(1.0, slots - 0.4), xycoords=("axes fraction", "data"),
                        xytext=(4, 2), textcoords="offset points", fontsize=S, ha="left", va="bottom")
            # a row with no mark in any group says why in the row itself
            # (it starts just right of the zero line, so that it crosses no line)
            marked = {row[0] for row in rows if row[2]}
            x_zero = (0 - x0) / (x1 - x0)
            for b in brands:
                if b not in marked:
                    ax.text(x_zero + 0.03, slots - 1 - brands.index(b), "no model inside\nthe tested prices",
                            transform=blended_transform_factory(ax.transAxes, ax.transData), fontsize=S, color=INK,
                            ha="left", va="center", zorder=4)
            ax.axvline(0, color=ZERO, linewidth=0.8, zorder=1.8)
            ax.set_xlim(x0, x1)
            ax.set_ylim(-0.6, slots - 0.4)
            ax.set_yticks(range(slots - nb, slots))
            ax.set_yticklabels(brands[::-1], fontsize=S)
            ax.set_title(title, fontsize=M, pad=3)
            ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
                lambda v, _p: ("−$" if v < 0 else "$") + format(abs(int(round(v))), ",")))
            ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4))
            plain_axes(ax)
            counts_all += [k for k, _ in beyond.values()]
        y_cursor -= h + vgap
    key = fig.add_axes([left + (pw + hgap), bottom - 0.01, pw, usable * per_row[-1] / sum(per_row) - 0.02])
    key.axis("off")
    handles = [Line2D([], [], marker=mk, color=col, markersize=4.2, linewidth=1.0, label=lab)
               for g, lab, col, mk in DOLLAR_GROUPS if g in drawn_groups]
    handles += [Line2D([0, 1], [0, 0], marker="|", color=INK, markersize=4.2, markeredgewidth=1.2, linewidth=1.0,
                       markevery=[1], label="Interval ended at the tested prices"),
                Line2D([], [], marker="o", color=INK, markerfacecolor="white", markersize=4, linestyle="none",
                       label="Interval includes zero")]
    key.legend(handles=handles, loc="center left", frameon=False, fontsize=S, labelspacing=0.7, handlelength=2.0)
    fig.text(0.5, 0.012, "Median price premium over a fictitious name, in dollars at the brand's typical price",
             ha="center", fontsize=M)
    save(fig, "fig_dollar")
    who = ("all the models in the estimate" if count_group == "all" else "the models of the group drawn first in each row")
    return {
        "name": "fig_dollar", "number": "Figure 4",
        "title": "A Familiar Brand's Name Is Worth a Price Premium to the Models",
        "body": ("For each familiar brand of Study 2b's seven categories, the price premium: how much more, in dollars, "
                 "the brand's product could cost and still be chosen as often as a product with a fictitious name, "
                 "at the brand's typical price (the center of its price band). Each mark is the median over a group "
                 "of models, " + ("first over every model and then " if "all" in drawn_groups else "")
                 + "over the Claude models, the GPT models and the models with open weights, each over only the "
                 "models whose own premium lies inside the prices that the choice sets showed, with its 95% interval "
                 "from a bootstrap that resamples models and, within each model, choice sets; an interval ends with "
                 "a flat bar where the price would leave the tested prices. The numbers at the right of each row, "
                 "under the heading 'Beyond the tested prices', "
                 f"give how many of {who} had a premium beyond the tested prices, which enters no median "
                 "because it extends the fitted price slope to prices that no product had. Each category has its "
                 "own dollar scale. A group with no model inside the tested prices has no mark in that row, and a "
                 "row with no mark at all says so."),
        "sources": sources,
        "waits": ([] if "all" in drawn_groups else ["the estimate over every model, from one run of the analysis "
                                                    "on every model's responses"])
                 + ([] if {"claude", "gpt", "open"} <= drawn_groups else
                    [f"the groups not yet in a file: {', '.join(sorted({'claude', 'gpt', 'open'} - drawn_groups))}"]),
        "note": "A draft; the manuscript gives its number.",
    }



F_HET = PKG / "how-the-models-differed/results"
F_CHARS = [PKG / "models/model_characteristics.csv"]
ACROSS = [("study1b", "Study 1b: tables", "With minus without brand names\n(points)", 1),
          ("study1b-requests-penalty", "Study 1b: typed requests", "With minus without brand names\n(points)", 1),
          ("study1c-store-gap-plain", "Study 1c: the store's plain listing",
           "With minus without brand names\n(points)", 1),
          ("study2a", "Study 2a: experience attributes stated",
           "Change with them stated\n(points; below zero: smaller effect)", 1),
          # each piece of information alone (the former Study 2b) went to the Web Appendix under the argument map, and
          # the main text's Study 2b is the former Study 2c (its heterogeneity file is still named study2c)
          ("study2c", "Study 2b: the same price", "Familiar minus fictitious product\n(points)", -1)]


def fig_models_across():
    """Each study's per-model estimates against the model's release date, open and closed weights apart. The rows are
    rebuilt with heterogeneity.py's own read_input and the arguments stored in each study's numbers.json, so the figure
    draws exactly the estimates that the spread was computed from; the per-year and open-against-closed coefficients are
    read from the same file. A model with no release date in model_characteristics.csv is drawn in a strip of its own."""
    import types
    from datetime import date
    sys.path.insert(0, str(JMR / "predictors"))
    import heterogeneity as H
    chars = {}
    for f in F_CHARS:
        with open(f, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                chars.setdefault(r["key"], r)

    def year(s):
        dd = date.fromisoformat(s)
        return dd.year + (dd.timetuple().tm_yday - 1) / 365.25

    fig, axes = plt.subplots(3, 2, figsize=(6.5, 7.4))
    fig.subplots_adjust(left=0.1, right=0.985, top=0.93, bottom=0.1, hspace=0.75, wspace=0.28)
    sources, counts, undated_all = [], [], set()
    for ax in list(axes.flat)[len(ACROSS):]:   # an empty slot when there are fewer results than panels
        ax.axis("off")
    for ax, (study, title, ylabel, sign) in zip(axes.flat, ACROSS):
        n = load(F_HET / study / "numbers.json")
        a = types.SimpleNamespace(**n["args"])
        a.input = str(REPO / n["input"]["file"])
        a.filter, a.scale = n["input"]["filter"], n["input"]["scale"]
        for k in ("se_col", "low_col", "high_col", "reason_col", "reliability_col"):
            if not hasattr(a, k):
                setattr(a, k, None)
        if not hasattr(a, "reliability_min"):
            a.reliability_min = 0.5
        keys, y, se, lows, highs = H.read_input(a)
        assert len(keys) == n["result"]["models"], f"{study}: {len(keys)} rows against {n['result']['models']}"
        assert all(k in chars for k in keys), f"{study}: a model without characteristics"
        dated = [year(chars[k]["release_date"]) for k in keys if chars[k].get("release_date")]
        d0, d1 = float(int(min(dated))), max(dated)   # from the January of the earliest release (2024 on these files)
        strip = d1 + 0.12 * (d1 - d0) + 0.25
        undated = 0
        for k, est, lo, hi in zip(keys, y, lows or [None] * len(keys), highs or [None] * len(keys)):
            if lo is None:
                lo, hi = est - 1.96 * se[keys.index(k)], est + 1.96 * se[keys.index(k)]
            est, lo, hi = sign * est, min(sign * lo, sign * hi), max(sign * lo, sign * hi)
            rd = chars[k].get("release_date")
            if rd:
                x = year(rd)
            else:
                undated += 1
                undated_all.add(k)
                x = strip + 0.05 * ((undated % 5) - 2)
            is_open = chars[k]["open"] == "open"
            dot(ax, x, est, lo, hi, color=MARK if is_open else MARK2, size=3.4, marker="o" if is_open else "s",
                horizontal=False)
        ax.axhline(0, color=ZERO, linewidth=0.8, zorder=1.8)
        if undated:
            ax.axvline((d1 + strip) / 2, color=LINE, linewidth=0.6, linestyle=(0, (2, 2)), zorder=1)
        ticks = list(range(int(d0) + 1 if d0 % 1 > 0.5 else int(d0), int(d1) + 1))
        ax.set_xticks(ticks + ([strip] if undated else []))
        ax.set_xticklabels([str(t) for t in ticks] + (["No date"] if undated else []))
        ax.set_xlim(d0 - 0.1, (strip if undated else d1) + 0.35)
        mods = n["result"]["moderators"]
        rd_m, ow_m = mods["release date (years)"], mods["open against closed weights"]

        def p_text(p):
            s = "1.00" if p >= 0.995 else (f"{p:.2f}" if p >= 0.01 else ("< .001" if p < 0.001 else f"{p:.3f}"))
            return s.replace("0.", ".", 1) if s.startswith("0.") else s

        rd_c, ow_c = sign * rd_m["coefficient"], sign * ow_m["coefficient"]
        ax.set_title(f"{title} ({len(keys)} models)", fontsize=M, pad=27)
        ax.text(0, 1.03, f"Change per year of release: {f1(rd_c)} points (Holm P {p_text(rd_m['holm'])})\n"
                f"Open minus closed weights: {f1(ow_c)} points (Holm P {p_text(ow_m['holm'])})",
                transform=ax.transAxes, fontsize=S, ha="left", va="bottom", linespacing=1.3)
        ax.set_ylabel(ylabel, fontsize=S)
        ax.grid(axis="y", color=GRID, linewidth=0.6, zorder=0)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(axis="both", labelsize=S)
        counts.append((title, len(keys), undated))
        sources.append((f"{title}: each model's estimate and interval, {len(keys)} models", rel(REPO / n["input"]["file"]),
                        f"rows as heterogeneity.py read_input reads them with the arguments in "
                        f"{rel(F_HET / study / 'numbers.json')} (input and args)"))
        sources.append((f"{title}: per year {f1(rd_c)} (Holm P {p_text(rd_m['holm'])}), open minus "
                        f"closed {f1(ow_c)} (Holm P {p_text(ow_m['holm'])})" + (" (the file's signs times -1)" if
                                                                                 sign < 0 else ""),
                        rel(F_HET / study / "numbers.json"),
                        "result.moderators['release date (years)'] and ['open against closed weights'], .coefficient "
                        "and .holm"))
    handles = [Line2D([], [], marker="o", color=MARK, linestyle="none", markersize=4, label="Open weights"),
               Line2D([], [], marker="s", color=MARK2, linestyle="none", markersize=4, label="Closed weights"),
               Line2D([], [], marker="o", color=INK, markerfacecolor="white", linestyle="none", markersize=4,
                      label="Interval includes zero")]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=S, bbox_to_anchor=(0.5, 0.0))
    fig.text(0.5, 0.045, "Release date", ha="center", fontsize=M)
    save(fig, "fig_models_across")
    sources.append(("release dates and open or closed weights", rel(F_CHARS[0]), "release_date, open (and the _open file)"))
    n_undated = len(undated_all)
    return {
        "name": "fig_models_across", "number": "Not placed (how the models differed)",
        "title": "Newer Models Show a Larger Effect of a Fictitious Name",
        "body": ("Each panel is one result whose spread between models we report, and each mark is one "
                 "model's estimate with its 95% interval, placed at the model's release date; circles are models "
                 "with open weights and squares models with closed weights, and a hollow mark has an interval that "
                 "includes zero. In every panel a higher value means a larger advantage of the familiar brand: in "
                 "Study 2b the value is the familiar product's share minus the fictitious product's at the same "
                 "price, and in Study 2a a value below zero means that stating the experience attributes made the "
                 "effect smaller. Above each panel are the number of models and two approximate tests that treat the "
                 "models as independent: the change in the estimate for each year of release and the difference "
                 "between models with open and closed weights, each with its Holm-corrected P across a model's six "
                 "features. "
                 + (f"{n_undated} models have no release date in the table of model features; they are drawn apart, "
                    "under \"No date\", and the per-year test leaves them out. " if n_undated else
                    "Each release date is the developer's announcement or the creation of its repository. ")
                 + "Panels: " + "; ".join(f"{t}, {k} models" + (f" ({u} without a date)" if u else "")
                                          for t, k, u in counts) + "."),
        "sources": sources,
        "waits": [],
        "note": "A draft; the manuscript gives its number.",
    }



def _settings_entry(name, number, caption_file):
    """A figure drawn by fig_settings.py: its caption paragraph is read from caption_file (the paragraph that
    opens with 'Figure N.' or 'Web Appendix Figure W.'), so that CAPTIONS.md and FIGURES.pdf show it with the others."""
    import re as _re
    text = (HERE / caption_file).read_text(encoding="utf-8")
    m = _re.search(r"^(?:Web Appendix )?Figure [NW]\. (.+?)(?:\n\s*\n|\Z)", text, _re.S | _re.M)
    if not m:
        raise ValueError(f"{caption_file}: no caption paragraph opening with 'Figure N.' or 'Web Appendix Figure W.'")
    para = " ".join(m.group(1).split())
    title, body = para.split(". ", 1)
    for f in (f"{name}.pdf", f"{name}.png"):
        if not (HERE / f).exists():
            raise FileNotFoundError(f"{f} is missing; run jmr-2026/figures/fig_settings.py")
    return {"name": name, "number": number, "title": title, "body": body,
            "sources": [("every message line", "", "ITEMS (read from the items by id); "
                         "the two model outputs in settings_sources.json")],
            "waits": [], "note": f"Drawn and captioned by figures/fig_settings.py ({caption_file}); run it again "
                                 "after COVERAGE.json changes."}


def fig_settings_main():
    return _settings_entry("fig_settings", "Web Appendix Figure (Study 1c, settings)", "fig_settings_caption.md")


def fig_settings_wa():
    return _settings_entry("wa_fig_settings", "Web Appendix Figure W", "wa_fig_settings_caption.md")


FIGURES = [fig_example_table_entry, fig_pyramid, fig_model, fig_study1_shares, fig_study1_models, fig_settings_main,
           fig_study2_split, fig_study2_price, fig_study2_audit, fig_study3_pages, fig_study3_stages, fig_study4, fig_settings_wa,
           fig_dollar, fig_models_across]
if dollar_groups_ready():
    FIGURES.append(fig_dollar_groups)
STUDY = {"Figure 1": "Conceptual development", "Figure 2": "Study 1a", "Figure 3": "Study 1b", "Figure 4": "Study 2b",
         "Figure 5": "Study 3a",
         "Web Appendix Figure (Study 1a, an example table)": "Web Appendix, Study 1a's tables",
         "Web Appendix Figure (conceptual development, the pyramid)": "Web Appendix, the conceptual development",
         "Web Appendix Figure (Study 1c, settings)": "Web Appendix, Study 1c",
         "Web Appendix Figure (Study 2b, price)": "Web Appendix, Study 2b",
         "Web Appendix Figure (Study 3b, the machine brand audit)": "Web Appendix, Study 3b",
         "Web Appendix Figure (Study 3, training stages)": "Web Appendix, Study 3",
         "Web Appendix Figure W": "Web Appendix",
         "Not placed (each piece of information alone)": "not placed",
         "Not placed (Study 4)": "not placed",
         "Not placed (each Claude model's dollars)": "not placed",
         "Not placed (how the models differed)": "not placed"}


def caption(r):
    return f"{r['number']}. {r['title']}. {r['body']}"


def write_captions(results):
    lines = ["# Captions of the main-text figures", "",
             "Written by jmr-2026/figures/main_figures.py from the same numbers that it draws; do not edit by hand. "
             "Each figure is in this folder as a PDF and as a PNG at 200 dpi, and FIGURES.pdf shows each one with "
             "its caption. The figure numbers follow the four studies (ROADMAP.json framework.structure); the "
             "manuscript sets the final numbers.", ""]
    for r in results:
        lines += [f"## {r['number']} ({STUDY[r['number']]}): {r['name']}.pdf", "", caption(r), ""]
        lines.append("Status: " + ("complete." if not r["waits"] else "drawn as far as the data go."))
        for w in r["waits"]:
            lines.append(f"- Waits: {w}")
        if r["note"]:
            lines += ["", f"Note: {r['note']}"]
        if r["sources"]:
            lines += ["", "Numbers shown, with the file and key each came from:", ""]
            for shown, path, key in r["sources"]:
                lines.append(f"- {shown}: `{path}`, `{key}`")
        lines.append("")
    (HERE / "CAPTIONS.md").write_text("\n".join(lines), encoding="utf-8")


def write_contact_sheet(results):
    with PdfPages(HERE / "FIGURES.pdf") as pdf:
        page = plt.figure(figsize=(8.5, 11))
        page.text(0.08, 0.93, "Machine-Based Brand Equity: the main-text figures for review", fontsize=14,
                  fontweight="semibold", color=INK)
        page.text(0.08, 0.905, "Each figure is on its own page with its caption below it. Built by "
                  "", fontsize=9, color=MUTED)
        y = 0.86
        for r in results:
            status = "complete" if not r["waits"] else "drawn as far as the data go; waits for data"
            page.text(0.08, y, f"{r['number']} ({STUDY[r['number']]})", fontsize=9.5, fontweight="semibold",
                      color=INK, va="top")
            page.text(0.27, y, textwrap.fill(f"{r['title']}. Status: {status}.", 92), fontsize=8.6, color=INK,
                      va="top")
            y -= 0.055
        pdf.savefig(page)
        plt.close(page)
        for r in results:
            img = plt.imread(HERE / f"{r['name']}.png")
            h_px, w_px = img.shape[:2]
            w_in = w_px / 200
            h_in = h_px / 200
            page = plt.figure(figsize=(8.5, 11))
            top = 0.94
            left = (8.5 - w_in) / 2 / 8.5
            height = h_in / 11
            ax = page.add_axes([left, top - height, w_in / 8.5, height])
            ax.imshow(img, interpolation="lanczos")
            ax.axis("off")
            page.text(0.08, 0.965, f"{r['name']}.pdf", fontsize=8, color=MUTED)
            text = textwrap.fill(caption(r), 112)
            if r["waits"]:
                text += "\n\n" + "\n".join(textwrap.fill("Waits: " + w, 112) for w in r["waits"])
            page.text(0.08, top - height - 0.025, text, fontsize=8.4, color=INK, va="top", linespacing=1.35)
            pdf.savefig(page)
            plt.close(page)


def reader_word_check(results):
    """No word of the project's own machinery in what a reader sees (reader_words.py): every figure's PDF text (its
    labels, legends, titles and notes) and every caption's title and body. Returns the problems found."""
    import pymupdf as fitz
    import reader_words
    out = []
    for r in results:
        text = " ".join(page.get_text() for page in fitz.open(HERE / f"{r['name']}.pdf"))
        for where, t in (("figure", text), ("caption", f"{r['title']}. {r['body']}")):
            for word, why in reader_words.find(t):
                out.append(f"{r['name']} ({where}): '{word}', {why}")
    return out


def build():
    HERE.mkdir(parents=True, exist_ok=True)
    results = [f() for f in FIGURES]
    problems = reader_word_check(results)
    if problems:
        raise SystemExit("REFUSED: words of our own machinery where a reader sees them:\n  " + "\n  ".join(problems))
    write_captions(results)
    write_contact_sheet(results)
    return [r["name"] for r in results]


if __name__ == "__main__":
    print(build())
