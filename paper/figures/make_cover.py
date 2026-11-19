"""Cover image for the article, 1600 x 900: the study at a glance, on a warm ground.

Run from the paper/ folder:  python3 figures/make_cover.py
Every number comes from the data literals of make_figures.py or from the strict
matches of scoring/gte/r1/ADJUDICATION.md (the lit dots).
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, PathPatch, Rectangle  # noqa: E402
from matplotlib.path import Path  # noqa: E402

import make_figures as F  # noqa: E402

W, H = 16, 9
BG0 = "#e9e3d5"
TXT, MUT, DIMC, RULE, LINE = "#1f1e1b", "#6f6b60", "#a39c8a", "#d3cbb8", "#dcd4c2"
COL = {"A": "#a9a393", "B": "#40668c", "C": "#d9584f"}
NAME = {"A": "AI model alone", "B": "with Hypatia", "C": "with Hypatia and a code map"}
IDS = [f"H-{i:02d}" for i in range(1, 11)] + [f"M-{i:02d}" for i in range(1, 26)]
FOUND = {"A": "H-01 H-04 H-06 H-07 H-08 H-09 M-12 M-17".split(),
         "B": "H-01 H-04 H-06 H-07 H-09 M-04 M-12 M-15 M-16 M-17".split(),
         "C": "H-01 H-03 H-04 H-05 H-06 H-07 H-08 M-02 M-04 M-12 M-15 M-16 M-17 M-19 M-23".split()}
MED = F.TITLE_WEIGHT


def box(ax, x, y, w, h, c, r=0.07, z=4, alpha=1.0):
    if w <= 0 or h <= 0:
        return
    r = min(r, w / 2, h / 2)
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", facecolor=c,
                                edgecolor="none", zorder=z, alpha=alpha))


def glow_bar(ax, x, y, w, h, c, vertical=True):
    """A bar with a soft halo, square at its baseline."""
    box(ax, x, y, w, h, c)
    if vertical:
        ax.add_patch(Rectangle((x, y), w, min(h, 0.08), facecolor=c, edgecolor="none", zorder=4))
    else:
        ax.add_patch(Rectangle((x, y), min(w, 0.08), h, facecolor=c, edgecolor="none", zorder=4))


def curve(ax, x1, y1, x2, y2):
    mx = (x1 + x2) / 2
    ax.add_patch(PathPatch(Path([(x1, y1), (mx, y1), (mx, y2), (x2, y2)],
                                [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]),
                           facecolor="none", edgecolor=LINE, linewidth=1.4, zorder=1))


def tree(ax, x, y, depth, spread, step):
    """A path tree in line art, behind the charts."""
    ax.add_patch(plt.Circle((x, y), 0.055, color=LINE, zorder=1))
    if depth:
        for dy in (spread, -spread):
            curve(ax, x, y, x + step, y + dy)
            tree(ax, x + step, y + dy, depth - 1, spread * 0.5, step)


def head(ax, x, y, s):
    ax.text(x, y, s.upper(), ha="left", va="center", fontsize=11.5, color=MUT, fontfamily="Menlo", zorder=8)


def main():
    fig = plt.figure(figsize=(W, H), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    fig.patch.set_facecolor(BG0)
    tree(ax, 0.45, 4.6, 5, 2.15, 3.02)
    rend = fig.canvas.get_renderer()
    wid = lambda t: t.get_window_extent(renderer=rend).width / 100  # noqa: E731

    with plt.rc_context(F.LIGHT):
        # ---- key
        kx = 0.9
        for a in "ABC":
            box(ax, kx, 8.2, 0.24, 0.24, COL[a], r=0.05, z=8)
            t = ax.text(kx + 0.36, 8.32, NAME[a], ha="left", va="center", fontsize=14.5, color=TXT, zorder=8)
            kx += 0.36 + wid(t) + 0.55

        # ---- A. grouped bars, three projects
        head(ax, 0.9, 7.55, "Reported vulnerabilities found, by project")
        base, scale, bw, gap = 4.25, 5.9, 0.64, 0.1
        ax.plot([0.9, 9.0], [base, base], color=TXT, lw=1.2, zorder=5)
        for lv in (0.2, 0.4):
            ax.plot([0.9, 9.0], [base + scale * lv] * 2, color=RULE, lw=0.8, zorder=1)
            ax.text(9.0, base + scale * lv + 0.08, f"{int(lv * 100)}%", ha="right", va="bottom", fontsize=10,
                    color=DIMC, zorder=2)
        groups = [("ONCHAINID", "of 12 · 2,058 lines · mean of 3 runs", 12, F.ONCHAINID_SEVERE),
                  ("Promis", "of 9 · 3,921 lines", 9, {"A": [2], "B": [2], "C": [4]}),
                  ("GTE", "of 35 · 5,260 lines", 35, {"A": [8], "B": [10], "C": [15]})]
        x0 = 1.2
        for name, sub, n, vals in groups:
            for i, a in enumerate("ABC"):
                k = sum(vals[a]) / len(vals[a])
                x = x0 + i * (bw + gap)
                glow_bar(ax, x, base, bw, scale * k / n, COL[a])
                ax.text(x + bw / 2, base + scale * k / n + 0.1, F.fmt(k), ha="center", va="bottom",
                        fontsize=21, fontweight=MED, color=TXT, zorder=8)
            cx = x0 + 1.5 * bw + gap
            ax.text(cx, base - 0.26, name, ha="center", va="top", fontsize=15.5, fontweight=MED, color=TXT)
            ax.text(cx, base - 0.62, sub, ha="center", va="top", fontsize=11, color=MUT)
            x0 += 2.68

        # ---- B. the question list, one cell per question
        head(ax, 0.9, 2.95, "804 questions derived from the code in one audit")
        cols = 67
        pitch = 8.1 / cols
        kinds = [(86, COL["C"]), (63, TXT), (649, "#bdb5a2"), (6, None)]
        cells = [c for n, c in kinds for _ in range(n)]
        for i, c in enumerate(cells):
            r, q = divmod(i, cols)
            ax.add_patch(Rectangle((0.9 + q * pitch, 2.52 - r * pitch), pitch * 0.72, pitch * 0.72,
                                   facecolor=c or BG0, edgecolor="none" if c else MUT, linewidth=0.6, zorder=4))
        tx, ty = 0.9, 2.52 - 12 * pitch - 0.1
        for n, c, t in ((86, COL["C"], "decided by a test"), (63, TXT, "inherited"),
                        (649, "#bdb5a2", "argued"), (6, None, "open")):
            ax.add_patch(Rectangle((tx, ty - 0.065), 0.13, 0.13, facecolor=c or BG0,
                                   edgecolor="none" if c else MUT, linewidth=0.7, zorder=8))
            t_ = ax.text(tx + 0.21, ty, f"{n} {t}", ha="left", va="center", fontsize=11.5, color=MUT, zorder=8)
            tx += 0.21 + wid(t_) + 0.4

        ax.plot([9.5, 9.5], [0.6, 8.45], color=RULE, lw=1.0, zorder=2)
        RX, RW = 9.95, 5.15

        # ---- C. which of the 35 each one found
        head(ax, RX, 8.3, "Which of the 35 in GTE each one found")
        pitch35, gap35 = (RW - 0.22) / 34.6, 0.22
        for r, a in enumerate("ABC"):
            y = 7.72 - r * 0.42
            hits = {IDS.index(i) for i in FOUND[a]}
            for i in range(35):
                x = RX + 0.07 + i * pitch35 + (gap35 if i >= 10 else 0)
                if i in hits:
                    ax.scatter(x, y, s=46, color=COL[a], zorder=5, linewidths=0)
                else:
                    ax.scatter(x, y, s=20, facecolor="none", edgecolor=DIMC, linewidths=1.0, zorder=4)
        ax.text(RX + 0.07 + 4.5 * pitch35, 6.52, "10 High", ha="center", va="center", fontsize=10.5, color=MUT)
        ax.text(RX + 0.07 + 22 * pitch35 + gap35, 6.52, "25 Medium", ha="center", va="center", fontsize=10.5,
                color=MUT)

        # ---- D. continued audit
        head(ax, RX, 5.75, "New findings when the audit continued")
        for i, a in enumerate("ABC"):
            y = 5.22 - i * 0.44
            k = sum(F.GTE2[a])
            glow_bar(ax, RX, y - 0.13, RW * 0.78 * k / 13, 0.26, COL[a], vertical=False)
            ax.text(RX + RW * 0.78 * k / 13 + 0.16, y, str(k), ha="left", va="center", fontsize=18,
                    fontweight=MED, color=TXT, zorder=8)

        # ---- E. where missed findings were lost, by step of the audit
        head(ax, RX, 3.35, "Where the 20 missed findings were lost")
        steps = [("Map", 0), ("Ask", 7), ("Decide", 1), ("Prove", 8), ("Report", 4)]
        b2, sc2, cw = 1.2, 0.2, 0.62
        ax.plot([RX, RX + RW], [b2, b2], color=TXT, lw=1.2, zorder=5)
        for i, (name, k) in enumerate(steps):
            x = RX + 0.2 + i * (RW - 0.4) / 5 + ((RW - 0.4) / 5 - cw) / 2
            if k:
                glow_bar(ax, x, b2, cw, sc2 * k, COL["C"])
            ax.text(x + cw / 2, b2 + sc2 * k + 0.08, str(k), ha="center", va="bottom", fontsize=17,
                    fontweight=MED, color=TXT, zorder=8)
            ax.text(x + cw / 2, b2 - 0.22, name, ha="center", va="top", fontsize=12, color=MUT)
            if i < 4:
                ax.annotate("", xy=(x + cw + 0.34, b2 - 0.36), xytext=(x + cw + 0.06, b2 - 0.36),
                            arrowprops=dict(arrowstyle="-|>", color=DIMC, lw=0.9, mutation_scale=8))
    fig.savefig(F.os.path.join(F.OUT, "cover.png"), dpi=100, facecolor=BG0)
    print("wrote cover.png")


if __name__ == "__main__":
    main()
