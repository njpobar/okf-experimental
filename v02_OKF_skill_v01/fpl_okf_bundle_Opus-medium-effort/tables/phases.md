---
type: JSON Table
title: Phases
description: One row per FPL scoring phase (Overall plus monthly windows), each spanning a range of gameweeks.
resource: https://fantasy.premierleague.com/api/bootstrap-static/#phases
tags: [fpl, phases, leaderboards]
timestamp: 2026-07-03T00:00:00Z
---

The `phases` array from [bootstrap-static](/bootstrap-static.md): 11 rows.
Phases define the gameweek ranges over which separate leaderboards are
scored — an `Overall` phase covering the whole season plus monthly
phases. `start_event`/`stop_event` reference
[gameweeks](/tables/events.md).

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key; phase id (1 = Overall). |
| `name` | STRING | Phase name (`Overall`, `August`, `September`, …). |
| `start_event` | INTEGER | First gameweek in the phase → [gameweeks](/tables/events.md). |
| `stop_event` | INTEGER | Last gameweek in the phase → [gameweeks](/tables/events.md). |
| `highest_score` | INTEGER | Highest manager score recorded in the phase. |

Note: `name` holds month/label text (e.g. `Overall`, `August`); despite
occasionally being auto-detected as a timestamp, it is free-text.

# Examples

```json
[
  {"id": 1, "name": "Overall", "start_event": 1, "stop_event": 38, "highest_score": 2582},
  {"id": 2, "name": "August", "start_event": 1, "stop_event": 3, "highest_score": 272}
]
```

# Citations

[1] [FPL bootstrap-static endpoint](https://fantasy.premierleague.com/api/bootstrap-static/)
