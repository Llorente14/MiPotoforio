import { expect, test, type Page } from '@playwright/test';

const html = (page: Page) => page.locator('html');

test('defaults to day with empty storage', async ({ page }) => {
  await page.goto('/');
  await expect(html(page)).toHaveAttribute('data-sky', 'day');
  await expect(page.getByRole('button', { name: 'Day' })).toHaveAttribute('aria-pressed', 'true');
});

test('toggle switches theme and changes the visible sky', async ({ page }) => {
  await page.goto('/');
  const bg = () => page.locator('.sky').evaluate((el) => getComputedStyle(el).backgroundImage);
  const day = await bg();

  await page.getByRole('button', { name: 'Dusk' }).click();
  await expect(html(page)).toHaveAttribute('data-sky', 'dusk');
  await expect(page.getByRole('button', { name: 'Dusk' })).toHaveAttribute('aria-pressed', 'true');
  await expect(page.getByRole('button', { name: 'Day' })).toHaveAttribute('aria-pressed', 'false');
  const dusk = await bg();

  await page.getByRole('button', { name: 'Night' }).click();
  await expect(html(page)).toHaveAttribute('data-sky', 'night');
  const night = await bg();

  expect(new Set([day, dusk, night]).size).toBe(3);
});

test('choice survives reload', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Dusk' }).click();
  await page.reload();
  await expect(html(page)).toHaveAttribute('data-sky', 'dusk');
  await expect(page.getByRole('button', { name: 'Dusk' })).toHaveAttribute('aria-pressed', 'true');
});

test('hero stays night under every theme', async ({ page }) => {
  await page.goto('/');
  const heroBg = () => page.locator('#hero').evaluate((el) => getComputedStyle(el).backgroundColor);
  const night = await heroBg();
  for (const name of ['Dusk', 'Night', 'Day']) {
    await page.getByRole('button', { name }).click();
    expect(await heroBg()).toBe(night);
  }
  await expect(page.getByRole('heading', { name: 'Axel Chrisdy Sanjaya', level: 1 })).toBeVisible();
});

test('toggle is keyboard operable', async ({ page }) => {
  await page.goto('/');
  const night = page.getByRole('button', { name: 'Night' });
  await night.focus();
  await night.press('Enter');
  await expect(html(page)).toHaveAttribute('data-sky', 'night');
  await expect(night).toHaveAttribute('aria-pressed', 'true');
});

test('falls back to day when localStorage throws', async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(window, 'localStorage', {
      get() {
        throw new Error('blocked');
      },
    });
  });
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('/');
  await expect(html(page)).toHaveAttribute('data-sky', 'day');
  await page.getByRole('button', { name: 'Dusk' }).click();
  await expect(html(page)).toHaveAttribute('data-sky', 'dusk');
  expect(errors).toEqual([]);
});
