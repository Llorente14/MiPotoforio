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
    featuredOrder: z.number().int().positive(),
    date: z.coerce.date(),
  }),
});

export const collections = { profile, projects };
