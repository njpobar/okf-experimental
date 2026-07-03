---
type: JSON Table
title: Players (elements)
description: One row per player available in Fantasy Premier League, with pricing, ownership, season totals and per-90 performance stats.
resource: https://fantasy.premierleague.com/api/bootstrap-static/#elements
tags: [fpl, players, stats, ownership]
timestamp: 2026-07-03T00:00:00Z
---

The `elements` array from [bootstrap-static](/bootstrap-static.md): every
selectable player. 841 rows, 105 fields. `id` is the primary key; `team`
joins to [teams](/tables/teams.md) and `element_type` to
[positions](/tables/element_types.md).

Note: many numeric-looking stat fields (`form`, `points_per_game`, `ict_index`,
`expected_goals`, `selected_by_percent`, …) are delivered by the API as
**strings**, not numbers — cast before doing arithmetic. Monetary values
(`now_cost`, `cost_change_*`) are in tenths of a million pounds (147 = £14.7m).

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key; player id within this season's payload. |
| `code` | INTEGER | Stable cross-season player code (matches `photo`/`opta_code`). |
| `web_name` | STRING | Short display name (e.g. `Haaland`). |
| `first_name` | STRING | Given name. |
| `second_name` | STRING | Family name. |
| `known_name` | STRING | Alternative/preferred name; usually empty. |
| `team` | INTEGER | FK to [teams](/tables/teams.md)`.id`. |
| `team_code` | INTEGER | Stable cross-season team code. |
| `element_type` | INTEGER | FK to [positions](/tables/element_types.md)`.id` (1=GKP…4=FWD). |
| `now_cost` | INTEGER | Current price, in tenths of £m (147 = £14.7m). |
| `cost_change_start` | INTEGER | Net price change since season start (tenths of £m). |
| `cost_change_start_fall` | INTEGER | Negation of `cost_change_start`. |
| `cost_change_event` | INTEGER | Price change in the current gameweek (tenths of £m). |
| `cost_change_event_fall` | INTEGER | Negation of `cost_change_event`. |
| `price_change_percent` | STRING | Price change as a percentage string. |
| `total_points` | INTEGER | Total FPL points scored this season. |
| `event_points` | INTEGER | Points scored in the current gameweek. |
| `points_per_game` | STRING | Average points per appearance (string). |
| `form` | STRING | Recent form — avg points over last `stats_form_days` (string). |
| `value_form` | STRING | Form per unit cost (string). |
| `value_season` | STRING | Season points per unit cost (string). |
| `ep_this` | STRING | Expected points this gameweek (string). |
| `ep_next` | STRING | Expected points next gameweek (string). |
| `selected_by_percent` | STRING | Ownership across all managers, percent (string). |
| `transfers_in` | INTEGER | Cumulative transfers in this season. |
| `transfers_out` | INTEGER | Cumulative transfers out this season. |
| `transfers_in_event` | INTEGER | Transfers in during the current gameweek. |
| `transfers_out_event` | INTEGER | Transfers out during the current gameweek. |
| `dreamteam_count` | INTEGER | Times included in the gameweek Dream Team. |
| `in_dreamteam` | BOOLEAN | In the current Dream Team. |
| `status` | STRING | Availability code: `a` available, `i` injured, `d` doubtful, `s` suspended, `u` unavailable. |
| `news` | STRING | Latest availability news; empty when none. |
| `news_added` | TIMESTAMP | When `news` was last updated (~25% null). |
| `chance_of_playing_this_round` | FLOAT | Percent chance of featuring this GW; null when unknown. |
| `chance_of_playing_next_round` | FLOAT | Percent chance of featuring next GW; null when unknown. |
| `minutes` | INTEGER | Minutes played this season. |
| `starts` | INTEGER | Matches started. |
| `goals_scored` | INTEGER | Goals scored. |
| `assists` | INTEGER | Assists. |
| `clean_sheets` | INTEGER | Clean sheets. |
| `goals_conceded` | INTEGER | Goals conceded while on pitch. |
| `own_goals` | INTEGER | Own goals. |
| `penalties_saved` | INTEGER | Penalties saved. |
| `penalties_missed` | INTEGER | Penalties missed. |
| `yellow_cards` | INTEGER | Yellow cards. |
| `red_cards` | INTEGER | Red cards. |
| `saves` | INTEGER | Saves made. |
| `bonus` | INTEGER | Bonus points awarded. |
| `bps` | INTEGER | Bonus Points System raw score. |
| `influence` | STRING | Influence index (string). |
| `creativity` | STRING | Creativity index (string). |
| `threat` | STRING | Threat index (string). |
| `ict_index` | STRING | Combined ICT index (string). |
| `clearances_blocks_interceptions` | INTEGER | CBI total (defensive actions). |
| `recoveries` | INTEGER | Ball recoveries. |
| `tackles` | INTEGER | Tackles. |
| `defensive_contribution` | INTEGER | Defensive contribution stat total. |
| `expected_goals` | STRING | Expected goals (xG) (string). |
| `expected_assists` | STRING | Expected assists (xA) (string). |
| `expected_goal_involvements` | STRING | xG + xA (string). |
| `expected_goals_conceded` | STRING | Expected goals conceded (xGC) (string). |
| `expected_goals_per_90` | FLOAT | xG per 90 minutes. |
| `expected_assists_per_90` | FLOAT | xA per 90 minutes. |
| `expected_goal_involvements_per_90` | FLOAT | xGI per 90 minutes. |
| `expected_goals_conceded_per_90` | FLOAT | xGC per 90 minutes. |
| `goals_conceded_per_90` | FLOAT | Goals conceded per 90 minutes. |
| `saves_per_90` | FLOAT | Saves per 90 minutes. |
| `starts_per_90` | FLOAT | Starts per 90 minutes. |
| `clean_sheets_per_90` | FLOAT | Clean sheets per 90 minutes. |
| `defensive_contribution_per_90` | FLOAT | Defensive contribution per 90 minutes. |
| `influence_rank` | INTEGER | Rank by influence across all players. |
| `influence_rank_type` | INTEGER | Rank by influence within the player's position. |
| `creativity_rank` | INTEGER | Rank by creativity across all players. |
| `creativity_rank_type` | INTEGER | Rank by creativity within position. |
| `threat_rank` | INTEGER | Rank by threat across all players. |
| `threat_rank_type` | INTEGER | Rank by threat within position. |
| `ict_index_rank` | INTEGER | Rank by ICT index across all players. |
| `ict_index_rank_type` | INTEGER | Rank by ICT index within position. |
| `now_cost_rank` | INTEGER | Rank by price across all players. |
| `now_cost_rank_type` | INTEGER | Rank by price within position. |
| `form_rank` | INTEGER | Rank by form across all players. |
| `form_rank_type` | INTEGER | Rank by form within position. |
| `points_per_game_rank` | INTEGER | Rank by points-per-game across all players. |
| `points_per_game_rank_type` | INTEGER | Rank by points-per-game within position. |
| `selected_rank` | INTEGER | Rank by ownership across all players. |
| `selected_rank_type` | INTEGER | Rank by ownership within position. |
| `corners_and_indirect_freekicks_order` | FLOAT | Set-piece order for corners/indirect FKs; null if not a taker. |
| `corners_and_indirect_freekicks_text` | STRING | Notes on corner/indirect FK duty. |
| `direct_freekicks_order` | FLOAT | Direct free-kick taking order; null if not a taker. |
| `direct_freekicks_text` | STRING | Notes on direct FK duty. |
| `penalties_order` | FLOAT | Penalty taking order; null if not a taker. |
| `penalties_text` | STRING | Notes on penalty duty. |
| `photo` | STRING | Player photo filename (`<code>.jpg`). |
| `opta_code` | STRING | Opta player identifier (`p<code>`). |
| `region` | FLOAT | Region/nationality code; mostly populated. |
| `team_join_date` | TIMESTAMP | Date the player joined their club (date only). |
| `birth_date` | TIMESTAMP | Player date of birth (date only). |
| `squad_number` | STRING | Shirt number; null across the dataset at capture. |
| `special` | BOOLEAN | Special-status flag (always false at capture). |
| `removed` | BOOLEAN | Whether the player has been removed from the game. |
| `can_transact` | BOOLEAN | Whether the player can currently be transacted. |
| `can_select` | BOOLEAN | Whether the player can currently be selected. |
| `has_temporary_code` | BOOLEAN | Whether `code` is a temporary placeholder. |
| `scout_risks` | ARRAY | Scout risk annotations (empty at capture). |
| `scout_news_link` | STRING | Link to scout news; empty at capture. |

# Examples

Top scorer in the captured snapshot:

```json
{
  "id": 430,
  "web_name": "Haaland",
  "first_name": "Erling",
  "second_name": "Haaland",
  "team": 13,
  "element_type": 4,
  "now_cost": 147,
  "total_points": 239,
  "minutes": 2953,
  "goals_scored": 27,
  "assists": 8,
  "selected_by_percent": "62.5",
  "expected_goals": "25.50",
  "status": "a"
}
```

# Joins

- `team` → [teams](/tables/teams.md)`.id`
- `element_type` → [positions](/tables/element_types.md)`.id`
- Stat field names align with the `name` column of
  [element_stats](/tables/element_stats.md).

# Citations

[1] [FPL bootstrap-static endpoint](https://fantasy.premierleague.com/api/bootstrap-static/)
