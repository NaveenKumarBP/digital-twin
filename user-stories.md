# Digital Twin Assembly-Line Simulation — User Stories

**Based on:** `digital-twin-assembly-line-requirements.md` (v0.2) and `high-level-design.md`. Each story references the functional/non-functional requirements and acceptance criteria it implements. Story IDs are stable (`US-NN`) for traceability.

## Epic A — Line Configuration

### US-01: Define a line's stations
**As a** manufacturing engineer, **I want** to define an ordered list of stations with names and cycle times, **so that** I can model my assembly line's basic layout.
- **Given** a new line, **when** I add stations in order with a unique name/ID and a cycle time greater than zero, **then** the line is saved with that station order.
- **Given** a station cycle time of 0 or negative, **when** I try to save, **then** the system rejects it with a field-level message identifying that station.
- Traces to: FR-01, FR-02, AC-07.

### US-02: Configure buffers between stations
**As a** manufacturing engineer, **I want** to set a buffer capacity between adjacent stations, including zero, **so that** I can represent direct transfer or limited in-process storage.
- **Given** two adjacent stations, **when** I set a non-negative integer buffer capacity between them, **then** the line stores that capacity for use in simulation.
- **Given** a negative buffer capacity, **when** I try to save, **then** the system rejects it with a validation message.
- Traces to: FR-03, AC-07.

### US-03: Configure scheduled downtime per station
**As a** production planner, **I want** to configure scheduled downtime intervals for a station, **so that** I can see their effect on output and utilization.
- **Given** a station, **when** I add a scheduled downtime with a start offset and duration (one-time or repeating) within the horizon, **then** the schedule is saved and visible in the run configuration.
- **Given** a downtime duration of 0 or negative, **when** I try to save, **then** the system rejects it with a validation message.
- Traces to: FR-07, D-02, AC-07.

### US-04: Configure transfer batch size
**As a** manufacturing engineer, **I want** to set a transfer batch size at a station's output, **so that** I can model units being released downstream in groups.
- **Given** a station, **when** I set an integer batch size of 1 or more, **then** the simulation releases completed units downstream only in groups of that size (per-unit cycle time is unaffected).
- **Given** a batch size of 0, **when** I try to save, **then** the system rejects it with a validation message.
- Traces to: FR-08, D-04, AC-05, AC-07.

### US-05: Validate a line configuration before running
**As an** operations analyst, **I want** the system to validate my full line configuration before I run it, **so that** I don't waste time on invalid setups.
- **Given** a line with any invalid field (cycle time, buffer capacity, downtime duration, batch size, horizon, initial WIP), **when** I attempt to run it, **then** the system blocks the run and lists every invalid field with a specific message.
- **Given** a fully valid line, **when** I attempt to run it, **then** validation passes and the run proceeds.
- Traces to: FR-04, NFR-02, AC-07.

## Epic B — Running Simulations

### US-06: Set simulation horizon and initial WIP
**As a** manufacturing engineer, **I want** to set the simulation horizon and starting in-process units per station, **so that** I can model realistic start conditions.
- **Given** a line, **when** I set a horizon greater than zero and a non-negative initial WIP count per station, **then** the run configuration stores these values and initial WIP units are included in WIP from time zero.
- Traces to: FR-05, D-03.

### US-07: Run a baseline simulation
**As a** manufacturing engineer, **I want** to run a baseline simulation of my line, **so that** I can see current expected performance.
- **Given** a valid line configuration and horizon, **when** I run the simulation, **then** the system reports total completed units, throughput rate, WIP over time, station utilization, downtime impact, and the bottleneck station.
- **Given** a single station with a 2-minute cycle time, no downtime, and a 20-minute horizon, **when** I run it, **then** total output is exactly 10 units.
- Traces to: FR-13..FR-16, AC-01.

### US-08: Run a scenario without altering the baseline
**As a** production planner, **I want** to change one or more parameters and run a scenario, **so that** I can compare it to the baseline without losing the original configuration.
- **Given** a saved baseline, **when** I change a parameter and run it as a scenario, **then** the baseline configuration record is unchanged and the scenario run is stored separately.
- Traces to: FR-10.

### US-09: Reproduce a run deterministically
**As an** operations analyst, **I want** identical inputs (and seed, when applicable) to always produce identical results, **so that** I can trust and re-check simulation outputs.
- **Given** a completed run's full input snapshot and seed, **when** I re-run it unchanged, **then** the summary results are identical.
- Traces to: FR-11, NFR-01, AC-06.

### US-10: Retain run inputs and model version
**As an** operations analyst, **I want** every completed run to retain its inputs and model version, **so that** I can audit or reproduce results later.
- **Given** a completed run, **when** I view its record, **then** I see the full input snapshot and the model version that produced it.
- Traces to: FR-12, NFR-01.

## Epic C — Reviewing Results

### US-11: Review throughput and output
**As a** production planner, **I want** to see throughput rate and total output for a run, **so that** I can assess expected production performance.
- **Given** a completed run, **when** I open its results, **then** throughput rate and total output are shown with their time/quantity units.
- Traces to: FR-13, FR-18.

### US-12: Review utilization, downtime, and blocking/starvation
**As a** manufacturing engineer, **I want** to see station utilization, downtime, and blocked/starved time, **so that** I can understand where capacity is lost.
- **Given** a completed run, **when** I open its results, **then** each station shows busy time, scheduled downtime time, blocked time, and starved time, with utilization computed as busy time divided by (horizon minus scheduled downtime).
- **Given** a station with a zero-capacity downstream buffer, **when** the downstream station is slower, **then** the upstream station's blocked time and the downstream station's starved time are both reported.
- Traces to: FR-14, D-07, AC-04.

### US-13: Review WIP over time
**As an** operations analyst, **I want** to see WIP over time and at run end, **so that** I can understand in-process inventory levels.
- **Given** a completed run, **when** I open its results, **then** a WIP time series and an end-of-run WIP value are shown.
- Traces to: FR-15.

### US-14: Identify the bottleneck station
**As a** production planner, **I want** the system to identify the bottleneck station, **so that** I know where to focus improvement efforts.
- **Given** a completed run, **when** I open its results, **then** the station with the greatest busy time is flagged as the bottleneck, with blocked time used to break ties.
- Traces to: FR-16, D-07.

## Epic D — Comparing Scenarios

### US-15: Compare a scenario against the baseline
**As a** production planner, **I want** to compare a scenario run against the baseline, **so that** I can see the effect of my parameter changes.
- **Given** two completed runs, **when** I select them for comparison, **then** the system lists every differing input field and the resulting change in throughput, output, WIP, utilization, and bottleneck station.
- Traces to: FR-17, AC-08.

### US-16: Be warned about non-comparable runs
**As an** operations analyst, **I want** to be warned when two runs differ in horizon, units, or initial conditions, **so that** I don't draw invalid conclusions from a comparison.
- **Given** two runs with different horizons or initial WIP, **when** I compare them, **then** the system displays a visible warning identifying the mismatched fields alongside the comparison.
- Traces to: FR-17, Risks (Misleading comparisons).

## Epic E — Exporting and Auditing

### US-17: Export a run's inputs and results
**As a** manufacturing engineer, **I want** to export a run's inputs and summary results as JSON, **so that** I can share or archive it outside the application.
- **Given** a completed run, **when** I export it, **then** a JSON file is produced containing the line configuration, horizon, initial WIP, model version, seed (if any), and summary results.
- Traces to: FR-19, D-09, AC-09.

## Traceability Matrix

| Requirement | User Stories | Design Area | Verification |
| --- | --- | --- | --- |
| FR-01, FR-02 | US-01 | Line Configuration Editor | AC-07 |
| FR-03 | US-02 | Line Configuration Editor | AC-07 |
| FR-04, NFR-02 | US-05 | Validation Service | AC-07 |
| FR-05, D-03 | US-06 | Run Configuration Manager | AC-01 |
| FR-06, D-01 | US-01, US-07 | Simulation Engine | AC-01, AC-02 |
| FR-07, D-02 | US-03 | Simulation Engine | AC-03 |
| FR-08, D-04 | US-04 | Simulation Engine | AC-05 |
| FR-09, D-05, D-06 | US-07 | Simulation Engine | AC-01, AC-04 |
| FR-10 | US-08 | Run Configuration Manager | — |
| FR-11, NFR-01 | US-09 | Simulation Engine | AC-06 |
| FR-12, NFR-01 | US-10 | Run & Configuration Repository | — |
| FR-13 | US-11 | Metrics Calculator | AC-01 |
| FR-14, D-07 | US-12 | Metrics Calculator | AC-04 |
| FR-15 | US-13 | Metrics Calculator | — |
| FR-16, D-07 | US-14 | Metrics Calculator | — |
| FR-17 | US-15, US-16 | Comparison Service | AC-08 |
| FR-18, D-08 | US-11 | Metrics Calculator, Result Dashboard | — |
| FR-19, D-09 | US-17 | Export Service | AC-09 |
| NFR-03 | — (quality attribute, no direct story) | Simulation Engine | Performance testing |
| NFR-04 | — (cross-cutting usability) | Result Dashboard | Usability review |
| NFR-05 | US-11, US-12, US-13 | Metrics Calculator | — |
| NFR-06 | — (cross-cutting testability) | Simulation Engine | Unit test design |
| NFR-07 | — (deployment/platform, deferred) | High-Level Design §12 | — |
| NFR-08 | — (governance, applies to all Proposed decisions) | Decision Log | Stakeholder review |

Quality-attribute NFRs (NFR-03, NFR-04, NFR-06, NFR-07, NFR-08) are intentionally not mapped to individual user stories; they constrain how all stories are implemented and are verified through non-functional testing and review rather than a single feature.
