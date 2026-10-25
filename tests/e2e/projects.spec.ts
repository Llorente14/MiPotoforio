import { expect, test } from '@playwright/test';

const order = ['Dapute', 'AlterEgo Esport', 'LnFTI'];

test('landing portfolio shows exactly 3 projects in featured order', async ({ page }) => {
  await page.goto('/');
  const cards = page.getByRole('list', { name: 'Featured projects' }).getByRole('listitem').filter({ has: page.getByRole('heading', { level: 3 }) });
  await expect(cards).toHaveCount(3);
  await expect(cards.getByRole('heading', { level: 3 })).toHaveText(order);
  await expect(page.getByRole('link', { name: 'View all projects' })).toHaveAttribute('href', '/projects/');
});

test('list page shows all 5 projects and opens a detail page', async ({ page }) => {
  await page.goto('/projects/');
  await expect(page.getByRole('heading', { level: 3 })).toHaveCount(5);
  await page.getByRole('link', { name: /Wanderwhale/ }).click();
  await expect(page).toHaveURL(/\/projects\/wanderwhale\/$/);
  await expect(page.getByRole('heading', { level: 1, name: 'Wanderwhale' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'GitHub repository' })).toHaveAttribute(
    'href',
    'https://github.com/Llorente14/Wanderwhale',
  );
  await expect(page.getByText(/live against the Amadeus Self-Service API/)).toBeVisible();
  await page.getByRole('link', { name: 'Back to projects' }).click();
  await expect(page).toHaveURL(/\/projects\/$/);
});

test('project images have alt text', async ({ page }) => {
  for (const url of ['/', '/projects/', '/projects/dapute/', '/projects/wanderwhale/']) {
    await page.goto(url);
    // Read every alt in one pass: islands may swap images while the page settles.
    const alts = await page.locator('main img:not([aria-hidden="true"])').evaluateAll((els) => els.map((el) => el.getAttribute('alt') ?? ''));
    expect(alts.length).toBeGreaterThan(0);
    for (const alt of alts) expect(alt).toMatch(/\S/);
  }
});

test('detail gallery steps through screenshots with at most 5 dots', async ({ page }) => {
  await page.goto('/projects/dapute/');
  const gallery = page.getByRole('region', { name: 'Dapute screenshots' });
  await expect(gallery.getByRole('img')).toHaveCount(1);
  await expect(gallery.getByRole('group', { name: 'Choose screenshot' }).getByRole('button')).toHaveCount(5);
  await expect(gallery.getByText('1 / 8')).toBeVisible();
  await gallery.getByRole('button', { name: 'Next screenshot' }).click();
  await expect(gallery.getByText('2 / 8')).toBeVisible();
  await gallery.getByRole('button', { name: 'Previous screenshot' }).click();
  await gallery.getByRole('button', { name: 'Previous screenshot' }).click();
  await expect(gallery.getByText('8 / 8')).toBeVisible();
  await gallery.getByRole('button', { name: 'Show screenshot 6' }).click();
  await expect(gallery.getByText('6 / 8')).toBeVisible();

  await page.goto('/projects/alterego-esport/');
  const many = page.getByRole('region', { name: 'AlterEgo Esport screenshots' });
  await expect(many.getByText('1 / 14')).toBeVisible();
  await expect(many.getByRole('group', { name: 'Choose screenshot' }).getByRole('button')).toHaveCount(5);
});

test('detail gallery advances on its own', async ({ page }) => {
  await page.clock.install();
  await page.goto('/projects/darshanease/');
  const gallery = page.getByRole('region', { name: 'Darshanease screenshots' });
  await expect(gallery.getByText('1 / 11')).toBeVisible();
  await page.clock.runFor(4500);
  await expect(gallery.getByText('2 / 11')).toBeVisible();
});

test('detail gallery does not autoplay with reduced motion', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.clock.install();
  await page.goto('/projects/darshanease/');
  const gallery = page.getByRole('region', { name: 'Darshanease screenshots' });
  await page.clock.runFor(9000);
  await expect(gallery.getByText('1 / 11')).toBeVisible();
});

test('project title never overlaps the gallery', async ({ page }, info) => {
  // Desktop also checks the narrowest two-column width and a wide screen.
  const widths = info.project.name === 'desktop' ? [1024, 1280, 1920] : [page.viewportSize()!.width];
  for (const width of widths) {
    for (const slug of ['dapute', 'alterego-esport', 'lnfti', 'wanderwhale', 'darshanease']) {
      await page.setViewportSize({ width, height: page.viewportSize()!.height });
      await page.goto(`/projects/${slug}/`);
      const heading = page.getByRole('heading', { level: 1 });
      expect(await heading.evaluate((el) => el.scrollWidth <= el.clientWidth), `${slug} title spills out of its column`).toBe(true);
      const title = await heading.boundingBox();
      const gallery = await page.getByRole('region', { name: /screenshots$/ }).boundingBox();
      expect(title && gallery).toBeTruthy();
      const beside = title!.x + title!.width <= gallery!.x;
      const above = title!.y + title!.height <= gallery!.y;
      expect(beside || above, `${slug} title overlaps the gallery at ${width}px`).toBe(true);
    }
  }
});

test('Dapute shows its I/O Fest highlight and the video folder link', async ({ page }) => {
  await page.goto('/projects/dapute/');
  await expect(page.getByText(/Demoed live at I\/O Fest UNTAR 2026/)).toBeVisible();
  const media = page.getByRole('region', { name: 'Videos & links' });
  await expect(media.getByRole('link', { name: /Documentation, app and demo videos/ })).toHaveAttribute(
    'href',
    'https://drive.google.com/drive/folders/1mOuv46wUWMqGUvJysRoRUmVmKijs8DZ9?usp=sharing',
  );
});

test('a video without a YouTube id shows a coming-soon card', async ({ page }) => {
  await page.goto('/projects/alterego-esport/');
  const media = page.getByRole('region', { name: 'Videos & links' });
  await expect(media.getByText('Video coming soon')).toBeVisible();
  await expect(media.getByText('Site walkthrough demo')).toBeVisible();
  await expect(page.locator('iframe')).toHaveCount(0);
});

test('projects without videos or links have no media section', async ({ page }) => {
  await page.goto('/projects/wanderwhale/');
  await expect(page.getByRole('heading', { name: 'Videos & links' })).toHaveCount(0);
});
