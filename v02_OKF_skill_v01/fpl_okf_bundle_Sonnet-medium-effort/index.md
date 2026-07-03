okf_version: "0.1"

# FPL Data Bundle

Open Knowledge Format documentation for the official Fantasy Premier
League (FPL) API — the game Premier League clubs, players, fixtures, and
gameweeks that power fantasypremierleague.com.

Generated from two live API calls made on 2026-07-03:
- `GET https://fantasy.premierleague.com/api/bootstrap-static/` — players, teams, gameweeks, positions, stat definitions, phases, chips, and game config in one payload.
- `GET https://fantasy.premierleague.com/api/fixtures/` — the full match list for the season.

At fetch time, `bootstrap-static.total_players` reported **13,107,732**
registered FPL manager accounts game-wide (not modeled as its own
concept — it's a single scalar, not a table).

## Contents

### Tables

- [Tables](/tables/index.md) — core and reference data tables (players, teams, fixtures, events, positions, stats, phases, chips).

### Configuration

- [Configuration](/config/index.md) — game-wide rules and scoring weights.

---

**Generated**: 2026-07-03
**Source**: Fantasy Premier League Official API
**Format**: Open Knowledge Format v0.1
