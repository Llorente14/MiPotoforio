import { expect, test } from '@playwright/test';

// Count requestAnimationFrame calls made by the page from the start.
const countRaf = () => {
  const w = window as unknown as { __raf: number };
  w.__raf = 0;
  const orig = window.requestAnimationFrame.bind(window);
  window.requestAnimationFrame = (cb) => {
    w.__raf++;
    return orig(cb);
  };
};

test('particle canvas exists, is aria-hidden and ignores pointer events', async ({ page }) => {
  await page.goto('/');
  const canvas = page.locator('canvas[data-sakura]');
  await expect(canvas).toHaveCount(1);
  await expect(canvas).toHaveAttribute('aria-hidden', 'true');
  await expect(canvas).toHaveCSS('pointer-events', 'none');
});

test('particles animate under normal motion', async ({ page }) => {
  await page.addInitScript(countRaf);
  await page.goto('/');
  await page.waitForTimeout(500);
  const before = await page.evaluate(() => (window as any).__raf as number);
  await page.waitForTimeout(500);
  const after = await page.evaluate(() => (window as any).__raf as number);
  expect(after).toBeGreaterThan(before);
});

test('reduced motion runs no animation loop', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.addInitScript(countRaf);
  await page.goto('/');
  await expect(page.locator('canvas[data-sakura]')).toHaveCount(1);
  await page.waitForTimeout(1000);
  const count = await page.evaluate(() => (window as any).__raf as number);
  expect(count).toBe(0);
});

test('particles cause no long main-thread tasks while idle', async ({ page }) => {
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(500);
  const longTasks = await page.evaluate(
    () =>
      new Promise<number[]>((resolve) => {
        const seen: number[] = [];
        new PerformanceObserver((list) => list.getEntries().forEach((e) => seen.push(e.duration))).observe({
          entryTypes: ['longtask'],
        });
        setTimeout(() => resolve(seen), 2000);
      }),
  );
  expect(longTasks.filter((d) => d > 50)).toEqual([]);
});
