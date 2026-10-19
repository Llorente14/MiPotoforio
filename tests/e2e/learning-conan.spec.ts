import { expect, test } from '@playwright/test';
import profile from '../../src/content/profile.json' with { type: 'json' };

test('current learning renders every profile item', async ({ page }) => {
  await page.goto('/');
  const section = page.locator('#learning');
  await expect(section.getByRole('heading', { level: 2, name: 'Current Learning' })).toBeVisible();
  for (const item of profile.currentLearning) {
    await expect(section.getByRole('heading', { level: 3, name: item.title })).toBeVisible();
    await expect(section.getByText(item.status)).toBeVisible();
  }
  // Decorative Japanese text is hidden from assistive tech.
  await expect(section.getByText('日本語')).toHaveAttribute('aria-hidden', 'true');
  await expect(section.getByRole('img', { name: /3D temple model/ })).toBeVisible();
});

test('learning panels zigzag on desktop and stack on mobile', async ({ page }, info) => {
  await page.goto('/');
  const [first, second] = await Promise.all(
    profile.currentLearning.map(async (item) => {
      const panel = page.locator(`[data-learning="${item.id}"]`);
      const text = await panel.getByRole('heading', { level: 3 }).boundingBox();
      const visual = await panel.getByRole('img').boundingBox();
      return { text: text!, visual: visual! };
    }),
  );
  if (info.project.name === 'desktop') {
    expect(first.text.x).toBeLessThan(first.visual.x);
    expect(second.visual.x).toBeLessThan(second.text.x);
  } else {
    expect(first.visual.y).toBeGreaterThan(first.text.y);
    expect(Math.abs(first.visual.x - first.text.x)).toBeLessThan(10);
  }
});

test('fun fact section shows the Conan fact, the episode from profile content and the disclaimer', async ({ page }) => {
  await page.goto('/');
  const section = page.locator('#conan');
  await expect(section.getByRole('heading', { level: 2, name: 'Fun fact' })).toBeVisible();
  const { funFact, episode, label } = profile.currentlyWatching;
  await expect(section.getByText(funFact)).toBeVisible();
  await expect(section.getByText(`Currently watching: Episode ${episode} (${label})`)).toBeVisible();
  await expect(section.getByText(/Gosho Aoyama \/ TMS; fan-made art/)).toBeVisible();
  await expect(section.getByRole('img', { name: /Akai Shuichi sniping scene/ })).toBeVisible();
});
