---
type: JSON Document
title: FPL Game Rules & Scoring Config
description: Global, non-tabular configuration for the current FPL season — squad-building constraints, league/cup settings, and the points-per-action scoring table used to compute every player's fantasy points.
resource: https://fantasy.premierleague.com/api/bootstrap-static/#game_config
tags: [fantasy-sports, premier-league, rules, scoring, reference-data]
timestamp: 2026-07-03T00:00:00Z
---

# Schema

Nested JSON object (`game_config`), three top-level sections:

## `settings`
| Key | Type | Description |
|---|---|---|
| `entry_per_event` | BOOLEAN | Whether managers can create a new team per gameweek (single-entry mode when `false`). |
| `timezone` | STRING | Timezone used for all displayed times; `"UTC"`. |
| `static_content_url` | STRING | Base URL for FPL's static asset CDN (shirts, badges, etc.). |

## `rules` (mirrors the standalone `game_settings` payload)
| Key | Type | Description |
|---|---|---|
| `squad_squadsize` | INTEGER | Total squad size (15). |
| `squad_squadplay` | INTEGER | Starting XI size (11). |
| `squad_team_limit` | INTEGER | Max players a manager may own from a single real club (3). |
| `squad_total_spend` | INTEGER | Starting budget, in tenths of £M (1000 = £100.0m). |
| `transfers_cap` | INTEGER | Max transfers allowed in a single gameweek (20). |
| `transfers_sell_on_fee` | FLOAT | Fraction of a player's price gain retained by FPL on sale (0.5 = 50%). |
| `max_extra_free_transfers` | INTEGER | Max free transfers that can be banked (4). |
| `element_sell_at_purchase_price` | BOOLEAN | Whether players are always sold at purchase price rather than current value. |
| `stats_form_days` | INTEGER | Rolling window (days) used to compute the `form` stat on [players](/tables/players.md) (30). |
| `league_join_private_max` / `league_join_public_max` | INTEGER | Max leagues a manager may join, private vs. public. |
| `league_max_size_public_classic` / `league_max_size_public_h2h` / `league_max_size_private_h2h` | INTEGER | League size caps by type. |
| `league_points_h2h_win` / `_lose` / `_draw` | INTEGER | Points awarded in head-to-head leagues (3/0/1). |
| `league_h2h_tiebreak_stats` | ARRAY | Ordered tiebreaker stats for H2H leagues, e.g. `["+goals_scored", "-goals_conceded"]`. |
| `cup_start_event_id` / `cup_stop_event_id` / `cup_qualifying_method` / `cup_type` | mixed | FPL Cup configuration; null outside of active cup rounds. |
| `percentile_ranks` | ARRAY | Percentile buckets FPL uses for rank-percentile displays. |
| `underdog_differential` | INTEGER | Threshold used by the "underdog" bonus-scoring rules for team managers mode. |
| `ui_currency_multiplier` | INTEGER | Divisor to convert integer price fields to £M display (10). |

## `scoring`
Points awarded per action, some split by position (`GKP`/`DEF`/`MID`/`FWD`):

| Key | Description |
|---|---|
| `long_play` / `short_play` | Points for playing ≥60 / <60 minutes. |
| `goals_scored` | Points per goal, by position (GKP:10, DEF:6, MID:5, FWD:4). |
| `assists` | Points per assist (flat, 3). |
| `clean_sheets` | Points per clean sheet, by position (GKP:4, DEF:4, MID:1, FWD:0). |
| `goals_conceded` | Points penalty per 2 goals conceded, by position (GKP:-1, DEF:-1, MID:0, FWD:0). |
| `saves` | Points per 3 saves (flat, 1). |
| `penalties_saved` / `penalties_missed` | Flat bonus/penalty (5 / -2). |
| `yellow_cards` / `red_cards` / `own_goals` | Flat penalties (-1 / -3 / -2). |
| `bonus` | Multiplier applied to BPS-derived bonus points (1). |
| `defensive_contribution` | Points for hitting the defensive-actions threshold, by position — new for 2025/26 (DEF:2, MID:2, FWD:2, GKP:0). |
| `bps`, `influence`, `creativity`, `threat`, `ict_index`, `tackles`, `clearances_blocks_interceptions`, `recoveries`, `starts`, `expected_*` | Present in the config but currently weighted `0` — tracked for potential future scoring rules, not currently scored. |
| `mng_*` | Scoring rules for "Manager Mode" fantasy teams (a separate FPL game mode); all `0` for standard classic/H2H play. |

# Notes

- This concept documents `game_config`, which nests `game_settings` (the standalone `rules` section here) alongside `scoring` weights — the two top-level API fields overlap almost entirely, so they're combined into one concept rather than duplicated.
- `scoring` is the authoritative source for how every point on [players](/tables/players.md) `total_points`/`event_points` is computed.
- Values here are effectively season-wide constants; re-fetch at the start of each new season, as scoring rules change year to year (e.g. `defensive_contribution` was introduced for 2025/26).

# Joins

- [players](/tables/players.md) `total_points`/`event_points` are derived by applying `scoring` to the player's per-gameweek stats.
- [element_types](/tables/element_types.md) `singular_name_short` gives the `GKP`/`DEF`/`MID`/`FWD` keys used throughout `scoring`.

# Citations

[1] Fantasy Premier League Official API — bootstrap-static: https://fantasy.premierleague.com/api/bootstrap-static/
