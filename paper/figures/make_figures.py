"""Data and shared style of the figures of the report.

All numbers are copied from the report's tables and written below as literals.
The figures are drawn by make_charts.py, make_flow_variants.py and make_cover.py.
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, PathPatch, Rectangle  # noqa: E402
from matplotlib.path import Path  # noqa: E402

# ---------------------------------------------------------------- data ----

APPROACHES = ["A", "B", "C"]
NAMES = {"A": "Plain model", "B": "Hypatia", "C": "Hypatia with code map"}

# Section 1 and 6.1, comparable basis: official Critical, High and Medium findings.
ONCHAINID_SEVERE = {"A": [3, 3, 4], "B": [4, 6, 5], "C": [5, 4, 6]}        # 5.1, of 12
ONCHAINID_ALL = {"A": [4, 4, 5], "B": [7, 9, 8], "C": [13, 8, 11]}         # 5.1, of 39
ONCHAINID_LOW = {a: [t - s for t, s in zip(ONCHAINID_ALL[a], ONCHAINID_SEVERE[a])]
                 for a in APPROACHES}                                       # of 27
SUMMARY = [  # project, official basis, per-run values (one value = one run)
    ("ONCHAINID", 12, ONCHAINID_SEVERE),
    ("GTE", 35, {"A": [8], "B": [10], "C": [15]}),
    ("Promis", 9, {"A": [2], "B": [2], "C": [4]}),
]

# 5.1 found in k of 3 runs, per official Critical/High/Medium finding.
# From ../scoring/onchainid/SUMMARY-3-RUNS.md, "Second read": Critical/High/Medium
# matches per approach and run (unchanged by the second read).
K3_FINDINGS = ["C-01", "H-01", "H-02", "M-01", "M-02", "M-03", "M-04", "M-05", "M-06",
               "M-07", "M-08", "M-09"]
K3_RUNS = {
    "A": [{"H-01", "H-02", "M-09"}, {"H-01", "H-02", "M-09"}, {"H-01", "H-02", "M-02", "M-09"}],
    "B": [{"H-01", "H-02", "M-01", "M-02"}, {"H-01", "H-02", "M-01", "M-02", "M-08", "M-09"},
          {"H-01", "H-02", "M-02", "M-08", "M-09"}],
    "C": [{"H-01", "H-02", "M-02", "M-08", "M-09"}, {"H-01", "H-02", "M-02", "M-08"},
          {"H-01", "H-02", "M-01", "M-02", "M-08", "M-09"}],
}

# 5.2 GTE round 1 (strict): High of 10, Medium of 25, minutes
GTE1 = {"A": [6, 2], "B": [5, 5], "C": [7, 8]}

# 5.4 loss analysis (approach C, GTE round 1), 20 missed: label, step of Figure 2, count
LOSS = [
    ("A question was asked and wrongly rejected", "step 5, Decide", 8),
    ("No question on the mechanism", "step 4, Ask", 7),
    ("Seen, but folded into another finding or downgraded", "step 7, Report", 4),
    ("The question was left open", "step 5, Decide", 1),
    ("The affected function was not in the code map", "step 2, Map", 0),
]

# 5.5 GTE round 2, distinct new findings: new official strict, other rated valid, doubtful
GTE2 = {"A": [0, 2, 0], "B": [0, 2, 0], "C": [2, 7, 4]}
GTE2_MIN = {"A": 21.3, "B": 19.0, "C": 79.1}

# 5.2, 5.5, 5.6: official findings matched strictly after one and two rounds, of 35
ROUNDS = [("A", 8, 8), ("B", 10, 10), ("C", 15, 17)]
ROUNDS_C_CORRECTED = (15, 18)

# 5.4 and 5.6: what became of the 20 findings approach C missed in the first round
FATE_BEFORE = [("rejected", "wrongly rejected", 8), ("noq", "no question", 7),
               ("folded", "folded or\ndowngraded", 4), ("open", "left\nopen", 1)]
FATE_AFTER = [("found", "found: 3 strictly,\n1 leniently", 4),
              ("rejected", "rejected, 6 of them also\nin the first round", 8),
              ("open", "closed by\nargument or\nunanswered", 3), ("noq", "no\nquestion", 3),
              ("folded", "kept in\nanother\nfinding", 2)]

# 5.6 and 5.7: status of approach C's question list
QSTATUS = [
    ("GTE", 804, [("test", "decided by a test", 86),
                                          ("inherited", "inherited as decided", 63),
                                          ("argued", "closed by a written argument", 649),
                                          ("pending", "pending review", 6)]),
    ("Promis", 463, [("test", "decided by a test", 17),
                     ("open", "open at the iteration limit", 446)]),
]

# 5.7 Promis, per official finding (scoring/promis/r1/ADJUDICATION.md, section 5)
PROMIS_HIGH = ["H-01", "H-02", "H-03", "H-04", "H-05"]
PROMIS_MED = ["M-01", "M-02", "M-03", "M-05"]                 # the 4 inside the audited files
PROMIS_LOW = [f"L-{i:02d}" for i in range(1, 15)]
PROMIS_FOUND = {"A": {"H-05", "M-03", "L-13"},
                "B": {"H-04", "H-05", "L-12"},
                "C": {"H-02", "H-04", "H-05", "M-03", "L-11", "L-12", "L-13"}}
PROMIS_OUTSIDE = {"A": 0, "B": 2, "C": 3}
PROMIS_MIN = {"A": 11.1, "B": 23.6, "C": 88.8}

# 5.9 minutes and distinct valid findings per run: (group, approach, minutes, valid)
RUNS = [
    ("ONCHAINID", "A", 10.8, 4), ("ONCHAINID", "B", 22.8, 8), ("ONCHAINID", "C", 47.5, 15),
    ("ONCHAINID", "A", 13.8, 5), ("ONCHAINID", "B", 31.4, 10), ("ONCHAINID", "C", 35.4, 8),
    ("ONCHAINID", "A", 9.9, 6), ("ONCHAINID", "B", 22.1, 9), ("ONCHAINID", "C", 54.2, 12),
    ("GTE1", "A", 84.6, 14), ("GTE1", "B", 48.1, 18), ("GTE1", "C", 76.3, 30),
    ("GTE2", "A", 21.3, 2), ("GTE2", "B", 19.0, 2), ("GTE2", "C", 79.1, 9),
    ("GTE2corr", "B", 22.8, 2), ("GTE2corr", "C", 105.2, 12),
    ("Promis", "A", 11.1, 3), ("Promis", "B", 23.6, 5), ("Promis", "C", 88.8, 10),
]
SECOND_ROUNDS = {"GTE2", "GTE2corr"}

# 4.2 judge outcomes over 97 judged tests
JUDGE = {"confirmed": 50, "fixed": 31, "per_fix": 19, "not_official": 3, "reading": 44,
         "not_demonstrated": 0, "total": 97}


# --------------------------------------------------------------- style ----

BG = "#faf9f5"
EDGE = "#dcd9cf"      # thin edge of the canvas, so it does not float on a white page
INK = "#1a1a1a"
INK2 = "#6b6b66"
GRID = "#e6e3da"
OTHER = "#cfccc2"
TRACK = "#ebe9e2"     # the pale track of every "found of N" meter and empty slot
COLOR = {"A": "#b4b1a6", "B": "#40668c", "C": "#e0655f"}
DARK = "#55534d"      # second category beside coral (validated with coral, see the report)
PALE = "#efede6"      # remaining categories: pale fill with a hairline edge
NEUTRAL_FILL = "#efede6"

DPI = 200
W = 9.6               # every figure is 1920 px wide
H_TALL, H_SHORT = 6.4, 4.6   # two heights only: 1280 px and 920 px

MARGIN = 0.4          # left and right margin of everything
Y_TITLE = 0.34        # top of the title, from the top edge
Y_SUB = 0.74          # top of the subtitle (up to two lines)
Y_KEY = 1.47          # centre of the legend row
TOP_KEY = 1.82        # top of the plot when there is a legend row
TOP = 1.55            # top of the plot when there is none
NOTE_Y = 0.30         # baseline of the single note, from the bottom edge

FS_TITLE = 17
FS_SUB = 12.5
FS_GROUP = 14         # category labels: approach, project, severity (near-black)
FS_KEY = 11.5
FS_TICK = 12
FS_VALUE = 13
FS_NOTE = 11
FS_SMALL = 10.5         # nothing is set smaller than this (6 pt at half width)
FS_BOX_NAME = 12
FS_BOX_LINE = 10.5

LW_BOX = 0.9
LW_ARROW = 1.1


def _has_bold(name):
    """A family counts only when matplotlib has a real bold face for it."""
    weights = {f.weight for f in font_manager.fontManager.ttflist if f.name == name}
    return bool(weights) and any(w in (700, "bold") for w in weights)


def _load_helvetica_neue():
    """matplotlib reads one face of a .ttc collection. Split out Regular, Medium and Bold
    into a temporary folder so the three weights can be used. Silent when not on macOS."""
    import tempfile
    src = "/System/Library/Fonts/HelveticaNeue.ttc"
    if not os.path.exists(src):
        return
    try:
        from fontTools.ttLib import TTCollection
        out = os.path.join(tempfile.gettempdir(), "report-figure-fonts")
        os.makedirs(out, exist_ok=True)
        for face in TTCollection(src).fonts:
            name = face["name"].getDebugName(4)
            if name in ("Helvetica Neue", "Helvetica Neue Light", "Helvetica Neue Medium",
                        "Helvetica Neue Bold"):
                path = os.path.join(out, name.replace(" ", "") + ".ttf")
                if not os.path.exists(path):
                    face.save(path)
                font_manager.fontManager.addfont(path)
    except Exception:  # fall back to Arial
        return


_load_helvetica_neue()
FONT = next(n for n in ["Helvetica Neue", "Arial", "DejaVu Sans"] if _has_bold(n))
TITLE_WEIGHT = 500 if FONT == "Helvetica Neue" else "bold"
NAME_WEIGHT = 400 if FONT == "Helvetica Neue" else "bold"    # names inside diagrams
LIGHT = {"font.weight": 300} if FONT == "Helvetica Neue" else {}   # body text of diagrams

plt.rcParams.update({
    "font.family": FONT,
    "font.size": FS_TICK,
    "xtick.labelsize": FS_TICK,
    "ytick.labelsize": FS_TICK,
    "xtick.color": INK2,
    "ytick.color": INK2,
    "axes.labelcolor": INK2,
    "axes.labelsize": FS_TICK,
    "axes.facecolor": BG,
    "figure.facecolor": BG,
    "savefig.facecolor": BG,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

OUT = os.path.dirname(os.path.abspath(__file__))


def tint(hex_color, strength):
    """Mix a colour with the canvas; strength 1 = colour, 0 = canvas."""
    c = [int(hex_color[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(BG[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(bb + (cc - bb) * strength):02x}" for cc, bb in zip(c, b))


# ------------------------------------------------------- shared layout ----

def text_width(fig, s, size, weight="normal"):
    t = fig.text(0, 0, s, fontsize=size, fontweight=weight)
    w = t.get_window_extent(renderer=fig.canvas.get_renderer()).width / DPI
    t.remove()
    return w


def wrap(fig, s, size, width):
    """Greedy wrap of s to a measured width in inches."""
    lines, cur = [], ""
    for word in s.split():
        cand = (cur + " " + word).strip()
        if cur and text_width(fig, cand, size) > width:
            lines.append(cur)
            cur = word
        else:
            cur = cand
    lines.append(cur)
    return "\n".join(lines)


def frame(title, subtitle=None, h=H_TALL):
    """Canvas with a thin edge, a title and a subtitle at the fixed positions of the grid.

    Returns the figure and one axes that covers it in inches, origin bottom left.
    """
    fig = plt.figure(figsize=(W, h), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, h)
    ax.axis("off")
    ax.text(MARGIN, h - Y_TITLE, title, fontsize=FS_TITLE, fontweight=TITLE_WEIGHT, color=INK,
            ha="left", va="top")
    if subtitle:
        ax.text(MARGIN, h - Y_SUB, wrap(fig, subtitle, FS_SUB, W - 2 * MARGIN), fontsize=FS_SUB,
                color=INK2, ha="left", va="top", linespacing=1.3)
    fig._h = h
    return fig, ax


def key_row(fig, ax, items, x=MARGIN):
    """Frameless legend on the grid: swatch + label. item = (label, face, edge or None, shape)."""
    y = fig._h - Y_KEY
    for item in items:
        label, face = item[0], item[1]
        edge = item[2] if len(item) > 2 else None
        shape = item[3] if len(item) > 3 else "square"
        if shape == "dot":
            ax.scatter([x + 0.08], [y], s=70, facecolor=face, edgecolor=edge or face,
                       linewidth=1.5, zorder=3)
        else:
            ax.add_patch(FancyBboxPatch((x, y - 0.08), 0.16, 0.16,
                                        boxstyle="round,pad=0,rounding_size=0.03",
                                        facecolor=face, edgecolor=edge or "none",
                                        linewidth=1.2 if edge else 0, zorder=3))
        ax.text(x + 0.25, y, label, fontsize=FS_KEY, color=INK, ha="left", va="center")
        x += 0.25 + text_width(fig, label, FS_KEY) + 0.35
    return x


def note(fig, ax, text):
    """The one note an image may carry, bottom left."""
    ax.text(MARGIN, NOTE_Y, text, fontsize=FS_NOTE, color=INK2, ha="left", va="baseline")


_M, _L, _C, _Z = Path.MOVETO, Path.LINETO, Path.CURVE3, Path.CLOSEPOLY


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=DPI, facecolor=BG)
    plt.close(fig)
    print("wrote", path)


# The approach labels at the left of every per-approach chart: same size, same weight.
NAME_COL = MARGIN               # left edge of the approach names
NAME_W = 2.25                   # width reserved for them


def fmt(v):
    return f"{v:.1f}" if abs(v - round(v)) > 1e-9 else f"{v:g}"


# ------------------------------------------------------------- figures ----


FATE_STYLE = {"found": (COLOR["C"], "none", "white"),
              "rejected": (DARK, "none", "white"),
              "noq": (PALE, OTHER, INK), "folded": (PALE, OTHER, INK), "open": (PALE, OTHER, INK)}


QS_STYLE = {"test": (COLOR["C"], "none", "white"), "inherited": (DARK, "none", "white"),
            "argued": (PALE, OTHER, INK), "pending": (PALE, OTHER, INK),
            "open": (PALE, OTHER, INK)}


# ------------------------------------------------------------ diagrams ----

PAD = 0.05  # gap between an arrow end and a box edge


def path_arrow(ax, pts, dashed=False, color=INK2, lw=LW_ARROW, head=0.11):
    """Polyline whose last segment ends in an arrowhead; the shaft stops under the head."""
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    d = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    s = min(head, d)
    ux, uy = (x2 - x1) / d, (y2 - y1) / d
    stop = (x2 - ux * 0.05, y2 - uy * 0.05)   # inside the head, which is 0.067 in long
    xs, ys = zip(*(pts[:-1] + [stop]))
    ax.plot(xs, ys, color=color, linewidth=lw, solid_joinstyle="round", solid_capstyle="butt",
            dash_joinstyle="round", dash_capstyle="butt",
            linestyle=(0, (4, 2.5)) if dashed else "-", zorder=1)
    ax.add_patch(FancyArrowPatch((x2 - ux * s, y2 - uy * s), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=12, color=color, linewidth=0,
                                 shrinkA=0, shrinkB=0, zorder=1))


CORAL_FILL = tint(COLOR["C"], 0.2)


# ------------------------------------------------------------ contact ----

ORDER = ["summary.png", "hypatia-flow-linear.png", "judge-flow.png", "onchainid-runs.png",
         "onchainid-k-of-3.png", "gte-round1.png", "loss-analysis.png", "gte-round2.png",
         "gte-two-rounds.png", "gte-before-after.png", "promis.png", "minutes-per-finding.png",
         "question-status.png"]


def contact_sheet():
    """All figures of the report, in order, at a common width, on one sheet."""
    from PIL import Image
    paths = [os.path.join(OUT, p) for p in ORDER if os.path.exists(os.path.join(OUT, p))]
    ims = [Image.open(p).convert("RGB") for p in paths]
    cw, gap, ncol = 640, 16, 4
    thumbs = [im.resize((cw, round(im.height * cw / im.width)), Image.LANCZOS) for im in ims]
    rows = [thumbs[i:i + ncol] for i in range(0, len(thumbs), ncol)]
    heights = [max(t.height for t in r) for r in rows]
    sheet = Image.new("RGB", (ncol * cw + (ncol + 1) * gap,
                              sum(heights) + (len(rows) + 1) * gap), (214, 211, 202))
    y = gap
    for r, rh in zip(rows, heights):
        x = gap
        for t in r:
            sheet.paste(t, (x, y))
            x += cw + gap
        y += rh + gap
    sheet.save(os.path.join(OUT, "_contact-sheet.png"))
    print("wrote", os.path.join(OUT, "_contact-sheet.png"))


if __name__ == "__main__":
    print("This module holds the data and the shared style. Run make_charts.py, "
          "make_flow_variants.py and make_cover.py to draw the figures.")
