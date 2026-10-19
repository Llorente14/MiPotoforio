import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';

const themes = ['Day', 'Dusk', 'Night'] as const;

async function scan(page: import('@playwright/test').Page) {
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
  return results.violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(' ')).join(' | ')}`);
}

for (const theme of themes) {
  test(`landing has no axe violations in the ${theme} sky theme`, async ({ page }) => {
    // Reduced motion keeps the Hero unpinned and every Section at rest, so the scan is deterministic.
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.goto('/');
    await page.getByRole('button', { name: theme }).click();
    expect(await scan(page)).toEqual([]);
  });
}

for (const url of ['/projects/', '/projects/dapute/', '/certificates/']) {
  test(`${url} has no axe violations`, async ({ page }) => {
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.goto(url);
    expect(await scan(page)).toEqual([]);
  });
}

test('heading order has a single h1 and no skipped levels on the landing page', async ({ page }) => {
  await page.goto('/');
  const levels = await page.locator('main :is(h1,h2,h3,h4)').evaluateAll((els) => els.map((e) => Number(e.tagName[1])));
  expect(levels.filter((l) => l === 1)).toHaveLength(1);
  levels.reduce((prev, cur) => {
    expect(cur - prev).toBeLessThanOrEqual(1);
    return cur;
  }, 1);
});

// axe cannot see through the fixed sky gradient, so check the real pairs from the design tokens.
const luminance = (hex: string) => {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255).map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};
const ratio = (a: string, b: string) => {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
};

for (const theme of themes) {
  test(`body text stays readable over the whole ${theme} sky`, async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: theme }).click();
    const t = await page.evaluate(() => {
      const css = getComputedStyle(document.documentElement);
      const get = (n: string) => css.getPropertyValue(n).trim();
      return { ink: get('--color-ink'), paper: get('--color-paper'), torii: get('--color-torii'), top: get('--sky-top'), bottom: get('--sky-bottom') };
    });
    expect(ratio(t.ink, t.top)).toBeGreaterThanOrEqual(4.5);
    expect(ratio(t.ink, t.bottom)).toBeGreaterThanOrEqual(4.5);
    expect(ratio(t.ink, t.paper)).toBeGreaterThanOrEqual(4.5);
    // Buttons: paper text on a torii background.
    expect(ratio(t.paper, t.torii)).toBeGreaterThanOrEqual(4.5);
  });
}
