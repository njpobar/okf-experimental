---
type: JSON Table
title: FPL Element Stats (Statistic Definitions)
description: Reference list of every per-player statistic tracked by FPL, mapping the machine-readable field name to its display label. Used to interpret fixtures.stats[].identifier.
resource: https://fantasy.premierleague.com/api/bootstrap-static/#element_stats
tags: [fantasy-sports, premier-league, reference-data]
timestamp: 2026-07-03T00:00:00Z
---

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `name` | STRING | Machine-readable field/identifier name, e.g. `"goals_scored"`. Matches both a column on [players](/tables/players.md) and the `identifier` used in [fixtures](/tables/fixtures.md) `stats[]`. |
| `label` | STRING | Human-readable display label, e.g. `"Goals scored"`. |

# Examples

```json
{"label": "Minutes played", "name": "minutes"}
{"label": "Goals scored", "name": "goals_scored"}
{"label": "Assists", "name": "assists"}
```

# Notes

- This is purely a lookup/reference table (26 rows) — it has no numeric data of its own, only definitions.

# Joins

- [players](/tables/players.md) — most `name` values are also column names on the players table.
- [fixtures](/tables/fixtures.md) — `name` matches `stats[].identifier`.

# Citations

[1] Fantasy Premier League Official API — bootstrap-static: https://fantasy.premierleague.com/api/bootstrap-static/
