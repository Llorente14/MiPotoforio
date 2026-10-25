import { expect, test } from '@playwright/test';

const pages = [
  { url: '/', title: /Axel Chrisdy Sanjaya \| Portfolio/ },
  { url: '/projects/dapute/', title: /Dapute \| Axel Chrisdy Sanjaya/ },
  { url: '/certificates/', title: /Certificates \| Axel Chrisdy Sanjaya/ },
  { url: '/projects/', title: /Projects \| Axel Chrisdy Sanjaya/ },
];

for (const { url, title } of pages) {
  test(`${url} has title, description, canonical, Open Graph and Twitter tags`, async ({ page }) => {
    await page.goto(url);
    await expect(page).toHaveTitle(title);
    const meta = (sel: string) => page.locator(sel).first().getAttribute('content');
    expect(await meta('meta[name="description"]')).toMatch(/\S{10}/);
    expect(await page.locator('link[rel="canonical"]').getAttribute('href')).toMatch(
      new RegExp(`^https://mipotoforio\.vercel\.app${url}$`),
    );
    expect(await meta('meta[property="og:title"]')).toMatch(title);
    expect(await meta('meta[property="og:description"]')).toMatch(/\S{10}/);
    expect(await meta('meta[property="og:image"]')).toBe('https://mipotoforio.vercel.app/og.png');
    expect(await meta('meta[property="og:type"]')).toBe('website');
    expect(await meta('meta[name="twitter:card"]')).toBe('summary_large_image');
    expect(await meta('meta[name="twitter:image"]')).toBe('https://mipotoforio.vercel.app/og.png');
  });
}

test('robots.txt allows crawling and links the sitemap; the share image and sitemap respond', async ({ request }) => {
  const robots = await request.get('/robots.txt');
  expect(robots.status()).toBe(200);
  const text = await robots.text();
  expect(text).toContain('User-agent: *');
  expect(text).toContain('Sitemap: https://mipotoforio.vercel.app/sitemap-index.xml');
  expect((await request.get('/og.png')).status()).toBe(200);
  const sitemap = await request.get('/sitemap-0.xml');
  expect(sitemap.status()).toBe(200);
  const xml = await sitemap.text();
  for (const path of ['/projects/', '/certificates/', '/projects/wanderwhale/']) {
    expect(xml).toContain(`https://mipotoforio.vercel.app${path}`);
  }
});

test('site icons and the web manifest resolve', async ({ page, request }) => {
  await page.goto('/');
  const hrefs = await page
    .locator('link[rel="icon"], link[rel="apple-touch-icon"], link[rel="manifest"]')
    .evaluateAll((links) => links.map((l) => l.getAttribute('href')));
  expect(hrefs).toEqual(expect.arrayContaining(['/favicon.ico', '/apple-touch-icon.png', '/site.webmanifest']));
  for (const href of hrefs) expect((await request.get(href!)).status()).toBe(200);
  const manifest = await (await request.get('/site.webmanifest')).json();
  for (const icon of manifest.icons) expect((await request.get(icon.src)).status()).toBe(200);
});

test('first paint waits on no stylesheet request', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('head link[rel="stylesheet"]')).toHaveCount(0);
});
