/* rust-index ต้นแบบเว็บเอกสาร เขียนเองทั้งหมด ไม่ใช้ไลบรารี
   tools/bundle.ts แปลงเป็น assets/site.js ตอน build */

const root = document.documentElement;
const THEME_KEY = "ri-theme";
const darkQuery = window.matchMedia("(prefers-color-scheme: dark)");

function $<T extends Element = HTMLElement>(sel: string, ctx: ParentNode = document): T | null {
  return ctx.querySelector<T>(sel);
}
function $all<T extends Element = HTMLElement>(sel: string, ctx: ParentNode = document): T[] {
  return Array.from(ctx.querySelectorAll<T>(sel));
}
function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/* ---------- โหมดมืด ---------- */

function effectiveTheme(): "light" | "dark" {
  const t = root.getAttribute("data-theme");
  if (t === "light" || t === "dark") return t;
  return darkQuery.matches ? "dark" : "light";
}

function syncThemeButton(): void {
  const btn = $(".theme-btn");
  if (!btn) return;
  const label = effectiveTheme() === "dark" ? "เปลี่ยนเป็นโหมดสว่าง" : "เปลี่ยนเป็นโหมดมืด";
  btn.setAttribute("aria-label", label);
  btn.setAttribute("title", label);
}

function initTheme(): void {
  const btn = $(".theme-btn");
  if (!btn) return;
  syncThemeButton();
  btn.addEventListener("click", () => {
    const next = effectiveTheme() === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try {
      localStorage.setItem(THEME_KEY, next);
    } catch {
      /* ไม่มีที่เก็บก็ยังสลับได้ */
    }
    syncThemeButton();
  });
  darkQuery.addEventListener("change", syncThemeButton);
}

/* ---------- เมนูบนจอแคบ ---------- */

function initDrawer(): void {
  const body = document.body;
  const openBtn = $(".menu-btn");
  const closeBtn = $(".drawer-close");
  const scrim = $(".scrim");
  if (!openBtn) return;

  function setOpen(open: boolean): void {
    body.classList.toggle("nav-open", open);
    openBtn?.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) {
      const current = $('.sidebar a[aria-current="page"]') ?? $(".sidebar a");
      current?.focus({ preventScroll: true });
    }
  }

  openBtn.addEventListener("click", () => setOpen(!body.classList.contains("nav-open")));
  closeBtn?.addEventListener("click", () => {
    setOpen(false);
    openBtn.focus();
  });
  scrim?.addEventListener("click", () => setOpen(false));
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && body.classList.contains("nav-open")) {
      setOpen(false);
      openBtn.focus();
    }
  });
  for (const a of $all(".sidebar a")) a.addEventListener("click", () => setOpen(false));
  window.addEventListener("resize", () => {
    if (window.innerWidth >= 960 && body.classList.contains("nav-open")) setOpen(false);
  });
}

/* ---------- สีไวยากรณ์ภาษา Rust ---------- */

const RUST_TYPES = /^(i8|i16|i32|i64|i128|isize|u8|u16|u32|u64|u128|usize|f32|f64|bool|char|str|String|Vec|Option|Result|Box|Rc|Arc|HashMap|HashSet|Mutex)$/;
const RUST_CTORS = /^(Some|None|Ok|Err)$/;
const RUST_KEYWORDS = /^(as|async|await|break|const|continue|crate|else|enum|extern|false|fn|for|if|impl|in|let|loop|match|mod|move|mut|pub|ref|return|self|Self|static|struct|super|trait|true|type|unsafe|use|where|while|dyn|_)$/;

/* ตำแหน่งที่จะใส่ปุ่มคำอธิบายแทน // (n)! */
const ANNO_MARK = "\u0000ANNO\u0000";

interface Highlighted {
  html: string;
  anno: string | null; // เลขคำอธิบาย ถ้าบรรทัดนี้มี // (n)!
}

function tk(cls: string, text: string): string {
  return '<span class="tk-' + cls + '">' + esc(text) + "</span>";
}

function hlString(s: string): string {
  let out = "";
  let last = 0;
  const re = /\\./g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(s))) {
    out += esc(s.slice(last, m.index)) + '<span class="tk-esc">' + esc(m[0]) + "</span>";
    last = m.index + m[0].length;
  }
  return '<span class="tk-str">' + out + esc(s.slice(last)) + "</span>";
}

function hlCodeRust(s: string): Highlighted {
  const re = /(\/\/.*$)|("(?:\\.|[^"\\])*")|('(?:\\.|[^'\\])*')|(\b\d[\d_]*(?:\.\d+)?\b)|([A-Za-z_]\w*)|(\s+)|([\s\S])/g;
  let out = "";
  let anno: string | null = null;
  let m: RegExpExecArray | null;
  while ((m = re.exec(s))) {
    const [whole, comment, dq, sq, num, word] = m;
    if (comment) {
      const a = /^\/\/\s*\((\d+)\)!\s*$/.exec(comment);
      if (a?.[1]) {
        anno = a[1];
        out += ANNO_MARK;
      } else out += tk("com", comment);
    } else if (dq) out += hlString(dq);
    else if (sq) out += hlString(sq);
    else if (num) out += tk("num", num);
    else if (word) {
      if (RUST_TYPES.test(word) || RUST_CTORS.test(word)) out += tk("type", word);
      else if (RUST_KEYWORDS.test(word)) out += tk("kw", word);
      else if (/^\s*[!(]/.test(s.slice(re.lastIndex))) out += tk("fn", word);
      else out += esc(word);
    } else out += esc(whole);
  }
  return { html: out, anno };
}

/* ---------- สีข้อความจาก rustc ---------- */

/* บรรทัดที่มีเลขหน้า | คือโค้ดของเรา บรรทัด | ที่ไม่มีเลขคือ ^ ชี้จุดผิด หรือคำแนะนำให้แก้ */
function hlRustc(line: string): string {
  const diag = /^(\s*)(error|warning|note|help)(\[[A-Za-z0-9_]+\])?(:)(.*)$/.exec(line);
  if (diag) {
    const [, indent = "", sev = "", code = "", colon = "", msg = ""] = diag;
    const cls = sev === "help" ? "note" : sev;
    return esc(indent) + tk("sev-" + cls, sev + code + colon) + esc(msg);
  }
  const arrow = /^(\s*-->\s*)(\S.*)$/.exec(line);
  if (arrow) {
    const [, mark = "", loc = ""] = arrow;
    return esc(mark) + tk("loc", loc);
  }
  const eq = /^(\s*)(= (?:note|help|warning):)(.*)$/.exec(line);
  if (eq) {
    const [, indent = "", head = "", msg = ""] = eq;
    return esc(indent) + tk("sev-note", head) + esc(msg);
  }
  const src = /^(\s*(?:\d+|\+\+\+)?\s*)\|(.*)$/.exec(line);
  if (src) {
    const [, num = "", code = ""] = src;
    const gutter = tk("gutter", num + "|");
    if (/\d/.test(num)) return gutter + esc(code);
    const mark = /^(\s*)([\^~-]+)(.*)$/.exec(code);
    if (mark) {
      const [, gap = "", marks = "", rest = ""] = mark;
      return gutter + esc(gap) + tk("caret", marks) + esc(rest);
    }
    if (/\S/.test(code)) return gutter + tk("fix", code);
    return gutter + esc(code);
  }
  return esc(line);
}

const ICON_COPY = '<svg class="i-copy" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1"/></svg>';
const ICON_CHECK = '<svg class="i-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>';

function copyText(text: string): Promise<void> {
  if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
  return new Promise((resolve, reject) => {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try {
      if (document.execCommand("copy")) resolve();
      else reject(new Error("copy failed"));
    } catch (e) {
      reject(e instanceof Error ? e : new Error(String(e)));
    }
    document.body.removeChild(ta);
  });
}

function initCode(): void {
  for (const block of $all(".code")) {
    const codeEl = $("code", block);
    if (!codeEl) continue;
    const lang = block.getAttribute("data-lang") ?? "text";
    const raw = (codeEl.textContent ?? "").replace(/\n$/, "");
    const cleanLines: string[] = [];

    const html = raw
      .split("\n")
      .map((line) => {
        let inner: string;
        if (lang === "rustc") {
          inner = hlRustc(line);
          cleanLines.push(line);
        } else if (lang === "rust") {
          const r = hlCodeRust(line);
          inner = r.html;
          if (r.anno) {
            inner = inner.replace(
              ANNO_MARK,
              '<button type="button" class="anno-btn" data-anno="' + r.anno + '" aria-expanded="false" aria-label="คำอธิบายข้อ ' + r.anno + '">' + r.anno + "</button>",
            );
            cleanLines.push(line.replace(/\s*\/\/\s*\(\d+\)!\s*$/, ""));
          } else cleanLines.push(line);
        } else {
          inner = esc(line);
          cleanLines.push(line);
        }
        return '<span class="ln">' + inner + "</span>";
      })
      .join("\n");

    codeEl.innerHTML = html;

    /* ผลลัพธ์จากโปรแกรมไม่มีอะไรให้คัดลอกไปใช้ */
    if (lang === "output") continue;

    const copyBtn = document.createElement("button");
    copyBtn.type = "button";
    copyBtn.className = "copy-btn";
    copyBtn.setAttribute("aria-label", "คัดลอกโค้ด");
    copyBtn.setAttribute("title", "คัดลอกโค้ด");
    copyBtn.innerHTML = ICON_COPY + ICON_CHECK;
    const cleanText = cleanLines.join("\n") + "\n";
    copyBtn.addEventListener("click", () => {
      copyText(cleanText).then(
        () => {
          copyBtn.classList.add("is-done");
          copyBtn.setAttribute("title", "คัดลอกแล้ว");
          setTimeout(() => {
            copyBtn.classList.remove("is-done");
            copyBtn.setAttribute("title", "คัดลอกโค้ด");
          }, 1600);
        },
        () => {
          /* คัดลอกไม่ได้ ปล่อยให้เลือกข้อความเอง */
        },
      );
    });
    block.appendChild(copyBtn);

    if (block.hasAttribute("data-annotate")) initAnnotations(block);
  }
}

/* ---------- คำอธิบายโค้ดแบบวงกลมตัวเลข ---------- */

interface OpenAnno {
  btn: HTMLElement;
  pop: HTMLElement;
  block: HTMLElement;
}

let openAnno: OpenAnno | null = null;

function closeAnno(): void {
  if (!openAnno) return;
  openAnno.btn.setAttribute("aria-expanded", "false");
  openAnno.pop.hidden = true;
  openAnno = null;
}

function placePop(block: HTMLElement, btn: HTMLElement, pop: HTMLElement): void {
  const b = btn.getBoundingClientRect();
  const w = block.getBoundingClientRect();
  const popW = pop.offsetWidth;
  let left = b.left - w.left - 14;
  left = Math.max(8, Math.min(left, w.width - popW - 8));
  pop.style.left = left + "px";
  pop.style.top = b.bottom - w.top + 8 + "px";
}

function initAnnotations(block: HTMLElement): void {
  const list = block.nextElementSibling;
  if (!list?.classList.contains("anno-list") || !(list instanceof HTMLElement)) return;
  const items = $all(":scope > li", list);
  const pop = document.createElement("div");
  pop.className = "anno-pop";
  pop.hidden = true;
  pop.id = "anno-pop-" + Math.random().toString(36).slice(2, 8);
  pop.setAttribute("role", "note");
  block.appendChild(pop);
  list.hidden = true;

  for (const btn of $all(".anno-btn", block)) {
    btn.setAttribute("aria-controls", pop.id);
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const same = openAnno?.btn === btn;
      closeAnno();
      if (same) return;
      const item = items[parseInt(btn.getAttribute("data-anno") ?? "", 10) - 1];
      if (!item) return;
      pop.innerHTML = item.innerHTML;
      pop.hidden = false;
      btn.setAttribute("aria-expanded", "true");
      placePop(block, btn, pop);
      openAnno = { btn, pop, block };
    });
  }

  $("pre", block)?.addEventListener("scroll", closeAnno);
  pop.addEventListener("click", (e) => e.stopPropagation());
}

function initAnnoGlobal(): void {
  document.addEventListener("click", closeAnno);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && openAnno) {
      const b = openAnno.btn;
      closeAnno();
      b.focus();
    }
  });
  window.addEventListener("resize", () => {
    if (openAnno) placePop(openAnno.block, openAnno.btn, openAnno.pop);
  });
}

/* ---------- สารบัญในหน้า และไฮไลต์ขณะเลื่อน ---------- */

function initToc(): void {
  const headings = $all(".doc h2[id], .doc h3[id]");
  const tocList = $("#toc-list");
  const inline = $(".toc-inline");
  const toc = $(".toc");

  for (const h of headings) {
    const a = document.createElement("a");
    a.className = "anchor";
    a.href = "#" + h.id;
    a.setAttribute("aria-label", "ลิงก์มาที่หัวข้อนี้");
    a.textContent = "#";
    h.appendChild(a);
  }

  if (!headings.length) {
    if (toc) toc.style.visibility = "hidden";
    return;
  }

  function title(h: HTMLElement): string {
    const clone = h.cloneNode(true);
    if (!(clone instanceof HTMLElement)) return "";
    for (const n of $all(".anchor", clone)) n.remove();
    return (clone.textContent ?? "").trim();
  }

  function build(ul: HTMLElement | null): HTMLAnchorElement[] {
    if (!ul) return [];
    return headings.map((h) => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = "#" + h.id;
      a.textContent = title(h);
      a.className = h.tagName === "H3" ? "lvl-3" : "lvl-2";
      li.appendChild(a);
      ul.appendChild(li);
      return a;
    });
  }

  const linksA = build(tocList);
  const linksB = build(inline);
  let activeIdx = -1;

  function update(): void {
    const offset = 90 + 24;
    let idx = 0;
    for (const [i, h] of headings.entries()) {
      if (h.getBoundingClientRect().top - offset <= 0) idx = i;
      else break;
    }
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) {
      idx = headings.length - 1;
    }
    if (idx === activeIdx) return;
    activeIdx = idx;
    for (const links of [linksA, linksB]) {
      links.forEach((a, i) => a.classList.toggle("is-active", i === idx));
    }
    const act = linksA[idx];
    if (act && toc && toc.offsetParent !== null) {
      const r = act.getBoundingClientRect();
      const tr = toc.getBoundingClientRect();
      if (r.top < tr.top || r.bottom > tr.bottom) act.scrollIntoView({ block: "nearest" });
    }
  }

  let ticking = false;
  window.addEventListener(
    "scroll",
    () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        ticking = false;
        update();
      });
    },
    { passive: true },
  );
  window.addEventListener("resize", update);
  update();
}

/* ---------- เช็กลิสต์ จำค่าไว้ในเครื่อง ---------- */

/* เบราว์เซอร์ไม่ให้เก็บ เช็กลิสต์ยังกดได้แต่จะไม่จำ */
function load(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function save(key: string, value: string | null): void {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch {
    /* ไม่จำก็ไม่เป็นไร */
  }
}

function initChecklist(): void {
  const page = location.pathname;
  const boxes = $all<HTMLInputElement>(".task-list input[type=checkbox]");
  boxes.forEach((box, i) => {
    const key = "ri-check:" + page + ":" + i;
    box.checked = load(key) === "1";
    box.addEventListener("change", () => {
      save(key, box.checked ? "1" : null);
      const all = boxes.every((b) => b.checked);
      save("ri-done:" + page, all ? "1" : null);
      markDone();
    });
  });
  markDone();
}

function markDone(): void {
  for (const a of $all<HTMLAnchorElement>(".sidebar a[href]")) {
    const path = new URL(a.getAttribute("href") ?? "", location.href).pathname;
    a.classList.toggle("is-done", load("ri-done:" + path) === "1");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initChecklist();
  initTheme();
  initDrawer();
  initCode();
  initAnnoGlobal();
  initToc();
});

export {};
