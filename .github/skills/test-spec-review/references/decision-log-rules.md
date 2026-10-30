# Decision Log — Condensed Correctness Rules

Quick-reference for checking whether a test case's **expected result** matches the
authoritative rule, without re-reading all of Section 9 of
`digital-twin-assembly-line-requirements.md` every time. Always confirm against
the source document if a rule seems to have changed.

| ID | Rule (what a correct test must assert) | Status |
| --- | --- | --- |
| D-01 | Line topology is strictly serial; cycle times are fixed, not sampled from a distribution. | Proposed |
| D-02 | Downtime is scheduled-only (start offset + duration, one-time or repeating). No MTBF/MTTR stochastic downtime in this release. | Proposed |
| D-03 | Initial WIP counts as WIP from `t=0`; counts as completed output only if it finishes **before** the horizon ends. No separate startup/shutdown phase. | Proposed |
| D-04 | Batch size governs transfer grouping only — it never changes per-unit cycle time. A partial batch remaining at horizon end is WIP, not output. | Proposed |
| D-05 | Strict horizon exclusion: a completion event at exactly `t === horizonMin` is **not** counted and is **not** executed. | Proposed |
| D-06 | Fixed tie-break order for simultaneous events: (1) `DOWNTIME_END`, (2) station completion/transfer, (3) `DOWNTIME_START`, (4) `ARRIVAL`. Same-type ties use a stable, deterministic (insertion-order) tie-break — never object identity/hash order. | Proposed |
| D-07 | Utilization denominator excludes scheduled downtime (`busyMin / (horizon - scheduledDowntimeMin)`), guarding against divide-by-zero when downtime equals the full horizon. Bottleneck = greatest `busyMin`; ties broken by greater combined `blockedMin`. Utilization alone must never be the bottleneck signal. | Proposed |
| D-08 | Units are fixed: minutes for time, whole integers for quantity. No unit conversion support — a test asserting conversion logic is out of scope. | Proposed |
| D-09 | Export format is JSON only; CSV is out of scope for this release. | Proposed |
| D-10 | Provisional performance targets: 20 stations, 100,000-minute horizon, 10 scenarios/line, ≤ 5s per run. | Proposed |
| D-11 | Quality loss, scrap, rework, changeovers, labor constraints, material shortages are out of scope — no test should assert behavior for these. | Confirmed |
| D-12 | Browser UI + server-side simulation service; framework/hosting/deployment are out of scope for requirements-level tests (see `high-level-design.md`). | Proposed |

## How to use this table

1. Find the test's expected-result cell.
2. Match it against the row for the Decision ID the test claims to cover.
3. If the wording diverges (e.g. a test allows a boundary event to execute, or
   computes utilization without excluding downtime), flag it as a
   **correctness issue**, citing the Decision ID.
4. Decisions marked *Proposed* (not yet *Confirmed*) are still the working
   model for testing per NFR-08 — do not flag a test as wrong just because the
   decision is unconfirmed; only flag tests that contradict the stated rule.
