// news-image-20261120 entrypoint (Node 22, stdlib only).
// Copies the pre-drawn front page (entry.png, produced by draw.py)
// into the grader's output directory.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const dir = path.dirname(fileURLToPath(import.meta.url));

const outDir = process.env.MAKEFUN_OUTPUT_DIR;
if (!outDir) {
  console.error("MAKEFUN_OUTPUT_DIR is not set");
  process.exit(1);
}

const src = path.join(dir, "entry.png");
const dst = path.join(outDir, "entry.png");

fs.mkdirSync(outDir, { recursive: true });
fs.copyFileSync(src, dst);
console.log("wrote " + dst);
