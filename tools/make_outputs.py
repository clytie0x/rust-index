"""สร้างไฟล์ .out ของแบบฝึกหัดจากเฉลย

    python tools/make_outputs.py src/exercises/rust/01-variables/01-total

คอมไพล์ solution.rs ในโฟลเดอร์นั้นด้วย rustc แล้วรันกับ tests/*.in ทุกไฟล์
เขียนผลเป็น tests/*.out ทับของเดิม
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_code import compile_source, run  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    d = Path(sys.argv[1])
    sol = next((p for p in sorted(d.iterdir()) if p.stem == "solution" and p.suffix == ".rs"), None)
    if sol is None:
        print(f"ไม่มี solution.rs ใน {d}", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        exe, err = compile_source(sol.read_text(encoding="utf-8"), Path(tmp), "solution", False, True)
        if exe is None:
            print(err, file=sys.stderr)
            return 1
        tests = sorted((d / "tests").glob("*.in"))
        for t in tests:
            code, out = run(exe, t.read_text(encoding="utf-8"))
            if code is None or code != 0:
                print(f"{t.name} รันไม่สำเร็จ", file=sys.stderr)
                return 1
            t.with_suffix(".out").write_text(out, encoding="utf-8", newline="\n")
    print(f"เขียน .out {len(tests)} ไฟล์ใน {d / 'tests'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
