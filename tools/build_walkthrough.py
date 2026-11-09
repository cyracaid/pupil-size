"""Build the line-by-line code walkthrough site (代码讲解/index.html).

Run:  python3 构建_代码讲解.py
Then open 代码讲解/index.html in a browser.

The content lives in 讲解内容.py: for every file a summary and a list of
blocks, each block = a line range plus the explanation. Files without blocks
still get a page with their full source, so the map is complete from day one.
"""
import html
import pathlib
import shutil

import os
from walkthrough_content import CONTENT, STAGES, FILES

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
CODE = pathlib.Path(os.environ.get("WALK_CODE", REPO.parent.parent / "代码_matlab"))
OUT = REPO / "walkthrough"

E = html.escape


def read_lines(rel):
    base = REPO if rel.startswith("code/") else CODE
    raw = (base / rel).read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:          # upstream files are partly latin-1
        text = raw.decode("cp1252", errors="replace")
    return text.split("\n")


def code_block(lines, a, b, cls="code"):
    """Lines a..b inclusive, 1-based, with line numbers."""
    out = ['<div class="%s"><table>' % cls]
    for n in range(a, b + 1):
        if n - 1 >= len(lines):
            break
        out.append('<tr><td class="ln">%d</td><td class="src">%s</td></tr>'
                   % (n, E(lines[n - 1]).replace("\t", "    ") or "&nbsp;"))
    out.append("</table></div>")
    return "\n".join(out)


def file_section(rel, meta, lines):
    fid = rel.replace("/", "-").replace(".", "-")
    parts = ['<article id="%s" class="file">' % fid]
    parts.append('<h2><code>%s</code> <span class="lines">%d 行</span></h2>'
                 % (E(rel), len(lines)))
    parts.append('<p class="summary">%s</p>' % meta.get("summary", ""))
    blocks = meta.get("blocks", [])
    covered = 0
    for a, b, note in blocks:
        parts.append(code_block(lines, a, b))
        parts.append('<div class="note">%s</div>' % note)
        covered += b - a + 1
    if meta.get("data"):
        parts.append('<div class="datawalk"><h3>落到你的数据上</h3>%s</div>' % meta["data"])
    if blocks:
        parts.append('<details class="full"><summary>看完整原文（%d 行，已逐行讲解 %d 行）</summary>%s</details>'
                     % (len(lines), covered, code_block(lines, 1, len(lines))))
    else:
        parts.append('<p class="todo">这个文件还没有逐行讲解，下面是完整原文。</p>')
        parts.append(code_block(lines, 1, len(lines)))
    parts.append("</article>")
    return fid, "\n".join(parts)


def build_map():
    cards = []
    for st in STAGES:
        chips = "".join(
            '<a class="chip" href="#%s">%s<span>%d</span></a>'
            % (rel.replace("/", "-").replace(".", "-"), E(rel), n)
            for rel, n in st["files"])
        cards.append(
            '<div class="stage"><div class="snum">%s</div>'
            '<div class="sname">%s</div><div class="sdesc">%s</div>'
            '<div class="chips">%s</div></div>'
            % (E(st["num"]), E(st["name"]), st["desc"], chips))
    return '<div class="map">%s</div>' % '<div class="arrow">→</div>'.join(cards)


def build():
    OUT.mkdir(exist_ok=True)
    sections, toc = [], []
    for rel, n in FILES:
        meta = CONTENT.get(rel, {})
        lines = read_lines(rel)
        fid = rel.replace("/", "-").replace(".", "-")
        toc.append('<a class="toc-item" href="#%s"><b>%s</b><span>%d 行</span></a>'
                   % (fid, E(rel), len(lines)))
        fid2, sec = file_section(rel, meta, lines)
        sections.append(sec)

    HEAD = """<!doctype html>
<html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>YMTC 代码讲解 · 逐行</title>
<style>
:root{--bg:#fbfaf7;--ink:#1d1d1f;--dim:#6b6b70;--line:#e3e0d8;--accent:#2f6f4f;--code:#f4f2ec}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
 font:16px/1.65 -apple-system,"Helvetica Neue","PingFang SC",sans-serif}
header{padding:36px 40px 8px;border-bottom:1px solid var(--line)}
h1{margin:0 0 6px;font-size:28px;letter-spacing:.3px}
.sub{color:var(--dim);margin:0 0 4px}
.layout{display:flex;gap:0;align-items:flex-start}
nav{position:sticky;top:0;width:260px;flex:0 0 260px;max-height:100vh;overflow:auto;
 padding:20px 14px 60px;border-right:1px solid var(--line);font-size:14px}
nav h3{margin:18px 0 6px;font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:var(--dim)}
.toc-item{display:flex;justify-content:space-between;gap:8px;padding:5px 8px;border-radius:6px;
 color:var(--ink);text-decoration:none}
.toc-item span{color:var(--dim);font-variant-numeric:tabular-nums}
.toc-item:hover,.toc-item.on{background:#efede6}
main{flex:1;min-width:0;padding:24px 40px 120px;max-width:1040px}
.map{display:flex;flex-wrap:wrap;align-items:stretch;gap:10px;margin:18px 0 8px}
.stage{flex:1 1 180px;background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px 14px;
 box-shadow:0 1px 2px rgba(0,0,0,.04)}
.snum{font:600 12px/1 ui-monospace,monospace;color:var(--accent);letter-spacing:.08em}
.sname{font-weight:600;margin:4px 0 2px}
.sdesc{font-size:13px;color:var(--dim);margin-bottom:8px}
.chip{display:inline-flex;gap:6px;align-items:center;margin:3px 6px 0 0;padding:2px 8px;border-radius:999px;
 background:#f2f0ea;color:var(--ink);text-decoration:none;font:12px ui-monospace,monospace}
.chip span{color:var(--dim)}
.chip:hover{background:#e7e3d8}
.arrow{align-self:center;color:var(--dim);font-size:18px}
.file{margin:56px 0 0;padding-top:8px;border-top:1px solid var(--line)}
.file h2{font-size:20px;margin:0 0 4px}
.file h2 code{font-size:20px}
.lines{font-weight:400;color:var(--dim);font-size:14px}
.summary{color:#333;margin:6px 0 18px}
.code{margin:14px 0 0;background:var(--code);border:1px solid var(--line);border-radius:10px;overflow:auto}
.code table{border-collapse:collapse;font:13px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace;width:100%}
.ln{width:1%;padding:0 10px;text-align:right;color:#a9a49a;user-select:none;vertical-align:top;
 border-right:1px solid #e7e3d8;background:#efece4}
.src{padding:0 12px;white-space:pre;vertical-align:top}
.note{margin:10px 0 26px;padding:12px 16px;background:#fff;border-left:3px solid var(--accent);
 border-radius:0 8px 8px 0;font-size:15px}
.note ul{margin:6px 0;padding-left:22px}
.note li{margin:3px 0}
.note code,.summary code,p code{background:#eee9dd;padding:1px 4px;border-radius:4px;
 font:12.5px ui-monospace,monospace}
.todo{color:var(--dim);font-style:italic}
details.full{margin:26px 0 40px}
details.full summary{cursor:pointer;color:var(--dim);font-size:14px}
.rtip{margin:0}
.datawalk{margin:26px 0 8px;padding:16px 20px;background:#eef4ee;border:1px solid #d3e2d3;
 border-radius:12px}
.datawalk h3{margin:0 0 8px;font-size:16px;color:#2f6f4f}
.datawalk table{border-collapse:collapse;margin:8px 0;font-size:14px}
.datawalk th,.datawalk td{border:1px solid #cfe0cf;padding:4px 10px;text-align:left}
.datawalk th{background:#e3eee3}
footer{color:var(--dim);font-size:13px;padding:0 40px 60px}
@media(max-width:860px){nav{display:none}main{padding:16px 18px 80px}header{padding:20px}}
</style></head><body>
<header>
<h1>YMTC 代码讲解</h1>
<p class="sub">从 <code>.trk</code> 到 <code>06_all_merged.csv</code>，每个文件、每一段代码在做什么，以及为什么这么写。</p>
<p class="sub">写给会 R、没写过 MATLAB 的读者。点上面的方块跳文件，点左边的目录跳章节。</p>
</header>
<div class="layout">
<nav><h3>流程图</h3><a class="toc-item" href="#map">回到总图</a>
<h3>文件</h3>
""" + "".join(toc) + """
</nav>
<main>
<section id="map">""" + build_map() + """</section>
""" + "".join(sections) + """
</main>
</div>
<footer>由 <code>构建_代码讲解.py</code> 生成 · 内容在 <code>讲解内容.py</code></footer>
<script>
const items=[...document.querySelectorAll('.toc-item')];
const obs=new IntersectionObserver(function(entries){
  entries.forEach(function(e){
    if(e.isIntersecting){
      items.forEach(function(i){ i.classList.toggle('on', i.getAttribute('href')==='#'+e.target.id); });
    }
  });
},{rootMargin:'-20% 0px -70% 0px'});
document.querySelectorAll('article.file').forEach(function(a){ obs.observe(a); });
</script>
</body></html>"""
    doc = HEAD
    (OUT / "index.html").write_text(doc, encoding="utf-8")
    print("built", OUT / "index.html", len(doc) // 1024, "KB")


if __name__ == "__main__":
    build()
