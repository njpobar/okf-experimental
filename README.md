# database-experimental

Experiments in generating structured data documentation and reports with Claude, organized as a series of dated attempts.

## v01_ecommerce-auto-reports

First step: use the "OKF bundle" idea (structured, per-table markdown documentation) as scaffolding for auto-generating reports over a seeded e-commerce SQLite database.

- `build_db.py` / `schema.sql` — builds `ecommerce.sqlite` (categories, customers, products, orders, order_items, reviews; ~5,000 rows total).
- `tables/*.md` — per-table documentation.
- `generate_feedback_report.py`, `generate_top_product_report.py` — generate the HTML reports in `reports/`.
- `experimentation.ipynb` — scratch notebook.

Known follow-up: the two report-generating Python files need revisiting/cleanup.

## v02_OKF_skill_v01

Second step: turn the OKF bundle idea into a proper Claude **skill** — `okf-generator-skill-v01/` — that converts a tabular/structured data source into a conformant Open Knowledge Format (OKF) v0.1 bundle (concept docs with YAML frontmatter, schema tables, index/log files). See `okf-generator-skill-v01/SKILL.md` for the workflow and `references/okf-spec-v0.1.md` for the spec.

The skill was exercised against the Fantasy Premier League (FPL) API (`fpl_raw.json`, `fpl_players.json`, `fpl_explorer.ipynb`) at three effort levels, for comparison:

- `fpl_okf_bundle_Haiku-medium-effort/`
- `fpl_okf_bundle_Sonnet-medium-effort/`
- `fpl_okf_bundle_Opus/`

Each is a bundle generated from the same FPL `bootstrap-static` payload, useful for comparing how much schema/documentation detail each model level produces. The skill itself (`okf-generator-skill-v01/`) may be iterated on further.
