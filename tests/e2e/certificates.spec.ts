import { expect, test } from '@playwright/test';

test('landing shows the 4 featured certificates and a working CV link', async ({ page, request }) => {
  await page.goto('/');
  const list = page.getByRole('list', { name: 'Featured certificates' });
  await expect(list.getByRole('listitem')).toHaveCount(4);
  const featured = [/MongoDB Node.js Developer Path for SmartBridge/, /DIGDAYA Practitioner Phase/, /Lab Assistant, Statistics and Calculus/, /I\/O Festival 2025 Committee/];
  for (const [i, name] of featured.entries()) await expect(list.getByRole('link').nth(i)).toHaveAccessibleName(name);
  await expect(page.getByRole('link', { name: 'View all certificates' })).toHaveAttribute('href', '/certificates/');
  const cv = page.getByRole('link', { name: 'Download CV' });
  await expect(cv).toHaveAttribute('href', '/Axel_Chrisdy_Sanjaya_CV.pdf');
  await expect(cv).toHaveAttribute('download', 'Axel_Chrisdy_Sanjaya_CV.pdf');
  const res = await request.get('/Axel_Chrisdy_Sanjaya_CV.pdf');
  expect(res.status()).toBe(200);
  expect(res.headers()['content-type']).toContain('application/pdf');
});

test('list page shows all certificates', async ({ page }) => {
  await page.goto('/certificates/');
  await expect(page.getByRole('heading', { level: 1, name: 'Certificates' })).toBeVisible();
  await expect(page.getByRole('button', { name: /Build an AI Agent/ })).toBeVisible();
  await expect(page.getByRole('button', { name: /IBM|MongoDB|Red Hat|LPPI|UNTAR/ })).toHaveCount(11);
  await expect(page.getByRole('button', { name: /I\/O Festival 2025/ })).toBeVisible();
  await expect(page.getByRole('button', { name: /SmartBridge/ })).toBeVisible();
});

test('enlarged view opens by mouse, closes with Escape and returns focus', async ({ page }) => {
  await page.goto('/certificates/');
  const trigger = page.getByRole('button', { name: /Build an AI Agent/ });
  await trigger.click();
  const dialog = page.getByRole('dialog', { name: 'Build an AI Agent' });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByText(/IBM/)).toBeVisible();
  await expect(dialog.getByRole('link', { name: 'Verify' })).toHaveAttribute(
    'href',
    'https://www.credly.com/badges/54cd8b99-4a9f-4ba6-bf3c-3d4d370f1fbd',
  );
  await page.keyboard.press('Escape');
  await expect(dialog).toBeHidden();
  await expect(trigger).toBeFocused();
});

test('enlarged view opens by keyboard and closes with the Close button', async ({ page }) => {
  await page.goto('/certificates/');
  const trigger = page.getByRole('button', { name: /MongoDB Basics for Students/ });
  await trigger.focus();
  await page.keyboard.press('Enter');
  const dialog = page.getByRole('dialog');
  await expect(dialog).toBeVisible();
  await dialog.getByRole('button', { name: 'Close' }).click();
  await expect(dialog).toBeHidden();
  await expect(trigger).toBeFocused();
});

test('an opened certificate fits the screen without scrolling under its frame', async ({ page }) => {
  await page.setViewportSize({ width: 1128, height: 823 });
  await page.goto('/certificates/');
  await page.getByRole('button', { name: /DIGDAYA Essential Phase/ }).first().click();
  const dialog = page.getByRole('dialog');
  await expect(dialog.getByRole('heading', { name: 'DIGDAYA Essential Phase' })).toBeVisible();
  await expect.poll(() => dialog.evaluate((el) => el.scrollHeight - el.clientHeight)).toBeLessThanOrEqual(1);
});
