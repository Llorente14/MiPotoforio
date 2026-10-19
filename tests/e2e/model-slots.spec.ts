import { expect, test } from '@playwright/test';

const slots = [
  { id: 'untar', alt: /UNTAR Building 2/ },
  { id: 'temple', alt: /3D temple model/ },
  { id: 'akai', alt: /Akai Shuichi sniping scene/ },
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
