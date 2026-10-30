# Digital Twin Assembly-Line Simulation Requirements

## 1. Purpose

Define requirements for a digital twin that models an assembly line and estimates production performance under changing operating conditions. The simulation will help users understand how station cycle times, downtime, and batch sizes affect throughput and related line metrics.

> **Document status:** This revision resolves the initial-release modeling ambiguities (downtime, batching, initial WIP, metric formulas, event ordering, and units) with explicit proposed decisions in [Section 9](#9-decision-log). Decisions marked *Proposed* are the working model for design and implementation but require manufacturing/operations stakeholder sign-off before results are treated as operationally representative (see [NFR-08](#6-non-functional-requirements) and [Section 11](#11-verification-and-validation)).

## 2. Goals and Success Measures

- Model the flow of units through a configurable sequence of assembly stations.
- Compare a baseline operating scenario with one or more parameter changes.
- Report throughput, production output, work in progress (WIP), station utilization, downtime impact, and bottlenecks.
- Make simulation runs reproducible when the same inputs and random seed are used.
- Clearly distinguish user-provided inputs from assumptions and generated results.

## 3. Scope

### In scope

- A single assembly line consisting of ordered stations and optional finite-capacity buffers.
- Station cycle-time settings, downtime settings, and batch-size settings.
- A configurable simulation horizon and production start conditions.
- Discrete-event simulation of unit movement, processing, blocking, starvation, and downtime.
- Scenario execution, comparison, and summary reporting.

### Out of scope for the initial release

- Live connection to production equipment, PLCs, MES, ERP, or IoT data sources.
- Automatic optimization or recommendations that change production settings.
- Detailed labor, cost, quality, rework, or supply-chain models unless explicitly added later.
- Multi-line plant-wide scheduling and resource sharing across lines.

## 4. Users and Primary Workflow

**Primary users:** Manufacturing engineers, production planners, and operations analysts.

1. Define the line layout, stations, buffers, and operating parameters.
2. Set the simulation duration and initial conditions.
3. Run a baseline simulation and review its results.
4. Change one or more parameters, run a scenario, and compare it with the baseline.
5. Export or otherwise retain the scenario inputs and results for review.

## 5. Functional Requirements

### Line configuration

- **FR-01:** The system shall allow a user to define a line as an ordered list of stations.
- **FR-02:** Each station shall have a unique name or identifier and a cycle time greater than zero.
- **FR-03:** The system shall allow a buffer capacity to be specified between adjacent stations, including zero capacity to represent direct transfer.
- **FR-04:** The system shall validate line configuration before a run and identify invalid or missing values.

### Simulation inputs and behavior

- **FR-05:** The user shall be able to set the simulation horizon and the starting WIP as a per-station in-process unit count. Units present at time zero are treated per the initial-WIP rule in [Section 7](#7-metric-definitions) (Decision D-03).
- **FR-06:** The user shall be able to configure a fixed station cycle time for each station. Variable cycle-time distributions are out of scope for the initial release (Decision D-01).
- **FR-07:** The user shall be able to configure downtime by station using scheduled downtime intervals (start offset and duration, repeating or one-time). The initial release models only scheduled downtime; failure-based (MTBF/MTTR) stochastic downtime is deferred to a documented future extension (Decision D-02). The selected downtime schedule shall be visible in the run configuration.
- **FR-08:** The user shall be able to configure a transfer batch size at each buffer/transfer point, defined as the number of completed units a station releases to the downstream buffer at once. Stations process one unit per cycle time regardless of batch size; batch size governs transfer grouping only, not per-unit processing time (Decision D-04).
- **FR-09:** The simulation shall represent station processing, scheduled downtime, buffer capacity, blocking, and starvation consistently with the configured line, using the deterministic event-ordering rule in Decision D-06.
- **FR-10:** The user shall be able to run a scenario without changing the saved baseline configuration.
- **FR-11:** The user shall be able to set a random seed for any future run that enables stochastic behavior. Identical inputs and seed shall produce identical results. The initial release's scheduled-downtime/fixed-cycle-time model is fully deterministic and does not require a seed.
- **FR-12:** The system shall retain the full input snapshot and model version associated with each completed run, consistent with NFR-01.

### Results and comparison

- **FR-13:** For each run, the system shall report completed-unit throughput over the simulation horizon and the total completed units.
- **FR-14:** The system shall report station utilization, downtime, and time blocked or starved when those states are modeled.
- **FR-15:** The system shall report WIP over time and at the end of the run.
- **FR-16:** The system shall identify the station or stations limiting line output, using the bottleneck rule in Decision D-07.
- **FR-17:** The user shall be able to compare at least two runs, including their input differences and key output metrics, and the system shall flag comparisons where horizon, units, or initial conditions differ (see Risk: Misleading comparisons).
- **FR-18:** The system shall indicate units and time basis for every input and reported metric, using the fixed unit set in Decision D-08.
- **FR-19:** The user shall be able to export scenario inputs and summary results as JSON, including the model version and, when applicable, the random seed (Decision D-09).

## 6. Non-Functional Requirements

- **NFR-01 Reproducibility:** A run shall record its full input snapshot, model version, and random seed where applicable; identical inputs and seed shall deterministically reproduce identical results.
- **NFR-02 Input safety:** Invalid values, unsupported configurations, and inconsistent units shall be rejected with actionable validation messages before simulation starts.
- **NFR-03 Performance:** The initial release shall support at least 20 stations, a horizon of at least 100,000 simulated minutes, and 10 retained scenarios per line, completing a single run in no more than 5 seconds on a typical analyst workstation; these targets are provisional pending stakeholder confirmation of real line sizes.
- **NFR-04 Usability:** Users shall be able to understand the line configuration, scenario differences, and metric definitions without consulting implementation details.
- **NFR-05 Result integrity:** Reported totals and rates shall use the time basis in Decision D-08 and round displayed values to 2 decimal places while retaining full precision internally.
- **NFR-06 Maintainability:** The model shall keep line configuration, simulation execution, and result calculation separable enough to test independently.
- **NFR-07 Portability:** The initial release targets a browser-based client and a server-side simulation service; concrete framework, hosting, and deployment platform are out of scope for this requirements document (see `high-level-design.md`).
- **NFR-08 Model governance:** Any requirement or metric marked *Proposed* in the decision log shall be reviewed and approved by a manufacturing/operations stakeholder before simulation results are used for operational decisions.

## 7. Metric Definitions

- **Throughput rate:** Completed units divided by the full simulation horizon duration (time 0 to horizon end). There is no separate startup/shutdown phase in the initial release; units present as initial WIP count toward output only if they complete before the horizon ends (Decision D-03).
- **Total output:** Number of units completed strictly before the simulation horizon end. A completion event scheduled exactly at the horizon end is not counted (Decision D-05).
- **Station utilization:** Busy (processing) time divided by (horizon duration minus scheduled downtime time) for that station. Scheduled downtime is excluded from the available-time denominator; blocked and starved time are reported separately and are not treated as busy time (Decision D-07).
- **WIP:** Units that have started but not completed, reported as a time series and as the end-of-run value. Initial WIP units are included from time zero.
- **Bottleneck:** The station with the greatest busy time; ties are broken by the station with the greater combined blocked time, since a station that is busy and also blocking upstream flow constrains the line more (Decision D-07). Utilization alone is not used, since it can be inflated by scheduled downtime exclusion.
- **Batch size:** Number of completed units a station releases to the downstream buffer in one transfer event. Batch size does not change per-unit station cycle time. A batch that is not yet full at the horizon end remains at the station as WIP, not as completed output (Decision D-04).

## 8. Acceptance Criteria

- **AC-01:** A single station with a 2-minute cycle time, no downtime, and a 20-minute horizon produces exactly 10 completed units (the unit whose completion would land exactly at minute 20 is excluded per Decision D-05).
- **AC-02:** For a deterministic two-station serial line with unlimited buffers and no downtime or batching, reducing station 1's cycle time from 5 to 3 minutes does not reduce total completed units over the same horizon, all other inputs unchanged.
- **AC-03:** Adding a 10-minute scheduled downtime event to a station reduces that station's available time by exactly 10 minutes and does not increase total output versus the same run without that downtime.
- **AC-04:** With a zero-capacity buffer between two stations of unequal cycle time, the faster upstream station accumulates blocked time and the slower downstream station's idle/starved time is reported; both durations sum consistently with the horizon.
- **AC-05:** With a transfer batch size of 5 at a station producing 1 unit/minute, no units are transferred downstream until 5 units have accumulated, and any partial batch remaining at the horizon end is reported as WIP, not completed output.
- **AC-06:** Re-running a scenario with a future stochastic downtime model, using identical inputs and seed, yields identical summary results.
- **AC-07:** A cycle time of 0, a negative buffer capacity, a negative downtime duration, and a batch size of 0 are each rejected with a validation message identifying the offending field.
- **AC-08:** Scenario comparison lists every changed input field alongside the baseline and scenario values, plus the resulting change in throughput, output, WIP, utilization, and bottleneck station.
- **AC-09:** Exported JSON results include the line configuration, model version, run timestamp, and (when applicable) the random seed, sufficient to reproduce the run.

## 9. Decision Log

Each entry resolves a previously open question. Status *Proposed* means the decision is the working model for design, implementation, and testing, but requires manufacturing/operations stakeholder approval (NFR-08) before results are treated as operationally representative. Status *Confirmed* means stakeholder approval has been recorded.

| ID | Decision | Rationale | Status |
| --- | --- | --- | --- |
| D-01 | Line topology is strictly serial (ordered stations, no merges/splits/rework/alternate routes); cycle times are fixed (not sampled from a distribution) in the initial release. | Smallest model that still supports the required metrics; matches the stated in-scope description. | Proposed |
| D-02 | Downtime is scheduled-only (fixed start offset and duration, one-time or repeating) in the initial release. Failure-based stochastic downtime (MTBF/MTTR) is a future extension requiring its own seed and distribution requirements. | Keeps the initial release fully deterministic, simplifying validation and reproducibility (NFR-01). | Proposed |
| D-03 | Initial WIP is specified per station as an in-process unit count at time zero. These units count as WIP immediately and as completed output only if their processing finishes before the horizon ends. No separate startup/shutdown phase is modeled. | Avoids ambiguity about whether pre-loaded units should be free completions at time zero. | Proposed |
| D-04 | Batch size governs transfer grouping only: a station releases completed units downstream in groups of the configured batch size. Per-unit station cycle time is unaffected by batch size. A partial batch remaining at the horizon end counts as WIP. | Matches FR-08's "transfer point" language and gives a single, testable behavior instead of two competing interpretations. | Proposed |
| D-05 | A unit whose completion event time equals the horizon end is not counted as completed output (strict less-than). Horizon-boundary events are not executed. | Produces a single unambiguous boundary rule usable in all boundary-condition tests. | Proposed |
| D-06 | At equal event timestamps, events are resolved in this fixed order: (1) downtime end, (2) station processing completion/transfer, (3) downtime start, (4) new arrival. | Prevents nondeterministic ordering of simultaneous events, which would otherwise break reproducibility (FR-11, NFR-01). | Proposed |
| D-07 | Utilization denominator excludes scheduled downtime. Bottleneck = station with greatest busy time, ties broken by combined blocked time. | Avoids a station's utilization appearing artificially low due to planned downtime, and avoids relying on utilization alone to find bottlenecks under blocking/starvation. | Proposed |
| D-08 | Time unit is minutes; quantity unit is whole units (integers). All inputs and reported metrics use these units; no unit conversion is supported in the initial release. | Removes unit-handling ambiguity flagged in FR-18 and NFR-05. | Proposed |
| D-09 | Export format is JSON only in the initial release; CSV is deferred. | Single format reduces initial implementation and testing scope; JSON naturally represents nested run metadata. | Proposed |
| D-10 | Maximum line size, horizon, and scenario count for the initial release are the provisional NFR-03 targets (20 stations, 100,000-minute horizon, 10 scenarios per line, 5-second run time). | Gives testable performance targets instead of leaving them unresolved; to be revised once real line sizes are confirmed. | Proposed |
| D-11 | Quality loss, scrap, rework, changeovers, labor constraints, and material shortages are out of scope for the initial release (reaffirms Section 3). | No requirement currently calls for these; keeps the initial model serial and deterministic. | Confirmed |
| D-12 | Initial release targets a browser-based UI calling a server-side simulation service; concrete framework, hosting, and deployment platform are deferred to `high-level-design.md` and later implementation decisions. | Separates product-level scope from technology selection. | Proposed |

Until all *Proposed* decisions are confirmed, treat simulation outputs as illustrative rather than operationally representative, per NFR-08 and Section 10 (Oversimplified model, Ambiguous batch behavior).

## 10. Risks and Mitigations

- **Oversimplified model:** A serial fixed-time model may not reflect real operations. Validate assumptions with manufacturing stakeholders and label model limitations in results.
- **Ambiguous batch behavior:** Different interpretations produce materially different throughput. Define batch semantics and add acceptance tests before implementation.
- **Misleading comparisons:** Different horizons, units, or initial states can invalidate comparisons. Show these inputs alongside comparison results and flag mismatches.
- **Uncalibrated parameters:** Incorrect inputs can make precise-looking outputs unreliable. Record parameter provenance and support calibration against observed production data in a future scope.
- **Boundary-condition errors:** Event ordering at the horizon, downtime boundaries, and batch completion can change totals. Define conventions and test boundary cases.

## 11. Verification and Validation

- Review requirements and metric definitions with manufacturing and operations stakeholders.
- Trace each functional requirement to one or more acceptance tests.
- Use deterministic test scenarios with hand-calculable expected outcomes for cycle time, downtime, buffers, and batch behavior.
- Test invalid inputs, time-boundary behavior, and reproducibility separately from performance tests.
- Compare representative simulation results with historical line data or an independently validated calculation before operational use.
- Record unresolved discrepancies, agreed assumptions, and requirement changes in the project documentation.

## 12. Change History

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-10-29 | Initial requirements draft based on the supplied topic. |
| 0.2 | 2026-10-29 | Resolved downtime, batch, initial-WIP, event-ordering, metric, unit, export, and performance-target ambiguities as proposed decisions (Section 9); added NFR-08 model governance; tightened FR-05–FR-09, FR-16–FR-19, and NFR-03/05/07; made acceptance criteria concrete and hand-calculable; removed open questions in favor of a traceable decision log. |