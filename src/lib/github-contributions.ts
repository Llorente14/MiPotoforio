// Build-time only: fetches the GitHub contribution calendar. Never throws.
// With a token it uses the GraphQL API; without one it reads the public calendar page instead.

export interface ContributionDay {
  date: string;
  count: number;
  level: 0 | 1 | 2 | 3 | 4;
}

export type ContributionResult =
  | { status: 'ok'; total: number; weeks: { days: ContributionDay[] }[] }
  | { status: 'unavailable'; reason: string };

export interface FetchContributionsOptions {
  username: string;
  token: string | undefined;
  fetch?: typeof fetch;
  // Skip the network entirely (deterministic test builds).
  offline?: boolean;
}

const QUERY = `query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount contributionLevel }
        }
      }
    }
  }
}`;

const LEVELS: Record<string, ContributionDay['level']> = {
  NONE: 0,
  FIRST_QUARTILE: 1,
  SECOND_QUARTILE: 2,
  THIRD_QUARTILE: 3,
  FOURTH_QUARTILE: 4,
};

const unavailable = (reason: string): ContributionResult => ({ status: 'unavailable', reason });

export async function fetchContributions({
  username,
  token,
  fetch: fetchImpl = fetch,
  offline = false,
}: FetchContributionsOptions): Promise<ContributionResult> {
  if (offline) return unavailable('offline');
  if (!token) return fetchPublicCalendar(username, fetchImpl);

  try {
    const res = await fetchImpl('https://api.github.com/graphql', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: QUERY, variables: { login: username } }),
    });
    if (!res.ok) return unavailable(`GitHub responded with HTTP ${res.status}`);
    return normalise(await res.json());
  } catch (error) {
    return unavailable(error instanceof Error ? error.message : 'request failed');
  }
}

function normalise(payload: any): ContributionResult {
  const calendar = payload?.data?.user?.contributionsCollection?.contributionCalendar;
  if (!calendar || !Array.isArray(calendar.weeks) || typeof calendar.totalContributions !== 'number') {
    return unavailable('unexpected response shape');
  }

  const weeks: { days: ContributionDay[] }[] = [];
  for (const week of calendar.weeks) {
    if (!Array.isArray(week?.contributionDays)) return unavailable('unexpected response shape');
    const days: ContributionDay[] = [];
    for (const d of week.contributionDays) {
      const level = LEVELS[d?.contributionLevel];
      if (typeof d?.date !== 'string' || typeof d?.contributionCount !== 'number' || level === undefined) {
        return unavailable('unexpected response shape');
      }
      days.push({ date: d.date, count: d.contributionCount, level });
    }
    weeks.push({ days });
  }
  return { status: 'ok', total: calendar.totalContributions, weeks };
}

// No token: GitHub's public profile calendar is a plain HTML fragment with one cell per day
// (data-date, data-level) and a tooltip per cell carrying the count.
async function fetchPublicCalendar(username: string, fetchImpl: typeof fetch): Promise<ContributionResult> {
  try {
    const res = await fetchImpl(`https://github.com/users/${encodeURIComponent(username)}/contributions`, {
      headers: { 'User-Agent': 'portfolio-build' },
    });
    if (!res.ok) return unavailable(`GitHub responded with HTTP ${res.status}`);
    return parsePublicCalendar(await res.text());
  } catch (error) {
    return unavailable(error instanceof Error ? error.message : 'request failed');
  }
}

export function parsePublicCalendar(html: string): ContributionResult {
  const counts = new Map<string, number>();
  for (const m of html.matchAll(/<tool-tip\b[^>]*\bfor="([^"]+)"[^>]*>([^<]*)<\/tool-tip>/g)) {
    const n = /^(\d[\d,]*) contributions?\b/.exec(m[2].trim());
    counts.set(m[1], n ? Number(n[1].replace(/,/g, '')) : 0);
  }

  const days: ContributionDay[] = [];
  for (const m of html.matchAll(/<td\b[^>]*\bdata-date="(\d{4}-\d{2}-\d{2})"[^>]*>/g)) {
    const id = /\bid="([^"]+)"/.exec(m[0])?.[1];
    const level = Number(/\bdata-level="(\d)"/.exec(m[0])?.[1]);
    if (!id || !(level >= 0 && level <= 4)) return unavailable('unexpected page shape');
    days.push({ date: m[1], count: counts.get(id) ?? 0, level: level as ContributionDay['level'] });
  }
  if (days.length === 0) return unavailable('unexpected page shape');

  // The page lists cells row by row (all Sundays, then all Mondays…); rebuild Sunday-first weeks by date.
  days.sort((a, b) => a.date.localeCompare(b.date));
  const weeks: { days: ContributionDay[] }[] = [];
  for (const day of days) {
    if (weeks.length === 0 || new Date(`${day.date}T00:00:00Z`).getUTCDay() === 0) weeks.push({ days: [] });
    weeks[weeks.length - 1].days.push(day);
  }
  return { status: 'ok', total: days.reduce((sum, d) => sum + d.count, 0), weeks };
}
