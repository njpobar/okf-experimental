---
type: JSON Table
title: Chips
description: One row per playable FPL chip window, defining which gameweeks each chip (wildcard, bench boost, etc.) is available in.
resource: https://fantasy.premierleague.com/api/bootstrap-static/#chips
tags: [fpl, chips, rules]
timestamp: 2026-07-03T00:00:00Z
---

The `chips` array from [bootstrap-static](/bootstrap-static.md): 8 rows.
Chips are one-off boosts a manager can play. Because the season is split
into two halves, most chips appear twice (once per half), which is why
`name` has fewer distinct values than there are rows.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key; chip-availability row id. |
| `name` | STRING | Chip name (e.g. `wildcard`, `bboost`, `freehit`, `3xc`). |
| `number` | INTEGER | Which instance of the chip this is. |
| `chip_type` | STRING | Chip category: `transfer` or `team`. |
| `start_event` | INTEGER | First gameweek the chip can be played → [gameweeks](/tables/events.md). |
| `stop_event` | INTEGER | Last gameweek the chip can be played → [gameweeks](/tables/events.md). |
| `overrides.element_types` | ARRAY | Position-rule overrides while the chip is active (empty when none). |
| `overrides.pick_multiplier` | STRING | Pick-multiplier override (e.g. for triple captain); null when none. |

# Examples

```json
{
  "id": 1, "name": "wildcard", "number": 1, "chip_type": "transfer",
  "start_event": 2, "stop_event": 19
}
```

# Citations

[1] [FPL bootstrap-static endpoint](https://fantasy.premierleague.com/api/bootstrap-static/)
