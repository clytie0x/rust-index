"""สร้างเว็บจาก src/ ไปไว้ที่ dist/

ใช้ Python 3.11 ขึ้นไป กับ Node 24 ขึ้นไป (รัน npm ci ก่อนครั้งแรก) ซึ่งใช้แปลง src/scripts/site.ts

    python tools/build.py          สร้างเว็บแล้วตรวจลิงก์
    python tools/build.py --serve  สร้างแล้วเปิดดูที่ http://127.0.0.1:8000

ลำดับหน้าทั้งหมดอยู่ใน src/site.toml ไฟล์ใน src/pages เก็บเฉพาะ <article> ของแต่ละหน้า
"""

from __future__ import annotations

import hashlib
import html
import posixpath
import re
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
PAGES = SRC / "pages"
EXERCISES = SRC / "exercises"
DIST = ROOT / "dist"

ICON_PREV = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg>'
ICON_NEXT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
TOC_INLINE = '<ul class="toc-inline" aria-label="ในหน้านี้"></ul>'


@dataclass
class Page:
    path: str            # ที่อยู่ใน dist เช่น c/00-start/why.html
    kind: str            # home, chapter หรือ page
    title: str           # ชื่อที่ใช้ในเมนู
    num: str = ""
    chapter: "Page | None" = None
    exercises: str = ""  # ถ้ามี หน้านี้สร้างจากโฟลเดอร์ src/exercises/<exercises> แทน src/pages

    @property
    def label(self) -> str:
        """ชื่อเต็มที่ใช้ในแท็บและปุ่มก่อนหน้าถัดไป"""
        return f"{self.num} {self.title}" if self.kind == "page" else self.title


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def load_site() -> tuple[dict, list[Page], list[tuple[Page, list[Page]]]]:
    site = tomllib.loads((SRC / "site.toml").read_text(encoding="utf-8"))
    home = Page(site["home"]["path"], "home", site["home"]["title"])
    order = [home]
    tree = []
    for ch in site.get("chapters", []):
        if "path" not in ch:
            continue  # บทที่วางแผนไว้ ยังไม่มีหน้า
        chapter = Page(ch["path"], "chapter", ch["title"], ch["num"])
        children = [Page(p["path"], "page", p["title"], p["num"], chapter, p.get("exercises", ""))
                    for p in ch.get("pages", [])]
        order += [chapter, *children]
        tree.append((chapter, children))
    return site, order, tree


BASE = "/"  # ที่อยู่ของเว็บบนเซิร์ฟเวอร์ ตั้งจาก site.toml ตอน build ใช้กับหน้า 404 ที่ถูกเปิดได้จากทุก URL


def rel(target: str, current: Page) -> str:
    if current.kind == "404":
        return BASE + target
    return posixpath.relpath(target, posixpath.dirname(current.path) or ".")


def render_nav(current: Page, home: Page, tree) -> str:
    def cur(p: Page) -> str:
        return ' aria-current="page"' if p is current else ""

    lines = ['    <ul class="nav">']
    toc = TOC_INLINE if home is current else ""
    lines.append(f'      <li><a href="{rel(home.path, current)}"{cur(home)}>{esc(home.title)}</a>{toc}</li>')
    for chapter, children in tree:
        # กางเฉพาะบทที่กำลังเปิด บทอื่นเหลือแค่ชื่อบท เมนูจะได้ไม่ยาวเกินเมื่อมีหลายสิบบท
        is_open = current is chapter or current in children
        lines.append(f'      <li class="nav-section{" is-open" if is_open else ""}">')
        lines.append(f'        <a class="nav-section-title" href="{rel(chapter.path, current)}"{cur(chapter)}>'
                     f'<span class="num-chip">{esc(chapter.num)}</span>{esc(chapter.title)}</a>')
        if chapter is current:
            lines.append(f"        {TOC_INLINE}")
        lines.append("        <ul>")
        for p in children:
            toc = TOC_INLINE if p is current else ""
            lines.append(f'          <li><a href="{rel(p.path, current)}"{cur(p)}><span class="num">{esc(p.num)}</span>'
                         f"<span>{esc(p.title)}</span></a>{toc}</li>")
        lines.append("        </ul>")
        lines.append("      </li>")
    lines.append("    </ul>")
    return "\n".join(lines)


def render_pager(current: Page, prev: Page | None, nxt: Page | None) -> str:
    if not prev and not nxt:
        return ""
    lines =['    <nav class="pager" aria-label="หน้าก่อนหน้าและถัดไป">']
    if prev:
        lines += [f'      <a class="prev" href="{rel(prev.path, current)}">',
                  f"        {ICON_PREV}",
                  f'        <span class="pg-text"><span class="pg-label">ก่อนหน้า</span><span class="pg-title">{esc(prev.label)}</span></span>',
                  "      </a>"]
    if nxt:
        lines += [f'      <a class="next" href="{rel(nxt.path, current)}">',
                  f'        <span class="pg-text"><span class="pg-label">ถัดไป</span><span class="pg-title">{esc(nxt.label)}</span></span>',
                  f"        {ICON_NEXT}",
                  "      </a>"]
    lines.append("    </nav>")
    return "\n".join(lines)


NOT_FOUND = """<article class="doc">
      <h1>ไม่พบหน้านี้</h1>

      <p>ลิงก์นี้อาจพิมพ์ผิด หรือหน้านี้ถูกย้ายไปแล้ว ลองเริ่มจาก<a href="{base}index.html">หน้าแรก</a> หรือเลือกบทจากเมนูด้านซ้าย</p>
    </article>
"""

LEVELS = {1: "ง่าย", 2: "กลาง", 3: "ยาก"}


def code_block(lang: str, text: str, title: str = "", extra: str = "") -> str:
    t = f' data-title="{html.escape(title)}"' if title else ""
    return f'<div class="code" data-lang="{lang}"{t}{extra}><pre><code>{html.escape(text, quote=False)}</code></pre></div>'


def indent(block: str, n: int) -> str:
    """เยื้องแค่บรรทัดแรก บรรทัดที่เหลืออาจอยู่ใน <pre> ซึ่งช่องว่างมีความหมาย"""
    return " " * n + block.strip("\n")


def render_exercises(page: Page) -> str:
    """หน้าแบบฝึกหัดของบท สร้างจาก src/exercises/<บท>/<ข้อ>/"""
    base = EXERCISES / page.exercises
    out = [f'<article class="doc">', f"      <h1>{esc(page.label)}</h1>", "",
           "      <p>แต่ละข้อให้ <code>cargo new</code> โปรเจกต์ใหม่ แล้วเขียนใน <code>src/main.rs</code> "
           "รันด้วย <code>cargo run</code> ถ้าข้อนั้นมีข้อมูลเข้า ให้ป้อนตามตัวอย่าง หรือส่งไฟล์เข้าไปด้วย <code>cargo run &lt; sample.in</code> "
           "เทียบผลที่พิมพ์ออกมากับผลลัพธ์ที่ต้องได้ให้ตรงทุกตัวอักษร รวมถึงช่องว่างและการขึ้นบรรทัด "
           "ติดจริงๆ ค่อยเปิดคำใบ้ และเปิดเฉลยหลังทำเสร็จแล้วเท่านั้น</p>"]
    for i, d in enumerate(sorted(p for p in base.iterdir() if (p / "task.toml").exists()), 1):
        task = tomllib.loads((d / "task.toml").read_text(encoding="utf-8"))
        slug = re.sub(r"^\d+-", "", d.name)
        out += ["", f'      <h2 id="ex-{slug}" class="ex-title">ข้อ {i} {esc(task["title"])}</h2>',
                f'      <p class="ex-meta">ระดับ{LEVELS[task.get("level", 1)]}  เวลาไม่เกิน {task.get("time_limit", 1)} วินาที</p>',
                "", indent((d / "statement.html").read_text(encoding="utf-8"), 6)]
        samples = sorted((d / "tests").glob("sample*.in"))
        for j, s in enumerate(samples, 1):
            inp = s.read_text(encoding="utf-8")
            ans = s.with_suffix(".out").read_text(encoding="utf-8")
            label = f" ตัวอย่างที่ {j}" if len(samples) > 1 else ""
            parts = ['<div class="io">']
            if inp.strip():
                parts.append(code_block("input", inp.rstrip("\n"), f"ข้อมูลเข้า{label}"))
            parts.append(code_block("expected", ans.rstrip("\n"), f"ผลลัพธ์ที่ต้องได้{label}"))
            parts.append("</div>")
            out += ["", indent("\n".join(parts), 6)]
        if task.get("hint"):
            out += ["", f'      <details class="reveal"><summary>ดูคำใบ้</summary>{task["hint"].strip()}</details>']
        sol = next((p for p in sorted(d.iterdir()) if p.stem == "solution" and p.suffix == ".rs"), None)
        if sol:
            out += ["", '      <details class="reveal"><summary>ดูเฉลย</summary>',
                    "        " + code_block("rust", sol.read_text(encoding="utf-8").rstrip("\n"), extra=" data-linenums"),
                    "      </details>"]
    out.append("    </article>")
    return "\n".join(out) + "\n"


def asset_version(name: str) -> str:
    return hashlib.sha256((DIST / "assets" / name).read_bytes()).hexdigest()[:10]


def render_course_map(site: dict, current: Page) -> str:
    """แผนที่คอร์สในหน้าแรก แต่ละบทเป็นช่องหนึ่งช่องเหมือนช่องในอาเรย์"""
    tracks: dict[str, list[dict]] = {}
    for ch in site.get("chapters", []):
        tracks.setdefault(ch["track"], []).append(ch)

    lines = ['<div class="course-map">']
    for track, chapters in tracks.items():
        lines.append(f'        <p class="track-title">{esc(track)}</p>')
        lines.append('        <ol class="cells">')
        for ch in chapters:
            short = re.sub(r"^บทที่\s*\S+\s*", "", ch["title"])
            body = (f'<span class="cell-index">[{esc(ch["num"])}]</span>'
                    f'<span class="cell-title">{esc(short)}</span>'
                    f'<span class="cell-sum">{esc(ch.get("summary", ""))}</span>')
            if "path" in ch:
                meta = f'{len(ch.get("pages", []))} หน้า'
                lines.append(f'          <li class="cell is-ready"><a href="{rel(ch["path"], current)}">{body}'
                             f'<span class="cell-meta">{meta}</span></a></li>')
            else:
                lines.append(f'          <li class="cell is-planned"><div>{body}'
                             f'<span class="cell-meta">กำลังเขียน</span></div></li>')
        lines.append("        </ol>")
    lines.append("      </div>")
    return "\n".join(lines)


THAI_MONTHS = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]


def last_updated(src: Path) -> str:
    """วันที่ commit ล่าสุดของไฟล์ต้นฉบับ เป็นปี พ.ศ. ถ้ายังไม่เคย commit ให้คืนค่าว่าง"""
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(src)], cwd=ROOT,
                           capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return ""
    if not r.stdout.strip():
        return ""
    y, m, d = (int(x) for x in r.stdout.strip().split("-"))
    return f"{d} {THAI_MONTHS[m - 1]} {y + 543}"


def render_page_meta(site: dict, page: Page) -> str:
    if page.kind == "404":
        return ""
    if page.exercises:
        src, url = EXERCISES / page.exercises, f"tree/main/src/exercises/{page.exercises}"
    else:
        src, url = PAGES / page.path, f"edit/main/src/pages/{page.path}"
    parts = [f'<a href="https://github.com/{site["repo"]}/{url}">แก้หน้านี้บน GitHub</a>']
    date = last_updated(src)
    if date:
        parts.append(f"แก้ล่าสุด {date}")
    return f'  <p class="page-meta">{"  ".join(parts)}</p>\n'


def render(site: dict, layout: str, page: Page, home: Page, tree, prev, nxt, article: str) -> str:
    if "<!-- course-map -->" in article:
        article = article.replace("<!-- course-map -->", render_course_map(site, page))
    crumbs = ""
    if page.kind == "page":
        crumbs = (f'    <nav class="crumbs" aria-label="ตำแหน่ง"><a href="{rel(page.chapter.path, page)}">'
                  f"{esc(page.chapter.title)}</a></nav>\n")
    values = {
        "title": site["name"] if page.kind == "home" else f"{page.label} - {site['name']}",
        "description": site["description"],
        "root": rel("assets/", page)[: -len("assets/")] if page.kind == "404" else rel("assets", page)[: -len("assets")],
        "body_attr": (' class="page-home"' if page.kind == "home" else "") + f' data-page="{page.path}"',
        "page_meta": render_page_meta(site, page),
        "home": rel(home.path, page),
        "name": esc(site["name"]),
        "repo": site["repo"],
        "author": esc(site["author"]),
        "nav": render_nav(page, home, tree),
        "crumbs": crumbs,
        "article": article.rstrip("\n"),
        "pager": render_pager(page, prev, nxt),
        # เปลี่ยนตามเนื้อไฟล์ เบราว์เซอร์จะได้ไม่ใช้ CSS JS และไอคอนตัวเก่าที่เก็บไว้
        "v_css": asset_version("site.css"),
        "v_js": asset_version("site.js"),
        "v_icon": asset_version("favicon.svg"),
    }
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], layout)


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.links: list[str] = []
        self.h1: list[str] = []
        self._in_h1 = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        for key in ("href", "src"):
            if a.get(key):
                self.links.append(a[key])
        if tag == "h1":
            self._in_h1 = True
            self.h1.append("")

    def handle_endtag(self, tag):
        if tag == "h1":
            self._in_h1 = False

    def handle_data(self, data):
        if self._in_h1:
            self.h1[-1] += data


def check_page_refs(site: dict, order: list[Page]) -> list[str]:
    """ข้อความอย่าง "หน้า 15.2" ต้องชี้ไปหน้าที่มีอยู่จริง ยกเว้นบทที่ยังวางแผนไว้"""
    nums = {p.num for p in order if p.kind == "page"}
    planned = {ch["num"] for ch in site.get("chapters", []) if "path" not in ch}
    errors = []
    for page in order:
        if page.exercises:
            continue
        text = re.sub(r"<pre>.*?</pre>", "", (PAGES / page.path).read_text(encoding="utf-8"), flags=re.S)
        for m in re.finditer(r"หน้า\s*(?:<[^>]+>)?(\d+)\.(\d+)", text):
            ref = f"{m.group(1)}.{m.group(2)}"
            if ref not in nums and m.group(1) not in planned:
                errors.append(f"{page.path}: อ้าง หน้า {ref} ซึ่งไม่มีอยู่")
    return errors


def check(order: list[Page]) -> list[str]:
    errors = []
    parsed = {}
    for f in DIST.rglob("*.html"):
        p = LinkCollector()
        p.feed(f.read_text(encoding="utf-8"))
        parsed[f.relative_to(DIST).as_posix()] = p

    for page in order:
        p = parsed[page.path]
        dupes = sorted({i for i in p.ids if p.ids.count(i) > 1})
        if dupes:
            errors.append(f"{page.path}: id ซ้ำ {dupes}")
        if page.kind != "home" and [h.strip() for h in p.h1] != [page.label]:
            errors.append(f"{page.path}: h1 {p.h1} ไม่ตรงกับชื่อใน site.toml '{page.label}'")
        for link in p.links:
            if re.match(r"^[a-z]+:", link) or link.startswith("//"):
                continue
            target, _, frag = link.partition("#")
            target = target.partition("?")[0]
            target_path = posixpath.normpath(posixpath.join(posixpath.dirname(page.path), target)) if target else page.path
            if not (DIST / target_path).is_file():
                errors.append(f"{page.path}: ลิงก์ {link} ชี้ไปไฟล์ที่ไม่มี")
            elif frag and target_path.endswith(".html") and frag not in parsed[target_path].ids:
                errors.append(f"{page.path}: ลิงก์ {link} ไม่มี id #{frag} ในหน้านั้น")
    return errors


def build() -> int:
    site, order, tree = load_site()
    home = order[0]

    listed = {p.path for p in order if not p.exercises}
    on_disk = {f.relative_to(PAGES).as_posix() for f in PAGES.rglob("*.html")}
    # บทที่ยังเขียนไม่เสร็จอยู่ในโฟลเดอร์ที่ยังไม่มีบทไหนใน site.toml ใช้ ข้ามไปก่อนแค่เตือน
    chapter_dirs = {posixpath.dirname(p.path) for p in order if p.kind == "chapter"}
    drafts = sorted(p for p in on_disk - listed if posixpath.dirname(p) not in chapter_dirs)
    errors = [f"site.toml มี {p} แต่ไม่มีไฟล์ src/pages/{p}" for p in sorted(listed - on_disk)]
    errors += [f"src/pages/{p} ไม่ได้อยู่ใน site.toml" for p in sorted(on_disk - listed - set(drafts))]
    ex_listed = {p.exercises for p in order if p.exercises}
    errors += [f"site.toml อ้าง src/exercises/{e} ที่ไม่มี" for e in sorted(ex_listed) if not (EXERCISES / e).is_dir()]
    if EXERCISES.exists():
        ex_dirs = {t.parent.parent.relative_to(EXERCISES).as_posix() for t in EXERCISES.rglob("task.toml")}
        unlisted = ex_dirs - ex_listed
        drafts += sorted(f"exercises/{e}" for e in unlisted if e not in chapter_dirs)
        errors += [f"src/exercises/{e} ไม่ได้อยู่ใน site.toml" for e in sorted(unlisted) if e in chapter_dirs]
    if drafts:
        print(f"ข้ามไฟล์ร่างที่ยังไม่อยู่ใน site.toml {len(drafts)} รายการ", file=sys.stderr)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(SRC / "assets", DIST / "assets")
    try:
        subprocess.run(["node", str(ROOT / "tools" / "bundle.ts"), str(DIST / "assets" / "site.js")], check=True)
    except FileNotFoundError:
        print("ไม่พบ node ต้องลง Node 24 ขึ้นไปแล้วรัน npm ci ก่อน", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError:
        print("แปลง src/scripts/site.ts ไม่สำเร็จ ลองรัน npm ci แล้ว npm run typecheck", file=sys.stderr)
        return 1

    layout = (SRC / "layout.html").read_text(encoding="utf-8")
    for i, page in enumerate(order):
        article = render_exercises(page) if page.exercises else (PAGES / page.path).read_text(encoding="utf-8")
        prev = order[i - 1] if i > 0 else None
        nxt = order[i + 1] if i + 1 < len(order) else None
        out = DIST / page.path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(site, layout, page, home, tree, prev, nxt, article), encoding="utf-8", newline="\n")

    global BASE
    BASE = site.get("base", "/")
    missing = Page("404.html", "404", "ไม่พบหน้านี้")
    article = NOT_FOUND.replace("{base}", BASE)
    (DIST / missing.path).write_text(render(site, layout, missing, home, tree, None, None, article),
                                     encoding="utf-8", newline="\n")

    errors = check(order) + check_page_refs(site, order)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"สร้าง {len(order)} หน้าที่ dist/ ตรวจลิงก์ผ่าน")
    return 0


def serve() -> None:
    import functools
    import http.server

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    with http.server.ThreadingHTTPServer(("127.0.0.1", 8000), handler) as httpd:
        print("เปิดดูที่ http://127.0.0.1:8000  กด Ctrl+C เพื่อหยุด")
        httpd.serve_forever()


if __name__ == "__main__":
    code = build()
    if code == 0 and "--serve" in sys.argv:
        serve()
    sys.exit(code)
