import { expect, test } from '@playwright/test';

test('landing page loads with an English document', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('html')).toHaveAttribute('lang', 'en');
});
