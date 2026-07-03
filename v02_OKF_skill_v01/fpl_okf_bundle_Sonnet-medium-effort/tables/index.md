# Tables

Core data tables from the FPL `bootstrap-static` and `fixtures` API endpoints.

* [FPL Players](players.md) - One row per player, with identity, price, and cumulative season performance stats.
* [FPL Teams](teams.md) - One row per Premier League club, with FPL's strength ratings and league standing.
* [FPL Fixtures](fixtures.md) - One row per match, with scores, difficulty ratings, and per-player match stats.
* [FPL Events (Gameweeks)](events.md) - One row per gameweek, with deadlines, scoring summaries, and chip usage.

# Reference Data

Small, mostly-static lookup tables that other tables' foreign keys point into.

* [Positions (Element Types)](element_types.md) - Goalkeeper/Defender/Midfielder/Forward definitions and squad rules.
* [Element Stats](element_stats.md) - Field-name-to-label lookup for every tracked per-player statistic.
* [Phases](phases.md) - Season and monthly scoring-phase windows.
* [Chips](chips.md) - Playable strategy chips (Wildcard, Free Hit, Bench Boost, Triple Captain) and their availability windows.
