"""คอมไพล์และรันโค้ดในเอกสาร เพื่อยืนยันว่าทุกตัวอย่างใช้ได้จริง

    python tools/check_code.py                    ตรวจทั้งเว็บ
    python tools/check_code.py rust/01-variables  ตรวจเฉพาะบท (ส่วนต้นของ path)

ตรวจสองส่วน
1. ตัวอย่างในหน้าเนื้อหา บล็อกโค้ดที่มี data-test="ชื่อ" จะถูกคอมไพล์ด้วย rustc
   ถ้ามีบล็อก data-lang="input" data-for="ชื่อ" จะใช้เป็น input
   ถ้ามีบล็อก data-lang="output" data-for="ชื่อ" ผลที่รันได้ต้องตรงกัน
   ใส่ data-allow-warnings ถ้าตั้งใจให้ตัวอย่างนั้นมีคำเตือน
   ทุกตัวอย่างรันสองแบบ แบบตัวตรวจ (-C opt-level=2 และ -D warnings) และแบบ rustc เปล่า
   แบบหลังใกล้เคียงกับ cargo run ตอน dev
2. แบบฝึกหัดใน src/exercises เฉลย solution.rs (และ naive.rs ถ้ามี) ต้องผ่านชุดทดสอบ
   วิธีช้า (naive*) ต้องผ่านทุกชุดที่ชื่อไม่ได้ขึ้นต้นด้วย big

น้องเขียนด้วย cargo ในโปรเจกต์ของตัวเอง ตัวตรวจใช้ rustc กับไฟล์เดียวเพราะตัวอย่างไม่มี dependency
เลือกคอมไพเลอร์ด้วย RI_RUSTC (ค่าเริ่มต้น rustc) และรุ่นภาษาด้วย RI_EDITION (ค่าเริ่มต้น 2021)
"""

from __future__ import annotations

import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "src" / "pages"
EXERCISES = ROOT / "src" / "exercises"

RUSTC = os.environ.get("RI_RUSTC", "rustc")
EDITION = os.environ.get("RI_EDITION", "2021")
RUN_TIMEOUT = 10

BLOCK = re.compile(r'<div class="code"([^>]*)><pre><code>(.*?)</code></pre></div>', re.S)
ATTR = re.compile(r'([\w-]+)(?:="([^"]*)")?')
ANNO = re.compile(r"[ \t]*//[ \t]*\(\d+\)![ \t]*$", re.M)


def normalize(text: str) -> str:
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").split("\n")]
    return "\n".join(lines).strip("\n")


def compile_source(src: str, workdir: Path, name: str, allow_warnings: bool,
                   strict: bool) -> tuple[Path | None, str]:
    source = workdir / f"{name}.rs"
    source.write_text(src, encoding="utf-8")
    exe = workdir / name
    cmd = [RUSTC, "--edition", EDITION, "--color", "never", str(source), "-o", str(exe)]
    if strict:
        cmd[1:1] = ["-C", "opt-level=2"]
        if not allow_warnings:
            cmd[1:1] = ["-D", "warnings"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        return None, (r.stderr or r.stdout).strip()
    return exe, ""


def run(exe: Path, stdin: str) -> tuple[int | None, str]:
    try:
        r = subprocess.run([str(exe)], input=stdin, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=RUN_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, ""
    return r.returncode, r.stdout


def blocks_in(path: Path) -> list[tuple[dict, str]]:
    out = []
    for m in BLOCK.finditer(path.read_text(encoding="utf-8")):
        attrs = {k: (v if v is not None else "") for k, v in ATTR.findall(m.group(1))}
        out.append((attrs, html.unescape(m.group(2))))
    return out


def check_example(workdir: Path, rel: str, name: str, attrs: dict, text: str,
                  stdin: str, expected: str | None) -> list[str]:
    src = ANNO.sub("", text)
    allow = "data-allow-warnings" in attrs
    safe = re.sub(r"\W", "_", f"{rel}_{name}")
    for label, strict, suffix in ((" แบบตัวตรวจ", True, ""), (" แบบ rustc เปล่า", False, "_plain")):
        exe, err = compile_source(src, workdir, safe + suffix, allow, strict)
        if exe is None:
            return [f"{rel} [{name}]{label} คอมไพล์ไม่ผ่าน\n{err}"]
        code, got = run(exe, stdin)
        if code is None:
            return [f"{rel} [{name}]{label} รันเกิน {RUN_TIMEOUT} วินาที"]
        if code != 0:
            return [f"{rel} [{name}]{label} จบด้วยรหัส {code}"]
        if expected is not None and normalize(got) != normalize(expected):
            want = normalize(expected)
            return [f"{rel} [{name}]{label} ผลลัพธ์ไม่ตรงกับในหน้า\n--- ในหน้า\n{want}\n--- รันได้\n{normalize(got)}"]
    return []


def page_jobs(workdir: Path, only: str) -> list:
    jobs = []
    for page in sorted(PAGES.rglob("*.html")):
        rel = page.relative_to(PAGES).as_posix()
        if not rel.startswith(only):
            continue
        blocks = blocks_in(page)
        inputs = {a["data-for"]: t for a, t in blocks if a.get("data-lang") == "input" and "data-for" in a}
        outputs = {a["data-for"]: t for a, t in blocks if a.get("data-lang") == "output" and "data-for" in a}
        for attrs, text in blocks:
            name = attrs.get("data-test")
            if name and attrs.get("data-lang", "rust") == "rust":
                jobs.append(lambda rel=rel, name=name, attrs=attrs, text=text, inputs=inputs, outputs=outputs:
                            check_example(workdir, rel, name, attrs, text, inputs.get(name, ""), outputs.get(name)))
    return jobs


def check_solution(workdir: Path, rel: str, sol: Path, tests: list[Path]) -> list[str]:
    errors = []
    exe, err = compile_source(sol.read_text(encoding="utf-8"), workdir,
                              re.sub(r"\W", "_", f"ex_{rel}_{sol.stem}"), False, True)
    if exe is None:
        return [f"แบบฝึกหัด {rel}/{sol.name} คอมไพล์ไม่ผ่าน\n{err}"]
    for t in tests:
        if sol.stem.startswith("naive") and t.stem.startswith("big"):
            continue
        ans = t.with_suffix(".out")
        if not ans.exists():
            errors.append(f"แบบฝึกหัด {rel} ไม่มี {ans.name}")
            continue
        code, got = run(exe, t.read_text(encoding="utf-8"))
        if code is None:
            errors.append(f"แบบฝึกหัด {rel}/{sol.name} ชุด {t.stem} รันเกิน {RUN_TIMEOUT} วินาที")
        elif code != 0:
            errors.append(f"แบบฝึกหัด {rel}/{sol.name} ชุด {t.stem} จบด้วยรหัส {code}")
        elif normalize(got) != normalize(ans.read_text(encoding="utf-8")):
            errors.append(f"แบบฝึกหัด {rel}/{sol.name} ชุด {t.stem} ได้คำตอบไม่ตรง")
    return errors


def exercise_jobs(workdir: Path, only: str) -> tuple[list, list[str]]:
    jobs, errors = [], []
    if not EXERCISES.exists():
        return jobs, errors
    for task in sorted(EXERCISES.rglob("task.toml")):
        d = task.parent
        rel = d.relative_to(EXERCISES).as_posix()
        if not rel.startswith(only):
            continue
        tomllib.loads(task.read_text(encoding="utf-8"))
        tests = sorted((d / "tests").glob("*.in"))
        if not tests:
            errors.append(f"แบบฝึกหัด {rel} ไม่มีชุดทดสอบ")
            continue
        solutions = sorted(p for p in d.iterdir()
                           if p.stem.startswith(("solution", "naive")) and p.suffix == ".rs")
        if not solutions:
            errors.append(f"แบบฝึกหัด {rel} ไม่มีเฉลย")
            continue
        for sol in solutions:
            jobs.append(lambda rel=rel, sol=sol, tests=tests: check_solution(workdir, rel, sol, tests))
    return jobs, errors


def main() -> int:
    if shutil.which(RUSTC) is None:
        print(f"ไม่พบ {RUSTC} ติดตั้ง rustup ก่อน หรือตั้ง RI_RUSTC", file=sys.stderr)
        return 1
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        p_jobs = page_jobs(work, only)
        e_jobs, errors = exercise_jobs(work, only)
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
            for result in pool.map(lambda job: job(), p_jobs + e_jobs):
                errors += result
    for e in errors:
        print(e, end="\n\n", file=sys.stderr)
    print(f"ตัวอย่างในหน้า {len(p_jobs)} ชิ้น เฉลยแบบฝึกหัด {len(e_jobs)} ไฟล์ พบปัญหา {len(errors)} จุด")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
