import { expect, test } from '@playwright/test';

test('sections ease in once when scrolled into view', async ({ page }) => {
  await page.goto('/');
  const github = page.locator('#github');
  await expect(github).toHaveClass(/reveal(?!-)/);
  await github.scrollIntoViewIfNeeded();
  await expect(github).toHaveClass(/reveal-in/);
  await expect.poll(() => github.evaluate((el) => getComputedStyle(el).opacity)).toBe('1');
  // Scrolling away does not replay it.
  await page.evaluate(() => window.scrollTo(0, 0));
  await expect(github).toHaveClass(/reveal-in/);
});

test('reduced motion adds no entrance animation', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  await expect(page.locator('.reveal')).toHaveCount(0);
  await expect(page.locator('#github')).toHaveCSS('opacity', '1');
});
