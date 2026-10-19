import { expect, test, type Page } from '@playwright/test';

const html = (page: Page) => page.locator('html');

test('defaults to light with empty storage', async ({ page }) => {
  await page.goto('/');
  await expect(html(page)).toHaveAttribute('data-sky', 'day');
  await expect(page.getByRole('button', { name: 'Light' })).toHaveAttribute('aria-pressed', 'true');
  await expect(page.getByRole('button', { name: 'Night' })).toHaveAttribute('aria-pressed', 'false');
});

test('the switch has exactly two themes: Light and Night', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('group', { name: 'Sky theme' }).getByRole('button')).toHaveCount(2);
});

test('toggle switches theme and changes the visible sky', async ({ page }) => {
  await page.goto('/');
  const bg = () => page.locator('.sky').evaluate((el) => getComputedStyle(el).backgroundImage);
  const light = await bg();

  await page.getByRole('button', { name: 'Night' }).click();
  await expect(html(page)).toHaveAttribute('data-sky', 'night');
  await expect(page.getByRole('button', { name: 'Night' })).toHaveAttribute('aria-pressed', 'true');
  await expect(page.getByRole('button', { name: 'Light' })).toHaveAttribute('aria-pressed', 'false');
  const night = await bg();

  await page.getByRole('button', { name: 'Light' }).click();
  await expect(html(page)).toHaveAttribute('data-sky', 'day');
  expect(light).not.toBe(night);
});

test('choice survives reload', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Night' }).click();
  await page.reload();
  await expect(html(page)).toHaveAttribute('data-sky', 'night');
  await expect(page.getByRole('button', { name: 'Night' })).toHaveAttribute('aria-pressed', 'true');
});

test('a stored theme from an older version falls back to light', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('sky-theme', 'dusk'));
  await page.goto('/');
  await expect(html(page)).toHaveAttribute('data-sky', 'day');
});

test('hero stays night under every theme', async ({ page }) => {
  await page.goto('/');
  const heroBg = () => page.locator('#hero [data-hero-sky]').evaluate((el) => getComputedStyle(el).backgroundColor);
  const night = await heroBg();
  for (const name of ['Night', 'Light']) {
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

test('falls back to light when localStorage throws', async ({ page }) => {
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
  await page.getByRole('button', { name: 'Night' }).click();
  await expect(html(page)).toHaveAttribute('data-sky', 'night');
  expect(errors).toEqual([]);
});
