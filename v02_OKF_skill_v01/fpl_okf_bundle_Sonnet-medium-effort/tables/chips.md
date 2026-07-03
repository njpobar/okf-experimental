---
type: JSON Table
title: FPL Chips
description: One row per playable "chip" (special one-off strategy boost, e.g. Wildcard, Triple Captain), with the gameweek window each is available.
resource: https://fantasy.premierleague.com/api/bootstrap-static/#chips
tags: [fantasy-sports, premier-league, reference-data]
timestamp: 2026-07-03T00:00:00Z
---

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Unique chip-availability-window identifier (not one row per chip type — chips like Wildcard appear twice, once per half-season window). |
| `name` | STRING | Chip identifier, e.g. `"wildcard"`, `"freehit"`, `"bboost"` (Bench Boost), `"3xc"` (Triple Captain). Matches `events.chip_plays[].chip_name`. |
| `number` | INTEGER | Instance number of this chip within the season (always `1` in this snapshot — one play per chip per half). |
| `start_event` | INTEGER | First gameweek this chip instance can be played. |
| `stop_event` | INTEGER | Last gameweek this chip instance can be played. |
| `chip_type` | STRING | Category of chip; observed value `"transfer"` for all rows in this snapshot. |
| `overrides` | OBJECT | Rule/scoring overrides applied while this chip is active; empty for all chips in this snapshot. |

# Examples

```json
{"id": 1, "name": "wildcard", "start_event": 2, "stop_event": 19, "chip_type": "transfer"}
{"id": 3, "name": "freehit", "start_event": 2, "stop_event": 19, "chip_type": "transfer"}
```

# Notes

- Each chip name (wildcard, free hit, bench boost, triple captain) typically appears as two rows — one for the first half of the season, one for the second — reflecting FPL's two-uses-per-season chip rule.

# Joins

- [events](/tables/events.md) via `chip_plays[].chip_name` = `chips.name`, and `start_event`/`stop_event` = `events.id`.

# Citations

[1] Fantasy Premier League Official API — bootstrap-static: https://fantasy.premierleague.com/api/bootstrap-static/
