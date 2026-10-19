import { expect, test } from '@playwright/test';

test('landing page loads with an English document', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('html')).toHaveAttribute('lang', 'en');
});

test('about section shows profile facts', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'About me' })).toBeVisible();
  const about = page.locator('#about');
  await expect(about.getByText('Axel Chrisdy Sanjaya', { exact: true })).toBeVisible();
  await expect(page.getByText('Universitas Tarumanagara')).toBeVisible();
  await expect(page.getByText('Informatics Engineering, semester 5')).toBeVisible();
  await expect(about.getByRole('list', { name: 'Semester 5 of 8' }).getByRole('listitem')).toHaveCount(8);
});

test('hero contact links have correct hrefs and accessible names', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('link', { name: 'Axel on GitHub' })).toHaveAttribute(
    'href',
    'https://github.com/Llorente14',
  );
  await expect(page.getByRole('link', { name: 'Axel on LinkedIn' })).toHaveAttribute(
    'href',
    'https://www.linkedin.com/in/axelchrisdy',
  );
  await expect(page.getByRole('link', { name: 'Write to Axel' })).toHaveAttribute(
    'href',
    'mailto:axel.chrisdy@gmail.com',
  );
});

test('skip link moves focus to main content', async ({ page }) => {
  await page.goto('/');
  const skip = page.getByRole('link', { name: 'Skip to content' });
  await skip.focus();
  await skip.press('Enter');
  await expect(page.locator('main')).toBeFocused();
});
