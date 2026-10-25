// Site icons and the share card, all from Kid's mark (Axel's artwork, the middle of the calling card):
//   public/brand/kaito-card.webp -> public/favicon.ico, favicon-32.png, apple-touch-icon.png,
//                                   icon-192.png, icon-512.png, icon-maskable-512.png, og.png
// Re-run after changing the mark or the palette:  node scripts/brand-icons.mjs
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from '@playwright/test';
import sharp from 'sharp';

sharp.cache(false);
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const pub = (f) => resolve(root, 'public', f);

// Washi paper and sumi ink, as in src/styles/global.css.
const PAPER = '#ece4d0';
const INK = '#17140f';

// The mark as an alpha mask (ink = opaque), trimmed to its drawing.
const mask = await sharp(pub('brand/kaito-card.webp'))
  .flatten({ background: '#ffffff' })
  .grayscale()
  .negate()
  .trim({ threshold: 20 })
  .toColourspace('b-w')
  .png()
  .toBuffer();
const { width: mw, height: mh } = await sharp(mask).metadata();
const side = Math.max(mw, mh);

// Thicken the lines so they survive at 16-48 px: blur the mask, then cut it at a low level.
async function thickMask(amount) {
  if (amount === 0) return mask;
  const blurred = await sharp(mask).blur(amount).png().toBuffer();
  return sharp(blurred).threshold(40).toColourspace('b-w').png().toBuffer();
}

// Ink mark centred on a paper tile. `pad` is the share of the tile left around the mark.
async function icon(size, { pad, radius, thicken = 0, tile = true }) {
  const inner = Math.round(size * (1 - pad * 2));
  const alpha = await sharp(await thickMask(thicken))
    .resize({ width: inner, height: inner, fit: 'contain', background: '#000000' })
    .extend({
      top: Math.floor((size - inner) / 2),
      bottom: Math.ceil((size - inner) / 2),
      left: Math.floor((size - inner) / 2),
      right: Math.ceil((size - inner) / 2),
      background: '#000000',
    })
    .linear(thicken ? 1.6 : 1, 0)
    .toColourspace('b-w')
    .raw()
    .toBuffer();
  const ink = await sharp({ create: { width: size, height: size, channels: 3, background: INK } })
    .joinChannel(alpha, { raw: { width: size, height: size, channels: 1 } })
    .png()
    .toBuffer();
  if (!tile) return ink;
  const r = Math.round(size * radius);
  const paper = Buffer.from(
    `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}"><rect width="${size}" height="${size}" rx="${r}" fill="${PAPER}"/></svg>`,
  );
  return sharp(paper).composite([{ input: ink }]).png().toBuffer();
}

// A .ico is a small directory of PNG images.
function ico(pngs) {
  const header = Buffer.alloc(6 + 16 * pngs.length);
  header.writeUInt16LE(0, 0);
  header.writeUInt16LE(1, 2);
  header.writeUInt16LE(pngs.length, 4);
  let offset = header.length;
  pngs.forEach(({ size, data }, i) => {
    const e = 6 + 16 * i;
    header.writeUInt8(size >= 256 ? 0 : size, e);
    header.writeUInt8(size >= 256 ? 0 : size, e + 1);
    header.writeUInt16LE(1, e + 4);
    header.writeUInt16LE(32, e + 6);
    header.writeUInt32LE(data.length, e + 8);
    header.writeUInt32LE(offset, e + 12);
    offset += data.length;
  });
  return Buffer.concat([header, ...pngs.map((p) => p.data)]);
}

const blur = (size) => Math.max(0.3, (side / size) * 0.32);
const small = await Promise.all(
  [16, 32, 48].map(async (size) => ({ size, data: await icon(size, { pad: 0.06, radius: 0.18, thicken: blur(size) }) })),
);
await writeFile(pub('favicon.ico'), ico(small));
await writeFile(pub('favicon-32.png'), small[1].data);
await writeFile(pub('apple-touch-icon.png'), await icon(180, { pad: 0.14, radius: 0 }));
await writeFile(pub('icon-192.png'), await icon(192, { pad: 0.1, radius: 0.18 }));
await writeFile(pub('icon-512.png'), await icon(512, { pad: 0.1, radius: 0.18 }));
// Maskable: the launcher crops to its own shape, so keep the mark inside the 80% safe zone.
await writeFile(pub('icon-maskable-512.png'), await icon(512, { pad: 0.2, radius: 0 }));

// Share card: the site's own type and palette, rendered in a browser so the fonts are the real ones.
const dataUrl = (buf, type) => `data:${type};base64,${buf.toString('base64')}`;
const font = async (pkg, file) => dataUrl(await readFile(resolve(root, 'node_modules', pkg, 'files', file)), 'font/woff2');
const archivo = await font('@fontsource-variable/archivo', 'archivo-latin-wdth-normal.woff2');
const zen = await font('@fontsource/zen-kaku-gothic-new', 'zen-kaku-gothic-new-latin-400-normal.woff2');
const markUrl = dataUrl(await icon(512, { pad: 0, radius: 0, tile: false }), 'image/png');
const html = `<!doctype html><style>
@font-face { font-family: Archivo; src: url(${archivo}); font-stretch: 62% 125%; font-weight: 100 900; }
@font-face { font-family: Zen; src: url(${zen}); }
html, body { margin: 0; }
body { width: 1200px; height: 630px; background: ${PAPER}; color: ${INK}; display: flex; align-items: center; gap: 64px; padding: 0 88px; box-sizing: border-box; position: relative; }
.frame { position: absolute; inset: 22px; border: 3px solid ${INK}; }
.frame::after { content: ''; position: absolute; inset: 8px; border: 1px solid ${INK}; }
.card { flex: none; width: 300px; height: 420px; background: #fff; border-radius: 14px; border: 2px solid #d6d3cc; display: grid; place-items: center; transform: rotate(-6deg); box-shadow: 0 18px 40px rgba(23, 20, 15, 0.18); }
.card { position: relative; }
.card img { width: 236px; }
.card i { position: absolute; font: 400 54px/1 'Times New Roman', serif; font-style: normal; color: #111; }
.card i:first-of-type { top: 18px; left: 24px; }
.card i:last-of-type { bottom: 18px; right: 24px; transform: rotate(180deg); }
.label { font: 600 20px/1 Archivo; letter-spacing: 0.18em; text-transform: uppercase; opacity: 0.75; }
h1 { margin: 22px 0 26px; font: 800 118px/0.88 Archivo; font-stretch: 62%; text-transform: uppercase; letter-spacing: -0.01em; }
h1 span { color: #b2301b; display: block; }
p { margin: 0; font: 400 30px/1.4 Zen; max-width: 640px; }
</style>
<div class="frame"></div>
<div class="card"><i>A</i><img src="${markUrl}" alt=""><i>A</i></div>
<div>
  <div class="label">Portfolio · UNTAR Informatics</div>
  <h1>Axel <span>Chrisdy</span> Sanjaya</h1>
  <p>Informatics Engineering student in Jakarta, building things for the web.</p>
</div>`;
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
await page.setContent(html, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await writeFile(pub('og.png'), await sharp(await page.screenshot()).png({ compressionLevel: 9, palette: true }).toBuffer());
await browser.close();

console.log(`icons: favicon.ico (16/32/48), favicon-32, apple-touch-icon, icon-192/512, maskable; og.png (${(await readFile(pub('og.png'))).length} bytes)`);
