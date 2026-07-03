#!/usr/bin/env python3
"""
validate_bundle.py — Check an OKF bundle against the v0.1 conformance rules (spec §9).

Checks:
  1. Every non-reserved .md file has a parseable YAML frontmatter block.
  2. Every frontmatter block has a non-empty `type` field.
  3. `index.md` files have NO frontmatter (except a bundle-root index.md,
     which MAY carry an `okf_version` field and nothing else meaningful).
  4. `log.md` files, if present, use ISO 8601 `## YYYY-MM-DD` date headings.

This performs the REQUIRED structural checks only. It does not (and per
spec, must not) reject a bundle for soft-guidance issues like missing
optional fields, unknown types, or broken links — those are reported as
warnings, not errors.

Usage:
    python validate_bundle.py <bundle_dir>

Exit code 0 = conformant (warnings allowed), 1 = non-conformant errors found.
"""

import re
import sys
from pathlib import Path

import yaml

RESERVED = {"index.md", "log.md"}
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)
DATE_HEADING_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$")


def check_concept(path: Path, bundle_root: Path, errors: list, warnings: list):
    text = path.read_text(encoding="utf-8", errors="replace")
    m = FRONTMATTER_RE.match(text)
    rel = path.relative_to(bundle_root)
    if not m:
        errors.append(f"{rel}: missing or malformed YAML frontmatter block")
        return
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        errors.append(f"{rel}: invalid YAML in frontmatter: {e}")
        return
    if not isinstance(fm, dict):
        errors.append(f"{rel}: frontmatter must be a YAML mapping")
        return
    if not fm.get("type"):
        errors.append(f"{rel}: missing required 'type' field")
    for field in ("title", "description", "resource", "tags", "timestamp"):
        if field not in fm:
            warnings.append(f"{rel}: missing recommended '{field}' field")


def check_index(path: Path, bundle_root: Path, errors: list, warnings: list):
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = path.relative_to(bundle_root)
    is_root = path.parent == bundle_root
    m = FRONTMATTER_RE.match(text)
    if m:
        if not is_root:
            errors.append(f"{rel}: index.md frontmatter is only permitted at the bundle root")
        else:
            try:
                fm = yaml.safe_load(m.group(1)) or {}
                extra = set(fm.keys()) - {"okf_version"}
                if extra:
                    warnings.append(f"{rel}: root index.md frontmatter has non-spec keys: {extra}")
            except yaml.YAMLError as e:
                errors.append(f"{rel}: invalid YAML in root index.md frontmatter: {e}")


def check_log(path: Path, bundle_root: Path, errors: list, warnings: list):
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = path.relative_to(bundle_root)
    date_headings = [l for l in text.splitlines() if l.startswith("## ")]
    for h in date_headings:
        if not DATE_HEADING_RE.match(h.strip()):
            warnings.append(f"{rel}: date heading '{h.strip()}' does not match '## YYYY-MM-DD'")


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_bundle.py <bundle_dir>")
        sys.exit(2)

    bundle_root = Path(sys.argv[1]).resolve()
    if not bundle_root.is_dir():
        print(f"Not a directory: {bundle_root}")
        sys.exit(2)

    errors, warnings = [], []
    md_files = sorted(bundle_root.rglob("*.md"))
    if not md_files:
        errors.append("Bundle contains no .md files")

    for path in md_files:
        if path.name == "index.md":
            check_index(path, bundle_root, errors, warnings)
        elif path.name == "log.md":
            check_log(path, bundle_root, errors, warnings)
        else:
            check_concept(path, bundle_root, errors, warnings)

    print(f"Checked {len(md_files)} markdown file(s) under {bundle_root}\n")

    if warnings:
        print(f"WARNINGS ({len(warnings)}) — soft guidance, not conformance blockers:")
        for w in warnings:
            print(f"  - {w}")
        print()

    if errors:
        print(f"ERRORS ({len(errors)}) — bundle is NOT conformant with OKF v0.1:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("Bundle is conformant with OKF v0.1.")
    sys.exit(0)


if __name__ == "__main__":
    main()
