// @ts-check
import { defineConfig } from 'astro/config';

import react from '@astrojs/react';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  // TODO: replace with custom domain when available
  site: 'https://mipotoforio.vercel.app',
  integrations: [react(), mdx(), sitemap()],

  // The whole stylesheet is ~9 KiB gzipped: inline it so first paint waits on no CSS request.
  build: { inlineStylesheets: 'always' },

  vite: {
    plugins: [tailwindcss()]
  }
});