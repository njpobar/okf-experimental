---
type: JSON Table
title: FPL Phases
description: One row per scoring "phase" (the full season plus each calendar month), used by FPL to compute monthly leaderboards and prizes.
resource: https://fantasy.premierleague.com/api/bootstrap-static/#phases
tags: [fantasy-sports, premier-league, reference-data]
timestamp: 2026-07-03T00:00:00Z
---

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Unique phase identifier. |
| `name` | STRING | Phase display name, e.g. `"Overall"` (the full season) or `"August"` (a calendar-month phase). |
| `start_event` | INTEGER | First gameweek (`events.id`) included in this phase. |
| `stop_event` | INTEGER | Last gameweek (`events.id`) included in this phase. |
| `highest_score` | INTEGER | Highest total points scored by any manager within this phase's gameweek range. |

# Examples

```json
{"id": 1, "name": "Overall", "start_event": 1, "stop_event": 38, "highest_score": 2582}
{"id": 2, "name": "August", "start_event": 1, "stop_event": 3, "highest_score": 272}
```

# Joins

- [events](/tables/events.md) on `start_event`/`stop_event` = `events.id`.

# Citations

[1] Fantasy Premier League Official API — bootstrap-static: https://fantasy.premierleague.com/api/bootstrap-static/
