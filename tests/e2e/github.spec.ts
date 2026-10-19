import { expect, test } from '@playwright/test';

// The e2e build runs without GITHUB_TOKEN, so the Section shows its empty state.
test('github section shows a friendly empty state and the profile link', async ({ page }) => {
  await page.goto('/');
  const section = page.locator('#github');
  await expect(section.getByRole('heading', { name: 'GitHub Activity' })).toBeVisible();
  await expect(section.getByText('Contribution activity is not available right now')).toBeVisible();
  await expect(section.getByRole('link', { name: /on GitHub/ })).toHaveAttribute(
    'href',
    'https://github.com/Llorente14',
  );
  await expect(section.getByRole('list', { name: /heatmap/i })).toHaveCount(0);
});
