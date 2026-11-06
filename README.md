# rust-index

เอกสารเรียนภาษา Rust ตั้งแต่ศูนย์ สำหรับติว น้องเริ่มจากติดตั้งเครื่องมือ ไปจนยืมค่าและเขียนฟังก์ชันเองได้

เว็บจะอยู่ที่ https://rust.teerapat.codes/ หลังจากชี้โดเมนแล้ว ก่อนหน้านั้นดูได้จาก GitHub Pages ของรีโปนี้

## โครงสร้าง

เขียน HTML CSS และ TypeScript เอง ไม่ใช้ framework มีสคริปต์ Python เล็กๆ ประกอบหน้าให้ จึงไม่ต้องเขียนเมนูซ้ำในทุกหน้า โครงเดียวกับ [zero-index](https://github.com/clytie0x/zero-index)

| ที่อยู่ | คืออะไร |
|---|---|
| `src/site.toml` | ลำดับบทและหน้าทั้งหมด เมนูซ้าย ปุ่มก่อนหน้าถัดไป และชื่อแท็บสร้างจากไฟล์นี้ |
| `src/pages/` | เนื้อหาของแต่ละหน้า เก็บเฉพาะ `<article>` |
| `src/layout.html` | โครงหน้าที่ทุกหน้าใช้ร่วมกัน |
| `src/assets/` | `site.css` และ favicon |
| `src/scripts/site.ts` | สีโค้ด ปุ่มคัดลอก คำอธิบายโค้ด สารบัญ โหมดมืด และเช็กลิสต์ ตอน build แปลงเป็น `assets/site.js` ด้วย `tools/bundle.ts` |
| `src/exercises/` | แบบฝึกหัด หนึ่งข้อหนึ่งโฟลเดอร์ |
| `tools/build.py` | ประกอบหน้าทั้งหมดไปไว้ที่ `dist/` แล้วตรวจลิงก์ |
| `tools/check_code.py` | คอมไพล์และรันโค้ดตัวอย่างกับเฉลยแบบฝึกหัดด้วย `rustc` |
| `.github/workflows/pages.yml` | build แล้วขึ้น GitHub Pages ทุกครั้งที่ push เข้า `main` |

`dist/` สร้างใหม่ทุกครั้ง ห้ามแก้ไฟล์ในนั้นโดยตรง และไม่ได้เก็บไว้ใน git

## เปิดดูในเครื่อง

ต้องมี Python 3.11 ขึ้นไป Node 24 ขึ้นไป และ Rust ผ่าน rustup (`rustc` อยู่ใน PATH) ครั้งแรกให้รัน `npm ci` ก่อน

```bash
npm ci
npm run typecheck
python tools/check_code.py
python tools/build.py --serve
```

`npm run typecheck` ตรวจ `src/scripts/` กับ `tools/bundle.ts` แบบ strict workflow ใช้ Node 24 แล้วเปิด http://127.0.0.1:8000

## ตรวจโค้ดในเอกสาร

```bash
python tools/check_code.py
```

ตัวตรวจใช้ `rustc --edition 2021` ไม่ได้เรียก `cargo` ทีละตัวอย่าง เพราะโค้ดในหน้าเป็นไฟล์เดียวไม่มี dependency น้องยังเขียนและรันด้วย `cargo new` แล้ว `cargo run` ตามบทเรียน

เลือกคอมไพเลอร์ได้ด้วย `RI_RUSTC` และรุ่นภาษาด้วย `RI_EDITION` ค่าเริ่มต้นคือ `rustc` กับ `2021`

- โค้ดตัวอย่างที่ใส่ `data-test="ชื่อ"` และ `data-lang="rust"` จะถูกคอมไพล์และรัน
- รันสองแบบ แบบตัวตรวจใส่ `-D warnings` กับ `-C opt-level=2` และแบบ `rustc` เปล่าที่ใกล้ `cargo run` ตอน dev
- บล็อก `data-lang="output" data-for="ชื่อ"` คือผลที่ต้องได้
- บล็อก `data-lang="input" data-for="ชื่อ"` คือข้อมูลเข้าของตัวอย่างนั้น
- ใส่ `data-allow-warnings` ถ้าตั้งใจให้ตัวอย่างนั้นมีคำเตือน
- ข้อความจากคอมไพเลอร์ในหน้าใช้ `data-lang="rustc"`

workflow ติดตั้ง rustup stable แล้วรัน `python3 tools/check_code.py` ก่อน `tools/build.py` ทุกครั้งที่ push เข้า `main`

## เพิ่มหน้าใหม่

1. สร้างไฟล์ใน `src/pages/` เช่น `src/pages/rust/01-variables/let-mut.html` ใส่เนื้อหาไว้ใน `<article class="doc">` และต้องมี `<h1>` เป็นชื่อเดียวกับใน `site.toml`
2. เพิ่มหน้านั้นใน `src/site.toml` ตามลำดับที่ต้องการ
3. รัน `python tools/build.py`

build จะหยุดพร้อมบอกสาเหตุถ้าเจอปัญหาเหล่านี้

- มีหน้าใน `site.toml` แต่ไม่มีไฟล์ หรือมีไฟล์แต่ไม่ได้ใส่ใน `site.toml`
- ลิงก์ชี้ไปไฟล์ที่ไม่มี หรือชี้ไป `#id` ที่ไม่มีในหน้านั้น
- `<h1>` ไม่ตรงกับชื่อใน `site.toml`
- มี `id` ซ้ำในหน้าเดียวกัน

น้ำเสียงและชิ้นส่วนที่ใช้ในเนื้อหาอยู่ใน `AUTHORING.md` ตัวอย่างครบอยู่ที่ `src/pages/rust/00-start/hello.html`

## เพิ่มแบบฝึกหัด

หนึ่งข้อคือหนึ่งโฟลเดอร์ใน `src/exercises/rust/<บท>/` ตั้งชื่อขึ้นต้นด้วยเลขลำดับ เช่น `01-hello-rust`

| ไฟล์ | คืออะไร |
|---|---|
| `task.toml` | `title` ชื่อข้อ, `level` 1 ถึง 3, `time_limit` วินาที, `hint` คำใบ้เป็น HTML (ไม่บังคับ) |
| `statement.html` | โจทย์ |
| `tests/sample*.in` `.out` | ตัวอย่างที่แสดงบนหน้าเว็บ |
| `tests/*.in` `.out` อื่นๆ | ชุดทดสอบที่ซ่อนไว้ |
| `solution.rs` | เฉลย ต้องผ่านทุกชุดทดสอบ |

ใส่หน้าแบบฝึกหัดของบทนั้นใน `site.toml` ด้วย `exercises = "rust/<บท>"` ดูบทที่ 0

สร้าง `.out` จากเฉลยได้ด้วย

```bash
python tools/make_outputs.py src/exercises/rust/01-variables/01-total
```

## โดเมน rust.teerapat.codes

zero-index ตั้งโดเมนที่หน้า Settings ของ GitHub Pages ไม่ได้เก็บไฟล์ `CNAME` ไว้ในรีโป ค่าที่ตั้งไว้คือ `zero.teerapat.codes` เว็บนี้ทำแบบเดียวกัน

1. พอ workflow บน `main` ผ่าน เว็บขึ้นที่ `https://clytie0x.github.io/rust-index/`
2. เจ้าของชี้ DNS เอง ไม่ได้ตั้งในรีโปนี้และไม่ได้ตั้งที่ Cloudflare จากที่นี่
   - ชนิดระเบียน `CNAME`
   - ชื่อ `rust`
   - ค่า `clytie0x.github.io`
3. ที่ GitHub เปิด Settings แล้ว Pages แล้ว Custom domain ใส่ `rust.teerapat.codes` แบบเดียวกับที่ zero-index ใส่ `zero.teerapat.codes`
4. รอให้ตรวจ DNS ผ่าน แล้วเปิด Enforce HTTPS

ถ้าอยากให้ชื่อโดเมนติดไปกับไฟล์ที่ deploy ให้วางไฟล์ชื่อ `CNAME` ที่รากของ `dist/` ทั้งไฟล์มีบรรทัดเดียวคือ

```text
rust.teerapat.codes
```

zero-index ไม่ได้ใส่ไฟล์นี้ โดเมนอยู่ที่การตั้งค่า Pages อย่าใส่ไฟล์นี้ก่อนที่ DNS จะชี้มา ไม่งั้นลิงก์ `github.io` อาจถูกพาไปโดเมนที่ยังไม่พร้อม

## สถานะ

`active` ชุดเริ่มต้น บทที่ 0 ถึง 3 มีแบบฝึกหัดสั้นๆ ให้ติวได้แล้ว บทที่ 4 ถึง 6 ยังเป็นแผนในหน้าแรก
