---
type: JSON Table
title: FPL Players
description: One row per player ("element") in the Fantasy Premier League, including identity, current market price, cumulative season performance stats, and real-time availability/injury status.
resource: https://fantasy.premierleague.com/api/bootstrap-static/#elements
tags: [fantasy-sports, premier-league, players, statistics]
timestamp: 2026-07-03T00:00:00Z
---

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Unique player identifier within FPL. Referenced as `element` by other endpoints (fixtures stats, picks, etc.). |
| `code` | INTEGER | Opta Sports identifier for the player; stable across seasons, used for the player photo CDN path. |
| `opta_code` | STRING | String-formatted Opta code, e.g. `"p154561"`. |
| `first_name` | STRING | Player's first name. |
| `second_name` | STRING | Player's surname. |
| `web_name` | STRING | Short display name used across the FPL website/app. |
| `known_name` | STRING | Alternative/common name the player goes by; empty for most players. |
| `photo` | STRING | Filename of the player's photo in the FPL CDN, e.g. `"154561.jpg"`. |
| `squad_number` | STRING | Shirt number; frequently empty/null. |
| `element_type` | INTEGER | Position ID; foreign key to [element_types](/tables/element_types.md) (1=Goalkeeper, 2=Defender, 3=Midfielder, 4=Forward). |
| `team` | INTEGER | Foreign key to [teams](/tables/teams.md) `id`. |
| `team_code` | INTEGER | Opta team code; matches `teams.code`. |
| `status` | STRING | Availability status: `a`=available, `d`=doubtful, `i`=injured, `s`=suspended, `u`=unavailable, `n`=not in squad. |
| `news` | STRING | Free-text injury/fitness/news note. |
| `news_added` | TIMESTAMP | UTC timestamp when `news` was last updated. |
| `chance_of_playing_this_round` | INTEGER | Estimated probability (0-100) of playing in the current gameweek; null if not a concern. |
| `chance_of_playing_next_round` | INTEGER | Estimated probability (0-100) of playing in the next gameweek. |
| `now_cost` | INTEGER | Current price in tenths of £M (e.g. 62 = £6.2m). |
| `cost_change_start` | INTEGER | Price change (tenths of £M) since the start of the season. |
| `cost_change_start_fall` | INTEGER | Magnitude of price *falls* since season start (tenths of £M), always ≤ 0. |
| `cost_change_event` | INTEGER | Price change (tenths of £M) since the last gameweek. |
| `cost_change_event_fall` | INTEGER | Magnitude of the price fall since the last gameweek. |
| `price_change_percent` | STRING | Price change since season start, expressed as a percentage string. |
| `total_points` | INTEGER | Total fantasy points accumulated this season. |
| `event_points` | INTEGER | Fantasy points scored in the most recently finished gameweek. |
| `points_per_game` | STRING | Average fantasy points per gameweek appearance (decimal string). |
| `form` | STRING | Average points over the last 30 days (decimal string). |
| `value_form` | STRING | `form` divided by price — short-term value metric. |
| `value_season` | STRING | Total points per £m spent this season — season-long value metric. |
| `ep_this` | STRING | FPL's expected-points prediction for the current gameweek. |
| `ep_next` | STRING | FPL's expected-points prediction for the next gameweek. |
| `selected_by_percent` | STRING | Percentage of all FPL managers who own this player. |
| `transfers_in` | INTEGER | Cumulative transfers in, all-time this season. |
| `transfers_in_event` | INTEGER | Transfers in during the current gameweek. |
| `transfers_out` | INTEGER | Cumulative transfers out, all-time this season. |
| `transfers_out_event` | INTEGER | Transfers out during the current gameweek. |
| `minutes` | INTEGER | Total minutes played this season. |
| `starts` | INTEGER | Matches started (vs. appearing from the bench). |
| `starts_per_90` | FLOAT | Starts normalized per 90 minutes of availability. |
| `goals_scored` | INTEGER | Total goals scored. |
| `assists` | INTEGER | Total assists. |
| `clean_sheets` | INTEGER | Matches where the player's team conceded zero goals while the player was on the pitch (for the required minutes threshold). |
| `clean_sheets_per_90` | FLOAT | Clean sheets normalized per 90 minutes. |
| `goals_conceded` | INTEGER | Goals conceded by the player's team while on the pitch (defenders/goalkeepers). |
| `goals_conceded_per_90` | FLOAT | Goals conceded normalized per 90 minutes. |
| `own_goals` | INTEGER | Total own goals. |
| `penalties_saved` | INTEGER | Penalties saved (goalkeepers). |
| `penalties_missed` | INTEGER | Penalties missed. |
| `saves` | INTEGER | Saves made (goalkeepers). |
| `saves_per_90` | FLOAT | Saves normalized per 90 minutes. |
| `yellow_cards` | INTEGER | Total yellow cards. |
| `red_cards` | INTEGER | Total red cards. |
| `bonus` | INTEGER | Total bonus points awarded (top 3 performers per match by BPS). |
| `bps` | INTEGER | Cumulative Bonus Points System score for the season. |
| `influence` | STRING | ICT sub-metric: overall match impact (decimal string). |
| `influence_rank` | INTEGER | Rank by `influence` among all players (1 = best). |
| `influence_rank_type` | INTEGER | Rank by `influence` within the player's position. |
| `creativity` | STRING | ICT sub-metric: chance creation (decimal string). |
| `creativity_rank` | INTEGER | Rank by `creativity` among all players. |
| `creativity_rank_type` | INTEGER | Rank by `creativity` within position. |
| `threat` | STRING | ICT sub-metric: goal-scoring threat (decimal string). |
| `threat_rank` | INTEGER | Rank by `threat` among all players. |
| `threat_rank_type` | INTEGER | Rank by `threat` within position. |
| `ict_index` | STRING | Combined Influence+Creativity+Threat index (decimal string). |
| `ict_index_rank` | INTEGER | Rank by `ict_index` among all players. |
| `ict_index_rank_type` | INTEGER | Rank by `ict_index` within position. |
| `expected_goals` | STRING | Expected goals (xG) from shot quality this season. |
| `expected_goals_per_90` | FLOAT | xG normalized per 90 minutes. |
| `expected_assists` | STRING | Expected assists (xA) this season. |
| `expected_assists_per_90` | FLOAT | xA normalized per 90 minutes. |
| `expected_goal_involvements` | STRING | Combined xG + xA. |
| `expected_goal_involvements_per_90` | FLOAT | xG+xA normalized per 90 minutes. |
| `expected_goals_conceded` | STRING | Expected goals conceded by the player's team while on the pitch. |
| `expected_goals_conceded_per_90` | FLOAT | xGC normalized per 90 minutes. |
| `clearances_blocks_interceptions` | INTEGER | Combined defensive actions (clearances + blocks + interceptions). |
| `recoveries` | INTEGER | Ball recoveries. |
| `tackles` | INTEGER | Tackles made. |
| `defensive_contribution` | INTEGER | Combined defensive-actions score used for the 2025/26 defensive-contribution bonus points rule. |
| `defensive_contribution_per_90` | FLOAT | `defensive_contribution` normalized per 90 minutes. |
| `dreamteam_count` | INTEGER | Number of gameweeks the player has featured in the "Team of the Week" (Dream Team). |
| `in_dreamteam` | BOOLEAN | Whether the player is in the most recent gameweek's Dream Team. |
| `form_rank` | INTEGER | Rank by `form` among all players. |
| `form_rank_type` | INTEGER | Rank by `form` within position. |
| `selected_rank` | INTEGER | Rank by `selected_by_percent` among all players. |
| `selected_rank_type` | INTEGER | Rank by `selected_by_percent` within position. |
| `now_cost_rank` | INTEGER | Rank by `now_cost` among all players (1 = most expensive). |
| `now_cost_rank_type` | INTEGER | Rank by `now_cost` within position. |
| `points_per_game_rank` | INTEGER | Rank by `points_per_game` among all players. |
| `points_per_game_rank_type` | INTEGER | Rank by `points_per_game` within position. |
| `corners_and_indirect_freekicks_order` | INTEGER | Set-piece priority order for corners/indirect free kicks at the player's club (1 = primary taker). |
| `corners_and_indirect_freekicks_text` | STRING | Free-text note on corner/indirect-freekick duties. |
| `direct_freekicks_order` | INTEGER | Set-piece priority order for direct free kicks. |
| `direct_freekicks_text` | STRING | Free-text note on direct-freekick duties. |
| `penalties_order` | INTEGER | Penalty-taking priority order at the player's club. |
| `penalties_text` | STRING | Free-text note on penalty duties. |
| `scout_risks` | ARRAY | Structured list of "scout notes" risk flags (usually empty). |
| `scout_news_link` | STRING | Link to further scout news, if any. |
| `region` | INTEGER | Geographic region identifier for the player's nationality. |
| `team_join_date` | STRING | Date (`YYYY-MM-DD`) the player joined their current club. |
| `birth_date` | STRING | Player's date of birth (`YYYY-MM-DD`). |
| `has_temporary_code` | BOOLEAN | Whether the player has a temporary (not-yet-finalized) Opta code. |
| `can_transact` | BOOLEAN | Whether the player can currently be bought/sold. |
| `can_select` | BOOLEAN | Whether the player can currently be selected in a squad. |
| `removed` | BOOLEAN | Whether the player has been removed from FPL (e.g. left the league). |
| `special` | BOOLEAN | Whether the player has special/placeholder status; almost always `false`. |

# Examples

```json
{
  "id": 1,
  "web_name": "Raya",
  "first_name": "David",
  "second_name": "Raya Martín",
  "element_type": 1,
  "team": 1,
  "status": "a",
  "total_points": 162,
  "now_cost": 62,
  "selected_by_percent": "36.4",
  "minutes": 3330,
  "clean_sheets": 19,
  "saves": 60,
  "bonus": 11
}
```

```json
{
  "id": 2,
  "web_name": "Arrizabalaga",
  "first_name": "Kepa",
  "second_name": "Arrizabalaga Revuelta",
  "element_type": 1,
  "team": 1,
  "status": "a",
  "total_points": 2,
  "now_cost": 40,
  "selected_by_percent": "0.4",
  "minutes": 90,
  "clean_sheets": 0,
  "saves": 2,
  "bonus": 0,
  "goals_conceded": 1
}
```

# Notes

- **Prices** (`now_cost`, `cost_change_*`) are in tenths of £M; divide by 10 (e.g. 62 → £6.2m).
- Many numeric-looking metrics (`form`, `points_per_game`, `influence`, `creativity`, `threat`, `ict_index`, `expected_*`, `value_*`) are returned as **strings**, not numbers — cast to float before computing with them.
- `element_type` and `team` are foreign keys; join with [element_types](/tables/element_types.md) and [teams](/tables/teams.md) respectively for display names.
- Fields specific to a position (e.g. `saves` for goalkeepers, `clean_sheets` for defenders/goalkeepers) are populated with `0` rather than `null` for players where they don't apply — treat `0` as "not applicable or none" per position, not necessarily a true zero performance.
- This is a season-to-date snapshot, not per-gameweek history; for gameweek-level detail, join against [fixtures](/tables/fixtures.md) `stats` (keyed by `element`) or the FPL `element-summary/<id>/` endpoint (not included in this bundle).

# Joins

- [teams](/tables/teams.md) on `team` = `teams.id` — team name, strength ratings.
- [element_types](/tables/element_types.md) on `element_type` = `element_types.id` — position name and squad-composition rules.
- [fixtures](/tables/fixtures.md) — per-fixture `stats[].a`/`stats[].h` arrays reference players by `element` = `players.id`.

# Citations

[1] Fantasy Premier League Official API — bootstrap-static: https://fantasy.premierleague.com/api/bootstrap-static/
