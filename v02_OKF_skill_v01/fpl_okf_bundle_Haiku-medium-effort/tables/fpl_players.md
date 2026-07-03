---
type: JSON Table
title: FPL Players
description: One row per player in the Fantasy Premier League, including performance statistics, valuations, and real-time game status.
resource: https://fantasy.premierleague.com/api/bootstrap-static/
tags: [fantasy-sports, premier-league, players, statistics]
timestamp: 2026-07-03T12:36:00Z
---

# Schema

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Unique player identifier within FPL |
| code | INTEGER | Unique Opta Sports code identifying the player |
| opta_code | STRING | String-formatted Opta code (e.g., "p154561") |
| first_name | STRING | Player's first name |
| second_name | STRING | Player's surname |
| web_name | STRING | Player's display name on FPL website |
| known_name | STRING | Alternative/common name used by player (mostly empty) |
| photo | STRING | Filename of player's photo in FPL CDN (e.g., "154561.jpg") |
| element_type | INTEGER | Position ID: 1=Goalkeeper, 2=Defender, 3=Midfielder, 4=Forward |
| team | INTEGER | ID of the team the player belongs to |
| team_code | INTEGER | Team code from Opta Sports |
| status | STRING | Player status: "a"=available, "s"=sidelined, "u"=uncertain, etc. |
| total_points | INTEGER | Total fantasy points accumulated across all gameweeks |
| points_per_game | STRING | Average fantasy points per gameweek appearance |
| event_points | INTEGER | Fantasy points from the most recent gameweek |
| now_cost | INTEGER | Current transfer market price in tenths of pounds (e.g., 62 = £6.2M) |
| cost_change_start | INTEGER | Price change in tenths of pounds since season start |
| cost_change_event | INTEGER | Price change in tenths of pounds from last gameweek |
| news | STRING | Latest injury/fixture news for the player |
| news_added | TIMESTAMP | Timestamp when news was added (UTC, ISO 8601 format) |
| chance_of_playing_this_round | FLOAT | Probability (0-100) player will be selected for current gameweek |
| chance_of_playing_next_round | FLOAT | Probability (0-100) player will be selected for next gameweek |
| selected_by_percent | STRING | Percentage of fantasy managers with this player in their squad |
| form | STRING | Form rating (typically 0 in mid-season updates) |
| transfers_in | INTEGER | Total transfers of this player into fantasy squads (all-time) |
| transfers_out | INTEGER | Total transfers of this player out of fantasy squads (all-time) |
| transfers_in_event | INTEGER | Number of transfers in during the most recent gameweek |
| transfers_out_event | INTEGER | Number of transfers out during the most recent gameweek |
| minutes | INTEGER | Total minutes played across all Premier League matches this season |
| goals_scored | INTEGER | Total goals scored |
| assists | INTEGER | Total assists (key passes leading directly to goals) |
| clean_sheets | INTEGER | Number of matches where player's team conceded zero goals |
| bonus | INTEGER | Total bonus points earned (awarded to top 3 performers each match) |
| bps | INTEGER | Bonus points system score in the most recent gameweek |
| red_cards | INTEGER | Total red cards received |
| yellow_cards | INTEGER | Total yellow cards received |
| own_goals | INTEGER | Total own goals |
| penalties_saved | INTEGER | Penalties saved (goalkeepers only) |
| penalties_missed | INTEGER | Penalties missed by this player |
| saves | INTEGER | Saves made by player (goalkeepers only) |
| saves_per_90 | FLOAT | Saves per 90 minutes played (goalkeepers only) |
| goals_conceded | INTEGER | Goals conceded by player's team (defenders/goalkeepers) |
| goals_conceded_per_90 | FLOAT | Goals conceded per 90 minutes |
| recoveries | INTEGER | Number of times player gained possession from opponent |
| tackles | INTEGER | Defensive tackles made |
| clearances_blocks_interceptions | INTEGER | Combined count of clearances, blocks, and interceptions |
| creativity | STRING | Creative index score (chance-creation opportunities) |
| threat | STRING | Threat index score (goal-scoring threat) |
| influence | STRING | Influence index score (overall impact on match) |
| ict_index | STRING | Creativity, Threat, Influence combined (ICT Index) |
| ict_index_rank | INTEGER | ICT Index ranking among all players (1 = best) |
| expected_goals | STRING | Expected goals value (xG) based on shot quality |
| expected_assists | STRING | Expected assists (xA) based on chance creation |
| expected_goal_involvements | STRING | Combined xG + xA |
| expected_goals_per_90 | FLOAT | Expected goals per 90 minutes |
| expected_assists_per_90 | FLOAT | Expected assists per 90 minutes |
| expected_goal_involvements_per_90 | FLOAT | Expected goal involvements per 90 minutes |
| expected_goals_conceded | STRING | Expected goals conceded by player's team (xGC) |
| expected_goals_conceded_per_90 | FLOAT | Expected goals conceded per 90 minutes |
| starts | INTEGER | Number of matches started (as opposed to coming off bench) |
| starts_per_90 | FLOAT | Starts per 90 minutes of available time |
| dreamteam_count | INTEGER | Number of times player was selected in "Dream Team" of the week |
| in_dreamteam | BOOLEAN | Whether player is in the current gameweek's Dream Team |
| in_dreamteam_count | INTEGER | Total Dream Team appearances (historical) |
| form_rank | INTEGER | Ranking by recent form among all players (1 = best form) |
| selected_rank | INTEGER | Ranking by selection percentage (1 = most selected) |
| now_cost_rank | INTEGER | Ranking by current transfer price (1 = most expensive) |
| value_form | STRING | Form ranking value for value analysis |
| value_season | STRING | Points per £M spent during season |
| points_per_game_rank | INTEGER | Ranking by points per game (1 = highest ppg) |
| can_transact | BOOLEAN | Whether player can be transferred (vs. locked) |
| can_select | BOOLEAN | Whether player can be selected in squads |
| special | BOOLEAN | Whether player has special status (usually false) |
| removed | BOOLEAN | Whether player has been removed from FPL (retired, etc.) |
| has_temporary_code | BOOLEAN | Whether player has temporary identification code |
| birth_date | STRING | Player's date of birth (YYYY-MM-DD format) |
| team_join_date | STRING | Date player joined their current team |
| region | INTEGER | Geographic region identifier for player's nationality |
| defensive_contribution | INTEGER | Contribution metric for defensive players |
| defensive_contribution_per_90 | FLOAT | Defensive contribution per 90 minutes |

# Examples

```json
{
  "id": 1,
  "first_name": "David",
  "second_name": "Raya Martín",
  "web_name": "Raya",
  "element_type": 1,
  "team": 1,
  "status": "a",
  "total_points": 162,
  "now_cost": 62,
  "selected_by_percent": "36.4",
  "minutes": 3330,
  "clean_sheets": 19,
  "saves": 60,
  "bonus": 11,
  "price_change_start": 7
}
```

```json
{
  "id": 4,
  "first_name": "Kepa",
  "second_name": "Arrizabalaga Revuelta",
  "web_name": "Arrizabalaga",
  "element_type": 1,
  "team": 2,
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

- **Price representation**: All price values (`now_cost`, `cost_change_*`) are in tenths of pounds; divide by 10 to get pounds sterling (e.g., 62 = £6.2M).
- **Nullable fields**: Some fields are only applicable to certain positions (e.g., `saves` for goalkeepers, `clean_sheets` for defenders/goalkeepers). Null values indicate not applicable.
- **Rankings**: Rank fields (e.g., `form_rank`, `selected_rank`) use 1 as the best; higher numbers = lower rankings.
- **Percentages**: String fields that represent percentages (e.g., `selected_by_percent`) are returned as strings and should be converted to float for calculations.
- **Timestamps**: Fields like `news_added` follow ISO 8601 format in UTC.
- **Element type mapping**: 1=Goalkeeper, 2=Defender, 3=Midfielder, 4=Forward.

# Joins

- **Teams**: Join on `team` or `team_code` with the FPL Teams dataset to get team name, abbreviation, and match schedule.
- **Gameweek data**: This snapshot represents season totals; connect to per-gameweek data via `code` (Opta identifier) for historical performance analysis.

# Citations

[1] Fantasy Premier League Official API: https://fantasy.premierleague.com/api/bootstrap-static/
