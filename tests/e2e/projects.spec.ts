import { expect, test } from '@playwright/test';

const order = ['Dapute', 'AlterEgo Esport', 'LnFTI'];

test('landing portfolio shows exactly 3 projects in featured order', async ({ page }) => {
  await page.goto('/');
  const cards = page.locator('#portfolio ul > li').filter({ has: page.getByRole('heading', { level: 3 }) });
  await expect(cards).toHaveCount(3);
  await expect(cards.getByRole('heading', { level: 3 })).toHaveText(order);
  await expect(page.getByRole('link', { name: 'View all projects' })).toHaveAttribute('href', '/projects/');
});

test('list page shows all 4 projects and opens a detail page', async ({ page }) => {
  await page.goto('/projects/');
  await expect(page.getByRole('heading', { level: 3 })).toHaveCount(4);
  await page.getByRole('link', { name: /Wanderwhale/ }).click();
  await expect(page).toHaveURL(/\/projects\/wanderwhale\/$/);
  await expect(page.getByRole('heading', { level: 1, name: 'Wanderwhale' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'GitHub repository' })).toHaveAttribute(
    'href',
    'https://github.com/Llorente14',
  );
  await expect(page.getByText('Placeholder: description coming soon.')).toBeVisible();
  await page.getByRole('link', { name: 'Back to projects' }).click();
  await expect(page).toHaveURL(/\/projects\/$/);
});

test('project images have alt text', async ({ page }) => {
  for (const url of ['/', '/projects/', '/projects/dapute/']) {
    await page.goto(url);
    const imgs = page.locator('main img');
    const n = await imgs.count();
    for (let i = 0; i < n; i++) {
      await expect(imgs.nth(i)).toHaveAttribute('alt', /\S/);
    }
  }
});
