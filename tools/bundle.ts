// แปลง src/scripts/site.ts เป็น assets/site.js ให้ tools/build.py
//     node tools/bundle.ts <ไฟล์ปลายทาง>
// ต้องใช้ Node 24 ขึ้นไป ซึ่งรันไฟล์ .ts ได้เอง
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as esbuild from "esbuild";

const ROOT = fileURLToPath(new URL("..", import.meta.url));
const outfile = process.argv[2];
if (!outfile) {
  console.error("ใช้ node tools/bundle.ts <ไฟล์ปลายทาง>");
  process.exit(2);
}

await esbuild.build({
  entryPoints: [path.join(ROOT, "src/scripts/site.ts")],
  outfile,
  bundle: true,
  format: "iife",
  minify: true,
  legalComments: "none",
  target: ["es2020"],
  logLevel: "warning",
});
