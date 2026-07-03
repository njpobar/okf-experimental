---
type: JSON Document
title: Game config
description: Nested FPL configuration object holding UI settings, the full league/squad ruleset, and the points-scoring table.
resource: https://fantasy.premierleague.com/api/bootstrap-static/#game_config
tags: [fpl, scoring, rules, config]
timestamp: 2026-07-03T00:00:00Z
---

The `game_config` object from [bootstrap-static](/bootstrap-static.md). It
is a nested object with three sections. The `scoring` section is the most
useful part: it defines how FPL points are awarded per action, with
position-dependent values given as `{DEF, MID, FWD, GKP}` maps.

# Schema

Top-level sections:

| Field | Type | Description |
|---|---|---|
| `settings` | OBJECT | Runtime UI/content settings. |
| `rules` | OBJECT | League/squad/transfer ruleset (mirrors [game settings](/config/game_settings.md)). |
| `scoring` | OBJECT | Points awarded per scoring action (see below). |

`settings` keys:

| Field | Type | Description |
|---|---|---|
| `entry_per_event` | BOOLEAN | Whether entry is per-gameweek. |
| `timezone` | STRING | Game timezone (`UTC`). |
| `static_content_url` | STRING | Base URL for static game content assets. |

`scoring` keys — integer points unless noted. Position-varying values are
objects keyed by `GKP`/`DEF`/`MID`/`FWD`:

| Field | Type | Description |
|---|---|---|
| `long_play` | INTEGER | Points for playing 60+ minutes. |
| `short_play` | INTEGER | Points for playing 1–59 minutes. |
| `goals_scored` | OBJECT | Points per goal, by position (GKP 10, DEF 6, MID 5, FWD 4). |
| `assists` | INTEGER | Points per assist. |
| `clean_sheets` | OBJECT | Points per clean sheet, by position. |
| `goals_conceded` | OBJECT | Points per goals-conceded threshold, by position. |
| `saves` | INTEGER | Saves per point awarded. |
| `penalties_saved` | INTEGER | Points per penalty saved. |
| `penalties_missed` | INTEGER | Points per penalty missed (negative). |
| `yellow_cards` | INTEGER | Points per yellow card (negative). |
| `red_cards` | INTEGER | Points per red card (negative). |
| `own_goals` | INTEGER | Points per own goal (negative). |
| `bonus` | INTEGER | Bonus points contribution. |
| `bps` | INTEGER | Bonus Points System contribution. |
| `starts` | INTEGER | Points related to starting. |
| `tackles` | INTEGER | Points contribution from tackles. |
| `clearances_blocks_interceptions` | INTEGER | Points contribution from CBI. |
| `recoveries` | INTEGER | Points contribution from recoveries. |
| `defensive_contribution` | OBJECT | Defensive-contribution points, by position. |
| `influence` / `creativity` / `threat` / `ict_index` | INTEGER | Weightings for the ICT indices. |
| `special_multiplier` | INTEGER | Multiplier applied to special scoring. |
| `expected_goals` / `expected_assists` / `expected_goal_involvements` / `expected_goals_conceded` | INTEGER | Weightings for expected-stat scoring. |
| `mng_win` / `mng_draw` / `mng_loss` | INTEGER | Manager-mode points for match results. |
| `mng_goals_scored` / `mng_clean_sheets` | INTEGER | Manager-mode points for goals/clean sheets. |
| `mng_underdog_win` / `mng_underdog_draw` | INTEGER | Manager-mode bonus for underdog results. |

# Examples

```json
{
  "settings": {"entry_per_event": false, "timezone": "UTC"},
  "scoring": {
    "long_play": 2, "short_play": 1, "assists": 3, "saves": 1,
    "goals_scored": {"GKP": 10, "DEF": 6, "MID": 5, "FWD": 4},
    "clean_sheets": {"GKP": 4, "DEF": 4, "MID": 1, "FWD": 0}
  }
}
```

# Citations

[1] [FPL bootstrap-static endpoint](https://fantasy.premierleague.com/api/bootstrap-static/)
