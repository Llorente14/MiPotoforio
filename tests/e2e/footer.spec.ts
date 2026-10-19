import { expect, test } from '@playwright/test';

for (const url of ['/', '/projects/', '/certificates/', '/projects/dapute/']) {
  test(`footer shows socials and copyright on ${url}`, async ({ page }) => {
    await page.goto(url);
    const footer = page.getByRole('contentinfo');
    await expect(footer.getByRole('link', { name: 'GitHub', exact: true })).toHaveAttribute(
      'href',
      'https://github.com/Llorente14',
    );
    await expect(footer.getByRole('link', { name: 'LinkedIn', exact: true })).toHaveAttribute(
      'href',
      'https://www.linkedin.com/in/axelchrisdy',
    );
    await expect(footer.getByRole('link', { name: 'Email', exact: true })).toHaveAttribute(
      'href',
      'mailto:axel.chrisdy@gmail.com',
    );
    await expect(footer.getByText(`© ${new Date().getFullYear()} Axel Chrisdy Sanjaya`)).toBeVisible();
  });
}

test('footer exposes the meadow top edge for particles', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('[data-meadow-top]')).toHaveCount(1);
});

test('scroll-to-top is hidden at the top and visible after scrolling', async ({ page }) => {
  await page.goto('/');
  const button = page.getByRole('button', { name: 'Scroll to top' });
  await expect(button).toBeHidden();
  await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
  await expect(button).toBeVisible();
});

test('scroll-to-top returns to the top by mouse', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
  await page.getByRole('button', { name: 'Scroll to top' }).click();
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBe(0);
  await expect(page.getByRole('button', { name: 'Scroll to top' })).toBeHidden();
});

test('scroll-to-top works by keyboard and moves focus to the document top', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
  const button = page.getByRole('button', { name: 'Scroll to top' });
  await button.focus();
  await page.keyboard.press('Enter');
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBe(0);
  await expect(page.locator('body')).toBeFocused();
});
