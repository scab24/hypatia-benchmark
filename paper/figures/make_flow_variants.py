"""The two diagrams of the report: how Hypatia runs an audit, and how a finding is scored.

Run from the paper/ folder:  python3 figures/make_flow_variants.py
Writes hypatia-flow-radial.png (Figure 2) and judge-flow.png (Figure 3).
The canvas, colours, font, text sizes and title positions come from make_figures.py.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_figures as mf  # noqa: E402  (importing sets the shared rcParams and font)
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch  # noqa: E402

BG, INK, INK2 = mf.BG, mf.INK, mf.INK2
CORAL = mf.COLOR["C"]
CORAL_FILL = mf.CORAL_FILL
CORAL_SOFT = mf.tint(CORAL, 0.1)
NEUTRAL_FILL, NEUTRAL_EDGE = mf.NEUTRAL_FILL, mf.OTHER
W, H = mf.W, mf.H_TALL
FS = mf.FS_SMALL           # 12, the floor of every text in the set
DASH = "#a8a59b"           # the next-round arrow: lighter than the main flow

TITLE = "A Hypatia audit in nine steps, two of them only with the code map"
SUBTITLE = "Step 4 builds the questions. Steps 5 to 7 work through them one by one"
NEXT_ROUND = "a later audit starts from the open questions"
LOOP = "steps 5 to 7 repeat until no question is open\nor the iteration limit is reached"


def coral_key(fig, ax, text="only with the code map"):
    """One-swatch key, right-aligned on the subtitle line."""
    y = H - mf.Y_SUB - 0.12
    w = mf.text_width(fig, text, mf.FS_KEY)
    ax.text(W - mf.MARGIN, y, text, fontsize=mf.FS_KEY, color=INK, ha="right", va="center")
    ax.add_patch(FancyBboxPatch((W - mf.MARGIN - w - 0.1 - 0.16, y - 0.08), 0.16, 0.16,
                                boxstyle="round,pad=0,rounding_size=0.03", facecolor=CORAL_FILL,
                                edgecolor=CORAL, linewidth=mf.LW_BOX, zorder=3))


def rbox(ax, x, y, w, h, fill, edge, lw=mf.LW_BOX, r=0.1, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                facecolor=fill, edgecolor=edge, linewidth=lw, zorder=z))


# ============================================================ variant 1 ====

LIN_STEPS = [  # name, one line, code map only
    ("Scope", "fixes the files\nto audit", False),
    ("Map", "functions, calls,\ndata, checks", True),
    ("Understand", "describes each\nfunction, flow", False),
    ("Ask", "builds the\nquestions, below", True),
    ("Decide", "one outcome\nper question", False),
    ("Prove", "a test for each\ncandidate", False),
    ("Report", "a report per\nproven finding", False),
    ("Close", "run frozen,\nfinal checks", False),
    ("Next round", "records what\nstayed open", False),
]
BW, BH, GAP = 1.46, 0.8, 0.3
X0 = mf.MARGIN + 0.32
ROW_TOP_IN = (1.38, 2.55)  # top edge of each row, inches from the top


# ============================================================ variant 2 ====

FSR = 10.5                # text size of the radial diagram
CX, CY = 4.05, 2.8        # centre of the ring, inches from the bottom-left
RX, RY = 1.85, 1.85       # ring radii
R_STEP = 0.4
R_HUB = 0.5
ANGLES = {i: 100 - 40 * (i - 1) for i in range(1, 10)}  # clockwise from the top, 40 degrees apart
RAD_STEPS = {1: ("Scope", False), 2: ("Map", True), 3: ("Under-\nstand", False),
             4: ("Ask", True), 5: ("Decide", False), 6: ("Prove", False),
             7: ("Report", False), 8: ("Close", False), 9: ("Next\nround", False)}


def ring_pos(i, k=1.0):
    a = math.radians(ANGLES[i])
    return CX + k * RX * math.cos(a), CY + k * RY * math.sin(a)


def ellipse_arc(ax, a_deg, b_deg, k, color, lw=mf.LW_ARROW, dashed=False, n=40):
    """Arc of the ellipse scaled by k from angle a to angle b, arrowhead at b."""
    a, b = math.radians(a_deg), math.radians(b_deg)
    ts = [a + (b - a) * j / n for j in range(n + 1)]
    pts = [(CX + k * RX * math.cos(t), CY + k * RY * math.sin(t)) for t in ts]
    xs, ys = zip(*pts[:-2])
    ax.plot(xs, ys, color=color, lw=lw, zorder=1, solid_capstyle="butt",
            linestyle=(0, (4, 2.5)) if dashed else "-")
    ax.add_patch(FancyArrowPatch(pts[-3], pts[-1], arrowstyle="-|>", mutation_scale=12,
                                 color=color, linewidth=0.1, shrinkA=0, shrinkB=0, zorder=1))


def side_list(ax, x, y_top, heading, items, coral, anchor):
    """An unboxed list beside the ring: a heading, a thin rule, name and description rows.

    anchor is the point of the step the list belongs to. Returns nothing.
    """
    stride = 0.44
    rule = CORAL if coral else NEUTRAL_EDGE
    y_bot = y_top - 0.3 - stride * (len(items) - 1) - 0.3
    ax.plot([x, x], [y_bot, y_top + 0.06], color=rule, lw=1.3, zorder=2, solid_capstyle="butt")
    ax.text(x + 0.14, y_top, heading, ha="left", va="center", fontsize=FSR - 1, color=INK2,
            zorder=3)
    for k, (name, desc) in enumerate(items):
        y = y_top - 0.36 - k * stride
        ax.text(x + 0.14, y, name, ha="left", va="center", fontsize=FSR,
                fontweight=mf.NAME_WEIGHT, color=INK, zorder=3)
        ax.text(x + 0.14, y - 0.17, desc, ha="left", va="center", fontsize=FSR - 0.5,
                color=INK2, zorder=3)


def fig_radial():
    with mf.plt.rc_context(mf.LIGHT):
        _fig_radial()


def _fig_radial():
    fig, ax = mf.frame(TITLE, "Read clockwise from step 1. Steps 4, 5 and 6 are detailed at the "
                              "sides")
    coral_key(fig, ax)

    # hub
    ax.add_patch(Circle((CX, CY), R_HUB, facecolor=INK, edgecolor="none", zorder=3))
    ax.text(CX, CY + 0.1, "Hypatia", ha="center", va="center", fontsize=FSR + 1,
            fontweight=mf.NAME_WEIGHT, color="white", zorder=4)
    ax.text(CX, CY - 0.11, "audit", ha="center", va="center", fontsize=FSR + 1,
            fontweight=mf.NAME_WEIGHT, color="white", zorder=4)

    # the order of the steps: arcs of the ring, clockwise (falling angle)
    def arc_between(i, j, dashed=False):
        a, b = ANGLES[i], ANGLES[j]
        if b > a:
            b -= 360
        pad = 14
        ellipse_arc(ax, a - pad, b + pad, 1.0, DASH if dashed else INK2, dashed=dashed)

    for i in range(1, 9):
        arc_between(i, i + 1)
    arc_between(9, 1, dashed=True)

    # the loop: from step 7 back to step 5, inside the ring
    ellipse_arc(ax, ANGLES[7] + 10, ANGLES[5] - 10, 0.7, INK2)
    ax.text(CX, CY - R_HUB - 0.27, "steps 5 to 7 repeat until no question\nis open or the "
            "iteration limit is reached", ha="center", va="center", fontsize=FSR - 1,
            color=INK2, linespacing=1.25, zorder=4)

    # steps
    for i, (name, coral) in RAD_STEPS.items():
        x, y = ring_pos(i)
        ax.add_patch(Circle((x, y), R_STEP, facecolor=CORAL_FILL if coral else NEUTRAL_FILL,
                            edgecolor=CORAL if coral else NEUTRAL_EDGE, linewidth=mf.LW_BOX,
                            zorder=3))
        ax.text(x, y + 0.17, str(i), ha="center", va="center", fontsize=FSR - 1.5,
                color=CORAL if coral else INK2, zorder=4)
        ax.text(x, y - 0.06, name, ha="center", va="center", fontsize=FSR,
                fontweight=mf.NAME_WEIGHT, color=INK, linespacing=1.0, zorder=4)

    x9, y9 = ring_pos(9)
    ax.text(x9 - R_STEP - 0.12, y9 + 0.38, "a later audit starts\nfrom the open questions",
            ha="right", va="center", fontsize=FSR - 1, color=INK2, linespacing=1.25, zorder=4)

    XR = 6.6
    x4, y4 = ring_pos(4)
    side_list(ax, XR, 4.7, "Step 4 builds the question list from",
              [("what-if questions", "a doubt about a function, flow or rule"),
               ("combinations", "pairs of calls over shared state"),
               ("path tree", "a pair extended into a longer path")],
              True, (x4 + R_STEP, y4))
    x5, y5 = ring_pos(5)
    side_list(ax, XR, 2.6, "Step 5 gives each question one outcome",
              [("impossible", "a check in the code stops it"),
               ("argued", "reasoned, no break found"),
               ("expanded", "split into longer paths"),
               ("candidate", "a possible finding, goes to step 6")],
              False, (x5 + R_STEP, y5))
    side_list(ax, 0.4, 1.85, "Step 6 tests each candidate",
              [("proven", "the test shows the harm"),
               ("rejected", "the test shows the rule holds"),
               ("undecided", "no proof, left for review")],
              False, None)
    mf.save(fig, "hypatia-flow-radial.png")


# ============================================================ scoring ====

def node(ax, x, yc, w, h, name, sub=None, fill="white", edge=None, ink=INK, ink2=INK2):
    """A box centred vertically on yc, its left edge at x: a name and up to two grey lines."""
    rbox(ax, x, yc - h / 2, w, h, fill, edge or NEUTRAL_EDGE, r=0.08)
    n = sub.count("\n") + 1 if sub else 0
    top = yc + (0.11 * n if sub else 0)
    ax.text(x + w / 2, top, name, ha="center", va="center", fontsize=11.5,
            fontweight=mf.NAME_WEIGHT, color=ink, zorder=3)
    if sub:
        ax.text(x + w / 2, top - 0.2, sub, ha="center", va="top", fontsize=9.8, color=ink2,
                linespacing=1.25, zorder=3)


def lane(ax, y0, y1, title, sub):
    rbox(ax, mf.MARGIN, y0, W - 2 * mf.MARGIN, y1 - y0, mf.tint(mf.OTHER, 0.16), "none", lw=0,
         r=0.12, z=0)
    ax.text(mf.MARGIN + 0.2, y1 - 0.24, title, ha="left", va="center", fontsize=11.5,
            fontweight=mf.TITLE_WEIGHT, color=INK, zorder=3)
    ax.text(mf.MARGIN + 0.2 + mf.text_width(ax.figure, title, 11.5, mf.TITLE_WEIGHT) + 0.14,
            y1 - 0.24, sub, ha="left", va="center", fontsize=10.2, color=INK2, zorder=3)


def fig_scoring():
    with mf.plt.rc_context(mf.LIGHT):
        _fig_scoring()


def _fig_scoring():
    fig, ax = mf.frame("A finding counts when a test confirms it or a reader matches it strictly",
                       "Scoring has two stages. The judge runs the tests, and readers match what "
                       "the tests cannot decide")
    # ---- stage 1
    lane(ax, 3.2, 5.3, "1  Judge", "runs the test of each finding")
    y = 4.35
    node(ax, 0.6, y, 1.55, 0.7, "Finding", "with its test")
    node(ax, 2.55, y, 1.9, 0.7, "Run on the audited code", "all 97 tests pass",
         fill=NEUTRAL_FILL)
    node(ax, 4.85, y, 2.1, 0.7, "Run on the fixed code", "and with each official fix alone",
         fill=NEUTRAL_FILL)
    node(ax, 7.85, y, 1.35, 0.7, "Confirmed", "50 of 97", fill=INK, edge=INK, ink="white",
         ink2="#d8d6cf")
    for x0, x1 in ((2.15, 2.55), (4.45, 4.85), (6.95, 7.85)):
        mf.path_arrow(ax, [(x0 + 0.04, y), (x1 - 0.04, y)])
    ax.text(7.4, y + 0.14, "a fix makes\nit fail", ha="center", va="bottom", fontsize=9.5,
            color=INK2, linespacing=1.2)
    node(ax, 5.8, 3.5, 1.15, 0.36, "Not official  3")
    mf.path_arrow(ax, [(6.37, y - 0.37), (6.37, 3.7)])
    ax.text(6.47, 3.84, "still passes", ha="left", va="center", fontsize=9.5, color=INK2)

    # ---- stage 2
    lane(ax, 0.75, 2.95, "2  Reading", "compares each finding with the official report")
    y2 = 1.75
    node(ax, 0.6, y2, 2.35, 0.95, "Left to reading", "44 tests the judge cannot decide\n"
                                                    "every GTE finding, no fixed version")
    node(ax, 3.3, y2, 1.7, 0.95, "First reader", "matches it to an\nofficial finding",
         fill=NEUTRAL_FILL)
    node(ax, 5.35, y2, 1.95, 0.95, "Second reader", "re-reads uncertain and lenient\n"
                                                   "matches, in most runs", fill=NEUTRAL_FILL)
    for x0, x1 in ((2.95, 3.3), (5.0, 5.35)):
        mf.path_arrow(ax, [(x0 + 0.04, y2), (x1 - 0.04, y2)])
    outs = [("Strict match", None, INK, "white", "#d8d6cf"),
            ("Lenient match", None, "white", INK, INK2),
            ("No match", "then rated for validity", "white", INK, INK2)]
    for k, (name, sub, fill, ink, ink2) in enumerate(outs):
        yo = y2 + 0.56 - k * 0.56
        rbox(ax, 7.85, yo - 0.21, 1.35, 0.42, fill, INK if fill == INK else NEUTRAL_EDGE, r=0.07)
        ax.text(7.97, yo, name, ha="left", va="center", fontsize=10.5,
                fontweight=mf.NAME_WEIGHT, color=ink, zorder=3)
        if sub:
            ax.text(7.97, yo - 0.36, sub, ha="left", va="center", fontsize=9.2, color=INK2,
                    zorder=3)
        mf.path_arrow(ax, [(7.34, y2), (7.57, y2), (7.57, yo), (7.81, yo)])
    # ---- from stage 1 to stage 2
    mf.path_arrow(ax, [(5.3, y - 0.37), (5.3, 3.08), (0.5, 3.08), (0.5, y2), (0.56, y2)])
    ax.text(2.9, 3.14, "cannot compile and no single fix decides: 44", ha="center", va="bottom",
            fontsize=9.5, color=INK2, bbox=dict(boxstyle="square,pad=0.12", fc=BG, ec="none"),
            zorder=4)
    mf.note(fig, ax, "Counted: findings confirmed by the judge and strict matches by reading.")
    mf.save(fig, "judge-flow.png")


if __name__ == "__main__":
    fig_radial()
    fig_scoring()
