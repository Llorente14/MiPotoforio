import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const profile = defineCollection({
  loader: glob({ pattern: 'profile.json', base: './src/content' }),
  schema: z.object({
    name: z.string().min(1),
    university: z.string().min(1),
    major: z.string().min(1),
    semester: z.number().int().positive(),
    totalSemesters: z.number().int().positive(),
    gpa: z.number().nonnegative(),
    gpaScale: z.number().positive(),
    tagline: z.string().min(1),
    // Campus coordinates shown as print metadata in the Hero, e.g. 6°10′S 106°47′E.
    coordinates: z.string().min(1),
    socials: z.object({
      github: z.url(),
      linkedin: z.url(),
      email: z.email(),
    }),
    currentLearning: z.array(
      z.object({
        id: z.string().min(1),
        title: z.string().min(1),
        decoration: z.string(),
        status: z.string().min(1),
        visual: z.enum(['temple', 'leaf']),
      }),
    ),
    currentlyWatching: z.object({
      // One-line fun fact shown above the episode counter.
      funFact: z.string().min(1),
      episode: z.number().int().positive(),
      label: z.string().min(1),
      title: z.string().optional(),
      total: z.number().int().positive().optional(),
    }),
  }),
});

const projects = defineCollection({
  loader: glob({ pattern: '*.mdx', base: './src/content/projects' }),
  schema: z.object({
    title: z.string().min(1),
    summary: z.string().min(1),
    stack: z.array(z.string().min(1)).min(1),
    repoUrl: z.url(),
    liveUrl: z.url().optional(),
    cover: z.string().startsWith('/'),
    coverAlt: z.string().min(1),
    screenshots: z.array(z.object({ src: z.string().startsWith('/'), alt: z.string().min(1) })).default([]),
    // One-line callout under the summary, e.g. where the project was demoed.
    highlight: z.string().min(1).optional(),
    // YouTube videos (unlisted is fine). No id yet renders a "coming soon" card.
    videos: z.array(z.object({ title: z.string().min(1), youtubeId: z.string().regex(/^[\w-]{11}$/).optional() })).default([]),
    links: z.array(z.object({ label: z.string().min(1), url: z.url(), note: z.string().min(1).optional() })).default([]),
    featuredOrder: z.number().int().positive(),
    date: z.coerce.date(),
  }),
});

const certificates = defineCollection({
  loader: glob({ pattern: '*.json', base: './src/content/certificates' }),
  schema: z.object({
    title: z.string().min(1),
    issuer: z.string().min(1),
    date: z.coerce.date(),
    image: z.string().startsWith('/'),
    imageAlt: z.string().min(1),
    verifyUrl: z.url().optional(),
    featuredOrder: z.number().int().positive(),
  }),
});

export const collections = { profile, projects, certificates };
