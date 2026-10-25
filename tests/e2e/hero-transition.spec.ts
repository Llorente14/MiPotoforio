import { expect, test } from '@playwright/test';

const cardOpacity = (page: import('@playwright/test').Page) =>
  page.locator('[data-hero-card]').evaluate((el) => Number(getComputedStyle(el).opacity));

test("desktop: the card grows from Kaito's hand to cover the viewport, About follows, scrolling back restores the Hero", async ({
  page,
}, info) => {
  test.skip(info.project.name !== 'desktop');
  await page.goto('/');
  await expect(page.locator('[data-model-slot="kaito"] canvas')).toHaveCount(1, { timeout: 15_000 });
  const vh = page.viewportSize()!.height;

  const card = page.locator('[data-hero-card]');
  const width = async () => (await card.boundingBox())!.width;

  // Early on the card has just left his fingers: visible and still small.
  await page.evaluate((y) => window.scrollTo(0, y), vh * 0.15);
  await expect.poll(() => cardOpacity(page)).toBeGreaterThan(0.8);
  expect(await width()).toBeLessThan(page.viewportSize()!.width * 0.3);

  // Late in the transition it has spread into a page that covers the whole viewport.
  await page.evaluate((y) => window.scrollTo(0, y), vh * 1.35);
  await expect.poll(width).toBeGreaterThanOrEqual(page.viewportSize()!.width * 0.95);
  expect((await card.boundingBox())!.height).toBeGreaterThanOrEqual(vh * 0.95);
  expect(await cardOpacity(page)).toBeGreaterThan(0.8);

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
  await page.getByRole('button', { name: 'Night' }).click();
  const heroNight = await page.locator('[data-hero-sky]').evaluate((el) => getComputedStyle(el).backgroundColor);
  await page.evaluate(() => document.querySelector('#about')!.scrollIntoView());
  await expect(page.locator('html')).toHaveAttribute('data-sky', 'night');
  await expect(page.locator('[data-hero-sky]')).toHaveCSS('opacity', '0');
  const night = await page.locator('.sky').evaluate((el) => getComputedStyle(el).backgroundImage);
  await page.getByRole('button', { name: 'Light' }).click();
  const light = await page.locator('.sky').evaluate((el) => getComputedStyle(el).backgroundImage);
  expect(light).not.toBe(night);
  // The Hero's own sky never follows the theme.
  expect(await page.locator('[data-hero-sky]').evaluate((el) => getComputedStyle(el).backgroundColor)).toBe(heroNight);
});

test('mobile: Hero uses a still Kaito, no 3D canvas or card, the sky crossfade runs and About is reachable', async ({ page }, info) => {
  test.skip(info.project.name !== 'mobile');
  await page.goto('/');
  await expect(page.getByRole('img', { name: /Kaito Kid/ })).toBeVisible();
  await expect(page.locator('canvas:not([data-sakura])')).toHaveCount(0);
  await expect(page.locator('#hero')).toHaveCSS('position', 'relative'); // not pinned
  const hero = page.locator('#hero');
  await expect(hero.getByText('UNTAR · Jakarta')).toBeVisible();
  await expect(hero.getByText(/106°47/)).toBeHidden();
  // The campus line sits under the social icons.
  const icons = (await hero.getByRole('list', { name: 'Find Axel online' }).boundingBox())!;
  expect((await hero.getByText('UNTAR · Jakarta').boundingBox())!.y).toBeGreaterThanOrEqual(icons.y + icons.height);
  const vh = page.viewportSize()!.height;
  await page.evaluate((y) => window.scrollTo(0, y), vh * 0.6);
  const skyOpacity = () => page.locator('[data-hero-sky]').evaluate((el) => Number(getComputedStyle(el).opacity));
  await expect.poll(skyOpacity).toBeLessThan(0.9);
  expect(await cardOpacity(page)).toBe(0);
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
