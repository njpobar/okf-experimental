---
type: JSON Table
title: Gameweeks (events)
description: One row per gameweek in the FPL season, with deadlines, aggregate scoring and per-gameweek popularity stats.
resource: https://fantasy.premierleague.com/api/bootstrap-static/#events
tags: [fpl, gameweeks, schedule]
timestamp: 2026-07-03T00:00:00Z
---

The `events` array from [bootstrap-static](/bootstrap-static.md): the 38
gameweeks. `id` is the primary key (1–38). Several fields point back to
[players](/tables/elements.md) (`top_element`, `most_captained`,
`most_selected`, `most_transferred_in`).

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key; gameweek number (1–38). |
| `name` | STRING | Display name (e.g. `Gameweek 1`). |
| `deadline_time` | TIMESTAMP | Squad-change deadline (ISO 8601 UTC). |
| `deadline_time_epoch` | INTEGER | Deadline as a Unix timestamp. |
| `deadline_time_game_offset` | INTEGER | Local game offset (seconds) applied to the deadline. |
| `release_time` | STRING | Gameweek release time; null in this snapshot. |
| `average_entry_score` | INTEGER | Average points scored by managers this gameweek. |
| `highest_score` | INTEGER | Highest points scored by any manager this gameweek. |
| `highest_scoring_entry` | INTEGER | Manager (entry) id that scored highest. |
| `finished` | BOOLEAN | Whether the gameweek is complete. |
| `data_checked` | BOOLEAN | Whether final scoring has been verified. |
| `is_previous` | BOOLEAN | Whether this is the immediately previous gameweek. |
| `is_current` | BOOLEAN | Whether this is the current gameweek. |
| `is_next` | BOOLEAN | Whether this is the next gameweek. |
| `released` | BOOLEAN | Whether the gameweek has been released. |
| `can_enter` | BOOLEAN | Whether new entries can be made. |
| `can_manage` | BOOLEAN | Whether teams can be managed. |
| `ranked_count` | INTEGER | Number of managers ranked this gameweek. |
| `cup_leagues_created` | BOOLEAN | Whether cup leagues were created this gameweek. |
| `h2h_ko_matches_created` | BOOLEAN | Whether H2H knockout matches were created. |
| `transfers_made` | INTEGER | Total transfers made across all managers this gameweek. |
| `most_selected` | INTEGER | Most-selected player id → [players](/tables/elements.md). |
| `most_transferred_in` | INTEGER | Most-transferred-in player id → [players](/tables/elements.md). |
| `most_captained` | INTEGER | Most-captained player id → [players](/tables/elements.md). |
| `most_vice_captained` | INTEGER | Most vice-captained player id → [players](/tables/elements.md). |
| `top_element` | INTEGER | Highest-scoring player id this gameweek → [players](/tables/elements.md). |
| `top_element_info.id` | INTEGER | Highest-scoring player id (nested). |
| `top_element_info.points` | INTEGER | Points scored by the top player this gameweek. |
| `chip_plays` | ARRAY | List of `{chip_name, num_played}` counts per chip this gameweek. |
| `overrides.element_types` | ARRAY | Position-rule overrides for the gameweek (empty when none). |
| `overrides.pick_multiplier` | STRING | Pick-multiplier override; null when none. |

# Examples

```json
{
  "id": 1, "name": "Gameweek 1",
  "deadline_time": "2025-08-15T17:30:00Z",
  "finished": true, "average_entry_score": 54, "highest_score": 127,
  "most_captained": 381, "top_element_info": {"id": 531, "points": 17}
}
```

# Citations

[1] [FPL bootstrap-static endpoint](https://fantasy.premierleague.com/api/bootstrap-static/)
