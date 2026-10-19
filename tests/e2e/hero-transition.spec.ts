import { expect, test } from '@playwright/test';

const cardOpacity = (page: import('@playwright/test').Page) =>
  page.locator('[data-hero-card]').evaluate((el) => Number(getComputedStyle(el).opacity));

test('desktop: card covers the viewport mid-transition, About follows, scrolling back restores the Hero', async ({
  page,
}, info) => {
  test.skip(info.project.name !== 'desktop');
  await page.goto('/');
  await expect(page.locator('[data-model-slot="kaito"] canvas')).toHaveCount(1, { timeout: 15_000 });
  const vh = page.viewportSize()!.height;

  // Mid-transition the card is large enough to cover the whole viewport.
  await page.evaluate((y) => window.scrollTo(0, y), vh * 0.55);
  await expect.poll(() => cardOpacity(page)).toBeGreaterThan(0.8);
  const box = (await page.locator('[data-hero-card]').boundingBox())!;
  expect(box.width).toBeGreaterThanOrEqual(page.viewportSize()!.width * 0.95);
  expect(box.height).toBeGreaterThanOrEqual(vh * 0.95);

  // Past the transition: card gone, About reachable.
  await page.evaluate(() => document.querySelector('#about')!.scrollIntoView());
  await expect(page.getByRole('heading', { name: 'About me' })).toBeInViewport();
  await expect.poll(() => cardOpacity(page)).toBe(0);

  // Reversible.
  await page.evaluate(() => window.scrollTo(0, 0));
  await expect(page.getByRole('heading', { level: 1 })).toBeInViewport();
  await expect.poll(() => cardOpacity(page)).toBe(0);
  await expect(page.locator('[data-hero-sky]')).toHaveCSS('opacity', '1');
});

test('desktop: after the transition the sky matches the chosen theme, the Hero stays night', async ({ page }, info) => {
  test.skip(info.project.name !== 'desktop');
  await page.goto('/');
  await page.getByRole('button', { name: 'Dusk' }).click();
  const heroNight = await page.locator('[data-hero-sky]').evaluate((el) => getComputedStyle(el).backgroundColor);
  await page.evaluate(() => document.querySelector('#about')!.scrollIntoView());
  await expect(page.locator('html')).toHaveAttribute('data-sky', 'dusk');
  await expect(page.locator('[data-hero-sky]')).toHaveCSS('opacity', '0');
  const dusk = await page.locator('.sky').evaluate((el) => getComputedStyle(el).backgroundImage);
  await page.getByRole('button', { name: 'Night' }).click();
  const night = await page.locator('.sky').evaluate((el) => getComputedStyle(el).backgroundImage);
  expect(dusk).not.toBe(night);
  // The Hero's own sky never follows the theme.
  expect(await page.locator('[data-hero-sky]').evaluate((el) => getComputedStyle(el).backgroundColor)).toBe(heroNight);
});

test('mobile: Hero uses a still Kaito, no 3D canvas, crossfade runs and About is reachable', async ({ page }, info) => {
  test.skip(info.project.name !== 'mobile');
  await page.goto('/');
  await expect(page.getByRole('img', { name: /Kaito Kid/ })).toBeVisible();
  await expect(page.locator('canvas:not([data-sakura])')).toHaveCount(0);
  await expect(page.locator('#hero')).toHaveCSS('position', 'relative'); // not pinned
  const vh = page.viewportSize()!.height;
  await page.evaluate((y) => window.scrollTo(0, y), vh * 0.5);
  await expect.poll(() => cardOpacity(page)).toBeGreaterThan(0.3);
  await page.evaluate(() => document.querySelector('#about')!.scrollIntoView());
  await expect(page.getByRole('heading', { name: 'About me' })).toBeInViewport();
});

test('reduced motion: no pinning and About is reachable by normal scroll', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  await expect(page.locator('.pin-spacer')).toHaveCount(0);
  expect(await cardOpacity(page)).toBe(0);
  await page.evaluate(() => document.querySelector('#about')!.scrollIntoView());
  await expect(page.getByRole('heading', { name: 'About me' })).toBeInViewport();
});
