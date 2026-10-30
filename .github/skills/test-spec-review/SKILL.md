---
name: test-spec-review
description: 'Review test-spec.md (or any test specification) for completeness, correctness, and traceability against requirements, decision log, acceptance criteria, and low-level design in the Digital Twin Assembly-Line Simulation project. Use when reviewing a test spec, checking test coverage, validating test cases, or performing a traceability review. Trigger phrases: review test spec, check test coverage, validate test cases, traceability review.'
---

# Test Spec Review

Read-only review workflow that checks a test specification against the project's requirements, decision log, acceptance criteria, user stories, and low-level design (LLD), and reports gaps, ambiguities, and inaccuracies without editing anything.

## When to Use
- Reviewing `test-spec.md` (or any test spec) before it is approved for implementation.
- Checking whether every FR/NFR/Decision/AC/US item has traceable test coverage.
- Validating that expected test results match the authoritative rules in the requirements decision log.

## Procedure

1. **Read sources.** Read the test spec under review in full, along with `digital-twin-assembly-line-requirements.md` (especially Section 9, the Decision Log), `high-level-design.md`, `low-level-design.md`, and `user-stories.md`.
2. **Run the traceability check.** Execute [scripts/check_traceability.py](./scripts/check_traceability.py) to automatically extract every `FR-NN`, `NFR-NN`, `D-NN`, `AC-NN`, and `US-NN` ID from the requirements/user-stories docs and cross-reference it against the test spec's IDs and its Traceability Summary table. Review the reported gaps — items with zero or only implicit coverage.
   ```
   python .github/skills/test-spec-review/scripts/check_traceability.py
   ```
   Run with `--help` to see options for passing non-default file paths.
3. **Check correctness against the decision log.** For every test case whose expected result depends on a Decision Log entry (batching, horizon boundary, event ordering, bottleneck tie-break, etc.), confirm it matches the rule — use the condensed lookup in [references/decision-log-rules.md](./references/decision-log-rules.md) rather than re-deriving each rule from scratch.
4. **Apply the full review checklist.** Work through determinism, boundary coverage, independence (pure-function/no-I/O), and missing-category checks described in [references/review-checklist.md](./references/review-checklist.md).
5. **Flag inconsistencies.** Look for duplicate test IDs, traceability-table entries that don't match the per-section "Traces to" lines, and contradictory expected results.
6. **Report findings.** Fill in [assets/findings-report-template.md](./assets/findings-report-template.md) with the verdict, gaps, correctness issues, missing categories, nitpicks, and recommended next actions. Do not rewrite the spec yourself.

## Constraints
- Do not modify the test spec, requirements, design docs, or any implementation/test code — this is a read-only review.
- Do not approve a spec as complete if any FR/NFR/AC/Decision Log item lacks at least one traceable test case.
- Script output is a starting point, not a substitute for judgment: a listed ID can still be "covered" only in spirit (e.g. implicit coverage) — note that distinction in the report rather than treating script silence as a full pass.

## Output Format
Respond using the structure in [assets/findings-report-template.md](./assets/findings-report-template.md):
1. Summary verdict (Pass / Pass with minor gaps / Needs rework)
2. Coverage gaps
3. Correctness issues
4. Missing categories
5. Minor/nitpick issues
6. Recommended next actions
