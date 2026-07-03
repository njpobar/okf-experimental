---
type: JSON Table
title: Positions (element_types)
description: One row per player position (GKP/DEF/MID/FWD) with squad-selection rules and per-position player counts.
resource: https://fantasy.premierleague.com/api/bootstrap-static/#element_types
tags: [fpl, positions, rules]
timestamp: 2026-07-03T00:00:00Z
---

The `element_types` array from [bootstrap-static](/bootstrap-static.md):
the 4 outfield/keeper positions. `id` is the primary key referenced by
[players](/tables/elements.md)`.element_type`.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key (1=GKP, 2=DEF, 3=MID, 4=FWD). |
| `singular_name` | STRING | Singular position name (e.g. `Goalkeeper`). |
| `singular_name_short` | STRING | Short singular name (e.g. `GKP`). |
| `plural_name` | STRING | Plural position name (e.g. `Goalkeepers`). |
| `plural_name_short` | STRING | Short plural name (e.g. `GKP`). |
| `squad_select` | INTEGER | Number of this position selected in a 15-man squad. |
| `squad_min_play` | INTEGER | Minimum of this position in the starting XI. |
| `squad_max_play` | INTEGER | Maximum of this position in the starting XI. |
| `squad_min_select` | STRING | Minimum selectable; null (governed by `squad_select`). |
| `squad_max_select` | STRING | Maximum selectable; null (governed by `squad_select`). |
| `element_count` | INTEGER | Number of players currently in this position. |
| `ui_shirt_specific` | BOOLEAN | Whether a position-specific shirt is shown in the UI. |
| `sub_positions_locked` | ARRAY | Sub-position ids locked for this position. |

# Examples

```json
{
  "id": 1, "singular_name": "Goalkeeper", "singular_name_short": "GKP",
  "plural_name": "Goalkeepers", "squad_select": 2,
  "squad_min_play": 1, "squad_max_play": 1, "element_count": 97
}
```

# Joins

Referenced by [players](/tables/elements.md)`.element_type` on `id`.

# Citations

[1] [FPL bootstrap-static endpoint](https://fantasy.premierleague.com/api/bootstrap-static/)
