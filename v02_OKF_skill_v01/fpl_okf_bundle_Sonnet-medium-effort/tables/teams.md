---
type: JSON Table
title: FPL Teams
description: One row per Premier League club, with FPL's proprietary strength ratings used to compute fixture difficulty, plus (in-season) league table standing.
resource: https://fantasy.premierleague.com/api/bootstrap-static/#teams
tags: [fantasy-sports, premier-league, teams]
timestamp: 2026-07-03T00:00:00Z
---

# Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Unique team identifier within FPL for the current season. Referenced by `players.team` and `fixtures.team_h`/`team_a`. |
| `code` | INTEGER | Opta Sports team code; stable across seasons. Matches `players.team_code`. |
| `pulse_id` | INTEGER | Internal Premier League "Pulse" identifier, used in some PL media/API integrations. |
| `name` | STRING | Full club name, e.g. `"Arsenal"`. |
| `short_name` | STRING | Three-letter club abbreviation, e.g. `"ARS"`. |
| `link_url` | STRING | External link; empty in this snapshot. |
| `unavailable` | BOOLEAN | Whether the team is temporarily unavailable (e.g. relegation/admin issue); normally `false`. |
| `team_division` | STRING | Division identifier; null for Premier League snapshots (single-division dataset). |
| `position` | INTEGER | Current league table position (1 = top). |
| `played` | INTEGER | Matches played this season. |
| `win` | INTEGER | Matches won. |
| `draw` | INTEGER | Matches drawn. |
| `loss` | INTEGER | Matches lost. |
| `points` | INTEGER | League points this season. |
| `form` | STRING | Recent-form string; typically null in this endpoint (form is computed elsewhere). |
| `strength` | INTEGER | Overall FPL strength rating (1-5 scale) used for general difficulty coloring. |
| `strength_overall_home` | INTEGER | FPL's overall strength rating for the team when playing at home. |
| `strength_overall_away` | INTEGER | FPL's overall strength rating for the team when playing away. |
| `strength_attack_home` | INTEGER | Attacking strength rating at home. |
| `strength_attack_away` | INTEGER | Attacking strength rating away. |
| `strength_defence_home` | INTEGER | Defensive strength rating at home. |
| `strength_defence_away` | INTEGER | Defensive strength rating away. |

# Examples

```json
{
  "id": 1,
  "code": 3,
  "name": "Arsenal",
  "short_name": "ARS",
  "position": 1,
  "strength": 5,
  "strength_overall_home": 1305,
  "strength_overall_away": 1370
}
```

# Notes

- Strength ratings (`strength*`) are FPL's proprietary difficulty inputs (roughly hundreds-scale), used to derive the `team_h_difficulty`/`team_a_difficulty` values (1-5) on [fixtures](/tables/fixtures.md); they are not raw Elo or public ratings.
- `win`/`draw`/`loss`/`points`/`played`/`position` reset to zero at the start of each season and reflect the *current* fetch time (this snapshot was taken outside an active gameweek, so may show a completed season's final standings).

# Joins

- [players](/tables/players.md) on `players.team` = `teams.id`.
- [fixtures](/tables/fixtures.md) on `fixtures.team_h` / `fixtures.team_a` = `teams.id`.

# Citations

[1] Fantasy Premier League Official API — bootstrap-static: https://fantasy.premierleague.com/api/bootstrap-static/
