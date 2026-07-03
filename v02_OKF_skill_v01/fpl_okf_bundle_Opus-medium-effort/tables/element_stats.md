---
type: JSON Table
title: Player stat definitions (element_stats)
description: A lookup of the per-player statistic fields the game tracks, mapping machine names to human-readable labels.
resource: https://fantasy.premierleague.com/api/bootstrap-static/#element_stats
tags: [fpl, stats, reference]
timestamp: 2026-07-03T00:00:00Z
---

The `element_stats` array from [bootstrap-static](/bootstrap-static.md):
26 rows enumerating the statistics the game tracks per player. The `name`
column corresponds to stat field names on
[players](/tables/elements.md) (e.g. `goals_scored`, `minutes`), so this
acts as a data dictionary / display-label lookup for those fields.

# Schema

| Column | Type | Description |
|---|---|---|
| `name` | STRING | Machine name of the stat; matches a field on [players](/tables/elements.md). |
| `label` | STRING | Human-readable display label for the stat. |

# Examples

```json
[
  {"label": "Minutes played", "name": "minutes"},
  {"label": "Goals scored", "name": "goals_scored"},
  {"label": "Assists", "name": "assists"}
]
```

# Citations

[1] [FPL bootstrap-static endpoint](https://fantasy.premierleague.com/api/bootstrap-static/)
