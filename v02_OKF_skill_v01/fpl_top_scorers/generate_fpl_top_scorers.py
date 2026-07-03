#!/usr/bin/env python3
"""
FPL top scorers report generator.

Pulls the most recently completed FPL season from the live API
(bootstrap-static + element-summary, per the OKF bundle at
../fpl_okf_bundle_Opus-medium-effort/), ranks players by total season
points, and renders a single self-contained HTML page with a
game-by-game points time series for each of the top players.

Edit TOP_N below and re-run to change how many players are covered.
The script re-fetches live data and regenerates OUTPUT_FILE each run.
"""

import json
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# The only setting you should need to touch.
# ---------------------------------------------------------------------------
TOP_N = 15  # number of top-scoring players to pull in and chart

# ---------------------------------------------------------------------------
# Fixed configuration
# ---------------------------------------------------------------------------
BOOTSTRAP_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
ELEMENT_SUMMARY_URL = "https://fantasy.premierleague.com/api/element-summary/{id}/"
OUTPUT_FILE = Path(__file__).parent / "fpl_top_scorers.html"
REQUEST_TIMEOUT = 20

# Fixed-order categorical palette (dataviz skill default), light / dark pair.
# Cycles if TOP_N > 8; identity per chart still holds since each chart is a
# standalone small multiple.
CATEGORICAL_PALETTE = [
    ("#2a78d6", "#3987e5"),  # blue
    ("#1baf7a", "#199e70"),  # aqua
    ("#eda100", "#c98500"),  # yellow
    ("#008300", "#008300"),  # green
    ("#4a3aa7", "#9085e9"),  # violet
    ("#e34948", "#e66767"),  # red
    ("#e87ba4", "#d55181"),  # magenta
    ("#eb6834", "#d95926"),  # orange
]

POSITION_NAMES = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return json.loads(resp.read())


def get_top_players(bootstrap, n):
    elements = sorted(bootstrap["elements"], key=lambda e: -e["total_points"])
    return elements[:n]


def get_team_lookup(bootstrap):
    return {t["id"]: t for t in bootstrap["teams"]}


def get_season_label(bootstrap):
    events = [e for e in bootstrap["events"] if e.get("deadline_time")]
    if not events:
        return "Most recent FPL season"
    start_year = min(e["deadline_time"][:4] for e in events)
    end_year = max(e["deadline_time"][:4] for e in events)
    if start_year == end_year:
        return f"{start_year} FPL season"
    return f"{start_year}-{end_year[-2:]} FPL season"


def build_player_series(player, teams):
    summary = fetch_json(ELEMENT_SUMMARY_URL.format(id=player["id"]))
    history = sorted(summary["history"], key=lambda h: h["kickoff_time"])
    games = []
    for h in history:
        opp = teams.get(h["opponent_team"], {})
        opp_short = opp.get("short_name", "???")
        games.append(
            {
                "round": h["round"],
                "points": h["total_points"],
                "opponent": opp_short,
                "was_home": h["was_home"],
                "kickoff_time": h["kickoff_time"],
                "minutes": h["minutes"],
            }
        )
    return games


def fmt_date(iso_ts):
    # "2025-08-16T16:30:00Z" -> "16 Aug"
    date_part = iso_ts[:10]
    y, m, d = date_part.split("-")
    months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{int(d)} {months[int(m)]}"


def render_chart_svg(games, light_color, dark_color, chart_id):
    """Build an inline SVG line chart (axes + gridlines) for one player's
    game-by-game points, plus the JS hook points needed for the crosshair
    tooltip layer."""
    width, height = 900, 260
    pad_left, pad_right, pad_top, pad_bottom = 44, 16, 16, 28
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    values = [g["points"] for g in games]
    y_max = max(4, max(values)) if values else 4
    # round y-max up to a clean step
    step = 2 if y_max <= 10 else (5 if y_max <= 25 else 10)
    y_max = ((y_max // step) + 1) * step

    n = len(games)

    def x_at(i):
        if n <= 1:
            return pad_left + plot_w / 2
        return pad_left + (plot_w * i / (n - 1))

    def y_at(v):
        return pad_top + plot_h * (1 - v / y_max)

    # gridlines (hairline, 4 horizontal bands)
    gridlines = []
    y_ticks = [round(y_max * f) for f in (0, 0.25, 0.5, 0.75, 1.0)]
    y_ticks = sorted(set(y_ticks))
    for t in y_ticks:
        gy = y_at(t)
        gridlines.append(
            f'<line x1="{pad_left}" y1="{gy:.1f}" x2="{width - pad_right}" '
            f'y2="{gy:.1f}" class="gridline" />'
        )
        gridlines.append(
            f'<text x="{pad_left - 8}" y="{gy + 4:.1f}" class="axis-label" '
            f'text-anchor="end">{t}</text>'
        )

    # x-axis ticks: label every ~5th game to avoid crowding
    x_ticks = []
    tick_stride = max(1, n // 8)
    for i, g in enumerate(games):
        if i % tick_stride == 0 or i == n - 1:
            x_ticks.append(
                f'<text x="{x_at(i):.1f}" y="{height - pad_bottom + 18}" '
                f'class="axis-label" text-anchor="middle">GW{g["round"]}</text>'
            )

    # baseline
    baseline_y = y_at(0)
    baseline = (
        f'<line x1="{pad_left}" y1="{baseline_y:.1f}" x2="{width - pad_right}" '
        f'y2="{baseline_y:.1f}" class="baseline" />'
    )

    # line path + area fill
    points_attr = " ".join(f"{x_at(i):.1f},{y_at(g['points']):.1f}" for i, g in enumerate(games))
    area_path = ""
    if n:
        area_pts = points_attr + f" {x_at(n-1):.1f},{baseline_y:.1f} {x_at(0):.1f},{baseline_y:.1f}"
        area_path = f'<polygon points="{area_pts}" fill="var(--chart-color)" opacity="0.10" />'

    line_path = f'<polyline points="{points_attr}" fill="none" stroke="var(--chart-color)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" />'

    # end marker on the last game
    end_marker = ""
    if n:
        ex, ey = x_at(n - 1), y_at(games[-1]["points"])
        end_marker = (
            f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="var(--chart-color)" '
            f'stroke="var(--surface-1)" stroke-width="2" />'
        )

    # invisible hit-target dots for hover/focus, keyed by data-index
    hit_targets = "".join(
        f'<circle cx="{x_at(i):.1f}" cy="{y_at(g["points"]):.1f}" r="12" '
        f'class="hit-target" data-idx="{i}" fill="transparent" />'
        for i, g in enumerate(games)
    )

    svg = f"""
<svg class="chart-svg" data-chart="{chart_id}" viewBox="0 0 {width} {height}"
     width="100%" height="{height}" role="img"
     aria-label="Points per game time series">
  {''.join(gridlines)}
  {baseline}
  {area_path}
  {line_path}
  <line class="crosshair" x1="0" y1="{pad_top}" x2="0" y2="{baseline_y:.1f}" />
  {end_marker}
  {''.join(x_ticks)}
  {hit_targets}
</svg>
""".strip()
    return svg


def build_player_data_json(games):
    return json.dumps(
        [
            {
                "round": g["round"],
                "points": g["points"],
                "opponent": g["opponent"],
                "venue": "H" if g["was_home"] else "A",
                "date": fmt_date(g["kickoff_time"]),
                "minutes": g["minutes"],
            }
            for g in games
        ]
    )


def render_player_card(rank, player, teams, index):
    team = teams.get(player["team"], {})
    games = build_player_series(player, teams)
    total_points = player["total_points"]
    games_played = sum(1 for g in games if g["minutes"] > 0)
    ppg = (total_points / games_played) if games_played else 0.0
    light_color, dark_color = CATEGORICAL_PALETTE[index % len(CATEGORICAL_PALETTE)]
    chart_id = f"p{player['id']}"

    svg = render_chart_svg(games, light_color, dark_color, chart_id)
    data_json = build_player_data_json(games)

    table_rows = "".join(
        f"<tr><td>GW{g['round']}</td><td>{'vs' if g['was_home'] else '@'} "
        f"{g['opponent']}</td><td>{fmt_date(g['kickoff_time'])}</td>"
        f"<td class='num'>{g['points']}</td></tr>"
        for g in games
    )

    return f"""
<section class="card" style="--chart-color-light: {light_color}; --chart-color-dark: {dark_color};">
  <div class="card-head">
    <div class="rank">#{rank}</div>
    <div class="who">
      <h2>{player['web_name']}</h2>
      <p class="meta">{team.get('name', 'Unknown')} &middot; {POSITION_NAMES.get(player['element_type'], '?')}</p>
    </div>
    <div class="stats">
      <div class="stat"><span class="stat-value">{total_points}</span><span class="stat-label">season points</span></div>
      <div class="stat"><span class="stat-value">{games_played}</span><span class="stat-label">games played</span></div>
      <div class="stat"><span class="stat-value">{ppg:.1f}</span><span class="stat-label">points / game</span></div>
    </div>
  </div>
  <div class="chart-wrap">
    {svg}
    <div class="tooltip" data-tooltip-for="{chart_id}"></div>
  </div>
  <details class="table-toggle">
    <summary>Show game-by-game data table</summary>
    <table>
      <thead><tr><th>Gameweek</th><th>Fixture</th><th>Date</th><th class="num">Points</th></tr></thead>
      <tbody>{table_rows}</tbody>
    </table>
  </details>
  <script type="application/json" class="chart-data" data-chart="{chart_id}">{data_json}</script>
</section>
"""


PAGE_CSS = """
:root {
  --surface-1: #fcfcfb;
  --page-plane: #f9f9f7;
  --text-primary: #0b0b0b;
  --text-secondary: #52514e;
  --text-muted: #898781;
  --gridline: #e1e0d9;
  --baseline: #c3c2b7;
  --border: rgba(11,11,11,0.10);
}
@media (prefers-color-scheme: dark) {
  :root {
    --surface-1: #1a1a19;
    --page-plane: #0d0d0d;
    --text-primary: #ffffff;
    --text-secondary: #c3c2b7;
    --text-muted: #898781;
    --gridline: #2c2c2a;
    --baseline: #383835;
    --border: rgba(255,255,255,0.10);
  }
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--page-plane);
  color: var(--text-primary);
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
}
.page {
  max-width: 980px;
  margin: 0 auto;
  padding: 32px 20px 64px;
}
header.page-head h1 {
  font-size: 26px;
  margin: 0 0 4px;
}
header.page-head p {
  color: var(--text-secondary);
  margin: 0 0 32px;
  font-size: 14px;
}
.card {
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px 20px 8px;
  margin-bottom: 20px;
  --chart-color: var(--chart-color-light);
}
@media (prefers-color-scheme: dark) {
  .card { --chart-color: var(--chart-color-dark); }
}
.card-head {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.rank {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px 10px;
}
.who h2 { margin: 0; font-size: 19px; }
.who .meta { margin: 2px 0 0; color: var(--text-secondary); font-size: 13px; }
.stats { display: flex; gap: 20px; margin-left: auto; }
.stat { text-align: right; }
.stat-value { display: block; font-size: 18px; font-weight: 600; }
.stat-label { display: block; font-size: 11px; color: var(--text-muted); }
.chart-wrap { position: relative; }
.chart-svg { display: block; overflow: visible; }
.gridline { stroke: var(--gridline); stroke-width: 1; }
.baseline { stroke: var(--baseline); stroke-width: 1; }
.axis-label { fill: var(--text-muted); font-size: 10px; }
.hit-target { cursor: crosshair; }
.crosshair {
  stroke: var(--baseline);
  stroke-width: 1;
  opacity: 0;
  pointer-events: none;
}
.tooltip {
  position: absolute;
  pointer-events: none;
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 12px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.15);
  opacity: 0;
  transform: translate(-50%, -110%);
  white-space: nowrap;
  z-index: 5;
}
.tooltip .tt-value { font-weight: 700; font-size: 14px; }
.tooltip .tt-meta { color: var(--text-secondary); }
.table-toggle { margin: 8px 0 12px; }
.table-toggle summary {
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  padding: 6px 0;
}
table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 8px; }
th, td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--gridline); }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
th { color: var(--text-muted); font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.03em; }
footer { color: var(--text-muted); font-size: 12px; margin-top: 24px; }
"""

PAGE_JS = """
document.querySelectorAll('.card').forEach(function (card) {
  var svg = card.querySelector('.chart-svg');
  var chartId = svg.getAttribute('data-chart');
  var dataEl = card.querySelector('script[data-chart="' + chartId + '"]');
  var data = JSON.parse(dataEl.textContent);
  var tooltip = card.querySelector('.tooltip[data-tooltip-for="' + chartId + '"]');
  var crosshair = svg.querySelector('.crosshair');
  var hitTargets = Array.prototype.slice.call(svg.querySelectorAll('.hit-target'));

  function showPoint(idx) {
    var target = hitTargets[idx];
    if (!target || !data[idx]) return;
    var cx = parseFloat(target.getAttribute('cx'));
    var cy = parseFloat(target.getAttribute('cy'));
    crosshair.setAttribute('x1', cx);
    crosshair.setAttribute('x2', cx);
    crosshair.style.opacity = 1;

    var d = data[idx];
    tooltip.innerHTML = '';
    var value = document.createElement('div');
    value.className = 'tt-value';
    value.textContent = d.points + ' pts';
    var meta = document.createElement('div');
    meta.className = 'tt-meta';
    meta.textContent = 'GW' + d.round + ' \\u00b7 ' + d.venue + ' ' + d.opponent + ' \\u00b7 ' + d.date;
    tooltip.appendChild(value);
    tooltip.appendChild(meta);

    var svgRect = svg.getBoundingClientRect();
    var scaleX = svgRect.width / svg.viewBox.baseVal.width;
    var scaleY = svgRect.height / svg.viewBox.baseVal.height;
    tooltip.style.left = (cx * scaleX) + 'px';
    tooltip.style.top = (cy * scaleY) + 'px';
    tooltip.style.opacity = 1;
  }

  function hide() {
    crosshair.style.opacity = 0;
    tooltip.style.opacity = 0;
  }

  hitTargets.forEach(function (t, idx) {
    t.addEventListener('pointerenter', function () { showPoint(idx); });
    t.addEventListener('focus', function () { showPoint(idx); });
  });
  svg.addEventListener('pointerleave', hide);
  card.addEventListener('focusout', function (e) {
    if (!card.contains(e.relatedTarget)) hide();
  });
});
"""


def build_html(bootstrap, top_players, teams):
    season_label = get_season_label(bootstrap)
    cards = [
        render_player_card(i + 1, player, teams, i)
        for i, player in enumerate(top_players)
    ]

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>FPL Top {len(top_players)} Scorers &mdash; {season_label}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
{PAGE_CSS}
</style>
</head>
<body>
<div class="page">
  <header class="page-head">
    <h1>FPL Top {len(top_players)} Scorers &mdash; {season_label}</h1>
    <p>Ranked by total points across the completed season. Each chart plots points scored in every game played, earliest to latest. Hover or focus a point for fixture detail.</p>
  </header>
  {''.join(cards)}
  <footer>Source: Fantasy Premier League API (bootstrap-static, element-summary). Generated by generate_fpl_top_scorers.py.</footer>
</div>
<script>
{PAGE_JS}
</script>
</body>
</html>"""
    return html


def main():
    print(f"Fetching bootstrap-static ({BOOTSTRAP_URL}) ...")
    bootstrap = fetch_json(BOOTSTRAP_URL)
    teams = get_team_lookup(bootstrap)

    top_players = get_top_players(bootstrap, TOP_N)
    print(f"Top {TOP_N} scorers:")
    for i, p in enumerate(top_players, 1):
        print(f"  {i}. {p['web_name']} - {p['total_points']} pts")

    print("Fetching per-player gameweek history ...")
    html = build_html(bootstrap, top_players, teams)

    OUTPUT_FILE.write_text(html)
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
