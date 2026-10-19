import { describe, expect, test } from 'vitest';
import { fetchContributions } from '../../src/lib/github-contributions';

const calendar = {
  data: {
    user: {
      contributionsCollection: {
        contributionCalendar: {
          totalContributions: 9,
          weeks: [
            {
              contributionDays: [
                { date: '2026-01-04', contributionCount: 0, contributionLevel: 'NONE' },
                { date: '2026-01-05', contributionCount: 1, contributionLevel: 'FIRST_QUARTILE' },
                { date: '2026-01-06', contributionCount: 2, contributionLevel: 'SECOND_QUARTILE' },
              ],
            },
            {
              contributionDays: [
                { date: '2026-01-11', contributionCount: 3, contributionLevel: 'THIRD_QUARTILE' },
                { date: '2026-01-12', contributionCount: 3, contributionLevel: 'FOURTH_QUARTILE' },
              ],
            },
          ],
        },
      },
    },
  },
};

const respond = (body: unknown, status = 200) =>
  (async () => new Response(typeof body === 'string' ? body : JSON.stringify(body), { status })) as typeof fetch;

describe('fetchContributions', () => {
  test('normalises weeks and days', async () => {
    const result = await fetchContributions({ username: 'Llorente14', token: 't', fetch: respond(calendar) });
    expect(result).toEqual({
      status: 'ok',
      total: 9,
      weeks: [
        {
          days: [
            { date: '2026-01-04', count: 0, level: 0 },
            { date: '2026-01-05', count: 1, level: 1 },
            { date: '2026-01-06', count: 2, level: 2 },
          ],
        },
        {
          days: [
            { date: '2026-01-11', count: 3, level: 3 },
            { date: '2026-01-12', count: 3, level: 4 },
          ],
        },
      ],
    });
  });

  test('maps every contribution level to 0-4', async () => {
    const result = await fetchContributions({ username: 'u', token: 't', fetch: respond(calendar) });
    expect(result.status === 'ok' && result.weeks.flatMap((w) => w.days.map((d) => d.level))).toEqual([0, 1, 2, 3, 4]);
  });

  test('reports the yearly total from GitHub', async () => {
    const result = await fetchContributions({ username: 'u', token: 't', fetch: respond(calendar) });
    expect(result.status === 'ok' && result.total).toBe(9);
  });

  test('sends username and token to the GraphQL endpoint', async () => {
    let seen: { url: unknown; init: RequestInit | undefined } | undefined;
    const spy = (async (url: unknown, init?: RequestInit) => {
      seen = { url, init };
      return new Response(JSON.stringify(calendar));
    }) as typeof fetch;
    await fetchContributions({ username: 'Llorente14', token: 'secret', fetch: spy });
    expect(seen?.url).toBe('https://api.github.com/graphql');
    expect((seen?.init?.headers as Record<string, string>).Authorization).toBe('Bearer secret');
    expect(JSON.parse(seen?.init?.body as string).variables).toEqual({ login: 'Llorente14' });
  });

  test('offline never calls fetch', async () => {
    let called = false;
    const spy = (async () => {
      called = true;
      return new Response('{}');
    }) as typeof fetch;
    const result = await fetchContributions({ username: 'u', token: 't', fetch: spy, offline: true });
    expect(result).toEqual({ status: 'unavailable', reason: 'offline' });
    expect(called).toBe(false);
  });

  // GitHub's public calendar fragment, trimmed: cells listed row by row, tooltips carry the counts.
  const page = `
    <td data-date="2026-01-04" id="day-0-0" data-level="0" class="ContributionCalendar-day"></td>
    <td data-date="2026-01-11" id="day-0-1" data-level="3" class="ContributionCalendar-day"></td>
    <td data-date="2026-01-05" id="day-1-0" data-level="1" class="ContributionCalendar-day"></td>
    <tool-tip for="day-0-0" class="sr-only">No contributions on January 4th.</tool-tip>
    <tool-tip for="day-0-1" class="sr-only">12 contributions on January 11th.</tool-tip>
    <tool-tip for="day-1-0" class="sr-only">1 contribution on January 5th.</tool-tip>`;

  test('without a token reads the public calendar page into Sunday-first weeks', async () => {
    let url = '';
    const spy = (async (input: RequestInfo | URL) => {
      url = String(input);
      return new Response(page);
    }) as typeof fetch;
    const result = await fetchContributions({ username: 'Llorente14', token: undefined, fetch: spy });
    expect(url).toBe('https://github.com/users/Llorente14/contributions');
    expect(result).toEqual({
      status: 'ok',
      total: 13,
      weeks: [
        {
          days: [
            { date: '2026-01-04', count: 0, level: 0 },
            { date: '2026-01-05', count: 1, level: 1 },
          ],
        },
        { days: [{ date: '2026-01-11', count: 12, level: 3 }] },
      ],
    });
  });

  test('is unavailable when the public page has no calendar', async () => {
    const result = await fetchContributions({ username: 'u', token: undefined, fetch: respond('<html></html>') });
    expect(result).toEqual({ status: 'unavailable', reason: 'unexpected page shape' });
  });

  test('is unavailable on a non-200 response', async () => {
    const result = await fetchContributions({ username: 'u', token: 't', fetch: respond({}, 401) });
    expect(result).toEqual({ status: 'unavailable', reason: 'GitHub responded with HTTP 401' });
  });

  test('is unavailable on malformed JSON', async () => {
    const result = await fetchContributions({ username: 'u', token: 't', fetch: respond('not json{') });
    expect(result.status).toBe('unavailable');
  });

  test('is unavailable when the payload has the wrong shape', async () => {
    const result = await fetchContributions({ username: 'u', token: 't', fetch: respond({ data: { user: null } }) });
    expect(result).toEqual({ status: 'unavailable', reason: 'unexpected response shape' });
  });

  test('is unavailable when fetch itself rejects', async () => {
    const boom = (async () => {
      throw new Error('network down');
    }) as typeof fetch;
    const result = await fetchContributions({ username: 'u', token: 't', fetch: boom });
    expect(result).toEqual({ status: 'unavailable', reason: 'network down' });
  });
});
