// Rasterise the vector playing card (src/assets/card/*.svg) into the textures the Kaito model uses.
// Run before blender/kaito.py:  node scripts/card-textures.mjs  (writes blender/.cache/card-*.png, gitignored)
import { mkdir, readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { chromium } from '@playwright/test';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const font = (p) => pathToFileURL(resolve(root, 'node_modules', p)).href;
const W = 640;
const H = Math.round((W * 1400) / 1000);

const fonts = `
  @font-face { font-family: 'Archivo Variable'; font-stretch: 62% 125%; font-weight: 100 900;
    src: url('${font('@fontsource-variable/archivo/files/archivo-latin-wdth-normal.woff2')}') format('woff2'); }
  @font-face { font-family: 'Shippori Mincho'; font-weight: 700;
    src: url('${font('@fontsource/shippori-mincho/files/shippori-mincho-japanese-700-normal.woff2')}') format('woff2'); }
  html, body { margin: 0; background: transparent; }
  [filter] { display: none; } /* paper fibre is invisible at texture size and bloats the PNG */
  svg { display: block; width: ${W}px; height: ${H}px; }
`;

const out = resolve(root, 'blender/.cache');
await mkdir(out, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: W, height: H } });
for (const side of ['front', 'back']) {
  const svg = await readFile(resolve(root, 'src/assets/card', `${side}.svg`), 'utf8');
  await page.setContent(`<!doctype html><style>${fonts}</style>${svg}`);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: resolve(out, `card-${side}.png`), omitBackground: true });
  console.log(`card-${side}.png ${W}x${H}`);
}
await browser.close();
