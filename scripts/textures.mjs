// Rasterise the vector face decals the Blender scripts paint onto the heads:
//   blender/decals/*.svg -> blender/.cache/<name>.png
// Run before the Blender scripts:  node scripts/textures.mjs   (blender/.cache is gitignored)
import { mkdir, readdir, readFile } from 'node:fs/promises';
import { basename, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from '@playwright/test';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const out = resolve(root, 'blender/.cache');
await mkdir(out, { recursive: true });

const decalDir = resolve(root, 'blender/decals');
const jobs = [
  ...(await readdir(decalDir))
    .filter((f) => f.endsWith('.svg'))
    .map((f) => ({ src: resolve(decalDir, f), name: basename(f, '.svg'), width: 1024 })),
];

const browser = await chromium.launch();
for (const job of jobs) {
  const svg = await readFile(job.src, 'utf8');
  const [, , , vw, vh] = svg.match(/viewBox="([\d.-]+) ([\d.-]+) ([\d.]+) ([\d.]+)"/).map(Number);
  const height = Math.round((job.width * vh) / vw);
  const page = await browser.newPage({ viewport: { width: job.width, height } });
  await page.setContent(
    `<!doctype html><style>html,body{margin:0;background:transparent}svg{display:block;width:${job.width}px;height:${height}px}</style>${svg}`,
  );
  await page.screenshot({ path: resolve(out, `${job.name}.png`), omitBackground: true });
  await page.close();
  console.log(`${job.name}.png ${job.width}x${height}`);
}
await browser.close();
