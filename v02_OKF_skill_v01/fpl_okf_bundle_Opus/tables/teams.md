---
type: JSON Table
title: Teams
description: One row per Premier League club in the current FPL season, with FPL strength ratings and (season-progress) league record.
resource: https://fantasy.premierleague.com/api/bootstrap-static/#teams
tags: [fpl, teams, clubs]
timestamp: 2026-07-03T00:00:00Z
---

The `teams` array from [bootstrap-static](/bootstrap-static.md): the 20
clubs. `id` is the primary key referenced by
[players](/tables/elements.md)`.team`. The league-record fields
(`played`, `win`, `draw`, `loss`, `points`, `form`) read as zero/null in
this snapshot — this payload carries FPL strength ratings, not a live
league table.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key; team id within this season's payload. |
| `code` | INTEGER | Stable cross-season club code (matches player `team_code`). |
| `name` | STRING | Full club name (e.g. `Arsenal`). |
| `short_name` | STRING | Three-letter abbreviation (e.g. `ARS`). |
| `strength` | INTEGER | Overall FPL strength tier (roughly 1–5). |
| `strength_overall_home` | INTEGER | Overall strength rating at home. |
| `strength_overall_away` | INTEGER | Overall strength rating away. |
| `strength_attack_home` | INTEGER | Attacking strength at home. |
| `strength_attack_away` | INTEGER | Attacking strength away. |
| `strength_defence_home` | INTEGER | Defensive strength at home. |
| `strength_defence_away` | INTEGER | Defensive strength away. |
| `position` | INTEGER | League position (0/placeholder in this snapshot). |
| `played` | INTEGER | Matches played (0 in this snapshot). |
| `win` | INTEGER | Wins (0 in this snapshot). |
| `draw` | INTEGER | Draws (0 in this snapshot). |
| `loss` | INTEGER | Losses (0 in this snapshot). |
| `points` | INTEGER | League points (0 in this snapshot). |
| `form` | STRING | Recent form; null in this snapshot. |
| `team_division` | STRING | Division; null (single division). |
| `unavailable` | BOOLEAN | Whether the club is flagged unavailable. |
| `link_url` | STRING | Club link URL; empty in this snapshot. |
| `pulse_id` | INTEGER | Premier League "Pulse" API club identifier. |

# Examples

```json
{
  "id": 1, "code": 3, "name": "Arsenal", "short_name": "ARS",
  "strength": 5, "strength_overall_home": 1305, "strength_overall_away": 1370,
  "strength_attack_home": 1340, "strength_defence_home": 1270, "pulse_id": 1
}
```

# Joins

Referenced by [players](/tables/elements.md)`.team` (on `id`) and
`team_code` (on `code`).

# Citations

[1] [FPL bootstrap-static endpoint](https://fantasy.premierleague.com/api/bootstrap-static/)
