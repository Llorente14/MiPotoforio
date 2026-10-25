import { expect, test } from '@playwright/test';

const slots = [
  { id: 'untar', alt: /UNTAR Building 2/ },
  { id: 'temple', alt: /3D temple model/ },
];

test('desktop mounts a canvas in each model slot once scrolled into view', async ({ page }, info) => {
  test.skip(info.project.name !== 'desktop');
  await page.goto('/');
  for (const { id } of slots) {
    const slot = page.locator(`[data-model-slot="${id}"]`);
    await slot.scrollIntoViewIfNeeded();
    await expect(slot.locator('canvas')).toHaveCount(1, { timeout: 15_000 });
  }
});

test('mobile never creates a 3D canvas and shows still images with alt text', async ({ page }, info) => {
  test.skip(info.project.name !== 'mobile');
  await page.goto('/');
  for (const { id, alt } of slots) {
    const slot = page.locator(`[data-model-slot="${id}"]`);
    await slot.scrollIntoViewIfNeeded();
    await expect(slot.getByRole('img', { name: alt })).toBeVisible();
  }
  await page.waitForTimeout(1000);
  await expect(page.locator('canvas:not([data-sakura])')).toHaveCount(0);
});

test('a scene does not capture page scrolling', async ({ page }, info) => {
  test.skip(info.project.name !== 'desktop');
  await page.goto('/');
  const slot = page.locator('[data-model-slot="untar"]');
  await slot.scrollIntoViewIfNeeded();
  await expect(slot.locator('canvas')).toHaveCount(1, { timeout: 15_000 });
  const box = (await slot.boundingBox())!;
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  const before = await page.evaluate(() => window.scrollY);
  await page.mouse.wheel(0, 400);
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBeGreaterThan(before);
});

test('reduced motion still shows the models', async ({ page }, info) => {
  test.skip(info.project.name !== 'desktop');
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  const slot = page.locator('[data-model-slot="temple"]');
  await slot.scrollIntoViewIfNeeded();
  await expect(slot.locator('canvas')).toHaveCount(1, { timeout: 15_000 });
});

test('a scene that loses its WebGL context comes back on a fresh canvas', async ({ page }, info) => {
  test.skip(info.project.name !== 'desktop');
  await page.goto('/');
  for (const { id } of slots) {
    const slot = page.locator(`[data-model-slot="${id}"]`);
    await slot.scrollIntoViewIfNeeded();
    const canvas = slot.locator('canvas');
    await expect(canvas).toHaveCount(1, { timeout: 15_000 });
    // What the GPU does to a frozen tab or a page restored from the back/forward cache.
    await canvas.evaluate((el: HTMLCanvasElement) => {
      el.dataset.lost = '';
      const lose = (el.getContext('webgl2') ?? el.getContext('webgl'))!.getExtension('WEBGL_lose_context')!;
      lose.loseContext();
      setTimeout(() => lose.restoreContext(), 300);
    });
    const fresh = slot.locator('canvas:not([data-lost])');
    await expect(fresh).toHaveCount(1, { timeout: 15_000 });
    expect(await fresh.evaluate((el: HTMLCanvasElement) => (el.getContext('webgl2') ?? el.getContext('webgl'))!.isContextLost())).toBe(false);
  }
});

test('a scene whose context never comes back still leaves the model visible', async ({ page }, info) => {
  test.skip(info.project.name !== 'desktop');
  await page.goto('/');
  const slot = page.locator('[data-model-slot="untar"]');
  await slot.scrollIntoViewIfNeeded();
  await expect(slot.locator('canvas')).toHaveCount(1, { timeout: 15_000 });
  await slot.locator('canvas').evaluate((el: HTMLCanvasElement) => {
    el.dataset.lost = '';
    (el.getContext('webgl2') ?? el.getContext('webgl'))!.getExtension('WEBGL_lose_context')!.loseContext();
  });
  // Either a fresh scene or the still render takes the old canvas's place.
  await expect(slot.locator('canvas:not([data-lost]), img')).toHaveCount(1, { timeout: 15_000 });
});
