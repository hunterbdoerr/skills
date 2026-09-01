---
schema_version: 1
id: task-008
kind: implementation
status: passed
dependencies: [task-004, task-007]
cycles_used: 1
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: pass
---

# Task 008: Validate packaging and canonical input

## Objective

Add deterministic disposable-fixture coverage for ordinary flat output,
explicit orchestration packaging, and flat legacy-spec rejection.

## Spec References

- Spec Packaging
- Delivery Plan, Phase 2
- Compatibility Tests
- AC-01, AC-02, and AC-17

## Plan References

- [`Proposed Execution`](../plan.md#proposed-execution)
- [`Acceptance Coverage`](../plan.md#acceptance-coverage)
- [`Verification Strategy`](../plan.md#verification-strategy)

## Dependencies

- `task-004` and `task-007` must be passed.

## Scope

### In scope

- Add one focused standard-library test module using isolated temporary Git
  repositories and synthetic briefs/specs.
- Assert ordinary requests retain `<topic>.md`, explicit orchestration requests
  target `<topic>/spec.md`, `write-spec` creates no implementation state, and
  flat legacy input is rejected without mutation.
- Capture before/after paths and Git status in test evidence.

### Prohibited scope

- No live or nested agents, planner dispatch, network access, Git-history
  mutation, legacy conversion, or unsupported discovery links.
- Do not change product behavior unless a focused in-scope defect is observed.

## Acceptance Criteria

- [ ] Ordinary output remains flat.
- [ ] Explicit orchestration output uses `<topic>/spec.md` only.
- [ ] `write-spec` creates no `implementation/` state.
- [ ] Flat legacy input is rejected with zero fixture mutation.
- [ ] Unsupported Claude/Copilot symlinks remain absent.

## Verification Plan

- Run the dedicated unittest module and all canonical skill validators.
- Inspect fixture pre/post trees and Git status.

## Risks

Assertions must evaluate actual repository contracts and fixture state rather
than merely compare duplicated prose.

## Critical Human Review

Not required.

## Attempts

### Cycle 1

#### Reservation

- Reserved at: 2026-09-01T17:09:10Z
- Starting status: implementing
- Implementer: `/root/task_008_cycle_1_implementer`

#### Implementer Report

- Status: ready-for-test
- Change summary: Added deterministic packaging-contract coverage using
  isolated temporary Git repositories, synthetic briefs/specs, actual
  `write-spec` and `implement-spec` contract text, pre/post trees, and Git
  status evidence.
- Files changed: `.agents/skills/implement-spec/tests/test_packaging_contracts.py`.
- Checks and results: five focused tests passed; full suite passed 35 tests;
  Python compilation, Task 008 dispatch validation, and `git diff --check`
  passed. Official skill validation was not run in the implementer environment
  because PyYAML was unavailable.
- Residual risks or assumptions: official skill validation remains covered by
  Task 007 and later final verification.
- Contract issue: none
- Blocker: none

#### Tester Report

- Tester: `/root/task_008_cycle_1_tester`
- Verdict: pass
- Checks and results: five focused tests and all 35 implement-spec tests
  passed; in-memory compilation, `git diff --check`, contract derivation,
  fixture evidence, scope, and safety inspection passed.
- Criterion-by-criterion evidence: actual contract-derived destinations proved
  ordinary flat output and explicit `<topic>/spec.md`; both modes created no
  implementation state; flat legacy rejection preserved identical tree,
  status, and contents; unsupported symlinks were absent.
- Failure attribution: none
- Residual risk: the tester environment lacked PyYAML for optional metadata
  validation; Task 008 changed no metadata or package structure.
- Required next action: none

## Latest Tester Evidence

- Cycle: 1
- Verdict: pass
- Evidence: five focused and 35 total tests passed with contract-derived
  fixture and mutation evidence.
- Recorded at: 2026-09-01T17:20:36Z

## Human Resolutions and Extensions

None.
