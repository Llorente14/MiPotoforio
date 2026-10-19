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

export const collections = { profile };
