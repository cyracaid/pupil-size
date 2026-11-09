"""Builds the documentation site into site/ from code/README.md content and docs/*.md.

Run: python3 tools/build_site.py   (needs: pip install markdown-it-py)
"""
import importlib.util, pathlib, re, html, shutil
from markdown_it import MarkdownIt

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
SITE = REPO / "site"
GH = "https://github.com/cyracaid/pupil-size/blob/ymtc-trk2csv/"

# reuse the content builder (importing it does not write anything)
spec = importlib.util.spec_from_file_location("bigreadme", HERE / "build_readme.py")
big = importlib.util.module_from_spec(spec)
spec.loader.exec_module(big)

md = MarkdownIt("commonmark", {"html": True}).enable("table")

GUIDES = [
    ("01", "01_pipeline_overview.md", "zh/01_流程总览.md", ("Pipeline overview", "파이프라인 개요", "流程总览")),
    ("02", "02_column_dictionary.md", "zh/02_列字典.md", ("Column dictionary", "열 사전", "列字典")),
    ("03", "03_pupil_size_internals.md", "zh/03_瞳孔算法.md", ("Pupil algorithm", "동공 알고리즘", "瞳孔算法")),
    ("04", "04_our_code.md", "zh/04_我们的代码.md", ("Our code", "우리 코드", "我们的代码")),
    ("05", "05_data_quality.md", "zh/05_数据质量.md", ("Data quality", "데이터 품질", "数据质量")),
    ("06", "06_faq.md", "zh/06_常见问题.md", ("FAQ", "FAQ", "常见问题")),
    ("07", "07_reading_path.md", "zh/07_审阅路径.md", ("Reading path", "읽는 순서", "审阅路径")),
    ("08", "08_roadmap.md", "zh/08_待办.md", ("Roadmap", "로드맵", "路线图与待办")),
]
# md file name -> html file name (relative to site/guides/)
MAPNAME = {}
for n, en, zh, _ in GUIDES:
    MAPNAME[en] = "g%s.html" % n
    MAPNAME[zh] = "g%s.zh.html" % n
    MAPNAME[zh.split("/")[-1]] = "g%s.zh.html" % n

LANG = {"en": "English", "ko": "한국어", "zh": "中文"}
SITE_TITLE = "pupil-size · YMTC"
NAV = {
    "en": {"ref": "Reference", "guides": "Guides", "home": "Home", "gh": "GitHub", "toc": "On this page", "theme": "Theme"},
    "ko": {"ref": "레퍼런스", "guides": "가이드", "home": "홈", "gh": "GitHub", "toc": "이 페이지", "theme": "테마"},
    "zh": {"ref": "参考手册", "guides": "指南", "home": "首页", "gh": "GitHub", "toc": "本页目录", "theme": "主题"},
}

CSS = """
:root{--bg:#fbfaf7;--surface:#fff;--ink:#1d2127;--muted:#5b6470;--line:#e3e0d8;--accent:#1f6f6b;--accent-ink:#fff;--code:#f1efe9;--mark:#fff3cd;--shadow:0 1px 2px rgba(0,0,0,.05)}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#14171b;--surface:#1b1f24;--ink:#e6e8eb;--muted:#9aa4b0;--line:#2c323a;--accent:#5fc2bb;--accent-ink:#0c1514;--code:#232830;--mark:#4a3f12}}
:root[data-theme=dark]{--bg:#14171b;--surface:#1b1f24;--ink:#e6e8eb;--muted:#9aa4b0;--line:#2c323a;--accent:#5fc2bb;--accent-ink:#0c1514;--code:#232830;--mark:#4a3f12}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:72px}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Noto Sans KR","Noto Sans CJK SC",sans-serif}
a{color:var(--accent)}
header.top{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(6px);border-bottom:1px solid var(--line)}
header.top .in{max-width:1180px;margin:0 auto;padding:10px 16px;display:flex;gap:16px;align-items:center;flex-wrap:wrap}
header.top .brand{font-weight:700;color:var(--ink);text-decoration:none;margin-right:auto}
header.top a.nav{color:var(--muted);text-decoration:none;padding:4px 8px;border-radius:6px}
header.top a.nav:hover,header.top a.nav.on{color:var(--ink);background:var(--code)}
.lang a{padding:3px 9px;border:1px solid var(--line);color:var(--muted);text-decoration:none;font-size:14px}
.lang a:first-child{border-radius:6px 0 0 6px}.lang a:last-child{border-radius:0 6px 6px 0}.lang a+a{border-left:0}
.lang a.on{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
button.theme{background:none;border:1px solid var(--line);color:var(--muted);border-radius:6px;padding:3px 9px;cursor:pointer;font:inherit;font-size:14px}
.wrap{max-width:1180px;margin:0 auto;padding:24px 16px 80px;display:grid;grid-template-columns:240px minmax(0,1fr);gap:40px}
aside.toc{position:sticky;top:76px;align-self:start;max-height:calc(100vh - 96px);overflow:auto;font-size:14px;border-right:1px solid var(--line);padding-right:12px}
aside.toc h4{margin:0 0 8px;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
aside.toc a{display:block;color:var(--muted);text-decoration:none;padding:3px 0;line-height:1.35}
aside.toc a:hover{color:var(--accent)}aside.toc a.l3{padding-left:14px;font-size:13px}
main{min-width:0}.wrap.one{grid-template-columns:minmax(0,1fr)}
main h1{font-size:2rem;line-height:1.25;margin:.2em 0 .6em}
main h2{margin:2.2em 0 .6em;padding-top:.6em;border-top:1px solid var(--line);font-size:1.45rem}
main h3{margin:1.8em 0 .5em;font-size:1.15rem}
main p,main li{max-width:78ch}
code{background:var(--code);padding:.1em .35em;border-radius:4px;font:.88em ui-monospace,SFMono-Regular,Menlo,monospace}
pre{background:var(--code);border:1px solid var(--line);border-radius:8px;padding:12px 14px;overflow:auto;line-height:1.45}
pre code{background:none;padding:0;font-size:.85rem}
table{border-collapse:collapse;display:block;overflow-x:auto;margin:1em 0;font-size:.93rem}
th,td{border:1px solid var(--line);padding:6px 10px;vertical-align:top;text-align:left}
th{background:var(--code);position:sticky;top:0}
tr:nth-child(even) td{background:color-mix(in srgb,var(--surface) 60%,transparent)}
details{background:var(--surface);border:1px solid var(--line);border-radius:8px;margin:.5em 0;box-shadow:var(--shadow)}
details>summary{cursor:pointer;padding:8px 12px;list-style:none;font-weight:600}
details>summary::-webkit-details-marker{display:none}
details>summary::before{content:"▸";display:inline-block;width:1.1em;color:var(--accent);transition:transform .15s}
details[open]>summary::before{transform:rotate(90deg)}
details>*:not(summary){margin-left:14px;margin-right:14px}
details>*:last-child{margin-bottom:12px}
td details{border:0;box-shadow:none;background:none;margin:0}
td details>summary{padding:0;font-weight:500;color:var(--accent);font-size:.9em}
td details>*:not(summary){margin:0}
td details[open]{min-width:260px}
.hero{padding:28px 0 8px}.hero p.lead{font-size:1.15rem;color:var(--muted);max-width:60ch}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px;margin:18px 0 8px}
.card{display:block;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px;text-decoration:none;color:var(--ink);box-shadow:var(--shadow)}
.card:hover{border-color:var(--accent)}.card b{display:block;margin-bottom:4px}.card span{color:var(--muted);font-size:.92rem}
footer{max-width:1180px;margin:0 auto;padding:20px 16px 40px;color:var(--muted);font-size:14px;border-top:1px solid var(--line)}
@media (max-width:860px){.wrap{grid-template-columns:1fr}aside.toc{position:static;max-height:none;border-right:0;border-bottom:1px solid var(--line);padding-bottom:10px}}
@media print{header.top,aside.toc{display:none}.wrap{display:block}details{break-inside:avoid}}
"""

JS = """
(function(){var r=document.documentElement,k='pupil-theme';
try{var s=localStorage.getItem(k);if(s)r.setAttribute('data-theme',s)}catch(e){}
document.addEventListener('click',function(e){var b=e.target.closest('button.theme');if(!b)return;
var cur=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');
var nx=cur==='dark'?'light':'dark';r.setAttribute('data-theme',nx);try{localStorage.setItem(k,nx)}catch(e){}});
var ex=document.getElementById('expand-all');if(ex){ex.addEventListener('click',function(){
var all=document.querySelectorAll('main details');var open=ex.dataset.open!=='1';
all.forEach(function(d){d.open=open});ex.dataset.open=open?'1':'0';ex.textContent=open?ex.dataset.close:ex.dataset.openlabel;});}
})();
"""


def slug(text, used):
    s = re.sub(r"<[^>]+>", "", text)
    s = html.unescape(s)
    s = re.sub(r"[`*_]", "", s).strip().lower()
    s = re.sub(r"[^\wㄱ-힝一-鿿]+", "-", s).strip("-") or "sec"
    base, n = s, 2
    while s in used:
        s = "%s-%d" % (base, n); n += 1
    used.add(s)
    return s


def render(markdown_text, linkmap=None):
    out = md.render(markdown_text)
    used, toc = set(), []

    def h(m):
        lvl, inner = m.group(1), m.group(2)
        sid = slug(inner, used)
        if lvl in ("2", "3"):
            toc.append((int(lvl), sid, html.unescape(re.sub(r"<[^>]+>", "", inner))))
        return '<h%s id="%s">%s</h%s>' % (lvl, sid, inner, lvl)
    out = re.sub(r"<h([1-4])>(.*?)</h\1>", h, out)
    if linkmap:
        out = re.sub(r'href="([^"]+)"', lambda m: 'href="%s"' % linkmap(m.group(1)), out)
    return out, toc


def shell(lang, title, body, toc, active, switch, depth=0, expand=False):
    pre = "../" * depth
    nv = NAV[lang]
    sw = ""
    if switch:
        sw = '<span class="lang">%s</span>' % "".join(
            '<a href="%s"%s>%s</a>' % (href, ' class="on"' if l == lang else "", LANG[l]) for l, href in switch)
    toc_html = ""
    if toc:
        toc_html = '<aside class="toc"><h4>%s</h4>%s</aside>' % (nv["toc"], "".join(
            '<a class="l%d" href="#%s">%s</a>' % (lv, sid, html.escape(tx)) for lv, sid, tx in toc))
    ex = ""
    if expand:
        lab = {"en": ("Expand all details", "Collapse all details"), "ko": ("세부 모두 펼치기", "세부 모두 접기"), "zh": ("展开全部细节", "收起全部细节")}[lang]
        ex = '<p><button class="theme" id="expand-all" data-open="0" data-openlabel="%s" data-close="%s">%s</button></p>' % (lab[0], lab[1], lab[0])
    ref_href = pre + ("reference.html" if lang == "en" else "reference.%s.html" % lang)
    gd_href = pre + ("guides/g01.html" if lang != "zh" else "guides/g01.zh.html")
    home_href = pre + ("index.html" if lang == "en" else "index.%s.html" % lang)
    return """<!doctype html>
<html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s · %s</title><style>%s</style></head><body>
<header class="top"><div class="in"><a class="brand" href="%s">%s</a>
<a class="nav%s" href="%s">%s</a><a class="nav%s" href="%s">%s</a><a class="nav" href="https://github.com/cyracaid/pupil-size/tree/ymtc-trk2csv">%s</a>
%s<button class="theme" type="button">%s</button></div></header>
<div class="wrap%s">%s<main>%s%s</main></div>
<footer>Kret, M. E., &amp; Sjak-Shie, E. E. (2019). Preprocessing pupil size data: Guidelines and code. <i>Behavior Research Methods, 51</i>(3), 1336–1342. · GPL-3.0</footer>
<script>%s</script></body></html>
""" % (lang, html.escape(title), SITE_TITLE, CSS, home_href, SITE_TITLE,
       " on" if active == "ref" else "", ref_href, nv["ref"],
       " on" if active == "guides" else "", gd_href, nv["guides"], nv["gh"], sw, nv["theme"],
       "" if toc else " one", toc_html, ex, body, JS)


def write(path, text):
    p = SITE / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def ref_linkmap(lang):
    def f(h):
        if h.startswith("../docs/"):
            rest = h[len("../docs/"):]
            name = rest.split("/")[-1].split("#")[0]
            frag = ("#" + rest.split("#", 1)[1]) if "#" in rest else ""
            if rest.startswith("zh/") or lang == "zh":
                key = [zh for _, en, zh, _ in GUIDES if zh.split("/")[-1] == name or en == name]
                for n, en, zh, _ in GUIDES:
                    if en == name or zh.split("/")[-1] == name:
                        return "guides/g%s%s.html%s" % (n, ".zh" if (lang == "zh" or rest.startswith("zh/")) else "", frag)
            for n, en, zh, _ in GUIDES:
                if en == name:
                    return "guides/g%s.html%s" % (n, frag)
        if h == "ymtc/README.md":
            return GH + "code/ymtc/README.md"
        return h
    return f


def guide_linkmap(h):
    if h.startswith("http") or h.startswith("#"):
        return h
    name = h.split("#")[0].split("/")[-1]
    frag = ("#" + h.split("#", 1)[1]) if "#" in h else ""
    if name in MAPNAME:
        return MAPNAME[name] + frag
    if h.startswith("../"):                 # repo-relative, e.g. ../code/ymtc/README.md
        return GH + re.sub(r"^(\.\./)+", "", h)
    if name.endswith(".md"):
        return GH + "docs/" + h.lstrip("./")
    return h


# ------------------------- pages -------------------------
if SITE.exists():
    shutil.rmtree(SITE)

# reference (the big README), one page per language
for lang in ("en", "ko", "zh"):
    text = big.sectionlang(lang)
    body, toc = render(text, ref_linkmap(lang))
    fname = "reference.html" if lang == "en" else "reference.%s.html" % lang
    switch = [(l, "reference.html" if l == "en" else "reference.%s.html" % l) for l in ("en", "ko", "zh")]
    toc = [t for t in toc if t[0] == 2 or t[0] == 3]
    write(fname, shell(lang, big.u("title", lang), body, toc, "ref", switch, 0, expand=True))

# guides
# There are no Korean guide pages; the Korean entry of the switcher therefore goes back to the
# Korean home instead of pretending to translate this page. Without it a reader who arrives from
# index.ko.html has no way back to Korean at all.
for n, en, zh, titles in GUIDES:
    for lang, fn in (("en", en), ("zh", zh)):
        src = (REPO / "docs" / fn).read_text(encoding="utf-8")
        body, toc = render(src, guide_linkmap)
        out = "guides/g%s%s.html" % (n, ".zh" if lang == "zh" else "")
        switch = [("en", "g%s.html" % n), ("zh", "g%s.zh.html" % n), ("ko", "../index.ko.html")]
        gl = "".join('<a class="card" href="g%s%s.html"><b>%s</b></a>' % (m, ".zh" if lang == "zh" else "", t[2 if lang == "zh" else 0]) for m, _, _, t in GUIDES)
        body = '<div class="cards" style="margin-top:0">%s</div>' % gl + body
        write(out, shell(lang, titles[2 if lang == "zh" else 0], body, toc, "guides", switch, 1))

# home
HOME = {
    "en": ("pupil-size · YMTC", "A documented fork of the Kret &amp; Sjak-Shie (2019) pupil-size preprocessing code, with our YMTC layer on top: MRC <code>.trk</code> to CSV, the event-marker table, Kret statistics and one merged final table. Every output column is explained.",
           [("reference.html", "Reference", "Everything on one page: pipeline map, all 14 output tables column by column, settings, troubleshooting."),
            ("guides/g02.html", "Column dictionary", "The shorter dictionary of the main tables."),
            ("guides/g01.html", "Pipeline overview", "The five layers and what flows between them."),
            ("guides/g05.html", "Data quality", "Missing-data structure, rejection rules, threshold sensitivity."),
            ("guides/g06.html", "FAQ", "The traps that bite most often."),
            ("guides/g07.html", "Reading path", "What to read, in what order, what to skip - upstream and our layer, and where the statistics live."),
            ("guides/g08.html", "Roadmap and to-do", "Done, next, and the decisions still open - each item with the file that shows it.")]),
    "ko": ("pupil-size · YMTC", "Kret &amp; Sjak-Shie (2019) pupil-size 전처리 코드를 문서화한 포크이며 그 위에 우리 YMTC 계층을 얹었다: MRC <code>.trk</code> → CSV, 이벤트 마커 표, Kret 통계, 병합된 최종 표. 모든 출력 열을 설명한다.",
           [("reference.ko.html", "레퍼런스", "한 페이지에: 파이프라인 지도, 출력 표 14개 열 단위, 설정, 문제 해결."),
            ("guides/g02.html", "열 사전(영어)", "주요 표의 짧은 사전."),
            ("guides/g01.html", "파이프라인 개요(영어)", "다섯 계층과 그 사이 흐름."),
            ("guides/g05.html", "데이터 품질(영어)", "결측 구조, 제외 규칙, 임계값 민감도."),
            ("guides/g06.html", "FAQ(영어)", "가장 자주 걸리는 함정."),
            ("guides/g07.html", "읽는 순서(영어)", "무엇을 어떤 순서로 읽고 무엇을 건너뛰는지 - 업스트림과 우리 계층, 통계의 위치."),
            ("guides/g08.html", "로드맵(영어)", "끝난 것, 다음 것, 아직 열린 결정 - 각 항목이 어디에 보이는지와 함께.")]),
    "zh": ("pupil-size · YMTC", "Kret &amp; Sjak-Shie (2019) pupil-size 预处理代码的带文档 fork，上面加了我们的 YMTC 层：MRC <code>.trk</code> 转 CSV、事件 marker 表、Kret 统计、合并的最终表。每个输出列都有说明。",
           [("reference.zh.html", "参考手册", "全部放在一页：流程总图、14 张输出表逐列说明、设置项、排错。"),
            ("guides/g02.zh.html", "列字典", "主要表的精简字典。"),
            ("guides/g01.zh.html", "流程总览", "五层结构，以及层与层之间流动的内容。"),
            ("guides/g05.zh.html", "数据质量", "缺失结构、剔除规则、阈值敏感性。"),
            ("guides/g06.zh.html", "常见问题", "最容易踩的坑。"),
            ("guides/g07.zh.html", "审阅路径", "按什么顺序读上游和我们自己的代码、哪些可以跳过、统计在哪里。"),
            ("guides/g08.zh.html", "路线图与待办", "完成了什么、下一步是什么、哪些还等决定 —— 每条都标出可见位置。")]),
}
for lang in ("en", "ko", "zh"):
    t, lead, cards = HOME[lang]
    cs = "".join('<a class="card" href="%s"><b>%s</b><span>%s</span></a>' % c for c in cards)
    body = '<div class="hero"><h1>%s</h1><p class="lead">%s</p></div><div class="cards">%s</div>' % (t, lead, cs)
    fname = "index.html" if lang == "en" else "index.%s.html" % lang
    switch = [(l, "index.html" if l == "en" else "index.%s.html" % l) for l in ("en", "ko", "zh")]
    write(fname, shell(lang, NAV[lang]["home"], body, None, "", switch, 0))

(SITE / ".nojekyll").write_text("")
n = sum(1 for _ in SITE.rglob("*.html"))
print(n, "pages ->", SITE)
