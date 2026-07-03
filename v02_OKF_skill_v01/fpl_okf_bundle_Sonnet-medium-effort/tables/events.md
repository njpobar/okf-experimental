---
type: JSON Table
title: FPL Events (Gameweeks)
description: One row per gameweek ("event") in the FPL season, including deadlines, scoring summary stats, and per-gameweek chip usage.
resource: https://fantasy.premierleague.com/api/bootstrap-static/#events
tags: [fantasy-sports, premier-league, gameweeks]
timestamp: 2026-07-03T00:00:00Z
---

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Gameweek number (1-38). |
| `name` | STRING | Display name, e.g. `"Gameweek 1"`. |
| `deadline_time` | TIMESTAMP | UTC ISO 8601 transfer deadline for the gameweek. |
| `deadline_time_epoch` | INTEGER | `deadline_time` as a Unix epoch integer. |
| `deadline_time_game_offset` | INTEGER | Seconds offset applied to the deadline for double-deadline gameweeks; usually `0`. |
| `release_time` | STRING | Scheduled release time for bonus-point-adjusted results; typically null. |
| `average_entry_score` | INTEGER | Average total points scored by all FPL managers in this gameweek. |
| `highest_score` | INTEGER | Highest single-manager score in this gameweek. |
| `highest_scoring_entry` | INTEGER | FPL manager (entry) ID with the highest score this gameweek. |
| `finished` | BOOLEAN | Whether the gameweek's matches have all completed. |
| `data_checked` | BOOLEAN | Whether FPL has finished verifying/finalizing bonus points and stats for the gameweek. |
| `is_previous` | BOOLEAN | Whether this is the most recently completed gameweek. |
| `is_current` | BOOLEAN | Whether this is the in-progress gameweek. |
| `is_next` | BOOLEAN | Whether this is the upcoming gameweek. |
| `can_enter` | BOOLEAN | Whether new managers can still enter/join before this gameweek's deadline. |
| `can_manage` | BOOLEAN | Whether existing managers can still make changes before the deadline. |
| `released` | BOOLEAN | Whether gameweek results have been publicly released. |
| `cup_leagues_created` | BOOLEAN | Whether FPL Cup fixtures have been generated as of this gameweek. |
| `h2h_ko_matches_created` | BOOLEAN | Whether head-to-head knockout league matches have been generated. |
| `ranked_count` | INTEGER | Number of managers ranked (i.e. total active entries) as of this gameweek. |
| `transfers_made` | INTEGER | Total transfers made by all managers during this gameweek. |
| `most_selected` | INTEGER | Player ID (`players.id`) most owned by managers this gameweek. |
| `most_transferred_in` | INTEGER | Player ID most transferred in this gameweek. |
| `most_captained` | INTEGER | Player ID most captained this gameweek. |
| `most_vice_captained` | INTEGER | Player ID most vice-captained this gameweek. |
| `top_element` | INTEGER | Player ID with the highest points this gameweek. |
| `top_element_info` | OBJECT | `{id, points}` — redundant convenience copy of the top scorer and their point total. |
| `chip_plays` | ARRAY | List of `{chip_name, num_played}` objects — how many managers played each chip (see [chips](/tables/chips.md)) this gameweek. |
| `overrides` | OBJECT | Gameweek-specific overrides to global `rules`/`scoring`/`element_types`; empty except for special exhibition-style events. |

# Examples

```json
{
  "id": 1,
  "name": "Gameweek 1",
  "deadline_time": "2025-08-15T17:30:00Z",
  "finished": true,
  "average_entry_score": 54,
  "highest_score": 127,
  "chip_plays": [
    {"chip_name": "bboost", "num_played": 342779},
    {"chip_name": "3xc", "num_played": 272642}
  ],
  "most_captained": 381
}
```

# Notes

- This snapshot was pulled at the start of the 2026-07-03 off-season, so every gameweek shows `finished: true` and `is_current`/`is_next` are `false` for all rows.
- `most_selected`, `most_transferred_in`, `most_captained`, `most_vice_captained`, and `top_element` are all foreign keys into [players](/tables/players.md) (`players.id`).

# Joins

- [players](/tables/players.md) via `most_selected`, `most_transferred_in`, `most_captained`, `most_vice_captained`, `top_element` (all → `players.id`).
- [chips](/tables/chips.md) via `chip_plays[].chip_name` → `chips.name`.
- [fixtures](/tables/fixtures.md) on `fixtures.event` = `events.id`.

# Citations

[1] Fantasy Premier League Official API — bootstrap-static: https://fantasy.premierleague.com/api/bootstrap-static/
