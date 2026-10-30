#!/usr/bin/env python3
"""Cross-reference requirement/decision/acceptance-criteria/user-story IDs against a test spec.

Extracts every FR-NN, NFR-NN, D-NN, AC-NN, and US-NN identifier that is *defined*
in the requirements and user-stories documents, then checks whether each one is
referenced somewhere in the test spec (either in a "Traces to:" line, a per-row
reference, or the Traceability Summary table). Reports IDs with zero references
so a reviewer can focus on real gaps instead of manually scanning every table.

This is a coverage-presence check, not a correctness check: an ID being
referenced does not mean the test's expected result is actually right.
"""
import argparse
import re
import sys
from pathlib import Path

# Matches defining lines such as "- **FR-05:**", "| D-04 |", "**AC-01:**"
ID_DEFINITION_PATTERN = re.compile(
    r"\b(FR|NFR|D|AC|US)-(\d+)\b"
)

# IDs are only counted as "defined" when they appear in a requirements-style
# document; this heuristic looks for the ID immediately followed by a colon
# or table-cell boundary, which is how definitions are formatted in this repo.
DEFINITION_CONTEXT_PATTERN = re.compile(
    r"(\*\*(FR|NFR|D|AC|US)-(\d+)\*\*\s*:?)|(\|\s*(FR|NFR|D|AC|US)-(\d+)\s*\|)"
)


def find_defined_ids(text: str) -> set[str]:
    defined = set()
    for match in DEFINITION_CONTEXT_PATTERN.finditer(text):
        prefix = match.group(2) or match.group(5)
        number = match.group(3) or match.group(6)
        defined.add(f"{prefix}-{number}")
    return defined


def find_referenced_ids(text: str) -> set[str]:
    referenced = set()
    for match in ID_DEFINITION_PATTERN.finditer(text):
        referenced.add(f"{match.group(1)}-{match.group(2)}")
    return referenced


def find_test_ids(text: str) -> set[str]:
    return {f"TS-{m.group(1)}" for m in re.finditer(r"\bTS-(\d+)\b", text)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--requirements",
        default="digital-twin-assembly-line-requirements.md",
        help="Path to the requirements doc (defines FR/NFR/D/AC IDs).",
    )
    parser.add_argument(
        "--user-stories",
        default="user-stories.md",
        help="Path to the user-stories doc (defines US IDs).",
    )
    parser.add_argument(
        "--test-spec",
        default="test-spec.md",
        help="Path to the test spec being reviewed.",
    )
    args = parser.parse_args()

    req_path = Path(args.requirements)
    stories_path = Path(args.user_stories)
    spec_path = Path(args.test_spec)

    for path in (req_path, stories_path, spec_path):
        if not path.exists():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            return 2

    req_text = req_path.read_text(encoding="utf-8")
    stories_text = stories_path.read_text(encoding="utf-8")
    spec_text = spec_path.read_text(encoding="utf-8")

    defined_ids = find_defined_ids(req_text) | find_defined_ids(stories_text)
    spec_referenced_ids = find_referenced_ids(spec_text)
    test_ids_in_spec = find_test_ids(spec_text)

    covered = sorted(defined_ids & spec_referenced_ids, key=sort_key)
    gaps = sorted(defined_ids - spec_referenced_ids, key=sort_key)

    print(f"Requirement/decision/AC/story IDs defined: {len(defined_ids)}")
    print(f"Test IDs found in spec: {len(test_ids_in_spec)}")
    print(f"IDs with at least one reference in the spec: {len(covered)}")
    print()

    if gaps:
        print("COVERAGE GAPS (no reference found anywhere in the test spec):")
        for item in gaps:
            print(f"  - {item}")
    else:
        print("No coverage gaps found: every defined ID is referenced at least once.")

    print()
    print("Reminder: this script only checks that an ID is *mentioned* somewhere in")
    print("the spec. Still manually verify each reference maps to a real, correct")
    print("test case rather than an incidental mention.")

    return 1 if gaps else 0


def sort_key(item: str):
    prefix, number = item.split("-")
    return (prefix, int(number))


if __name__ == "__main__":
    raise SystemExit(main())
