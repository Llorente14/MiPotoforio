import { expect, test } from '@playwright/test';

test('landing page loads with an English document', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('html')).toHaveAttribute('lang', 'en');
});

test('about section shows profile facts', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'About me' })).toBeVisible();
  await expect(page.getByText('Axel Chrisdy Sanjaya', { exact: true })).toBeVisible();
  await expect(page.getByText('Universitas Tarumanagara')).toBeVisible();
  await expect(page.getByText('Informatics Engineering, semester 5')).toBeVisible();
});

test('social links have correct hrefs and accessible names', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('link', { name: 'GitHub profile' })).toHaveAttribute(
    'href',
    'https://github.com/Llorente14',
  );
  await expect(page.getByRole('link', { name: 'LinkedIn profile' })).toHaveAttribute(
    'href',
    'https://www.linkedin.com/in/axelchrisdy',
  );
  await expect(page.getByRole('link', { name: 'Email Axel' })).toHaveAttribute(
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
