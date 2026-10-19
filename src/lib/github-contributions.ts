// Build-time only: fetches the GitHub contribution calendar. Never throws.

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
}: FetchContributionsOptions): Promise<ContributionResult> {
  if (!token) return unavailable('missing token');

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
