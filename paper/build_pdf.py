"""Build REPORT.pdf from REPORT.md: pandoc Markdown -> LaTeX -> PDF with pdflatex.

Run from the paper/ folder:  python3 build_pdf.py
pandoc's default LaTeX article, 11pt, A4, 1in margins, blue links and contents.
REPORT.md is the source.
The intermediate REPORT.tex is kept.
"""

import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
DATE = "November 2026"

FRONT = r"""---
title: "%(title)s"
subtitle: "%(sub)s"
author: "%(author)s"
date: "%(date)s"
lang: en-GB
header-includes:
  - \usepackage{float}
  - \floatplacement{figure}{H}
  - |
    ```{=latex}
    \makeatletter
    \newcommand{\needlines}[1]{\par\penalty-100\begingroup\setlength{\dimen@}{#1\baselineskip}\dimen@ii\pagegoal\advance\dimen@ii-\pagetotal\ifdim\dimen@>\dimen@ii\ifdim\dimen@ii>\z@\vfil\fi\break\fi\endgroup}
    \makeatother
    \widowpenalty=10000
    \clubpenalty=10000
    ```
---

"""


def fit_tables(body):
    """Give each column a width in proportion to its content, and set tables with many
    columns in a smaller size, as papers do, so that no cell runs into the next one."""
    lines, out, i = body.split("\n"), [], 0
    while i < len(lines):
        if lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|\s*$", lines[i + 1]):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines[i:j]]
            n = len(rows[0])
            plain = lambda c: re.sub(r"\[([^\]]*)\]\([^)]*\)|[*`]", r"\1", c)  # noqa: E731
            wide = lambda w: sum(1.35 if ch.isupper() else 1.0 for ch in w)  # noqa: E731
            cells = [r for r in rows if r is not rows[1]]
            longest = [max(wide(plain(r[k])) for r in cells if k < len(r)) for k in range(n)]
            need = [max((wide(w) for r in cells if k < len(r) for w in plain(r[k]).split()), default=3) + 2.5
                    for k in range(n)]
            size = "footnotesize" if n >= 8 else "small" if n >= 5 else None
            room = {"footnotesize": 112, "small": 98, None: 88}[size] - 1.6 * n
            if sum(need) > room and size != "footnotesize":
                size = "footnotesize" if size == "small" else "small"
                room = {"footnotesize": 112, "small": 98}[size] - 1.6 * n
            want = [max(min(longest[k], 36), need[k]) for k in range(n)]
            if sum(want) > room:
                spare = max(room - sum(need), 0)
                extra = [want[k] - need[k] for k in range(n)]
                tot = sum(extra) or 1
                want = [need[k] + spare * extra[k] / tot for k in range(n)]
            sep = "|" + "|".join("-" * max(3, round(w * 2)) for w in want) + "|"
            if size:
                out += ["```{=latex}", "\\begingroup\\" + size + "\\setlength{\\tabcolsep}{4pt}", "```", ""]
            out += [lines[i], sep] + lines[i + 2:j]
            if size:
                out += ["", "```{=latex}", "\\endgroup", "```"]
            i = j
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)


def main():
    src = open(os.path.join(HERE, "REPORT.md"), encoding="utf-8").read()
    m = re.match(r"# (.+)\n\n(.+)\n\n(.+)\n", src)
    full_title, author, meta = m.group(1), m.group(2), m.group(3)
    if "? " in full_title:
        title, _, sub = full_title.partition("? ")
        title += "?"
    else:
        title, _, sub = full_title.partition(": ")
    sub = sub[:1].upper() + sub[1:]
    note = re.sub(r"^(Draft of [^.]*|[A-Z][a-z]+ \d{4})\.\s*", "", meta)
    body = src[m.end():]

    # The hand-written contents list is replaced by LaTeX's own.
    body = re.sub(r"## Contents\n.*?(?=\n<a id=|\n## )", "", body, count=1, flags=re.S)

    # Anchors become labels of the heading that follows them, so the links keep working.
    body = re.sub(r'<a id="([^"]+)"></a>\n\n(#+ [^\n]+)', r"\2 {#\1}", body)

    # An image followed by its italic caption becomes one numbered figure.
    def figure(mm):
        cap = re.sub(r"^Figure \d+\.\s*", "", mm.group(3))
        return f"![{cap}]({mm.group(2)}){{width=84%}}\n"
    body = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)\n\n\*(Figure \d+\..+?)\*\n", figure, body)

    body = fit_tables(body)
    # A heading is never left alone at the foot of a page.
    body = re.sub(r"^(#{2,4} .+)$", r"\\needlines{7}\n\n\1", body, flags=re.M)

    # Characters pdflatex has no glyph for in text mode.
    for a, b in (("→", r"$\rightarrow$"), ("≤", r"$\leq$"), ("≥", r"$\geq$")):
        body = body.replace(a, b)

    md = os.path.join(HERE, "_report_pdf.md")
    front = FRONT % {"title": title, "sub": sub, "author": author, "date": DATE}
    open(md, "w", encoding="utf-8").write(front + (f"**Note.** {note}\n\n" if note.strip() else "") + body)
    common = ["pandoc", md, "--from", "markdown-implicit_header_references", "--toc",
              "--resource-path=.", "-V", "documentclass=article", "-V", "fontsize=11pt",
              "-V", "papersize=a4", "-V", "geometry:margin=1in", "-V", "colorlinks=true",
              "-V", "linkcolor=blue", "-V", "urlcolor=blue", "-V", "toccolor=blue"]
    subprocess.run(common + ["--standalone", "-o", os.path.join(HERE, "REPORT.tex")], check=True, cwd=HERE)
    r = subprocess.run(common + ["--pdf-engine=pdflatex", "-o", os.path.join(HERE, "REPORT.pdf")],
                       cwd=HERE, capture_output=True, text=True)
    os.remove(md)
    if r.returncode:
        print(r.stderr[-2500:])
        raise SystemExit(1)
    warn = [l for l in r.stderr.splitlines() if l.strip()]
    print("wrote", os.path.join(HERE, "REPORT.pdf"), "| messages:", len(warn))
    for l in warn[:10]:
        print("  ", l[:170])


if __name__ == "__main__":
    main()
