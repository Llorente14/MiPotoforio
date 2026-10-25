import { expect, test } from '@playwright/test';

test('Ctrl+K opens the palette with the input focused', async ({ page }, info) => {
  test.skip(info.project.name !== 'desktop', 'keyboard shortcut is a desktop path');
  await page.goto('/');
  await page.keyboard.press('Control+k');
  const dialog = page.getByRole('dialog', { name: 'Command palette' });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole('combobox')).toBeFocused();
});

test('the search bar opens the palette', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Open search' }).click();
  await expect(page.getByRole('dialog', { name: 'Command palette' })).toBeVisible();
});

test('a misspelled project name finds it and Enter opens its detail page', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Open search' }).click();
  const input = page.getByRole('combobox');
  await input.fill('wanderwhal');
  await expect(page.getByRole('option').first()).toHaveText(/Wanderwhale/);
  await input.press('Enter');
  await expect(page).toHaveURL(/\/projects\/wanderwhale\/$/);
  await expect(page.getByRole('heading', { level: 1, name: 'Wanderwhale' })).toBeVisible();
});

test('typing "about" and Enter scrolls to the About section', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Open search' }).click();
  const input = page.getByRole('combobox');
  await input.fill('about');
  await input.press('Enter');
  await expect(page).toHaveURL(/#about$/);
  await expect(page.getByRole('heading', { name: 'About me' })).toBeInViewport();
});

test('arrow keys move the selection', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Open search' }).click();
  const options = page.getByRole('option');
  await expect(options.first()).toHaveAttribute('aria-selected', 'true');
  await page.getByRole('combobox').press('ArrowDown');
  await expect(options.nth(1)).toHaveAttribute('aria-selected', 'true');
  await page.getByRole('combobox').press('ArrowUp');
  await expect(options.first()).toHaveAttribute('aria-selected', 'true');
});

test('shows a no results state', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Open search' }).click();
  await page.getByRole('combobox').fill('zzzzqqqq');
  await expect(page.getByRole('status')).toHaveText(/Nothing matches “zzzzqqqq”/);
  await expect(page.getByRole('option')).toHaveCount(0);
});

test('Escape closes the palette and restores focus', async ({ page }) => {
  await page.goto('/');
  const trigger = page.getByRole('button', { name: 'Open search' });
  await trigger.focus();
  await trigger.click();
  const dialog = page.getByRole('dialog', { name: 'Command palette' });
  await expect(dialog).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(dialog).toBeHidden();
  await expect(trigger).toBeFocused();
});
