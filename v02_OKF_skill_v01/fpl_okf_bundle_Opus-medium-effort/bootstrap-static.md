---
type: API Endpoint
title: FPL bootstrap-static
description: The Fantasy Premier League bootstrap-static endpoint — the game's core reference payload, bundling players, teams, gameweeks, positions and rules in one JSON object.
resource: https://fantasy.premierleague.com/api/bootstrap-static/
tags: [fpl, football, api, reference]
timestamp: 2026-07-03T00:00:00Z
---

`GET https://fantasy.premierleague.com/api/bootstrap-static/` returns a
single JSON **object** (not a list) that acts as the reference/lookup
payload for the whole Fantasy Premier League game. It is unauthenticated
and returns the current season's state at request time.

The response is decomposed here into one concept per top-level entity.
The list-shaped entities are documented as tables under
[tables/](/tables/index.md); the two configuration objects are under
[config/](/config/index.md).

# Schema

Top-level keys of the response object and where each is documented:

| Key             | Shape                | Concept |
|-----------------|----------------------|---------|
| `elements`      | list — 841 records   | [players](/tables/elements.md) |
| `teams`         | list — 20 records    | [teams](/tables/teams.md) |
| `events`        | list — 38 records    | [gameweeks](/tables/events.md) |
| `element_types` | list — 4 records     | [positions](/tables/element_types.md) |
| `element_stats` | list — 26 records    | [player stat definitions](/tables/element_stats.md) |
| `chips`         | list — 8 records     | [chips](/tables/chips.md) |
| `phases`        | list — 11 records    | [phases](/tables/phases.md) |
| `game_settings` | object               | [game settings](/config/game_settings.md) |
| `game_config`   | object               | [game config](/config/game_config.md) |
| `total_players` | INTEGER (scalar)     | *documented below* |

`total_players` is a single integer: the number of registered FPL
managers for the season. At capture time it was **13,107,732**.

# Notes

- The payload is a snapshot; counts (`total_players`, transfer totals,
  ownership, ranks) drift continuously through the season.
- Cross-entity foreign keys: player `team` → [teams](/tables/teams.md)`.id`,
  player `element_type` → [positions](/tables/element_types.md)`.id`,
  gameweek `top_element` → [players](/tables/elements.md)`.id`.

# Citations

[1] [FPL bootstrap-static endpoint](https://fantasy.premierleague.com/api/bootstrap-static/)
