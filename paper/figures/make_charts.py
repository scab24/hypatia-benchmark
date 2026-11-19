"""Bar charts for REPORT.md: one message per chart, numbers on the bars.

Run from the paper/ folder:  python3 figures/make_charts.py
Data and style come from make_figures.py. The diagrams (judge, Hypatia flow) are drawn
elsewhere. Mark rules: slim bars with a rounded data end and a square baseline, a thin
gap in the canvas colour between touching fills, hairline grid, text in ink colours only.
"""

from matplotlib.patches import Circle, PathPatch
from matplotlib.path import Path

import make_figures as F
from make_figures import (APPROACHES, BG, COLOR, DARK, INK, INK2, MARGIN, NAMES, TOP,
                          TOP_KEY, TRACK, W, frame, key_row, note, save, tint)

H = 5.4              # one height for every chart: 1080 px
BOTTOM = 0.95        # room under the plot for the category labels
BOTTOM_NOTE = 1.40   # the same, when the chart carries a note
FS_VALUE = 13        # the number on a bar
FS_CAT = 13.5        # category names under the plot
FS_SUB = 11.5        # second line under a category, and axis ticks
MEDIUM = F.NAME_WEIGHT
HAIR = "#e9e6dd"     # gridlines
BASE = "#bdbab0"     # the baseline
R = 0.05             # corner radius of a data end, inches
GAP = 1.6            # width of the canvas-colour gap around a fill, points

_M, _L, _C, _Z = Path.MOVETO, Path.LINETO, Path.CURVE3, Path.CLOSEPOLY


def plot_axes(fig, top, bottom, xlim, ylim, left=0.95, right=MARGIN):
    """A real axes inside the frame, positioned in inches, limits fixed up front."""
    h = fig._h
    ax = fig.add_axes([left / W, bottom / h, (W - left - right) / W, (h - top - bottom) / h])
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    for side in ("left", "top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(BASE)
    ax.spines["bottom"].set_linewidth(0.9)
    ax.tick_params(length=0)
    ax.set_axisbelow(True)
    ax._inch = ((W - left - right), (h - top - bottom))
    return ax


def _radii(ax):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    return R * (x1 - x0) / ax._inch[0], R * (y1 - y0) / ax._inch[1]


def col(ax, x, y0, y1, w, color, cap=True):
    """Vertical bar from y0 to y1, centred on x. cap rounds the top corners."""
    if y1 <= y0:
        return
    rx, ry = _radii(ax)
    rx, ry = (min(rx, w / 2), min(ry, (y1 - y0))) if cap else (0, 0)
    a, b = x - w / 2, x + w / 2
    verts = [(a, y0), (a, y1 - ry), (a, y1), (a + rx, y1), (b - rx, y1), (b, y1), (b, y1 - ry),
             (b, y0), (a, y0)]
    codes = [_M, _L, _C, _C, _L, _C, _C, _L, _Z]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor=color, edgecolor=BG, linewidth=GAP,
                           zorder=3, joinstyle="round"))


def row(ax, y, x0, x1, h, color, cap=True):
    """Horizontal bar from x0 to x1, centred on y. cap rounds the right corners."""
    if x1 <= x0:
        return
    rx, ry = _radii(ax)
    rx, ry = (min(rx, (x1 - x0)), min(ry, h / 2)) if cap else (0, 0)
    a, b = y - h / 2, y + h / 2
    verts = [(x0, a), (x1 - rx, a), (x1, a), (x1, a + ry), (x1, b - ry), (x1, b), (x1 - rx, b),
             (x0, b), (x0, a)]
    codes = [_M, _L, _C, _C, _L, _C, _C, _L, _Z]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor=color, edgecolor=BG, linewidth=GAP,
                           zorder=3, joinstyle="round"))


def y_axis(ax, step, suffix=""):
    top = ax.get_ylim()[1]
    ticks = list(range(0, int(top) + 1, step))
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{t}{suffix}" for t in ticks], fontsize=FS_SUB, color=INK2)
    ax.tick_params(axis="y", pad=8)
    ax.grid(axis="y", color=HAIR, linewidth=0.8)


def categories(ax, centres, labels, subs=None):
    ax.set_xticks(list(centres))
    ax.set_xticklabels(labels, fontsize=FS_CAT, color=INK)
    ax.tick_params(axis="x", pad=9)
    if subs:
        for x, s in zip(centres, subs):
            ax.annotate(s, (x, ax.get_ylim()[0]), xytext=(0, -31), textcoords="offset points",
                        ha="center", va="top", fontsize=FS_SUB, color=INK2)


def approach_key(fig, fax):
    key_row(fig, fax, [(NAMES[a], COLOR[a]) for a in APPROACHES])


def value(ax, x, y, s, size=FS_VALUE):
    ax.annotate(s, (x, y), xytext=(0, 5), textcoords="offset points", ha="center", va="bottom",
                fontsize=size, color=INK, fontweight=MEDIUM)


def inside(ax, x, y, s, light=False):
    ax.text(x, y, s, ha="center", va="center", fontsize=FS_VALUE - 0.5,
            color="white" if light else INK, fontweight=MEDIUM, zorder=4)


BW = 0.2             # bar width in a group of three
OFF = {"A": -0.215, "B": 0.0, "C": 0.215}
SINGLE = 0.36        # width of a bar that stands alone in its category
ON_DARK = {"A": False, "B": True, "C": True}   # white text inside a full-colour fill


# ------------------------------------------------------------------ 1 ----

def fig_summary():
    fig, fax = frame("Hypatia with code map finds the most on the two larger projects",
                     "Share of the official Critical, High and Medium findings found by each "
                     "approach, same model in all three", h=H)
    approach_key(fig, fax)
    ax = plot_axes(fig, TOP_KEY, BOTTOM_NOTE, (-0.5, 2.5), (0, 60))
    y_axis(ax, 10, "%")
    for g, (_, n, vals) in enumerate(F.SUMMARY):
        for a in APPROACHES:
            k = sum(vals[a]) / len(vals[a])
            col(ax, g + OFF[a], 0, 100 * k / n, BW, COLOR[a])
            value(ax, g + OFF[a], 100 * k / n, F.fmt(k))
    categories(ax, [0, 1, 2], ["ONCHAINID", "GTE", "Promis"],
               ["of 12 official, mean of three runs", "of 35 official, one run",
                "of 9 official, one run"])
    note(fig, fax, "Number on each bar: findings found. Bar height: share of the official count.")
    save(fig, "summary.png")


# ------------------------------------------------------------------ 4 ----

def fig_onchainid_runs():
    fig, fax = frame("Both Hypatia approaches beat the Plain model in every ONCHAINID run",
                     "Official findings found in three independent runs. Bar at the mean, one "
                     "dot per run", h=H)
    approach_key(fig, fax)
    ax = plot_axes(fig, TOP_KEY, BOTTOM_NOTE, (-0.5, 1.5), (0, 10))
    y_axis(ax, 2)
    for g, data in enumerate([F.ONCHAINID_SEVERE, F.ONCHAINID_LOW]):
        for a in APPROACHES:
            runs = data[a]
            m = sum(runs) / 3
            x = g + OFF[a]
            pale = g == 1 and a == "A"
            col(ax, x, 0, m, BW, tint(COLOR[a], 0.4) if pale else COLOR[a])
            ax.scatter([x - 0.045, x, x + 0.045], runs, s=30, color=INK, zorder=5,
                       edgecolor=BG, linewidth=1.3)
            value(ax, x, max(max(runs), m), F.fmt(round(m, 1)))
    categories(ax, [0, 1], ["Critical, High and Medium", "Low and Notes"],
               ["of 12 official", "of 27 official"])
    note(fig, fax, "Pale bar: the Plain model was told not to report Low findings, so that "
                   "bar is not comparable.")
    save(fig, "onchainid-runs.png")


# ------------------------------------------------------------- 5, 10 ----

def grouped_of_n(name, title, subtitle, groups, ymax, step):
    """Grouped bars per severity. groups: (label, official count, {approach: found})."""
    fig, fax = frame(title, subtitle, h=H)
    approach_key(fig, fax)
    ax = plot_axes(fig, TOP_KEY, BOTTOM, (-0.5, len(groups) - 0.5), (0, ymax))
    y_axis(ax, step)
    for g, (_, n, found) in enumerate(groups):
        for a in APPROACHES:
            x = g + OFF[a]
            col(ax, x, 0, found[a], BW, COLOR[a])
            value(ax, x, found[a], str(found[a]))
    categories(ax, range(len(groups)), [g[0] for g in groups],
               [f"of {g[1]} official" for g in groups])
    save(fig, name)


def fig_gte_round1():
    g = F.GTE1
    grouped_of_n(
        "gte-round1.png", "On GTE the code map's lead is in Medium findings",
        "Official findings found in the first round, by severity. One run per approach",
        [("High", 10, {a: g[a][0] for a in APPROACHES}),
         ("Medium", 25, {a: g[a][1] for a in APPROACHES}),
         ("High and Medium", 35, {a: sum(g[a]) for a in APPROACHES})], 18, 3)


def fig_promis():
    hi = {a: len(F.PROMIS_FOUND[a] & set(F.PROMIS_HIGH)) for a in APPROACHES}
    me = {a: len(F.PROMIS_FOUND[a] & set(F.PROMIS_MED)) for a in APPROACHES}
    grouped_of_n(
        "promis.png", "On Promis, Hypatia with code map found 4 of 9, the others 2 each",
        "Official findings found, by severity. One run per approach, report published after "
        "the model's knowledge cutoff",
        [("High", 5, hi), ("Medium", 4, me),
         ("High and Medium", 9, {a: hi[a] + me[a] for a in APPROACHES})], 5, 1)


# ------------------------------------------------------------------ 7 ----

def fig_gte_round2():
    fig, fax = frame("Asked to continue, Hypatia with code map produced 13 new findings",
                     "GTE, second round. New distinct findings by how each was rated, one run "
                     "per approach", h=H)
    approach_key(fig, fax)
    ax = plot_axes(fig, TOP_KEY, BOTTOM, (-0.5, 3.5), (0, 15))
    y_axis(ax, 3)
    kinds = [("In the official report", 0), ("Other, rated valid", 1), ("Doubtful", 2)]
    for g, (_, idx) in enumerate(kinds):
        for a in APPROACHES:
            v = F.GTE2[a][idx]
            col(ax, g + OFF[a], 0, v, BW, COLOR[a])
            value(ax, g + OFF[a], v, str(v))
    for a in APPROACHES:
        v = sum(F.GTE2[a])
        col(ax, 3 + OFF[a], 0, v, BW, COLOR[a])
        value(ax, 3 + OFF[a], v, str(v))
    ax.axvline(2.5, color=HAIR, linewidth=1.0, zorder=1)
    categories(ax, range(4), [k[0] for k in kinds] + ["All new findings"],
               ["matched strictly", "by a reader", "by a reader",
                "in " + ", ".join(f"{F.GTE2_MIN[a]:.0f}" for a in APPROACHES) + " minutes"])
    save(fig, "gte-round2.png")


# ------------------------------------------------------------------ 8 ----

def fig_two_rounds():
    fig, fax = frame("A second round added official findings only with the code map",
                     "GTE, official findings found after one and two rounds, of 35. One run per "
                     "approach and per version", h=H)
    steps = (0.3, 0.6, 1.0)
    key_row(fig, fax, [("after the first round", tint(DARK, steps[0])),
                       ("after the second round", tint(DARK, steps[1])),
                       ("second round, corrected version", DARK)])
    ax = plot_axes(fig, TOP_KEY, BOTTOM, (-0.6, 2.6), (0, 21))
    y_axis(ax, 3)
    for i, (a, r1, r2) in enumerate(F.ROUNDS):
        vals = [r1, r2] + ([F.ROUNDS_C_CORRECTED[1]] if a == "C" else [])
        xs = [i + (j - (len(vals) - 1) / 2) * 0.215 for j in range(len(vals))]
        for x, v, s in zip(xs, vals, steps):
            col(ax, x, 0, v, BW, tint(COLOR[a], s))
            value(ax, x, v, str(v))
    categories(ax, [0, 1, 2], [NAMES[a] for a in APPROACHES])
    save(fig, "gte-two-rounds.png")


# --------------------------------------------------------------- 6, 9 ----

def horizontal_counts(name, title, subtitle, rows, total, note_text=None):
    """Horizontal bars with the label at the left and 'k of total' at the bar end.

    rows: (label, sub-label or None, count, colour).
    """
    fig, fax = frame(title, subtitle, h=H)
    left = 5.0
    ax = plot_axes(fig, TOP, 1.0 if note_text else 0.5, (0, max(r[2] for r in rows) * 1.02),
                   (-0.6, len(rows) - 0.4), left=left, right=1.3)
    ax.spines["bottom"].set_visible(False)
    ax.axvline(0, color=BASE, linewidth=0.9, zorder=4)
    ax.set_xticks([])
    ax.set_yticks([])
    for y, (label, sub, k, c) in zip(range(len(rows))[::-1], rows):
        row(ax, y, 0, k, 0.5, c)
        ax.annotate(f"{k} of {total}", (k, y), xytext=(9, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=FS_VALUE, color=INK, fontweight=MEDIUM)
        dy = 8 if sub else 0
        ax.annotate(label, (0, y), xytext=(-12, dy), textcoords="offset points", ha="right",
                    va="center", fontsize=FS_CAT, color=INK)
        if sub:
            ax.annotate(sub, (0, y), xytext=(-12, -9), textcoords="offset points", ha="right",
                        va="center", fontsize=FS_SUB, color=INK2)
    if note_text:
        note(fig, fax, note_text)
    save(fig, name)


def fig_loss():
    """One bar per step of the audit, in the order of the process."""
    fig, fax = frame("Most missed findings were wrongly rejected or never asked about",
                     "GTE, first round, one run. The 20 official findings Hypatia with code map "
                     "missed, by the step where each was lost", h=H)
    c = COLOR["C"]
    steps = [("Map", "step 2", [0], "function not in\nthe code map"),
             ("Ask", "step 4", [7], "no question on\nthe mechanism"),
             ("Decide", "step 5", [1], "question\nleft open"),
             ("Prove", "step 6", [8], "asked and\nwrongly rejected"),
             ("Report", "step 7", [4], "folded into another\nfinding or downgraded")]
    ax = plot_axes(fig, TOP, 1.75, (-0.6, 4.6), (0, 10))
    y_axis(ax, 2)
    for i, (_, _, parts, _) in enumerate(steps):
        col(ax, i, 0, parts[0], SINGLE, c, cap=len(parts) == 1)
        if len(parts) > 1:
            col(ax, i, parts[0], sum(parts), SINGLE, tint(c, 0.45))
            inside(ax, i, parts[0] / 2, str(parts[0]), True)
        value(ax, i, sum(parts), str(sum(parts)))
    ax.set_xticks(range(5))
    ax.set_xticklabels([f"{n}" for n, _, _, _ in steps], fontsize=FS_CAT, color=INK)
    ax.tick_params(axis="x", pad=9)
    for i, (_, num, _, why) in enumerate(steps):
        ax.annotate(num, (i, 0), xytext=(0, -31), textcoords="offset points", ha="center",
                    va="top", fontsize=FS_SUB, color=INK2)
        ax.annotate(why, (i, 0), xytext=(0, -52), textcoords="offset points", ha="center",
                    va="top", fontsize=FS_SUB, color=INK2, linespacing=1.3)
        if i < 4:
            ax.annotate("", xy=(i + 0.72, 0), xytext=(i + 0.28, 0),
                        xycoords=("data", "axes fraction"), textcoords=("data", "axes fraction"),
                        arrowprops=dict(arrowstyle="-|>", color=BASE, lw=1.0, shrinkA=0,
                                        shrinkB=0, mutation_scale=11, relpos=(0, 0)),
                        annotation_clip=False)
    save(fig, "loss-analysis.png")


def fig_before_after():
    """One bar per outcome of the 20 findings after the correction."""
    fig, fax = frame("After correction, 4 of the 20 missed findings were found",
                     "GTE, corrected second round, one run. What became of the 20 official "
                     "findings missed in the first round", h=H)
    pale = tint(DARK, 0.4)
    rows = [("Found", "3 strictly,\n1 leniently", 4, COLOR["C"]),
            ("Rejected again", "6 also rejected\nin the first round", 8, DARK),
            ("Closed by argument\nor unanswered", None, 3, pale),
            ("Still no\nquestion", None, 3, pale),
            ("Still inside\nanother finding", None, 2, pale)]
    ax = plot_axes(fig, TOP, 1.6, (-0.6, 4.6), (0, 10))
    y_axis(ax, 2)
    for i, (_, _, k, colour) in enumerate(rows):
        col(ax, i, 0, k, SINGLE, colour)
        value(ax, i, k, f"{k} of 20")
    ax.set_xticks(range(5))
    ax.set_xticklabels([r[0] for r in rows], fontsize=FS_CAT - 1, color=INK, linespacing=1.25)
    ax.tick_params(axis="x", pad=9)
    for i, (label, sub, _, _) in enumerate(rows):
        if sub:
            ax.annotate(sub, (i, 0), xytext=(0, -34), textcoords="offset points", ha="center",
                        va="top", fontsize=FS_SUB, color=INK2, linespacing=1.3)
    save(fig, "gte-before-after.png")


def fig_layers():
    """Section 6: the Plain model's count, and what Hypatia and the code map add to it."""
    fig, fax = frame("What Hypatia adds to the model, and what the code map adds to Hypatia",
                     "Official Critical, High and Medium findings found, as a share of the "
                     "official count of each project", h=H)
    key_row(fig, fax, [("Plain model", COLOR["A"]), ("added by Hypatia", COLOR["B"]),
                       ("added by the code map", COLOR["C"])])
    ax = plot_axes(fig, TOP_KEY, BOTTOM, (-0.6, 2.6), (0, 60))
    y_axis(ax, 10, "%")
    for g, (_, n, vals) in enumerate(F.SUMMARY):
        k = {a: sum(vals[a]) / len(vals[a]) for a in APPROACHES}
        a_, b_, c_ = k["A"], k["B"] - k["A"], k["C"] - k["B"]
        pct = 100 / n
        col(ax, g, 0, a_ * pct, SINGLE, COLOR["A"], cap=b_ + c_ < 1e-9)
        inside(ax, g, a_ * pct / 2, F.fmt(a_))
        if b_ > 1e-9:
            col(ax, g, a_ * pct, (a_ + b_) * pct, SINGLE, COLOR["B"], cap=c_ < 1e-9)
            inside(ax, g, (a_ + b_ / 2) * pct, "+" + F.fmt(round(b_, 1)), True)
        if c_ > 1e-9:
            col(ax, g, (a_ + b_) * pct, (a_ + b_ + c_) * pct, SINGLE, COLOR["C"])
            inside(ax, g, (a_ + b_ + c_ / 2) * pct, "+" + F.fmt(round(c_, 1)), True)
        value(ax, g, k["C"] * pct, f"{F.fmt(k['C'])} of {n}")
    categories(ax, [0, 1, 2], ["ONCHAINID", "GTE", "Promis"],
               ["mean of three runs, code map adds 0", "one run", "one run, Hypatia adds 0"])
    save(fig, "layers.png")


# ----------------------------------------------------------------- 11 ----

def fig_minutes():
    fig, fax = frame("With the code map, a valid finding took longer in 4 of 5 first audits",
                     "Minutes of wall-clock time per distinct valid finding. Lower is faster",
                     h=H)
    approach_key(fig, fax)
    ax = plot_axes(fig, TOP_KEY, BOTTOM_NOTE, (-0.5, 4.5), (0, 10))
    y_axis(ax, 2)
    audits = [("ONCHAINID", 0), ("ONCHAINID", 1), ("ONCHAINID", 2), ("GTE1", 0), ("Promis", 0)]
    for g, (group, idx) in enumerate(audits):
        runs = [r for r in F.RUNS if r[0] == group]
        for a in APPROACHES:
            _, _, minutes, valid = [r for r in runs if r[1] == a][idx]
            v = minutes / valid
            col(ax, g + OFF[a], 0, v, BW, COLOR[a])
            value(ax, g + OFF[a], v, f"{v:.1f}", FS_VALUE - 1.5)
    categories(ax, range(5), ["ONCHAINID", "ONCHAINID", "ONCHAINID", "GTE", "Promis"],
               ["run 1", "run 2", "run 3", "first round", "one run"])
    note(fig, fax, "Valid findings include Low findings, which the Plain model was told not to "
                   "report, and findings a reader rated valid.")
    save(fig, "minutes-per-finding.png")


# ----------------------------------------------------------------- 12 ----

def fig_question_status():
    fig, fax = frame("Few questions were decided by a test: 86 of 804, and 17 of 463",
                     "Question list of Hypatia with code map at the end of the run, in the two "
                     "runs where it was counted", h=H)
    fill = {"test": COLOR["C"], "inherited": DARK, "argued": tint(DARK, 0.4), "pending": TRACK,
            "open": TRACK}
    key_row(fig, fax, [("decided by a test", fill["test"]),
                       ("inherited as decided", fill["inherited"]),
                       ("closed by a written argument", fill["argued"]),
                       ("not decided", TRACK, BASE)])
    ax = plot_axes(fig, TOP_KEY, 1.3, (0, 100), (-0.6, 1.6), left=3.5)
    ax.spines["bottom"].set_visible(False)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=FS_SUB, color=INK2)
    ax.set_yticks([])
    labels = [("GTE, corrected second round", "804 questions"), ("Promis", "463 questions")]
    for y, (_, total, parts), (name, sub) in zip([1, 0], F.QSTATUS, labels):
        x = 0
        for j, (kind, _, k) in enumerate(parts):
            w = 100 * k / total
            row(ax, y, x, x + w, 0.46, fill[kind], cap=j == len(parts) - 1)
            if w > 6:
                inside(ax, x + w / 2, y, str(k), kind in ("test", "inherited"))
            x += w
        ax.annotate(name, (0, y), xytext=(-12, 8), textcoords="offset points", ha="right",
                    va="center", fontsize=FS_CAT, color=INK)
        ax.annotate(sub, (0, y), xytext=(-12, -9), textcoords="offset points", ha="right",
                    va="center", fontsize=FS_SUB, color=INK2)
    note(fig, fax, "Not labelled: 17 questions decided by a test on Promis and 6 not decided "
                   "on GTE.")
    save(fig, "question-status.png")


F.ORDER[:] = ["summary.png", "hypatia-flow-radial.png", "judge-flow.png", "onchainid-runs.png",
              "gte-round1.png", "loss-analysis.png", "gte-round2.png", "gte-two-rounds.png",
              "gte-before-after.png", "promis.png", "minutes-per-finding.png", "layers.png",
              "question-status.png"]

if __name__ == "__main__":
    with F.plt.rc_context(F.LIGHT):
        fig_summary()
        fig_onchainid_runs()
        fig_gte_round1()
        fig_promis()
        fig_gte_round2()
        fig_two_rounds()
        fig_loss()
        fig_before_after()
        fig_minutes()
        fig_question_status()
        fig_layers()
    F.contact_sheet()
