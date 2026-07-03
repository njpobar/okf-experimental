---
type: JSON Table
title: FPL Positions (Element Types)
description: One row per playable position (Goalkeeper, Defender, Midfielder, Forward), defining squad-composition rules used across the game.
resource: https://fantasy.premierleague.com/api/bootstrap-static/#element_types
tags: [fantasy-sports, premier-league, positions, reference-data]
timestamp: 2026-07-03T00:00:00Z
---

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Position identifier; foreign key from `players.element_type` (1=GKP, 2=DEF, 3=MID, 4=FWD). |
| `singular_name` | STRING | Full singular name, e.g. `"Goalkeeper"`. |
| `singular_name_short` | STRING | Three-letter abbreviation, e.g. `"GKP"`. |
| `plural_name` | STRING | Full plural name, e.g. `"Goalkeepers"`. |
| `plural_name_short` | STRING | Abbreviated plural name, e.g. `"GKP"`. |
| `squad_select` | INTEGER | Number of players of this position required in a full 15-man squad. |
| `squad_min_select` | STRING | Minimum selectable of this position in a squad; null unless position-specific constraints apply. |
| `squad_max_select` | STRING | Maximum selectable of this position in a squad; null unless constrained. |
| `squad_min_play` | INTEGER | Minimum number of this position required in the starting XI. |
| `squad_max_play` | INTEGER | Maximum number of this position allowed in the starting XI. |
| `ui_shirt_specific` | BOOLEAN | Whether the FPL UI renders a position-specific shirt graphic (true for goalkeepers). |
| `sub_positions_locked` | ARRAY | List of position IDs this position is locked to when substituting (used for goalkeeper-only substitution rules). |
| `element_count` | INTEGER | Total number of players currently registered at this position (should sum to the total row count of [players](/tables/players.md)). |

# Examples

```json
{
  "id": 1,
  "singular_name": "Goalkeeper",
  "singular_name_short": "GKP",
  "squad_select": 2,
  "squad_min_play": 1,
  "squad_max_play": 1,
  "element_count": 97
}
```

# Joins

- [players](/tables/players.md) on `players.element_type` = `element_types.id`.

# Citations

[1] Fantasy Premier League Official API — bootstrap-static: https://fantasy.premierleague.com/api/bootstrap-static/
