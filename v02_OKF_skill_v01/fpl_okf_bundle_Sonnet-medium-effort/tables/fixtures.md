---
type: JSON Table
title: FPL Fixtures
description: One row per Premier League match in the FPL fixture list, including kickoff time, score, FPL difficulty ratings, and per-player match statistics.
resource: https://fantasy.premierleague.com/api/fixtures/
tags: [fantasy-sports, premier-league, fixtures, matches]
timestamp: 2026-07-03T00:00:00Z
---

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Unique fixture identifier within FPL. |
| `code` | INTEGER | Opta Sports match code; stable, globally unique across seasons. |
| `pulse_id` | INTEGER | Premier League "Pulse" match identifier. |
| `event` | INTEGER | Gameweek number this fixture belongs to; foreign key to [events](/tables/events.md) `id`. |
| `kickoff_time` | TIMESTAMP | UTC ISO 8601 scheduled kickoff time. |
| `provisional_start_time` | BOOLEAN | Whether `kickoff_time` is provisional and may still be rescheduled. |
| `started` | BOOLEAN | Whether the match has kicked off. |
| `finished` | BOOLEAN | Whether the match has fully finished (including stoppage time). |
| `finished_provisional` | BOOLEAN | Whether the match result is finished but not yet officially confirmed. |
| `minutes` | INTEGER | Minutes played so far (90 once finished). |
| `team_h` | INTEGER | Home team; foreign key to [teams](/tables/teams.md) `id`. |
| `team_a` | INTEGER | Away team; foreign key to [teams](/tables/teams.md) `id`. |
| `team_h_score` | INTEGER | Home team's final/current goal count; null before kickoff. |
| `team_a_score` | INTEGER | Away team's final/current goal count; null before kickoff. |
| `team_h_difficulty` | INTEGER | FPL fixture difficulty rating (1-5) for the home team, derived from the away team's strength. |
| `team_a_difficulty` | INTEGER | FPL fixture difficulty rating (1-5) for the away team, derived from the home team's strength. |
| `stats` | ARRAY | List of per-statistic objects `{identifier, a: [...], h: [...]}` — e.g. `goals_scored`, `assists`, `yellow_cards`, `bonus`, `bps`, `defensive_contribution` — where each `a`/`h` entry is `{value, element}` keyed by player (`element` → `players.id`), split by away/home side. |

# Examples

```json
{
  "id": 1,
  "code": 2561895,
  "event": 1,
  "kickoff_time": "2025-08-15T19:00:00Z",
  "finished": true,
  "team_h": 12,
  "team_a": 4,
  "team_h_score": 4,
  "team_a_score": 2,
  "team_h_difficulty": 3,
  "team_a_difficulty": 4
}
```

# Notes

- `stats[].identifier` values correspond to the `name` field in [element_stats](/tables/element_stats.md) — the definitive list of trackable per-match statistics.
- Before a match starts, `team_h_score`/`team_a_score`/`minutes` are `0`/null and `stats` entries have empty `a`/`h` arrays.
- This dataset was fetched from the separate `/api/fixtures/` endpoint (not `bootstrap-static`), which is why it isn't nested inside the main bootstrap payload.

# Joins

- [events](/tables/events.md) on `event` = `events.id`.
- [teams](/tables/teams.md) on `team_h`/`team_a` = `teams.id`.
- [players](/tables/players.md) via `stats[].a[].element` / `stats[].h[].element` = `players.id`.
- [element_stats](/tables/element_stats.md) via `stats[].identifier` = `element_stats.name`.

# Citations

[1] Fantasy Premier League Official API — fixtures: https://fantasy.premierleague.com/api/fixtures/
