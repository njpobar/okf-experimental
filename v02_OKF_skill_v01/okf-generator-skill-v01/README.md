# OKF Generator Skill

This is a complete backup of the `okf-generator` skill for Claude, which automates the creation of Open Knowledge Format (OKF) v0.1 concept documents and bundles from tabular data assets.

## Directory Structure

```
okf-generator/
├── SKILL.md                         # Main skill definition and workflow guide
├── README.md                        # This file
├── references/
│   └── okf-spec-v0.1.md            # OKF v0.1 specification (authoritative)
└── scripts/
    ├── infer_schema.py             # Schema inference from data files
    └── validate_bundle.py          # OKF bundle conformance checker
```

## Files Overview

### SKILL.md
The primary skill definition. Contains:
- Metadata (name, description, trigger conditions)
- Complete workflow guide (7 steps: identify assets → infer schema → build documents → assemble bundle → validate → deliver)
- Type selection guidance
- Frontmatter field descriptions
- Body section conventions
- Notes on dependencies and spec compliance

### references/okf-spec-v0.1.md
The authoritative OKF v0.1 specification. This is the definitive reference for:
- Bundle structure and reserved filenames
- Concept document format (frontmatter, body, examples)
- Cross-linking conventions
- Index and log file formats
- Citations
- Conformance rules (§9)
- Versioning

**Always read this in full before generating OKF bundles.**

### scripts/infer_schema.py
Deterministic schema inference tool. Given a tabular data source (CSV, TSV, JSON, JSONL, Excel, Parquet), outputs JSON with:
- Detected format
- Row count
- Per-column analysis: name, OKF type, pandas dtype, null stats, uniqueness, sample values

Handles non-tabular JSON objects by returning a recursive structure outline.

**Dependencies:** `pandas`, `pyyaml`

### scripts/validate_bundle.py
OKF bundle conformance checker. Enforces spec §9 hard requirements:
1. Every non-reserved `.md` file has parseable YAML frontmatter
2. Every frontmatter contains non-empty `type`
3. Reserved filenames (`index.md`, `log.md`) follow spec structure

Flags missing recommended fields as warnings (not errors).

**Dependencies:** `pyyaml`

## Installation

1. Copy this entire directory to your local filesystem.
2. Ensure Python 3.7+ is available.
3. Install dependencies:
   ```bash
   pip install pandas pyyaml
   ```

## Usage

### Basic workflow (from Claude's perspective)

1. User asks to convert data to OKF (e.g., "convert this CSV to an OKF bundle")
2. Load this skill via SKILL.md instructions
3. Infer schema: `python scripts/infer_schema.py <data_file> --sample-rows 5`
4. Build OKF concept document(s) following spec §4
5. Assemble bundle directory per spec §3
6. Validate: `python scripts/validate_bundle.py <bundle_dir>`
7. Deliver to user

### Direct schema inference

```bash
python scripts/infer_schema.py orders.csv --sample-rows 10
```

Output: JSON with column-level type, null, and uniqueness stats.

### Direct bundle validation

```bash
python scripts/validate_bundle.py ./my_bundle/
```

Output: Errors (if non-conformant) and warnings (soft guidance).

## Skill Metadata

| Field | Value |
|-------|-------|
| Name | `okf-generator` |
| Type | Data documentation / OKF authoring |
| Trigger | Explicit mention of "OKF", "Open Knowledge Format", "generate/create OKF bundle", etc. |
| **Not** triggered by | Generic requests like "document this data" or "describe this table" (unless OKF explicitly mentioned) |
| Dependencies | pandas, pyyaml |
| Python version | 3.7+ |

## Versioning

- **Skill version:** As of 2026-07-03
- **OKF spec version:** 0.1 (Draft)
- **Python dependencies:** pandas, pyyaml (versions unspecified; use latest stable)

## Key Design Principles

1. **Opt-in only**: This skill triggers only on explicit OKF mentions. Never use for generic data documentation unless the user names OKF.
2. **Spec-first**: Always refer to `references/okf-spec-v0.1.md` for edge cases, not inference or guessing.
3. **Deterministic schema inference**: Use `scripts/infer_schema.py` to avoid manual eyeballing.
4. **Soft guidance on consumption, strict on production**: Validation enforces only hard requirements; recommended fields should be filled in when possible.
5. **Human-readable output**: OKF is markdown + YAML, readable without tools.

## References

- **OKF Specification**: See `references/okf-spec-v0.1.md`
- **Skill Workflow Guide**: See `SKILL.md` (§Workflow)
- **Schema Inference Logic**: See `scripts/infer_schema.py` docstring and `okf_type()` function
- **Conformance Rules**: See `references/okf-spec-v0.1.md` §9

## License & Attribution

This skill package is provided as-is for use with Claude. The OKF specification (v0.1, Draft) is included for reference and authority.

---

**Last updated:** 2026-07-03
