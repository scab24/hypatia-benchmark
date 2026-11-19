"""Build REPORT.html from REPORT.md. Local file, no network, figures referenced in place.

Run from the paper/ folder:  python3 build_html.py
Needs pandoc. REPORT.md stays the source: edit it and rebuild.
"""

import os
import re
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

CSS = r"""
:root {
  --bg: #faf9f5; --ink: #1a1a1a; --ink2: #5e5d59; --rule: #dedbd0; --soft: #f0eee6;
  --accent: #b5524d; --hair: #e9e6dd;
  --serif: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  --sans: "Helvetica Neue", Helvetica, Arial, sans-serif;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
main h2, main h3, main h4, main a[id] { scroll-margin-top: 20px; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--serif);
  font-size: 16.5px; line-height: 1.62; -webkit-font-smoothing: antialiased; }
.page { display: grid; grid-template-columns: minmax(0, 1fr); max-width: 1100px;
  margin: 0 auto; padding: 0 24px 120px; }
header.title { max-width: 820px; margin: 96px auto 56px; text-align: center; }
header.title .kicker { font-family: var(--sans); font-size: 13px; letter-spacing: .08em;
  text-transform: uppercase; color: var(--ink2); margin-bottom: 20px; }
header.title h1 { font-family: var(--sans); font-weight: 500; font-size: 36px; line-height: 1.14;
  letter-spacing: -0.015em; margin: 0 0 18px; text-wrap: balance; }
header.title .sub { font-family: var(--sans); font-size: 18px; line-height: 1.4;
  color: var(--ink2); margin: 0 auto 26px; max-width: 660px; text-wrap: balance; }
header.title .author { font-family: var(--sans); font-size: 17px; margin: 0 0 14px; }
header.title .contact { font-family: var(--sans); font-size: 14px; margin: 0 0 18px; }
header.title .contact a { color: var(--ink2); text-decoration: none; margin: 0 9px;
  border-bottom: 1px solid var(--rule); }
header.title .contact a:hover { color: var(--ink); }
header.title .meta { font-family: var(--sans); font-size: 14px; color: var(--ink2);
  max-width: 620px; margin: 0 auto; line-height: 1.5; }
.layout { display: grid; grid-template-columns: 232px minmax(0, 1fr); gap: 64px;
  align-items: start; }
nav.toc { position: sticky; top: 32px; max-height: calc(100vh - 64px); overflow-y: auto;
  font-family: var(--sans); font-size: 13px; line-height: 1.35; padding: 2px 6px 24px 0;
  scrollbar-width: thin; scrollbar-color: var(--rule) transparent; }
nav.toc .label { font-size: 11px; letter-spacing: .1em; text-transform: uppercase;
  color: var(--ink2); margin: 0 0 14px 14px; }
nav.toc ul { list-style: none; margin: 0; padding: 0; }
nav.toc > ul { border-left: 1px solid var(--rule); }
nav.toc li { margin: 0; }
nav.toc a { display: block; padding: 6px 0 6px 14px; margin-left: -1px; color: var(--ink2);
  text-decoration: none; border-left: 1px solid transparent; transition: color .15s; }
nav.toc > ul > li > a { font-weight: 500; }
nav.toc a:hover { color: var(--ink); }
nav.toc a.active { color: var(--ink); border-left-color: var(--accent); }
nav.toc ul ul { max-height: 0; overflow: hidden; opacity: 0;
  transition: max-height .28s ease, opacity .2s ease; }
nav.toc li.open > ul { max-height: 34rem; opacity: 1; padding: 2px 0 8px; }
nav.toc > ul > li { position: relative; }
nav.toc > ul > li > a { padding-right: 30px; }
nav.toc button.chev { all: unset; position: absolute; right: 0; top: 2px; width: 26px; height: 26px;
  display: grid; place-items: center; cursor: pointer; color: var(--ink2); border-radius: 6px; }
nav.toc button.chev:hover { background: var(--soft); color: var(--ink); }
nav.toc button.chev:focus-visible { outline: 2px solid var(--accent); }
nav.toc button.chev svg { width: 10px; height: 10px; transition: transform .2s ease; }
nav.toc li.open > button.chev svg { transform: rotate(90deg); }
nav.toc .tools { display: flex; align-items: center; justify-content: space-between;
  margin: 0 0 12px 14px; }
nav.toc .tools .label { margin: 0; }
nav.toc .tools button, button.toc-open { all: unset; cursor: pointer; font-family: var(--sans);
  font-size: 11.5px; color: var(--ink2); padding: 3px 8px; border-radius: 6px; }
nav.toc .tools button:hover, button.toc-open:hover { background: var(--soft); color: var(--ink); }
button.toc-open { position: fixed; top: 18px; left: 20px; z-index: 12; display: none;
  border: 1px solid var(--rule); background: var(--bg); border-radius: 999px; padding: 7px 14px;
  font-size: 13px; }
body.toc-hidden nav.toc { display: none; }
body.toc-hidden button.toc-open { display: block; }
body.toc-hidden .layout { grid-template-columns: minmax(0, 1fr); justify-items: center; }
body.toc-hidden main { width: 100%; }
nav.toc .tools button[data-toc="hide"] { display: none; }
@media (max-width: 960px) { nav.toc .tools button[data-toc="hide"] { display: inline-block; } }
@media (min-width: 961px) { body.toc-hidden nav.toc { display: block; } body.toc-hidden button.toc-open { display: none; }
  body.toc-hidden .layout { grid-template-columns: 232px minmax(0, 1fr); justify-items: stretch; } }
@media print { button.toc-open { display: none !important; } }
nav.toc ul ul a { padding: 4px 0 4px 26px; font-size: 12.5px; font-weight: 400; }
#progress { position: fixed; top: 0; left: 0; height: 2px; width: 0; background: var(--accent);
  z-index: 20; }
@media print { #progress { display: none; } }
main { max-width: 700px; min-width: 0; }
main h2 { font-family: var(--sans); font-weight: 500; font-size: 25px; line-height: 1.2;
  letter-spacing: -0.01em; margin: 72px 0 18px; padding-top: 28px;
  border-top: 1px solid var(--rule); }
main h2:first-of-type { margin-top: 0; }
main h3 { font-family: var(--sans); font-weight: 500; font-size: 18.5px; line-height: 1.3;
  margin: 44px 0 12px; }
main h4 { font-family: var(--sans); font-weight: 600; font-size: 15.5px; margin: 30px 0 8px; }
main p { margin: 0 0 18px; }
main ul, main ol { margin: 0 0 18px; padding-left: 24px; }
main li { margin-bottom: 6px; }
main a { color: var(--ink); text-decoration: underline; text-decoration-color: #b9b6aa;
  text-underline-offset: 3px; }
main a:hover { text-decoration-color: var(--ink); }
main strong { font-weight: 600; }
code { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: .86em;
  background: var(--soft); padding: 1px 5px; border-radius: 4px; }
pre { background: var(--soft); padding: 14px 16px; border-radius: 8px; overflow-x: auto;
  font-size: 14px; line-height: 1.5; }
pre code { background: none; padding: 0; }
p.q { font-family: var(--sans); font-size: 17px; line-height: 1.45; margin: 4px 0 22px; }
p.q strong, p.concl strong, p.part strong { font-family: var(--sans); font-size: 12px;
  font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--ink2);
  display: block; margin-bottom: 4px; }
p.part { margin-top: 26px; }
p.concl { background: var(--soft); border-radius: 10px; padding: 16px 20px; margin: 26px 0 8px;
  font-family: var(--sans); font-size: 15px; line-height: 1.5; }
section.card { border: 1px solid var(--rule); border-radius: 12px; padding: 18px 22px 8px;
  margin: 0 0 16px; border-left-width: 4px; }
section.card h4 { margin: 0 0 10px; font-size: 12px; letter-spacing: .08em;
  text-transform: uppercase; font-weight: 600; color: var(--ink2); }
section.card ul { font-family: var(--sans); font-size: 15.5px; line-height: 1.5;
  padding-left: 18px; margin-bottom: 10px; }
section.card.good { border-left-color: #40668c; }
section.card.bad { border-left-color: var(--accent); }
section.card.note { border-left-color: #b4b1a6; }
.table-wrap { margin: 10px 0 30px; }
.table-wrap.wide table { font-size: 12px; }
.table-wrap.wide thead th, .table-wrap.wide tbody td { padding-right: 10px; }
@media (min-width: 1100px) { .table-wrap.wide { margin-right: -70px; } }
table th, table td { overflow-wrap: break-word; hyphens: manual; }
table { border-collapse: collapse; width: 100%; font-family: var(--sans); font-size: 13.5px;
  line-height: 1.45; font-variant-numeric: tabular-nums; border-top: 1.5px solid var(--ink);
  border-bottom: 1.5px solid var(--ink); }
thead th { text-align: left; font-weight: 600; padding: 10px 18px 9px 0;
  border-bottom: 0.75px solid var(--ink); vertical-align: bottom; }
tbody td { padding: 9px 18px 9px 0; border-bottom: 1px solid var(--hair); vertical-align: top; }
tbody tr:first-child td { padding-top: 11px; }
tbody tr:last-child td { border-bottom: 0; padding-bottom: 11px; }
thead th:last-child, tbody td:last-child { padding-right: 0; }
td.num, th.num { text-align: right; }
td.num { white-space: nowrap; }
td.dash { color: var(--ink2); }
figure { margin: 34px 0 34px; }
figure img { display: block; width: 100%; height: auto; border: 1px solid var(--rule);
  border-radius: 10px; }
figcaption { font-family: var(--sans); font-size: 13px; line-height: 1.5; color: var(--ink2);
  margin-top: 12px; }
figcaption b { color: var(--ink); font-weight: 600; }
@media (min-width: 1100px) { figure { margin-right: -70px; } }
@media (max-width: 960px) {
  .layout { grid-template-columns: minmax(0, 1fr); }
  nav.toc { position: fixed; inset: 0 auto 0 0; width: min(86vw, 320px); max-height: none; z-index: 15;
    background: var(--bg); border-right: 1px solid var(--rule); padding: 64px 14px 24px 10px;
    box-shadow: 0 0 40px rgba(0,0,0,.18); top: 0; }
  header.title { margin-top: 56px; }
  header.title h1 { font-size: 32px; }
  body { font-size: 17px; }
}
@media (max-width: 720px) {
  /* A table or a figure wider than the screen scrolls sideways inside its own box. */
  .table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; margin-left: -20px;
    margin-right: -20px; padding: 0 20px; }
  /* Edge shadows that appear only while there is more of the table to the side. */
  .table-wrap { background:
    linear-gradient(90deg, var(--bg) 40%, transparent) 0 0 / 34px 100% no-repeat local,
    linear-gradient(270deg, var(--bg) 40%, transparent) 100% 0 / 34px 100% no-repeat local,
    linear-gradient(90deg, rgba(120,120,120,.28), transparent) 0 0 / 12px 100% no-repeat scroll,
    linear-gradient(270deg, rgba(120,120,120,.28), transparent) 100% 0 / 12px 100% no-repeat scroll; }
  .table-wrap table { min-width: calc(var(--cols, 3) * 96px); font-size: 12.5px; }
  .table-wrap.wide table { min-width: calc(var(--cols, 7) * 82px); font-size: 12px; }
  thead th, tbody td { padding-right: 12px; }
  figure { margin: 26px -20px; }
  /* A figure fills the width of the screen. Touching it opens the full image. */
  figure a { display: block; }
  figure img { width: 100%; border-radius: 0; border-left: 0; border-right: 0; }
  figcaption { padding: 0 20px; font-size: 13px; line-height: 1.5; }
  figcaption::after { content: " Touch the figure to enlarge it."; color: var(--ink2); opacity: .8; }
  header.title { margin: 44px auto 36px; }
  header.title h1 { font-size: 27px; line-height: 1.18; }
  header.title h1, header.title .sub { text-wrap: balance; }
  header.title .links a { white-space: nowrap; }
  header.title .sub { font-size: 16px; }
  body { font-size: 16.5px; }
  h2 { font-size: 23px; }
  h3 { font-size: 18.5px; }
  p.concl { padding: 14px 16px; }
  pre { font-size: 12px; }
}
@media print { nav.toc { display: none; } .layout { display: block; }
  figure { margin-right: 0; break-inside: avoid; } }
:root[data-theme="dark"] { --bg: #171614; --ink: #ece9e1; --ink2: #a3a097; --rule: #383631;
  --soft: #24231f; --accent: #e0655f; --hair: #2e2c28; }
:root[data-theme="dark"] main a { text-decoration-color: #6a675f; }
:root[data-theme="dark"] figure img { filter: invert(0.91) hue-rotate(180deg) saturate(1.15);
  border-color: #c9c6bb; }
button.theme { position: fixed; top: 18px; right: 20px; z-index: 10; font-family: var(--sans);
  font-size: 13px; color: var(--ink2); background: var(--bg); border: 1px solid var(--rule);
  border-radius: 999px; padding: 7px 14px; cursor: pointer; }
button.theme:hover { color: var(--ink); }
@media print { button.theme { display: none; } }
"""

JS = r"""
const links = [...document.querySelectorAll('nav.toc a')];
const map = new Map(links.map(a => [a.getAttribute('href').slice(1), a]));
const heads = [...document.querySelectorAll('main h2[id], main h3[id]')];
const tops = [...document.querySelectorAll('nav.toc > ul > li')];
const bar = document.getElementById('progress');
const CHEV = '<svg viewBox="0 0 10 10" aria-hidden="true"><path d="M3 1.5 6.5 5 3 8.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
// A section the reader opened or closed by hand keeps that state; the others follow the scroll.
tops.forEach(li => {
  if (!li.querySelector(':scope > ul')) return;
  const b = document.createElement('button');
  b.type = 'button'; b.className = 'chev'; b.innerHTML = CHEV;
  b.setAttribute('aria-label', 'Show or hide the subsections');
  b.addEventListener('click', () => {
    const open = !li.classList.contains('open');
    li.classList.toggle('open', open); li.dataset.pinned = open ? 'open' : 'closed';
    b.setAttribute('aria-expanded', open);
  });
  li.insertBefore(b, li.querySelector(':scope > ul'));
});
const allBtn = document.querySelector('[data-toc="all"]');
allBtn.addEventListener('click', () => {
  const expand = allBtn.textContent === 'Expand all';
  tops.forEach(li => { if (li.querySelector(':scope > ul')) { li.classList.toggle('open', expand); li.dataset.pinned = expand ? 'open' : 'closed'; } });
  if (!expand) { tops.forEach(li => delete li.dataset.pinned); spy(); }
  allBtn.textContent = expand ? 'Collapse all' : 'Expand all';
});
const small = () => matchMedia('(max-width: 960px)').matches;
const setToc = (hidden, save) => {
  document.body.classList.toggle('toc-hidden', hidden);
  if (save) { try { localStorage.setItem('report-toc', hidden ? 'hidden' : 'shown'); } catch (e) {} }
};
let tocSaved = null;
try { tocSaved = localStorage.getItem('report-toc'); } catch (e) {}
setToc(small(), false);
addEventListener('resize', () => { if (!small()) setToc(false, false); });
document.querySelector('[data-toc="hide"]').addEventListener('click', () => setToc(true, false));
document.querySelector('button.toc-open').addEventListener('click', () => setToc(false, false));
links.forEach(a => a.addEventListener('click', () => { if (small()) setToc(true, false); }));
function spy() {
  let cur = heads[0];
  for (const h of heads) { if (h.getBoundingClientRect().top < 130) cur = h; }
  links.forEach(a => a.classList.remove('active'));
  const a = cur && map.get(cur.id);
  if (a) {
    a.classList.add('active');
    const top = a.closest('nav.toc > ul > li');
    tops.forEach(li => { if (!li.dataset.pinned) li.classList.toggle('open', li === top); });
    const first = top && top.querySelector(':scope > a');
    if (first && first !== a) { first.classList.add('active'); }
  }
  const max = document.documentElement.scrollHeight - innerHeight;
  bar.style.width = (max > 0 ? 100 * scrollY / max : 0) + '%';
}
document.addEventListener('scroll', spy, { passive: true });
spy();
const root = document.documentElement, btn = document.querySelector('button.theme');
const apply = t => { root.dataset.theme = t; btn.textContent = t === 'dark' ? 'Light' : 'Dark'; };
let saved = null;
try { saved = localStorage.getItem('report-theme'); } catch (e) {}
apply(saved || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
btn.addEventListener('click', () => {
  const t = root.dataset.theme === 'dark' ? 'light' : 'dark';
  apply(t);
  try { localStorage.setItem('report-theme', t); } catch (e) {}
});
"""

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>__CSS__</style>
</head>
<body>
<div id="progress"></div>
<button class="toc-open" type="button" aria-label="Show contents">Contents</button>
<button class="theme" type="button">Dark</button>
<div class="page">
<header class="title">
<div class="kicker">Research report</div>
<h1>__HEAD__</h1>
<p class="sub">__SUB__</p>
<p class="author">__AUTHOR__</p>
<p class="contact"><a href="mailto:git.seco@protonmail.com">git.seco@protonmail.com</a>
<a href="https://x.com/Seecoalba">X</a>
<a href="https://www.linkedin.com/in/sergio-corrales-alonso-barajas-52b6911a0/">LinkedIn</a>
<a href="https://github.com/scab24">GitHub</a></p>
<p class="meta">__META__</p>
</header>
<div class="layout">
<nav class="toc" aria-label="Contents"><div class="tools"><div class="label">Contents</div><span><button type="button" data-toc="all">Expand all</button><button type="button" data-toc="hide" aria-label="Close contents">Close</button></span></div>
$table-of-contents$
</nav>
<main>
$body$
</main>
</div>
</div>
<script>__JS__</script>
</body>
</html>
"""


NUM = re.compile(r"^[\d.,]+( of \d+)?%?$")


def style_cells(html):
    """Approach letters become badges, numbers align right, and a column is right-aligned
    when every body cell in it is a number."""
    def table(m):
        t = m.group(0)
        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", t, flags=re.S)
        body = [re.findall(r"<td[^>]*>(.*?)</td>", r, flags=re.S) for r in rows]
        body = [r for r in body if r]
        ncol = max((len(r) for r in body), default=0)
        numeric = [all(len(r) > i and (NUM.match(re.sub(r"<[^>]+>", "", r[i]).strip()) or
                                       not r[i].strip()) for r in body) and
                   any(len(r) > i and r[i].strip() for r in body) for i in range(ncol)]

        def row(rm):
            i = -1

            def cell(cm):
                nonlocal i
                i += 1
                tag, inner = cm.group(1), cm.group(2)
                plain = re.sub(r"<[^>]+>", "", inner).strip()
                cls = "num" if i < ncol and numeric[i] and i > 0 else ""
                if tag == "td" and plain in ("–", "-"):
                    cls = (cls + " dash").strip()
                return f'<{tag} class="{cls}">{inner}</{tag}>' if cls else f"<{tag}>{inner}</{tag}>"
            return "<tr>" + re.sub(r"<(t[dh])[^>]*>(.*?)</t[dh]>", cell, rm.group(1), flags=re.S) + "</tr>"
        return re.sub(r"<tr[^>]*>(.*?)</tr>", row, t, flags=re.S)
    return re.sub(r"<table>.*?</table>", table, html, flags=re.S)


def png_size(path):
    """Width and height of a PNG, so the page reserves the space before the image loads."""
    import struct
    with open(path, "rb") as fh:
        head = fh.read(24)
    return struct.unpack(">II", head[16:24])


def main():
    src = open(os.path.join(HERE, "REPORT.md"), encoding="utf-8").read()

    # Title block: "# Head? Sub" then one draft line.
    m = re.match(r"# (.+)\n\n(.+)\n\n(.+)\n", src)
    full_title, author, meta = m.group(1), m.group(2), m.group(3)
    if "? " in full_title:
        head, _, sub = full_title.partition("? ")
        head += "?"
    else:
        head, _, sub = full_title.partition(": ")
    sub = sub[:1].upper() + sub[1:]
    body = src[m.end():]

    # The hand-written contents list is replaced by the generated one.
    body = re.sub(r"## Contents\n.*?(?=\n<a id=|\n## )", "", body, count=1, flags=re.S)

    # An image followed by its italic caption becomes one figure.
    def figure(mm):
        alt, path, cap = mm.group(1), mm.group(2), mm.group(3)
        cap = re.sub(r"^(Figure \d+\.)", r"<b>\1</b>", cap)
        cap = re.sub(r"\(section (\d+)\.(\d+)\)", r'(<a href="#sec-\1-\2">section \1.\2</a>)', cap)
        w, h = png_size(os.path.join(HERE, path))
        src = f"{path}?v={int(os.path.getmtime(os.path.join(HERE, path)))}"
        return (f'<figure><a href="{path}"><img src="{src}" alt="{alt}" width="{w}" height="{h}"></a>'
                f"<figcaption>{cap}</figcaption></figure>\n")
    body = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)\n\n\*(Figure \d+\..+?)\*\n", figure, body)

    with tempfile.TemporaryDirectory() as tmp:
        tpl = os.path.join(tmp, "t.html")
        md = os.path.join(tmp, "body.md")
        page = (TEMPLATE.replace("__CSS__", CSS).replace("__JS__", JS)
                .replace("__TITLE__", full_title).replace("__HEAD__", head)
                .replace("__SUB__", sub).replace("__META__", meta)
                .replace("__AUTHOR__", author))
        open(tpl, "w", encoding="utf-8").write(page)
        open(md, "w", encoding="utf-8").write(body)
        html = subprocess.run(
            ["pandoc", md, "-f", "gfm+smart", "-t", "html5", "--toc", "--toc-depth=3",
             "--template", tpl, "--wrap=none"],
            check=True, capture_output=True, text=True).stdout

    for label, cls in (("Question", "q"), ("Conclusion", "concl")):
        html = html.replace(f"<p><strong>{label}.</strong>", f'<p class="{cls}"><strong>{label}.</strong>')
    html = re.sub(r"<p><strong>(Method|Results|Reading)\.</strong>",
                  r'<p class="part"><strong>\1.</strong>', html)
    for label, cls in (("What works", "good"), ("What does not", "bad"),
                       ("What to keep in mind", "note")):
        html = re.sub(rf"<p><strong>{label}</strong></p>\s*(<ul>.*?</ul>)",
                      rf'<section class="card {cls}"><h4>{label}</h4>\1</section>', html,
                      count=1, flags=re.S)
    html = style_cells(html)
    def wrap_table(m):
        cols = len(re.findall(r"<th[ >]", m.group(0).split("</thead>")[0]))
        return (f'<div class="table-wrap{" wide" if cols >= 7 else ""}" style="--cols:{cols}">'
                + m.group(0) + "</div>")
    html = re.sub(r"<table>.*?</table>", wrap_table, html, flags=re.S)
    out = os.path.join(HERE, "REPORT.html")
    open(out, "w", encoding="utf-8").write(html)
    print("wrote", out, f"({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
