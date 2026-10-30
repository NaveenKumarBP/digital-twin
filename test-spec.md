# Digital Twin Assembly-Line Simulation — Test Spec

**Based on:** `low-level-design.md`, `digital-twin-assembly-line-requirements.md` (v0.2), `high-level-design.md`, `user-stories.md`. Every test case traces to a requirement (FR/NFR), decision (D-NN), acceptance criterion (AC-NN), or user story (US-NN) so coverage gaps are visible. Test IDs are stable (`TS-NNN`) for traceability.

## 1. Scope and Test Levels

| Level | Target | Tooling notes |
| --- | --- | --- |
| Unit | Pure modules with no I/O: `validateLine`/`validateRunInput`, `SimulationEngine.runSimulation`, `MetricsCalculator`, `ComparisonService.compare` | No network/DB/clock dependency; fully deterministic (LLD §3 "Key design rule") |
| Integration | API controllers + repository against a real (test) database | Asserts HTTP status, error envelope shape, append-only persistence |
| Boundary/property | Event-ordering (D-06) and horizon-boundary (D-05) edge cases | Hand-calculable fixtures per LLD §6, HLD §11 |
| Performance | Simulation engine at scale | NFR-03 targets: 20 stations, 100,000-minute horizon, ≤ 5s |
| Security | Input validation, error envelope, export content | OWASP mapping, LLD §9 |

All unit-level test cases below operate directly on the domain types in LLD §4 and call the pure functions in LLD §5/§6.5/§8.1 — no HTTP or persistence layer involved.

## 2. Validation Module (`validateLine`, `validateRunInput`)

Traces to: FR-02, FR-03, FR-04, FR-05, FR-07, FR-08, NFR-02, AC-07, US-01..US-05.

| Test ID | Given | When | Then | Error code |
| --- | --- | --- | --- | --- |
| TS-001 | Station with `cycleTimeMin = 0` | `validateLine` runs | Returns an error for `stations[i].cycleTimeMin` | `CYCLE_TIME_NOT_POSITIVE` |
| TS-002 | Station with `cycleTimeMin = -3` | `validateLine` runs | Returns an error for `stations[i].cycleTimeMin` | `CYCLE_TIME_NOT_POSITIVE` |
| TS-003 | Station with `bufferCapacityOut = -1` | `validateLine` runs | Returns an error for `stations[i].bufferCapacityOut` | `BUFFER_CAPACITY_NEGATIVE` |
| TS-004 | Station with `bufferCapacityOut = 0` | `validateLine` runs | No error (zero is valid, direct transfer) | — |
| TS-005 | Station with `bufferCapacityOut = 2.5` (non-integer) | `validateLine` runs | Returns an error | `BUFFER_CAPACITY_NEGATIVE` or `FIELD_NOT_NUMERIC` (define one canonical code) |
| TS-006 | Downtime entry with `durationMin = 0` | `validateLine` runs | Returns an error | `DOWNTIME_DURATION_NOT_POSITIVE` |
| TS-007 | Downtime entry with `durationMin = -5` | `validateLine` runs | Returns an error | `DOWNTIME_DURATION_NOT_POSITIVE` |
| TS-008 | Downtime `startOffsetMin` beyond `runInput.horizonMin` | `validateRunInput` runs | Returns an error | `DOWNTIME_OUTSIDE_HORIZON` |
| TS-009 | Station with `batchSize = 0` | `validateLine` runs | Returns an error | `BATCH_SIZE_INVALID` |
| TS-010 | Station with `batchSize = 1.5` | `validateLine` runs | Returns an error | `BATCH_SIZE_INVALID` |
| TS-011 | Station with `batchSize = 1` | `validateLine` runs | No error | — |
| TS-012 | `runInput.horizonMin = 0` | `validateRunInput` runs | Returns an error | `HORIZON_NOT_POSITIVE` |
| TS-013 | `initialWipByStation` has negative count | `validateRunInput` runs | Returns an error | `INITIAL_WIP_INVALID` |
| TS-014 | `initialWipByStation` references a station id not in the line | `validateRunInput` runs | Returns an error | `INITIAL_WIP_INVALID` |
| TS-015 | Two stations share the same `id` | `validateLine` runs | Returns an error | `STATION_ID_DUPLICATE` |
| TS-016 | Line with cycle time 0, buffer -1, downtime duration -5, and batch size 0 simultaneously (AC-07 compound case) | `validateLine` runs | Returns **all four** errors in one call, not just the first | multiple |
| TS-017 | Numeric field is `NaN`/`Infinity`/non-numeric string | `validateLine`/`validateRunInput` runs | Returns an error, never throws an unhandled exception | `FIELD_NOT_NUMERIC` |
| TS-018 | Fully valid line and run input | Both validators run | Returns an empty error list | — |

## 3. Simulation Engine (`runSimulation`)

Traces to: FR-05..FR-09, FR-11, D-01..D-06, NFR-01, AC-01..AC-06, US-06..US-09.

### 3.1 Acceptance-criteria scenarios (hand-calculable)

| Test ID | Scenario | Expected result | AC |
| --- | --- | --- | --- |
| TS-020 | Single station, `cycleTimeMin = 2`, no downtime, `horizonMin = 20` | `totalOutput === 10` (unit completing exactly at t=20 excluded) | AC-01 |
| TS-021 | Two-station serial line, unlimited buffers, no downtime/batching, station 1 `cycleTimeMin = 5` | Baseline `totalOutput` recorded | AC-02 (baseline) |
| TS-022 | Same line as TS-021 but station 1 `cycleTimeMin = 3`, all else unchanged, same horizon | `totalOutput >= ` TS-021's output (reducing upstream cycle time never reduces output) | AC-02 |
| TS-023 | Single station, add a 10-minute scheduled downtime | Station's `scheduledDowntimeMin === 10` exactly, and `totalOutput` ≤ the no-downtime run's output over the same horizon | AC-03 |
| TS-024 | Zero-capacity buffer between a fast upstream (`cycleTimeMin=1`) and slow downstream (`cycleTimeMin=5`) station | Upstream accrues `blockedMin > 0`; downstream accrues `starvedMin > 0`; `blockedMin + busyMin + starvedMin + scheduledDowntimeMin ≈ horizonMin` for each station (durations sum consistently) | AC-04 |
| TS-025 | Station with `batchSize = 5`, `cycleTimeMin = 1`, downstream buffer unlimited | No units appear in downstream buffer until 5th completion; batch arrives as one `ARRIVAL` event | AC-05 |
| TS-026 | Same as TS-025 but horizon ends with a partial batch (e.g. 3 of 5 units completed) at the originating station | Partial batch counted in `wipAtEnd`/`wipSeries`, **not** in `totalOutput` | AC-05, D-04 |
| TS-027 | Deterministic config run twice with identical inputs (and identical seed, once stochastic extension exists) | Two `RunResult` objects are deeply equal (byte-identical JSON) | AC-06, NFR-01, FR-11 |

### 3.2 Boundary and ordering rules (D-05, D-06)

| Test ID | Scenario | Expected result |
| --- | --- | --- |
| TS-030 | Station completion event scheduled at exactly `tMin === horizonMin` | Event is not executed; unit not counted in `totalOutput`; not present as a completed unit in `wipSeries` after horizon | D-05 |
| TS-031 | Event scheduled at `horizonMin - epsilon` (just before horizon) | Event **is** executed | D-05 |
| TS-032 | At a single timestamp `t`, a `DOWNTIME_END`, a `COMPLETION`, a `DOWNTIME_START`, and an `ARRIVAL` are all pending for different stations | Engine processes them in the fixed order: `DOWNTIME_END` → `COMPLETION` → `DOWNTIME_START` → `ARRIVAL`, verified via recorded event trace | D-06 |
| TS-033 | Two events of the **same** type tied at the same `tMin` (e.g. two `ARRIVAL`s at different stations) | Processed in a stable, deterministic order across repeated runs (insertion-sequence tie-break), not dependent on object identity/hash order | D-06, NFR-01 |
| TS-034 | Downtime start occurs mid-cycle (station already processing a unit) | The in-process unit's completion is deferred to after the downtime ends, not lost or double-counted | D-02, D-06 |

### 3.3 Initial WIP (D-03)

| Test ID | Scenario | Expected result |
| --- | --- | --- |
| TS-040 | Station with `initialWipByStation[id] = 2`, `horizonMin` large enough for both to finish | Both units counted in `wipSeries` from `t=0` and in `totalOutput` once each completes before horizon end | D-03 |
| TS-041 | Station with initial WIP whose completion would land exactly at/after horizon end | Unit remains WIP at horizon end; not counted in `totalOutput` | D-03, D-05 |

### 3.4 Downtime extension point

| Test ID | Scenario | Expected result |
| --- | --- | --- |
| TS-045 | `ScheduledDowntimeProvider` given a repeating downtime (`repeatEveryMin` set) and a horizon spanning multiple repeats | Generates one `DOWNTIME_START`/`DOWNTIME_END` pair per repeat occurring within the horizon, none beyond it | FR-07, D-02 |
| TS-046 | `SimulationEngine` depends only on the `DowntimeProvider` interface | A test double/mock provider can be substituted without modifying engine code (verifies isolation, no behavioral assertion needed beyond compile/substitution) | HLD §5 isolation requirement, D-02 |

## 4. Metrics Calculator

Traces to: FR-13..FR-16, D-07, NFR-05, US-11..US-14.

| Test ID | Given | Expected result |
| --- | --- | --- |
| TS-050 | `StationState` fixture with known `busyMin`, `scheduledDowntimeMin` | `utilization === busyMin / (horizon - scheduledDowntimeMin)` | D-07 |
| TS-051 | `scheduledDowntimeMin === horizon` (available time = 0) | `utilization === 0` (no division by zero / NaN) | D-07 |
| TS-052 | Two stations, station A has greater `busyMin` than station B | `selectBottleneck` returns station A's id | D-07 |
| TS-053 | Two stations tied on `busyMin`, station A has greater `blockedMin` | `selectBottleneck` returns station A's id (tie-break) | D-07 |
| TS-054 | Raw internal busy time `12.345678` minutes | Displayed/returned `StationMetrics.busyMin` rounds to `12.35`, but internal accumulation prior to rounding is not truncated mid-calculation | NFR-05 |
| TS-055 | `totalOutput = 10`, `horizonMin = 20` | `throughputPerMin === 0.5` | FR-13 |

## 5. Comparison Service

Traces to: FR-17, AC-08, US-15, US-16.

| Test ID | Given | Expected result |
| --- | --- | --- |
| TS-060 | Two `RunConfig`s differing only in one station's `cycleTimeMin` | `inputDiffs` contains exactly one entry for that field, with correct `valueA`/`valueB` | AC-08 |
| TS-061 | Two runs with different `totalOutput`, `throughputPerMin`, `wipAtEnd`, utilization, and bottleneck | `metricDiffs` reports all five differences correctly, `bottleneckChanged === true` when ids differ | AC-08 |
| TS-062 | Two runs with identical `horizonMin` and `initialWipByStation` | `warnings` is empty | US-16 |
| TS-063 | Two runs with different `horizonMin` | `warnings` contains a message naming both horizon values | FR-17, US-16 |
| TS-064 | Two runs with different `initialWipByStation` for at least one station | `warnings` contains a message identifying the mismatched station(s) | FR-17, US-16 |
| TS-065 | `compare` called with no network/DB access (pure function test) | Produces correct `ComparisonResult` from in-memory fixtures alone | NFR-06 |

## 6. API / Integration Tests

Traces to: LLD §8, FR-01..FR-19, NFR-02.

| Test ID | Endpoint | Scenario | Expected result |
| --- | --- | --- | --- |
| TS-070 | `POST /lines` | Valid line payload | `201` with created `Line` including generated `id` | FR-01 |
| TS-071 | `POST /lines` | Invalid payload (e.g. `cycleTimeMin = 0`) | `400` with error envelope containing `CYCLE_TIME_NOT_POSITIVE` and the offending field path; no stack trace/internal path in response | NFR-02, AC-07 |
| TS-072 | `PUT /lines/{id}` | Valid update | `200` with updated `Line`; prior `run` rows for this line are unaffected (line edits don't touch historical runs) | FR-01, LLD §7 |
| TS-073 | `GET /lines/{id}` | Unknown id | `404` | — |
| TS-074 | `POST /lines/{id}/runs` | Valid `runInput`, no `baselineRunId` | `201` with `runConfig.baselineRunId` absent/null and a computed `result` | FR-05, FR-09 |
| TS-075 | `POST /lines/{id}/runs` | Valid `runInput` with `baselineRunId` set, one override field | `201`; new run's `baselineRunId` set; original baseline's `line_snapshot_json`/`run_input_json` unchanged in storage | FR-10 |
| TS-076 | `POST /lines/{id}/runs` | Invalid `runInput` (e.g. `horizonMin = 0`) | `400` with error envelope; no run row created | NFR-02, AC-07 |
| TS-077 | `POST /lines/{id}/runs` | `baselineRunId` references a run belonging to a different line | `409` | LLD §8 |
| TS-078 | `GET /runs/{id}` | Known run id | `200` with full `runConfig` and `result` | FR-12, US-10 |
| TS-079 | `GET /runs?lineId=` | Line with 3 runs | `200` with array of exactly those 3 `RunConfig`s | — |
| TS-080 | `GET /runs/compare?a=&b=` | Two valid run ids | `200` with `ComparisonResult` matching TS-060/TS-061 expectations | FR-17, AC-08 |
| TS-081 | `GET /runs/compare?a=&b=` | One run id unknown | `404` | — |
| TS-082 | `GET /runs/{id}/export` | Known run id | `200`, `Content-Type: application/json`, body contains line configuration, horizon, initial WIP, model version, seed (if any), and summary results | FR-19, AC-09, D-09 |
| TS-083 | `GET /runs/{id}/export` | Export body inspected for sensitive content | No credentials, tokens, or env data present | LLD §9 |

## 7. Persistence / Repository Tests

Traces to: LLD §7, FR-10, FR-12, NFR-01.

| Test ID | Scenario | Expected result |
| --- | --- | --- |
| TS-090 | Insert a `run` row, then attempt to update `line_snapshot_json` or `run_input_json` via the repository API | Repository layer rejects/has no method to perform the update (append-only enforced) | FR-10, FR-12 |
| TS-091 | Insert a line, create two runs against it, update the line | `run.line_snapshot_json` for both prior runs remains the original snapshot, not the updated line | FR-10 |
| TS-092 | Query `run` by `baseline_run_id` | Returns exactly the scenario runs created from that baseline | FR-10 |
| TS-093 | Insert/query round trip for `run_result` | All `StationMetrics` and `wipSeries` fields survive JSON round-trip without precision loss beyond the documented rounding (NFR-05) | NFR-05 |

## 8. Performance Tests

Traces to: NFR-03, D-10.

| Test ID | Scenario | Expected result |
| --- | --- | --- |
| TS-100 | 20 stations, 100,000-minute horizon, representative downtime/batch config | `runSimulation` completes in ≤ 5 seconds on a typical analyst workstation | NFR-03 |
| TS-101 | Same config, repeated 3 times | Wall-clock time variance stays within an agreed tolerance (no pathological GC/heap growth) | NFR-03 |
| TS-102 | 10 scenarios created against one line sequentially | Each run creation + execution stays within the per-run 5s target | NFR-03, D-10 |

## 9. Security Tests

Traces to: LLD §9 (OWASP mapping), NFR-02.

| Test ID | Scenario | Expected result |
| --- | --- | --- |
| TS-110 | Submit a line/station `id` or `name` containing SQL-meta characters (`'; DROP TABLE run;--`) | Value is stored/queried safely via parameterized queries; no injection occurs; value round-trips as plain data | OWASP A03 |
| TS-111 | Trigger a validation failure and inspect the HTTP response body | Response contains only `field`/`code`/`message`; no stack trace, file path, or internal identifier | OWASP A09, NFR-02 |
| TS-112 | Trigger an unexpected server error (e.g. malformed JSON body) | `400`/`500` response contains a generic message; detailed error is only in server-side logs | OWASP A09 |
| TS-113 | Export a run and inspect the JSON body | No environment variables, credentials, or tokens present, only documented fields (line config, horizon, initial WIP, model version, seed, results) | AC-09, LLD §9 |

## 10. Traceability Summary

| Requirement/Decision/AC | Test IDs |
| --- | --- |
| FR-01..FR-04, AC-07 | TS-001..TS-018, TS-070..TS-073 |
| FR-05, D-03 | TS-012..TS-014, TS-040, TS-041, TS-074 |
| FR-06, D-01 | TS-020..TS-022 |
| FR-07, D-02 | TS-006..TS-008, TS-023, TS-034, TS-045, TS-046 |
| FR-08, D-04 | TS-009..TS-011, TS-025, TS-026 |
| FR-09, D-05, D-06 | TS-030..TS-034 |
| FR-10 | TS-075, TS-090..TS-092 |
| FR-11, NFR-01, AC-06 | TS-027, TS-033 |
| FR-12 | TS-078, TS-090 |
| FR-13..FR-16, D-07 | TS-050..TS-055 |
| FR-17, AC-08 | TS-060..TS-065, TS-080, TS-081 |
| FR-18, D-08 | covered implicitly by unit fields in TS-055, TS-082 (units always minutes/whole units; no dedicated negative test since conversion is unsupported) |
| FR-19, D-09, AC-09 | TS-082, TS-083, TS-113 |
| NFR-01 | TS-027, TS-033, TS-090..TS-092 |
| NFR-02 | TS-001..TS-018, TS-071, TS-076, TS-111 |
| NFR-03, D-10 | TS-100..TS-102 |
| NFR-05 | TS-054, TS-093 |
| NFR-06 | TS-065, and the "pure function, no I/O" framing of every §2–§5 test |
| Security (OWASP) | TS-110..TS-113 |

## 11. Out of Scope for This Test Spec

- Model validation against historical production data (HLD §11, requirements §11) — a stakeholder activity, not an automated test.
- Authentication/authorization tests — deferred until an auth model is selected (LLD §11 open item).
- Tests for the future stochastic downtime model — only the extension point (TS-045, TS-046) is covered until that feature is designed.
