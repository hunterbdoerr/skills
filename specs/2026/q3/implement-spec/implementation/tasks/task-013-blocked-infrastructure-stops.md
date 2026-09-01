---
schema_version: 1
id: task-013
kind: implementation
status: pending
dependencies: [task-006, task-007, task-011, task-020]
cycles_used: 0
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: none
---

# Task 013: Validate blocked and infrastructure stops

## Objective

Isolate tester-blocked and repeated infrastructure-failure stop behavior.

## Spec References

- Retry and Stop Policy
- Human handoff contract
- AC-12

## Plan References

- [`Execution Bounds`](../plan.md#execution-bounds)
- [`Risks and Guardrails`](../plan.md#risks-and-guardrails)

## Dependencies

- `task-006`, `task-007`, `task-011`, and `task-020` must be passed.

## Scope

### In scope

- Tester-blocked environment; one proven side-effect-free communication retry;
  second infrastructure failure; actionable attribution and handoff; preserved
  reserved-cycle evidence.

### Prohibited scope

- No nested agents, tester repair, extra cycle for the same safe retry,
  simulated success after a blocker, or misclassification as implementation
  failure.

## Acceptance Criteria

- [ ] Tester `blocked` stops immediately.
- [ ] One safe retry remains in the reserved cycle.
- [ ] A second infrastructure failure stops without refunding the cycle.
- [ ] The handoff distinguishes environment from implementation and preserves
      append-only evidence.

## Verification Plan

- Run focused stop-branch fixture tests and compare state snapshots.
- Independently review every handoff field and failure attribution.

## Risks

Synthetic infrastructure failures must be explicit and side-effect free.

## Critical Human Review

Not required.

## Attempts

None.

## Latest Tester Evidence

- Cycle: none
- Verdict: none
- Evidence: none
- Recorded at: none

## Human Resolutions and Extensions

None.
