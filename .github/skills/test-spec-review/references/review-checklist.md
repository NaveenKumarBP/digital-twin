# Test Spec Review Checklist

Detailed checks to apply to every test case, beyond the automated traceability
scan in [../scripts/check_traceability.py](../scripts/check_traceability.py).

## 1. Correctness

- Does the expected result match the authoritative rule in the requirements or
  [decision-log-rules.md](./decision-log-rules.md) (e.g. D-05 strict horizon
  exclusion, D-06 event ordering, D-07 bottleneck tie-break, D-04 batch
  semantics)?
- For acceptance-criteria tests (AC-01..AC-09), is the expected number/value
  hand-calculable from the scenario as stated, and does it match the AC text
  exactly?
- Do error-code assertions match a single canonical code per validation rule
  (not two possible codes left ambiguous, e.g. "`X` or `Y` — define one")?

## 2. Determinism

- Can the expected result be computed by hand, or is it vague ("should work
  correctly", "should behave reasonably")?
- Do comparisons use exact values (`=== 10`) rather than fuzzy/unstated
  tolerances, except where floating-point rounding is explicitly allowed
  (NFR-05, 2-decimal display rounding)?

## 3. Boundary coverage

Confirm these edge cases are present wherever the design calls them out as
risk areas:

- Exactly-at-horizon vs. just-before-horizon events (D-05).
- Zero values: zero cycle time, zero buffer capacity, zero batch size, zero
  downtime duration (all should be *rejected*, not silently accepted).
- Negative values: negative buffer capacity, negative downtime duration,
  negative WIP count.
- Ties: equal `busyMin` for bottleneck selection, simultaneous same-type
  events (D-06).
- Division-by-zero guards (e.g. utilization when `scheduledDowntimeMin ===
  horizon`).

## 4. Independence (pure-function / no I/O)

- Do unit-level test cases avoid requiring network/DB/UI access, per the
  LLD's "pure function" testability rule?
- Are integration/API-level tests clearly separated from unit tests, so a
  reader can tell which layer each test exercises?

## 5. Missing test categories

Check whether the LLD/requirements imply categories that aren't represented:

- Security/OWASP cases (injection, error-envelope content, no
  credentials/secrets in exports).
- Append-only persistence guarantees (no in-place mutation of
  `line_snapshot_json` / `run_input_json` after a run is created).
- Error envelope shape (consistent `field`/`code`/`message`, no stack traces
  or internal paths leaked).
- Performance targets (NFR-03/D-10 scale and timing targets).
- Reproducibility (NFR-01: identical inputs + seed → identical results).

## 6. Internal consistency

- Duplicate test IDs across sections.
- A test ID appearing in the Traceability Summary table but not in any
  per-section table (or vice versa).
- Two test cases whose expected results for the same scenario contradict each
  other.
