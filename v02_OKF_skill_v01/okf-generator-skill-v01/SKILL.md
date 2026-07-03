---
name: okf-generator
description: Converts a data asset (CSV, TSV, JSON/JSONL, Excel, Parquet, a pandas dataframe, or a database view/query result) into an Open Knowledge Format (OKF) concept document or bundle — a markdown file with YAML frontmatter (and a Schema table) that conforms to the OKF v0.1 spec. Only use this skill when the user explicitly says "OKF", "Open Knowledge Format", asks to "generate/create/build an OKF bundle", "convert to OKF", "package this dataset as OKF", or similarly names OKF by name. Do not trigger on generic requests to "document this data", "describe this table", or "write metadata" unless OKF is explicitly mentioned — this skill is opt-in only.
---

# OKF Generator

Turns a tabular/structured data asset into a conformant Open Knowledge
Format (OKF) v0.1 concept document, and assembles one or more concepts
into a bundle (directory tree of markdown files) per the spec.

**Read `references/okf-spec-v0.1.md` in full before generating anything.**
It is the authoritative source for frontmatter fields, body conventions,
bundle structure, index/log file formats, and conformance rules. The
summary below is a workflow guide, not a substitute for the spec.

## When this triggers

Only when the user explicitly names OKF ("OKF", "Open Knowledge Format",
"OKF bundle", "convert to OKF", etc.). If someone just asks to "document
this CSV" or "describe this table" without mentioning OKF, don't use
this skill — do that as a normal response instead.

## Workflow

### 1. Identify the data asset(s)

The input can be:
- A file: CSV, TSV, JSON, JSONL/NDJSON, Excel, Parquet.
- An in-memory pandas dataframe already in the conversation/session.
- A "view" — the result of a SQL query or similar — which should first
  be materialized (e.g. to a dataframe or a temp CSV) before inferring
  its schema.

If the user references multiple data assets, or a whole directory of
files, plan to produce **one concept per asset**, assembled into a
single bundle (see step 5).

### 2. Infer the schema

For file-based sources, run:

```bash
python scripts/infer_schema.py <path-to-file> --sample-rows 5
```

This returns JSON with the detected format, row count, and per-column
`name`, `okf_type` (STRING / INTEGER / FLOAT / BOOLEAN / TIMESTAMP /
ARRAY / OBJECT), null stats, uniqueness, and sample values. Use this
instead of eyeballing the raw file — it's deterministic and catches
things like all-null or fully-unique columns you'd otherwise miss.

If the top-level JSON is a nested object rather than a list of records
(`detected_format: "json_object"`), the script instead returns a
recursive key/type outline. In that case, decide with the user (or use
best judgment) whether to represent it as a single concept with a
nested `# Schema`, or split it into multiple concepts (e.g. one per
top-level entity).

For an in-memory dataframe already in this session, you can skip the
script and inspect it directly (`df.dtypes`, `df.isna().sum()`,
`df.head()`, etc.) — apply the same type-mapping conventions the script
uses (see `okf_type()` in the script for the exact mapping logic).

### 3. Decide the concept's `type` value

Per spec §4.1, `type` is free text but should be descriptive. Pick
based on the source, e.g.:

| Source | Suggested `type` |
|---|---|
| CSV file | `CSV Table` |
| TSV file | `TSV Table` |
| JSON array of records | `JSON Table` |
| JSON object (non-tabular) | `JSON Document` |
| Excel sheet | `Spreadsheet Table` |
| Parquet file | `Parquet Table` |
| Pandas dataframe (no clear file origin) | `DataFrame Table` |
| Database view / query result | `SQL View` or name the source system, e.g. `BigQuery Table` if applicable |

If the user tells you the source system explicitly (e.g. "this came
from our BigQuery warehouse"), prefer their framing to match the
spec's own examples (`BigQuery Table`, `BigQuery Dataset`).

### 4. Build the concept document

Frontmatter (spec §4.1) — always include `type`; include the others
whenever you have a reasonable value, don't leave them out just because
they take a little inference:

- `type` — from step 3.
- `title` — human-readable name; derive from filename/variable name if
  not given (e.g. `orders.csv` → `Orders`).
- `description` — one sentence, written by you based on the schema and
  a skim of sample values (e.g. "One row per completed customer order.").
  Flag it to the user as inferred/best-effort so they can correct it.
- `resource` — canonical URI/path to the underlying asset. Use the file
  path (or a `file://` URI) for local files, the source URL if the user
  gave one, or omit if there truly isn't one (e.g. an ephemeral
  in-memory dataframe with no origin).
- `tags` — a few short cross-cutting labels inferred from column names/
  context (e.g. `[sales, orders]`). Keep to 2-5.
- `timestamp` — ISO 8601 datetime; use current time unless the source
  has its own last-modified time.

Body — use the conventional section headings from spec §4.2:

- `# Schema` (required in practice for tabular data) — a markdown table
  with columns `Column | Type | Description`. Use `okf_type` from step 2
  for Type. For Description, write a short best-effort note per column
  based on the name and sample values (e.g. `customer_id` → "Foreign
  key identifying the customer."); don't leave these blank.
- `# Examples` (optional but recommended) — a small fenced code block
  or table with 2-3 real sample rows, so a reader can see real shape,
  not just types.
- `# Joins` / other free-form sections — only if you have genuine
  relational context (e.g. the user mentions a related table); link to
  other concepts in the bundle using bundle-relative links (`/tables/x.md`).
- `# Citations` — only if there's an external source URL worth citing
  (spec §8); one entry per source, numbered.

Don't invent relationships, joins, or business meaning you don't have
evidence for. It's fine — expected, even — for a generated concept to
be schema-only when there's nothing else to say.

### 5. Assemble the bundle

- If the user already has an OKF bundle and wants to add to it, place
  new concept file(s) into its existing directory structure (ask where,
  if unclear, e.g. "should this go under `tables/`?").
- Otherwise, create a new bundle directory. A sensible default layout
  for tabular data:
  ```
  <bundle_name>/
  ├── index.md
  └── tables/
      ├── index.md
      └── <asset_name>.md   (one per data asset)
  ```
  Adjust the subdirectory name/grouping to fit what the data actually
  is (`tables/`, `datasets/`, `views/`, etc. — producer's choice per spec).
- Write a root `index.md` (no frontmatter, unless you want to declare
  `okf_version: "0.1"` there — spec §11) listing each concept with its
  `description` from frontmatter, grouped under a heading (spec §6).
- Write a `tables/index.md` (or equivalent) the same way if there's more
  than one concept in that subdirectory.
- Optionally write a `log.md` with a single dated entry recording the
  bundle's creation (spec §7), e.g.:
  ```markdown
  # Directory Update Log

  ## 2026-07-03
  * **Creation**: Generated OKF bundle from <source description>.
  ```

### 6. Validate

Run the conformance checker before handing back the bundle:

```bash
python scripts/validate_bundle.py <bundle_dir>
```

It enforces the spec's hard requirements (§9: parseable frontmatter,
non-empty `type`, index.md frontmatter rules) as errors, and flags
missing recommended fields as warnings (not blockers). Fix any errors.
Warnings are fine to leave if you've made a deliberate choice (e.g. no
sensible `resource` for an ephemeral dataframe).

### 7. Deliver

Present the bundle directory to the user (zip it if it's easier to hand
over as one file, or just point to the directory if they're working in
the same filesystem). Briefly summarize what was inferred vs. what's a
best-effort guess they should sanity-check — especially per-column and
concept `description` text, since those are semantic judgments made
without full business context.

## Notes

- `scripts/infer_schema.py` requires `pandas`, `pyyaml` (already used by
  `scripts/validate_bundle.py`) — both are standard in this environment.
- Always re-read `references/okf-spec-v0.1.md` for edge cases not
  covered above (e.g. citation formatting, log file conventions,
  bundle distribution as git repo vs. tarball) rather than guessing.
- The spec is deliberately permissive on consumption (§9) but that's a
  reason to be *more* careful on production: a good-faith bundle should
  still fill in every recommended field where you can, not lean on the
  spec's tolerance for omissions as an excuse to skip them.
