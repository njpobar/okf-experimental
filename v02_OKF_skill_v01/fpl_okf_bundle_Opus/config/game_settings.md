---
type: JSON Document
title: Game settings
description: Global FPL game rules — squad composition, budget, transfer, league and cup parameters — as a single settings object.
resource: https://fantasy.premierleague.com/api/bootstrap-static/#game_settings
tags: [fpl, rules, config]
timestamp: 2026-07-03T00:00:00Z
---

The `game_settings` object from [bootstrap-static](/bootstrap-static.md).
Unlike the tables in this bundle this is a flat key/value object (one
record), so the schema below documents its keys rather than columns.
Many of the same keys are echoed under `game_config.rules` — see
[game config](/config/game_config.md).

# Schema

| Field | Type | Description |
|---|---|---|
| `squad_squadsize` | INTEGER | Total players in a squad (15). |
| `squad_squadplay` | INTEGER | Players in the starting lineup (11). |
| `squad_total_spend` | INTEGER | Total budget, in tenths of £m (1000 = £100.0m). |
| `squad_team_limit` | INTEGER | Max players allowed from any one club (3). |
| `squad_special_min` | INTEGER | Min special players; null. |
| `squad_special_max` | INTEGER | Max special players; null. |
| `transfers_cap` | INTEGER | Max free transfers that can be stored. |
| `transfers_sell_on_fee` | FLOAT | Fraction of profit taken as sell-on fee (0.5 = 50%). |
| `max_extra_free_transfers` | INTEGER | Max extra free transfers granted. |
| `element_sell_at_purchase_price` | BOOLEAN | Whether players sell at their purchase price. |
| `stats_form_days` | INTEGER | Rolling window (days) used to compute player `form`. |
| `underdog_differential` | INTEGER | Rating gap defining an "underdog" for manager scoring. |
| `league_join_private_max` | INTEGER | Max private leagues a manager can join. |
| `league_join_public_max` | INTEGER | Max public leagues a manager can join. |
| `league_max_size_public_classic` | INTEGER | Max size of a public classic league. |
| `league_max_size_public_h2h` | INTEGER | Max size of a public head-to-head league. |
| `league_max_size_private_h2h` | INTEGER | Max size of a private head-to-head league. |
| `league_max_ko_rounds_private_h2h` | INTEGER | Max knockout rounds in a private H2H league. |
| `league_prefix_public` | STRING | Naming prefix for public leagues. |
| `league_points_h2h_win` | INTEGER | H2H league points for a win. |
| `league_points_h2h_draw` | INTEGER | H2H league points for a draw. |
| `league_points_h2h_lose` | INTEGER | H2H league points for a loss. |
| `league_ko_first_instead_of_random` | BOOLEAN | Whether KO seeding uses rank rather than random draw. |
| `league_h2h_tiebreak_stats` | ARRAY | Ordered stat names used to break H2H ties. |
| `cup_start_event_id` | INTEGER | Gameweek the cup starts; null when unset. |
| `cup_stop_event_id` | INTEGER | Gameweek the cup ends; null when unset. |
| `cup_qualifying_method` | STRING | Cup qualification method; null when unset. |
| `cup_type` | STRING | Cup type; null when unset. |
| `percentile_ranks` | ARRAY | Percentile boundaries (20 values) used for rank banding. |
| `featured_entries` | ARRAY | Featured manager entries (empty at capture). |
| `ui_currency_multiplier` | INTEGER | UI multiplier for displaying currency values. |
| `ui_use_special_shirts` | BOOLEAN | Whether special shirts are shown in the UI. |
| `ui_special_shirt_exclusions` | ARRAY | Teams excluded from special shirts (empty at capture). |
| `sys_vice_captain_enabled` | BOOLEAN | Whether the vice-captain feature is enabled. |
| `timezone` | STRING | Game timezone (`UTC`). |

# Examples

```json
{
  "squad_squadsize": 15, "squad_squadplay": 11, "squad_total_spend": 1000,
  "squad_team_limit": 3, "transfers_cap": 20, "transfers_sell_on_fee": 0.5,
  "stats_form_days": 30, "timezone": "UTC"
}
```

# Citations

[1] [FPL bootstrap-static endpoint](https://fantasy.premierleague.com/api/bootstrap-static/)
