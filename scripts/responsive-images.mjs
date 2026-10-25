// Smaller copies of the large stills so phones don't download desktop-sized images:
//   public/renders/<name>.webp -> <name>-480.webp, <name>-720.webp
//   public/covers/<name>.webp  -> <name>-480.webp, <name>-800.webp
// The originals stay as the largest srcset candidate. Re-run after adding or replacing an image:
//   node scripts/responsive-images.mjs
import { readdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const jobs = [
  { dir: 'public/renders', widths: [480, 720] },
  { dir: 'public/covers', widths: [480, 800] },
];

for (const { dir, widths } of jobs) {
  const abs = resolve(root, dir);
  const originals = (await readdir(abs)).filter((f) => /^[a-z0-9-]+\.webp$/.test(f) && !/-\d+\.webp$/.test(f));
  for (const file of originals) {
    for (const width of widths) {
      const out = resolve(abs, file.replace(/\.webp$/, `-${width}.webp`));
      await sharp(resolve(abs, file)).resize({ width }).webp({ quality: 80 }).toFile(out);
    }
  }
  console.log(`${dir}: ${originals.length} images x ${widths.join(', ')}w`);
}
