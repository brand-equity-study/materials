"""Figures 1 and 2 of the JMR paper (the pyramid and the conceptual model), drawn as SVG in points (468 points = 6.5
inches) and printed by Chrome to a vector PDF and a 200 dpi PNG. Every number in them is read from a results file.

Schematic rules (nature-figure's vector-schematic-style-rules.md, read on 21 November 2026): one typeface (Fira Sans)
in three sizes; all text in one dark ink, white only on the one dark accent; one accent; pale or white fills; every
directed edge with an arrowhead; dashed lines carry one meaning (not measured); no line passes through a label.
"""
import json
import textwrap
from pathlib import Path

CODE = Path(__file__).resolve().parent   # the figure and table code
PKG = CODE.parents[1]   # the package
REPO = JMR = PKG   # the names that the code gives the top folder
HERE = PKG / "exhibits" / "results" / "figures"   # where the figures are written
HERE.mkdir(parents=True, exist_ok=True)
F_SPLIT = PKG / "study2a-experience-attributes-stated-for-every-product/results/all-models/numbers.json"     # Study 2b over every model (pool_all.py)
F_AUDIT = PKG / "study3b-brand-knowledge-and-training-text-in-released-models/results/audit/numbers-all.json"             # Study 2d over every model that answered
import os  # noqa: E402
FONT_DIR = Path(os.environ.get("FIRA_DIR", PKG / "exhibits" / "fonts"))   # Fira Sans

ACCENT = "#134961"      # batlow at 0.15, the figures' main colour
INK = "#1F2A36"
LINE = "#B9C1C9"
PALE = "#EAEEF1"
PALER = "#F5F7F9"
S, M, L = 6.5, 7.5, 8.5  # the three type sizes, in points

AUDIT_JS = """() => {
  const svg = document.querySelector('svg'); const vb = svg.viewBox.baseVal; const out = [];
  const T = [...svg.querySelectorAll('text')].map(t => ({t, b: t.getBBox(), s: t.textContent}));
  for (const a of T) {
    const b = a.b;
    if (b.x < vb.x - 0.3 || b.y < vb.y - 0.3 || b.x + b.width > vb.x + vb.width + 0.3 || b.y + b.height > vb.y + vb.height + 0.3)
      out.push('outside the page: ' + a.s);
    const lo = a.t.dataset.xmin, hi = a.t.dataset.xmax;
    if (lo !== undefined && (b.x < +lo || b.x + b.width > +hi)) out.push('wider than its shape: ' + a.s);
  }
  for (let i = 0; i < T.length; i++) for (let j = i + 1; j < T.length; j++) {
    const a = T[i].b, c = T[j].b;
    if (a.x < c.x + c.width - 0.3 && c.x < a.x + a.width - 0.3 && a.y < c.y + c.height - 1.0 && c.y < a.y + a.height - 1.0)
      out.push('overlap: ' + T[i].s + ' / ' + T[j].s);
  }
  for (const e of svg.querySelectorAll('.edge')) {
    const n = e.getTotalLength();
    for (let d = 0; d <= n; d += 0.5) {
      const p = e.getPointAtLength(d);
      for (const a of T) { const b = a.b;
        if (p.x > b.x && p.x < b.x + b.width && p.y > b.y + 0.8 && p.y < b.y + b.height - 0.8) out.push('a line crosses: ' + a.s); }
    }
  }
  const R = el => el.getBBox();
  for (const t of svg.querySelectorAll('.tag')) for (const b of svg.querySelectorAll('.box')) {
    const p = R(t), q = R(b);
    if (p.x < q.x + q.width + 1.5 && q.x < p.x + p.width + 1.5 && p.y < q.y + q.height + 1.5 && q.y < p.y + p.height + 1.5)
      out.push('a tag touches a box: ' + t.nextElementSibling.textContent);
  }
  if (!document.fonts.check('7.5px "Fira Sans"')) out.push('Fira Sans did not load');
  return [...new Set(out)];
}"""


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def rel(path):
    return Path(path).resolve().relative_to(REPO).as_posix()


def f1(x):
    s = f"{x:.1f}"
    return "0.0" if s == "-0.0" else s.replace("-", "\u2212")


def t1(x):
    s = f"{x:.1f}"
    return "0.0" if s == "-0.0" else s


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=M, weight=400, anchor="middle", fill=INK, xmin=None, xmax=None):
    fit = "" if xmin is None else f' data-xmin="{xmin:.2f}" data-xmax="{xmax:.2f}"'
    return (f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" '
            f'fill="{fill}"{fit}>{esc(s)}</text>')


def truetype(name):
    """Fira Sans ships as OpenType with CFF outlines, which Chrome's PDF writer embeds as Type 3 fonts (journals
    refuse those). The cubic outlines are converted once to quadratic TrueType outlines (fontTools' otf2ttf script),
    which Chrome embeds as CID TrueType fonts."""
    import tempfile
    from fontTools.pens.cu2quPen import Cu2QuPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.ttLib import TTFont, newTable
    out = Path(tempfile.gettempdir()) / "fira-truetype" / f"{name}.ttf"
    if out.exists():
        return out
    out.parent.mkdir(exist_ok=True)
    font = TTFont(FONT_DIR / f"{name}.otf")
    order = font.getGlyphOrder()
    gs = font.getGlyphSet()
    quad = {}
    for g in order:
        pen = TTGlyphPen(gs)
        gs[g].draw(Cu2QuPen(pen, 1.0, reverse_direction=True))
        quad[g] = pen.glyph()
    font["loca"] = newTable("loca")
    font["glyf"] = glyf = newTable("glyf")
    glyf.glyphOrder = order
    glyf.glyphs = quad
    del font["CFF "]
    glyf.compile(font)
    for g, glyph in glyf.glyphs.items():
        if hasattr(glyph, "xMin"):
            font["hmtx"][g] = (font["hmtx"][g][0], glyph.xMin)
    font["maxp"] = maxp = newTable("maxp")
    maxp.tableVersion = 0x00010000
    for k in ("maxZones", "maxTwilightPoints", "maxStorage", "maxFunctionDefs", "maxInstructionDefs",
              "maxStackElements", "maxSizeOfInstructions", "maxComponentElements"):
        setattr(maxp, k, 1 if k == "maxZones" else 0)
    font["post"].formatType = 2.0
    font["post"].extraNames = []
    font["post"].mapping = {}
    font["post"].glyphOrder = order
    font.sfntVersion = "\000\001\000\000"
    font.save(out)
    return out


def page(svg_body, w_pt, h_pt):
    w_in, h_in = w_pt / 72, h_pt / 72
    reg = truetype("FiraSans-Regular").as_uri()
    semi = truetype("FiraSans-SemiBold").as_uri()
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: "Fira Sans"; src: url("{reg}"); font-weight: 400; }}
@font-face {{ font-family: "Fira Sans"; src: url("{semi}"); font-weight: 600; }}
@page {{ size: {w_in}in {h_in}in; margin: 0; }}
html, body {{ margin: 0; padding: 0; background: #ffffff; }}
svg {{ display: block; width: {w_in}in; height: {h_in}in; }}
text {{ font-family: "Fira Sans"; font-feature-settings: "tnum" 1, "lnum" 1; }}
</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_pt} {h_pt}">
<defs><marker id="head" viewBox="0 0 8 8" refX="7.2" refY="4" markerWidth="6.2" markerHeight="6.2" orient="auto">
<path d="M0,0.6 L7.6,4 L0,7.4 Z" fill="{INK}"/></marker></defs>
{svg_body}
</svg></body></html>"""


def render(name, html, w_pt, h_pt):
    """Write the page, refuse it on any collision, then print it to PDF and capture it at 200 dpi."""
    from playwright.sync_api import sync_playwright
    src = HERE / "diagrams" / f"{name}.html"
    src.parent.mkdir(exist_ok=True)
    src.write_text(html, encoding="utf-8")
    w_px, h_px = round(w_pt / 72 * 96), round(h_pt / 72 * 96)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        pg = browser.new_page(viewport={"width": w_px, "height": h_px}, device_scale_factor=200 / 96)
        pg.goto(src.as_uri())
        pg.evaluate("document.fonts.ready.then(() => true)")
        problems = pg.evaluate(AUDIT_JS)
        if problems:
            browser.close()
            raise AssertionError(f"{name}: " + "; ".join(problems))
        pg.screenshot(path=str(HERE / f"{name}.tmp.png"), clip={"x": 0, "y": 0, "width": w_px, "height": h_px})
        pg.pdf(path=str(HERE / f"{name}.tmp.pdf"), width=f"{w_pt / 72}in", height=f"{h_pt / 72}in",
               print_background=True, margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        browser.close()
    import pymupdf
    doc = pymupdf.open(HERE / f"{name}.tmp.pdf")
    kinds = {f[2] for f in doc[0].get_fonts()}
    sizes = [s["size"] for b in doc[0].get_text("dict")["blocks"] for ln in b.get("lines", []) for s in ln["spans"]
             if s["text"].strip()]
    pages, width = len(doc), doc[0].rect.width
    doc.close()
    assert pages == 1 and abs(width - w_pt) < 0.5, f"{name}: {pages} pages, {width} pt wide"
    assert "Type3" not in kinds, f"{name}: Type 3 fonts in the PDF ({kinds})"
    assert min(sizes) >= 6.0 - 0.05, f"{name}: text at {min(sizes)} pt"
    for ext in ("png", "pdf"):
        replace_when_free(HERE / f"{name}.tmp.{ext}", HERE / f"{name}.{ext}")


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


# ---------------------------------------------------------------------------------------------------------------
# Figure 1: Keller's pyramid beside the machine version, with what the studies found
# ---------------------------------------------------------------------------------------------------------------

def fig_pyramid():
    s2b = load(F_SPLIT)["2b"]
    s2a = load(F_SPLIT)["2a"]
    n_2a = len(s2a["models"])
    n_au = len(load(F_AUDIT)["models"])
    p2a = s2a["pooled"]
    gap_none, gap_stated = 100 * p2a["gap_none"]["estimate"], 100 * p2a["gap_supplied"]["estimate"]
    change, change_ci, change_p = (100 * p2a["change"]["estimate"], [100 * v for v in p2a["change"]["ci95"]],
                                   p2a["change"]["p_two_sided"])
    audit = load(F_AUDIT)
    r2_name = 100 * audit["exploratory"]["invented_benchmark"]["r2"]["est"]
    r2_all = 100 * audit["test3"]["r2"]["est"]
    fam = audit["test1_familiar"]
    # the measures of the two levels above awareness (image: typicality, tone; judgments: inferred quality,
    # credibility); salience and recognition belong to awareness, the base
    forest = [("typicality", "Typicality"), ("tone", "Tone"), ("quality", "Inferred quality"),
              ("credibility", "Credibility")]
    # Holm over the six measures among familiar brands, as the analysis plan corrects test 1 (the manuscript's
    # auholm table gives the same values)
    six = ["salience", "recognition", "typicality", "tone", "quality", "credibility"]
    order = sorted(six, key=lambda k: fam[k]["p"])
    holm, run_max = {}, 0.0
    for i, k in enumerate(order):
        run_max = max(run_max, min(1.0, (len(six) - i) * fam[k]["p"]))
        holm[k] = run_max
    excl = [lab for k, lab in forest if fam[k]["lo"] > 0 or fam[k]["hi"] < 0]
    holm_ok = [lab for k, lab in forest if holm[k] < 0.05 and fam[k]["lo"] > 0]

    W, H = 468, 272
    y_top, y_bot, gap, base_w, top_w = 30.0, 266.0, 3.5, 146.0, 42.0
    h = (y_bot - y_top - 3 * gap) / 4

    def hw(y):
        return (top_w + (base_w - top_w) * (y - y_top) / (y_bot - y_top)) / 2

    def span(cx, baseline, size, pad=2.0, side=None):
        """The horizontal room inside the pyramid at the top of a line of text (its narrowest point)."""
        half = hw(baseline - 0.78 * size)
        if side == "left":
            return cx - half + pad, cx - 1.6 - pad
        if side == "right":
            return cx + 1.6 + pad, cx + half - pad
        return cx - half + pad, cx + half - pad

    def tier(i):
        b = y_bot - i * (h + gap)
        return b - h, b

    def trap(cx, a, b, fill, stroke="none", dash=None, side=None, sw=0.75):
        if side is None:
            pts = [(cx - hw(a), a), (cx + hw(a), a), (cx + hw(b), b), (cx - hw(b), b)]
        elif side == "left":
            pts = [(cx - hw(a), a), (cx - 1.6, a), (cx - 1.6, b), (cx - hw(b), b)]
        else:
            pts = [(cx + 1.6, a), (cx + hw(a), a), (cx + hw(b), b), (cx + 1.6, b)]
        d = f' stroke-dasharray="{dash}"' if dash else ""
        return (f'<polygon points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in pts)}" fill="{fill}" stroke="{stroke}" '
                f'stroke-width="{sw}" stroke-linejoin="round"{d}/>')

    out = []
    kx, mx, x0 = 74.0, 230.0, 318.0
    # Keller's pyramid: pale fills, no outline
    for i, names in enumerate((["Salience"], ["Performance", "Imagery"], ["Judgments", "Feelings"], ["Resonance"])):
        a, b = tier(i)
        ym = (a + b) / 2 + 2.6
        if len(names) == 1:
            out.append(trap(kx, a, b, PALE))
            lo_, hi_ = span(kx, ym, M)
            out.append(text(kx, ym, names[0], M, xmin=lo_, xmax=hi_))
        else:
            out.append(trap(kx, a, b, PALE, side="left"))
            out.append(trap(kx, a, b, PALE, side="right"))
            for nm, side in zip(names, ("left", "right")):
                lo_, hi_ = span(kx, ym, S, pad=1.0, side=side)
                out.append(text((lo_ + hi_) / 2, ym, nm, S, xmin=lo_, xmax=hi_))
    # the machine version: the base in the accent (it does most of the work), the next two white with an outline (they
    # do not rank known brands), the top dashed (not measured)
    tiers = [("Awareness", ["recognition and recall"], ACCENT, "none", None, "#ffffff"),
             ("Image", ["typicality, tone"], "#ffffff", INK, None, INK),
             ("Judgments", ["inferred quality,", "credibility"], "#ffffff", INK, None, INK),
             ("Resonance", ["not measured"], "#ffffff", "#8C969F", "2.2,1.8", INK)]
    for i, (name, subs, fill, stroke, dash, ink) in enumerate(tiers):
        a, b = tier(i)
        ym = (a + b) / 2 - 4.0 * (len(subs) - 1)
        out.append(trap(mx, a, b, fill, stroke, dash))
        lo_, hi_ = span(mx, ym - 1.2, M)
        out.append(text(mx, ym - 1.2, name, M, 600 if i == 0 else 400, fill=ink, xmin=lo_, xmax=hi_))
        for k, sub in enumerate(subs):
            y = ym + 8.6 + 8.2 * k
            lo_, hi_ = span(mx, y, S)
            out.append(text(mx, y, sub, S, fill=ink, xmin=lo_, xmax=hi_))
    out.append(text(kx, 13, "Consumers: Keller's pyramid", L, 600))
    out.append(text(mx, 13, "AI assistants: the machine version", L, 600))
    out.append(text(x0, 13, "What the studies found", L, 600, anchor="start"))

    def edge(x1, y1, x2, y2):
        return (f'<path class="edge" d="M{x1:.2f},{y1:.2f} L{x2:.2f},{y2:.2f}" stroke="{LINE}" stroke-width="0.7" '
                f'fill="none"/>')

    def bars(y, rows, top, unit):
        """rows: (label, value); a bar per row on a scale from 0 to top, the value printed at its end."""
        g = []
        for k, (lab, v) in enumerate(rows):
            yy = y + k * 9.0
            g.append(text(x0 + 62, yy + 2.3, lab, S, anchor="end"))
            g.append(f'<rect x="{x0 + 66:.2f}" y="{yy - 2.6:.2f}" width="{58 * v / top:.2f}" height="5.2" '
                     f'fill="{ACCENT}"/>')
            g.append(text(x0 + 66 + 58 * v / top + 3, yy + 2.3, f"{f1(v)}{unit}", S, anchor="start"))
        return g

    # the base: does most of the work
    a, b = tier(0)
    ym = (a + b) / 2
    out.append(edge(mx + hw(ym) + 4, ym, x0 - 6, ym))
    # plain labels over the numbers (22 November 2026): the headings were claims typed into this script, which the
    # results over every model no longer matched in the same words
    out.append(text(x0, a + 12, "Awareness (Study 3b)", M, 600, anchor="start"))
    out.append(text(x0, a + 22, "Share of the difference explained (R\u00b2)", S, anchor="start"))
    top = 5 * (max(r2_name, r2_all) // 5 + 1)
    out += bars(a + 33, [("Fictitious name alone", r2_name), ("All six measures", r2_all)], top, "%")
    # the two levels above it: a bracket, then two findings
    a1, b1 = tier(1)
    a2, b2 = tier(2)
    y1, y2 = (a1 + b1) / 2, (a2 + b2) / 2
    bx = x0 - 6
    out.append(edge(mx + hw(y2) + 4, y2, bx, y2))
    out.append(edge(mx + hw(y1) + 4, y1, bx, y1))
    out.append(edge(bx, y2, bx, y1))
    yy = a2 - 4
    out.append(text(x0, yy + 8, "Image and judgments (Study 3b)", M, 600, anchor="start"))
    out.append(text(x0, yy + 18, "Familiar brands only: points per SD", S, anchor="start"))
    lo = min(fam[k]["lo"] for k, _ in forest)
    hi = max(fam[k]["hi"] for k, _ in forest)
    s_lo, s_hi = 2 * (lo // 2), 2 * (hi // 2 + 1)

    def sx(v):
        return x0 + 66 + 72 * (v - s_lo) / (s_hi - s_lo)

    fy = yy + 29
    for k, (key, lab) in enumerate(forest):
        ry = fy + k * 8.2
        v = fam[key]
        out.append(text(x0 + 62, ry + 2.3, lab, S, anchor="end"))
        out.append(f'<line x1="{sx(v["lo"]):.2f}" y1="{ry:.2f}" x2="{sx(v["hi"]):.2f}" y2="{ry:.2f}" '
                   f'stroke="{ACCENT}" stroke-width="1.1"/>')
        filled = v["lo"] > 0 or v["hi"] < 0     # the house code: filled when the 95% interval excludes zero
        out.append(f'<circle cx="{sx(v["est"]):.2f}" cy="{ry:.2f}" r="1.75" fill="{ACCENT if filled else "#ffffff"}" '
                   f'stroke="{ACCENT}" stroke-width="0.9"/>')
    zero_top, zero_bot = fy - 4.2, fy + (len(forest) - 1) * 8.2 + 4.2
    out.append(f'<line x1="{sx(0):.2f}" y1="{zero_top:.2f}" x2="{sx(0):.2f}" y2="{zero_bot:.2f}" stroke="#56616B" '
               f'stroke-width="0.6"/>')
    for t in range(int(s_lo), int(s_hi) + 1, 2):
        out.append(f'<line x1="{sx(t):.2f}" y1="{zero_bot:.2f}" x2="{sx(t):.2f}" y2="{zero_bot + 2:.2f}" '
                   f'stroke="#8C969F" stroke-width="0.5"/>')
        out.append(text(sx(t), zero_bot + 8.6, f1(t).replace(".0", ""), S))
    yb = zero_bot + 20
    out.append(text(x0, yb, "Experience attributes (Study 2a)", M, 600, anchor="start"))
    out.append(text(x0, yb + 10, "Effect of the fictitious name, points", S, anchor="start"))
    top = 5 * (gap_none // 5 + 1)
    out += bars(yb + 21, [("Not stated", gap_none), ("Stated", gap_stated)], top, "")
    # the top: not measured
    a3, b3 = tier(3)
    y3 = (a3 + b3) / 2
    out.append(edge(mx + hw(y3) + 4, y3, x0 - 6, y3))
    out.append(text(x0, y3 + 2.6, "No counterpart measured", M, anchor="start"))
    assert yb + 21 + 9 + 4 < b1 + 6, "the findings run past the image level"

    render("fig1_pyramid", page("\n".join(out), W, H), W, H)
    a_rel, s_rel = rel(F_AUDIT), rel(F_SPLIT)
    sources = [(f"{f1(r2_name)}%", a_rel, "exploratory.invented_benchmark.r2.est (x 100)"),
               (f"{f1(r2_all)}%", a_rel, "test3.r2.est (x 100)")]
    sources += [(f"{lab}: {t1(fam[k]['est'])} ({t1(fam[k]['lo'])} to {t1(fam[k]['hi'])}), drawn", a_rel,
                 f"test1_familiar.{k}.est, .lo and .hi") for k, lab in forest]
    sources += [(f1(gap_none), s_rel, "2a.pooled.gap_none.estimate (x 100)"),
                (f1(gap_stated), s_rel, "2a.pooled.gap_supplied.estimate (x 100)"),
                (f"change {t1(change)} ({t1(change_ci[0])} to {t1(change_ci[1])}), P {change_p:.3f} (caption)", s_rel,
                 "2a.pooled.change.estimate, .ci95 and .p_two_sided (x 100)"),
                (f"Holm P over the six measures among familiar brands (caption), computed from", a_rel,
                 "test1_familiar.<measure>.p")]

    def names(xs):
        return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]

    if not excl:
        fam_text = "each interval includes zero."
    else:
        fam_text = (f"the interval of {names([x.lower() for x in excl])} excludes zero"
                    + (f", and after Holm correction across the six measures none is reliable (smallest P = "
                       f"{min(holm[k] for k, _ in forest):.2f})." if not holm_ok else
                       f", and after Holm correction across the six measures {names(holm_ok)} remains reliable."))
    p_text = "P < .001" if change_p < 0.001 else f"P = {change_p:.3f}".replace("0.", ".", 1)
    most = "most of what" if r2_name >= 0.5 * r2_all else "part of what"
    return {
        "name": "fig1_pyramid", "number": "Web Appendix Figure (conceptual development, the pyramid)",
        "title": "Machine Brand Awareness and Image Explain Little of a Brand's Equity in the Models",
        "body": ("The left pyramid is Keller's (2001) brand resonance pyramid for consumers. The middle pyramid has "
                 "the same levels for an AI assistant: awareness at the base, image and judgments above it, and "
                 "resonance at the top, which we did not measure. The base is filled because whether a brand's name "
                 f"is fictitious explains {most} the six measures of the machine brand audit explain together. The "
                 "results for each level over all models are in the right column. At the base, whether a name is "
                 f"fictitious explains {t1(r2_name)}% of the variance in a brand's equity, and the six measures "
                 f"together explain {t1(r2_all)}% (Study 3b, {n_au} models). For image and judgments, "
                 "the four intervals are the slopes of equity on each measure among familiar brands, in percentage "
                 f"points per standard deviation; {fam_text} For the experience attributes, the bars are the effect "
                 f"of the fictitious name without them ({t1(gap_none)} points) and with them stated for every product "
                 f"({t1(gap_stated)} points), over the {n_2a} models of Study 2a, so the effect was attenuated by "
                 f"{t1(-change)} points (95% CI {t1(-change_ci[1])} to {t1(-change_ci[0])}, {p_text})."),
        "sources": sources,
        "waits": [],
        "note": ("The citation of the pyramid is to be checked: the outline (writing/OUTLINE-1121.md, Part D of the "
                 "citation map) says that Keller (2001) is a working paper and that the pyramid is printed in "
                 "Keller's book Strategic Brand Management; the manuscript cites one checked edition."),
    }


# ---------------------------------------------------------------------------------------------------------------
# Figure 2: the conceptual model, with the study that tests each arrow
# ---------------------------------------------------------------------------------------------------------------

def fig_model_causal():
    W, H = 468, 214
    yc = 120.0
    out = []

    def box(x, y, w, h, fill="#ffffff", stroke=LINE, sw=0.75, r=4):
        return (f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="{sw}"/>')

    def lines(cx, y, rows, size, xmin, xmax, weight=400, step=9.0):
        return [text(cx, y + k * step, r, size, weight, xmin=xmin, xmax=xmax) for k, r in enumerate(rows)]

    def arrow(x1, y1, x2, y2):
        return (f'<path class="edge" d="M{x1},{y1} L{x2},{y2}" stroke="{INK}" stroke-width="0.9" fill="none" '
                f'marker-end="url(#head)"/>')

    def tag(cx, cy, s):
        w = 3.55 * len(s) + 9
        return (f'<rect class="tag" x="{cx - w / 2:.2f}" y="{cy - 6.2:.2f}" width="{w:.2f}" height="12.4" rx="6.2" '
                f'fill="{ACCENT}"/>' + text(cx, cy + 2.3, s, S, 600, fill="#ffffff"))

    # training text
    out.append(box(4, 94, 72, 52, fill=PALE, stroke="none"))
    out += lines(40, 113, ["Training text"], M, 5, 75)
    out += lines(40, 126, ["pages about a brand,", "stages of training"], S, 6, 74)
    # machine brand knowledge (the container), with awareness and image
    cx = 185.0
    out.append(box(132, 54, 106, 134, fill=PALER, stroke=INK, sw=0.75, r=5))
    out += lines(cx, 69, ["Machine brand knowledge"], M, 133, 237, weight=600)
    out.append(box(141, 80, 88, 46))
    out += lines(cx, 96, ["Awareness"], M, 142, 228)
    out += lines(cx, 108, ["does the model", "know the brand?"], S, 143, 227)
    out.append(box(141, 134, 88, 44))
    out += lines(cx, 150, ["Image"], M, 142, 228)
    out += lines(cx, 162, ["what the name", "is linked to"], S, 143, 227)
    # information in the listing at answer time
    mid = 267.0
    out.append(box(mid - 88, 6, 176, 31, fill=PALE, stroke="none"))
    out += lines(mid, 19, ["Information in the listing at answer time"], M, mid - 87, mid + 87)
    out += lines(mid, 30, ["warranty, failure rate, lab testing, returns, price"], S, mid - 86, mid + 86)
    # the recommendation and people's choices
    out.append(box(296, 94, 70, 52, stroke=INK, sw=1.1))
    out += lines(331, 113, ["Recommendation"], M, 297, 365)
    out += lines(331, 126, ["names shown", "against hidden"], S, 298, 364)
    out.append(box(406, 94, 58, 52, fill=PALE, stroke="none"))
    out += lines(435, 109, ["People's", "choices"], M, 407, 463)
    out += lines(435, 131, ["with and without", "the advice"], S, 407, 463, step=8.4)
    # the edges: the main path left to right, and the information down onto the arrow it changes
    out.append(arrow(76, yc, 131, yc))
    out.append(arrow(238, yc, 295, yc))
    out.append(arrow(366, yc, 405, yc))
    out.append(arrow(mid, 37, mid, yc - 2.2))
    out.append(f'<circle cx="{mid}" cy="{yc}" r="1.6" fill="{INK}"/>')
    # which study tests which arrow
    out.append(tag(104, yc - 12, "Study 3 \u00b7 H3"))
    out.append(tag(mid, yc + 13, "Study 1 \u00b7 H1"))
    out.append(tag(mid + 31, 66, "Study 2 \u00b7 H2"))
    out.append(tag(386, yc - 12, "Study 4"))
    out.append(tag(cx, 200, "Study 3 \u00b7 awareness or image?"))
    render("fig2_model_causal", page("\n".join(out), W, H), W, H)
    return {
        "name": "fig2_model", "number": "Figure 2",
        "title": "The Conceptual Model and the Study That Tests Each Part",
        "body": ("Training text gives a model its knowledge of a brand, which has two parts, awareness and image "
                 "(Keller 1993). At the time of the answer, that knowledge changes the recommendation of a listed "
                 "product, measured as the difference between answers with brand names shown and hidden, and the "
                 "information in the listing can replace it. People then choose with or without the "
                 "recommendation. Each tag names the study and hypothesis that test that arrow: Study 1 tests the "
                 "effect and how far it holds (H1), Study 2 tests whether supplied information replaces the name "
                 "(H2) and whether awareness or image does the work, Study 3 tests whether training text creates "
                 "the knowledge (H3), and Study 4 tests whether people follow the recommendation."),
        "sources": [],
        "waits": [],
        "note": "A diagram: it prints no number.",
    }



def fig_model_order():
    W, H = 468, 262
    yc = 96.0
    out = []

    def box(x, y, w, h, fill="#ffffff", stroke=LINE, sw=0.75, r=4):
        return (f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="{sw}"/>')

    def lines(cx, y, rows, size, xmin, xmax, weight=400, step=9.0):
        return [text(cx, y + k * step, r, size, weight, xmin=xmin, xmax=xmax) for k, r in enumerate(rows)]

    def arrow(x1, y1, x2, y2):
        return (f'<path class="edge" d="M{x1},{y1} L{x2},{y2}" stroke="{INK}" stroke-width="0.9" fill="none" '
                f'marker-end="url(#head)"/>')

    def tag(cx, cy, s):
        w = 3.55 * len(s) + 9
        return (f'<rect class="tag" x="{cx - w / 2:.2f}" y="{cy - 6.2:.2f}" width="{w:.2f}" height="12.4" rx="6.2" '
                f'fill="{ACCENT}"/>' + text(cx, cy + 2.3, s, S, 600, fill="#ffffff"))

    # the center row: the brand's name, the recommendation, people's choices
    out.append(box(6, 72, 116, 48, stroke=INK, sw=1.1))
    out += lines(64, 91, ["The brand's name"], M, 7, 121)
    out += lines(64, 104, ["unfamiliar or familiar,", "shown or hidden"], S, 8, 120)
    out.append(box(214, 72, 104, 48, stroke=INK, sw=1.1))
    out += lines(266, 91, ["Recommendation"], M, 215, 317)
    out += lines(266, 104, ["of the optimal product"], S, 216, 316)
    out.append(box(392, 72, 70, 48, fill=PALE, stroke="none"))
    out += lines(427, 91, ["People's choices"], M, 393, 461)
    out += lines(427, 104, ["with and without", "the recommendation"], S, 393, 461, step=8.4)
    out.append(arrow(122, yc, 213, yc))
    out.append(arrow(318, yc, 391, yc))
    # the listing's quality information, down onto the arrow of the effect
    mid = 170.0
    out.append(box(mid - 80, 6, 160, 31, fill=PALE, stroke="none"))
    out += lines(mid, 19, ["Experience attributes stated"], M, mid - 79, mid + 79)
    out += lines(mid, 30, ["warranty, failure rate, lab testing, returns"], S, mid - 78, mid + 78)
    out.append(arrow(mid, 37, mid, yc - 2.2))
    out.append(f'<circle cx="{mid}" cy="{yc}" r="1.6" fill="{INK}"/>')
    out.append(box(6, 140, 116, 58, fill=PALER, stroke=INK, sw=0.75, r=5))
    out += lines(64, 153, ["Machine brand knowledge"], M, 7, 121, weight=600)
    out.append(box(13, 161, 49, 29))
    out += lines(37.5, 178, ["Awareness"], S, 14, 61)
    out.append(box(66, 161, 49, 29))
    out += lines(90.5, 178, ["Image"], S, 67, 114)
    out.append(box(6, 222, 116, 32, fill=PALE, stroke="none"))
    out += lines(64, 235, ["Training text"], M, 7, 121)
    out += lines(64, 246, ["pages about a brand, stages"], S, 8, 120)
    out.append(arrow(64, 222, 64, 199))
    out.append(arrow(64, 140, 64, 121))
    # which study tests which part, numbered in the order of the paper
    out.append(tag(mid, yc + 13, "Study 1 · the effect"))
    out.append(tag(mid + 34, 56, "Study 2 · why"))
    out.append(tag(190, 169, "Study 3 · awareness or image?"))
    out.append(tag(110, 210.5, "Study 3 · where from"))
    out.append(tag(355, yc - 12, "Study 4"))
    render("fig2_model_order", page("\n".join(out), W, H), W, H)
    return {"name": "fig2_model_order", "number": "Figure 2 (redrawn for review)"}



def _products(user):
    """The products of one item's message, in the order shown: name, brand, price, the listed attributes, reviews."""
    out, cur = [], None
    for ln in user.splitlines():
        s = ln.strip()
        if s.startswith("--- Product"):
            cur = {"specs": []}
            out.append(cur)
        elif cur is None or not s:
            continue
        elif s.startswith("Name:"):
            cur["name"] = s[5:].strip()
        elif s.startswith("Brand:"):
            cur["brand"] = s[6:].strip()
        elif s.startswith("Price:"):
            cur["price"] = s[6:].strip()
        elif s.startswith("Reviews:"):
            cur["reviews"] = s[8:].strip()
        elif ":" in s and s != "Specs:":
            k, v = s.split(":", 1)
            cur["specs"].append((k.strip(), v.strip()))
    return out


SPEC_LABELS = {"cpu": "Processor", "ram": "Memory", "storage": "Storage", "display": "Screen", "battery": "Battery"}
EXAMPLE_TABLE, EXAMPLE_ITEM = "sr_laptops_01_dom", "59fdf284d36cbff1"


def fig_example_table(table=EXAMPLE_TABLE):
    import sys
    sys.path.insert(0, str(CODE))
    import tables as wa
    shown = wa.s2_item(table, "original", 0, 0)
    hidden = wa.s2_item(table, "hidden", 0, 0)
    if table == EXAMPLE_TABLE:
        assert shown["id"] == EXAMPLE_ITEM, (shown["id"], EXAMPLE_ITEM)
    best = shown["best"]
    order = shown["order"]
    rows_shown, rows_hidden = _products(shown["user"]), _products(hidden["user"])
    request = shown["user"].splitlines()[0].strip()
    spec_names = [k for k, _ in rows_shown[0]["specs"]]
    cols = ["Name", "Brand", "Price"] + [SPEC_LABELS.get(k, k.capitalize()) for k in spec_names] + ["Reviews"]
    widths = [58, 40, 40, 44, 54, 46, 42, 38, 86]
    assert len(widths) == len(cols), (cols, widths)
    W = 468
    x0 = (W - sum(widths)) / 2
    row_h, head_h = 13.0, 13.0
    out = []

    def table_block(y, title, rows):
        parts = [text(x0, y, title, M, 600, anchor="start")]
        y += 6
        parts.append(f'<rect x="{x0}" y="{y}" width="{sum(widths)}" height="{head_h}" fill="{PALE}"/>')
        x = x0
        for c, w in zip(cols, widths):
            parts.append(text(x + 4, y + 9, c, S, 600, anchor="start", xmin=x, xmax=x + w))
            x += w
        y += head_h
        for letter, r in zip(order, rows):
            fill = PALER if letter != best else "#DCE6EC"
            parts.append(f'<rect x="{x0}" y="{y}" width="{sum(widths)}" height="{row_h}" fill="{fill}"/>')
            cells = [r["name"], r["brand"], r["price"]] + [v for _, v in r["specs"]] + [r["reviews"]]
            x = x0
            for c, w in zip(cells, widths):
                weight = 600 if letter == best else 400
                parts.append(text(x + 4, y + 9, c, S, weight, anchor="start", xmin=x, xmax=x + w))
                x += w
            y += row_h
        parts.append(f'<line x1="{x0}" y1="{y}" x2="{x0 + sum(widths)}" y2="{y}" stroke="{LINE}" stroke-width="0.6"/>')
        return parts, y

    out.append(text(x0, 12, f"Shopper's request: “{request}”", S, 400, anchor="start"))
    y = 30.0
    parts, y = table_block(y, "With brand names", rows_shown)
    out += parts
    parts, y = table_block(y + 22, "Without brand names", rows_hidden)
    out += parts
    k = order.index(best)
    out.append(text(x0 + sum(widths), 30, "Bold row: the optimal product", S, 400, anchor="end"))
    H = round(y + 8)
    render("fig_example_table", page("\n".join(out), W, H), W, H)
    return {"name": "fig_example_table", "rows": len(rows_shown), "attributes": len(spec_names), "best_row": k + 1,
            "item": shown["id"], "table": table, "trial": shown["trial"]}



def _panel(kind, dx, dy):
    out = []

    def X(x):
        return x + dx

    def Y(y):
        return y + dy

    def box(x, y, w, h, fill="#ffffff", stroke=LINE, sw=0.75, r=4):
        return (f'<rect class="box" x="{X(x)}" y="{Y(y)}" width="{w}" height="{h}" rx="{r}" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="{sw}"/>')

    def lines(cx, y, rows, size, xmin, xmax, weight=400, step=9.0):
        return [text(X(cx), Y(y) + k * step, r, size, weight, xmin=X(xmin), xmax=X(xmax)) for k, r in enumerate(rows)]

    def arrow(x1, y1, x2, y2):
        return (f'<path class="edge" d="M{X(x1)},{Y(y1)} L{X(x2)},{Y(y2)}" stroke="{INK}" stroke-width="0.9" '
                f'fill="none" marker-end="url(#head)"/>')

    def dot(x, y):
        return f'<circle cx="{X(x)}" cy="{Y(y)}" r="1.6" fill="{INK}"/>'

    def tag(cx, cy, s):
        w = 3.55 * len(s) + 9
        return (f'<rect class="tag" x="{X(cx) - w / 2:.2f}" y="{Y(cy) - 6.2:.2f}" width="{w:.2f}" height="12.4" '
                f'rx="6.2" fill="{ACCENT}"/>' + text(X(cx), Y(cy) + 2.3, s, S, 600, fill="#ffffff"))

    if kind == "A":  # the paper's order: the effect in the center row
        yc, mid = 96.0, 170.0
        out.append(box(6, 72, 116, 48, stroke=INK, sw=1.1))
        out += lines(64, 91, ["The brand's name"], M, 7, 121)
        out += lines(64, 104, ["unfamiliar or familiar,", "branded or unbranded"], S, 8, 120)
        out.append(box(214, 72, 104, 48, stroke=INK, sw=1.1))
        out += lines(266, 91, ["Recommendation"], M, 215, 317)
        out += lines(266, 104, ["of the optimal product"], S, 216, 316)
        out.append(box(392, 72, 70, 48, fill=PALE, stroke="none"))
        out += lines(427, 91, ["People's choices"], M, 393, 461)
        out += lines(427, 104, ["with and without", "the recommendation"], S, 393, 461, step=8.4)
        out += [arrow(122, yc, 213, yc), arrow(318, yc, 391, yc)]
        # the three experience attributes that Study 2a states for every product (22 November 2026)
        out.append(box(mid - 80, 6, 160, 39, fill=PALE, stroke="none"))
        out += lines(mid, 19, ["Experience attributes stated"], M, mid - 79, mid + 79)
        out += lines(mid, 30, ["warranty, failure rate and", "time on the market"], S,
                     mid - 78, mid + 78, step=8.4)
        out += [arrow(mid, 45, mid, yc - 2.2), dot(mid, yc)]
        out.append(box(6, 140, 116, 58, fill=PALER, stroke=INK, sw=0.75, r=5))
        out += lines(64, 153, ["Machine brand knowledge"], M, 7, 121, weight=600)
        out.append(box(13, 161, 49, 29))
        out += lines(37.5, 178, ["Awareness"], S, 14, 61)
        out.append(box(66, 161, 49, 29))
        out += lines(90.5, 178, ["Image"], S, 67, 114)
        out.append(box(6, 222, 116, 32, fill=PALE, stroke="none"))
        out += lines(64, 235, ["Training text"], M, 7, 121)
        out += lines(64, 246, ["pages about a brand, stages"], S, 8, 120)
        out += [arrow(64, 222, 64, 199), arrow(64, 140, 64, 121)]
        out.append(tag(mid, yc + 13, "Study 1"))
        out.append(tag(mid + 24, 56, "Study 2"))
        out.append(tag(190, 169, "Study 3 · awareness or image?"))
        out.append(tag(98, 210.5, "Study 3"))
        out.append(tag(355, yc - 12, "Study 4"))
    else:  # the causal order, left to right
        yc, mid, cx = 120.0, 267.0, 185.0
        out.append(box(4, 94, 72, 52, fill=PALE, stroke="none"))
        out += lines(40, 113, ["Training text"], M, 5, 75)
        out += lines(40, 126, ["pages about a brand,", "stages of training"], S, 6, 74)
        out.append(box(132, 54, 106, 134, fill=PALER, stroke=INK, sw=0.75, r=5))
        out += lines(cx, 69, ["Machine brand knowledge"], M, 133, 237, weight=600)
        out.append(box(141, 80, 88, 46))
        out += lines(cx, 96, ["Awareness"], M, 142, 228)
        out += lines(cx, 108, ["does the model", "know the brand?"], S, 143, 227)
        out.append(box(141, 134, 88, 44))
        out += lines(cx, 150, ["Image"], M, 142, 228)
        out += lines(cx, 162, ["what the name", "is linked to"], S, 143, 227)
        out.append(box(mid - 80, 6, 160, 31, fill=PALE, stroke="none"))
        out += lines(mid, 19, ["Experience attributes stated"], M, mid - 79, mid + 79)
        out += lines(mid, 30, ["warranty, failure rate, lab testing, returns"], S, mid - 78, mid + 78)
        out.append(box(296, 94, 70, 52, stroke=INK, sw=1.1))
        out += lines(331, 113, ["Recommendation"], M, 297, 365)
        out += lines(331, 126, ["of the optimal", "product"], S, 298, 364)
        out.append(box(406, 94, 58, 52, fill=PALE, stroke="none"))
        out += lines(435, 109, ["People's", "choices"], M, 407, 463)
        out += lines(435, 131, ["with and without", "the advice"], S, 407, 463, step=8.4)
        out += [arrow(76, yc, 131, yc), arrow(238, yc, 295, yc), arrow(366, yc, 405, yc)]
        out += [arrow(mid, 37, mid, yc - 2.2), dot(mid, yc)]
        out.append(tag(104, yc - 12, "Study 1"))
        out.append(tag(mid, yc + 13, "Study 3"))
        out.append(tag(mid + 24, 66, "Study 2"))
        out.append(tag(386, yc - 12, "Study 4"))
        out.append(tag(cx, 200, "Study 3 · awareness or image?"))
    return out


def fig_model_compare():
    PW, GAP, TOP = 468, 34, 22
    W, H = PW * 2 + GAP, TOP + 262 + 62
    out = []
    heads = {"A": "A. The current order: the effect first", "B": "B. The causal order: training text first"}
    notes = {
        "A": ["Order of the studies: 1, the effect and how far it holds; 2, why (the listing's quality information;",
              "awareness or image); 3, where it comes from (training text); 4, people's choices."],
        "B": ["Order of the studies: 1, training text; 2, the model's brand knowledge and the listing's information;",
              "3, the effect across models; 4, people's choices. Study 1 would first have to show that text about a",
              "brand creates a preference in a model, before any study has shown that the effect exists in the",
              "assistants that consumers use."],
    }
    for k, dx in (("A", 0), ("B", PW + GAP)):
        out.append(text(dx + 6, 12, heads[k], L, 600, anchor="start"))
        out += _panel(k, dx, TOP)
        for j, ln in enumerate(notes[k]):
            out.append(text(dx + 6, TOP + 272 + 9 * j, ln, S, 400, anchor="start"))
    out.append(f'<line x1="{PW + GAP / 2}" y1="4" x2="{PW + GAP / 2}" y2="{H - 4}" stroke="{LINE}" stroke-width="0.6"/>')
    render("fig2_model_compare", page("\n".join(out), W, H), W, H)
    return {"name": "fig2_model_compare"}


def fig_model():
    W, H = 468, 262
    render("fig2_model", page("\n".join(_panel("A", 0, 0)), W, H), W, H)
    return {
        "name": "fig2_model", "number": "Figure 1",
        "title": "The Conceptual Model and the Study in Which Each Part Is Tested",
        "body": ("The center row is the effect: a brand's name changes how often a model recommends "
                 "the optimal product (Study 1). Stating the experience attributes in the listing moderates that "
                 "effect (Study 2). We propose that the model's knowledge of the brand, which has two parts, "
                 "awareness and image (Keller 1993), mediates the effect; in Study 3, we test whether a model "
                 "acquires that knowledge from its training text and which of its two parts predicts the effect. "
                 "People then choose with or without the recommendation (Study 4)."),
        "sources": [],
        "waits": [],
        "note": "A diagram: it prints no number.",
    }


def fig_example_table_entry():
    """The example table as a main-text figure."""
    info = fig_example_table()
    return {
        "name": "fig_example_table", "number": "Web Appendix Figure (Study 1a, an example table)",
        "title": "In Each Table, the Optimal Product Has a Fictitious Name and the Other Four Have Familiar Names",
        "body": ("The laptop table of Study 1a, at the price of the cheapest other product and with no experience attributes "
                 "stated: the shopper's request and five laptops, each with a name, a brand, a price, its listed "
                 "attributes and its reviews. Above, the laptops with their brand names; below, the same five laptops "
                 "without them. The bold row is the optimal product. The models saw each product as a block of text, in "
                 "the order shown here, and answered with the letter of one product. We describe this table in the "
                 "introduction, and the same five laptops appear in the figure of the settings of Study 1c."),
        "sources": [("every cell", "",
                     f"item {EXAMPLE_ITEM} and its version without brand names")], "waits": [],
        "note": (f"Read from the controlled test's items: table {info['table']}, trial {info['trial']}, item "
                 f"{info['item']}; {info['rows']} products, {info['attributes']} listed attributes."),
    }


if __name__ == "__main__":
    import sys as _sys
    if _sys.argv[1:] == ["review"]:
        print(fig_model_order()["name"], fig_example_table())
    elif _sys.argv[1:] == ["compare"]:
        print(fig_model_compare()["name"])
    else:
        print(fig_pyramid()["name"], fig_model()["name"])
