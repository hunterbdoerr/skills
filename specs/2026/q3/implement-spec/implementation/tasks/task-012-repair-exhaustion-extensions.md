---
schema_version: 1
id: task-012
kind: implementation
status: pending
dependencies: [task-003, task-006, task-007, task-011, task-020]
cycles_used: 0
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: none
---

# Task 012: Validate repair, exhaustion, and extensions

## Objective

Validate failed review, later repair, three-cycle exhaustion, and explicitly
authorized bounded extensions with deterministic state fixtures.

## Spec References

- Retry and Stop Policy
- Persisted State Contract
- AC-10 and AC-11

## Plan References

- [`Execution Bounds`](../plan.md#execution-bounds)
- [`Risks and Guardrails`](../plan.md#risks-and-guardrails)

## Dependencies

- `task-003`, `task-006`, `task-007`, `task-011`, and `task-020` must be
  passed.

## Scope

### In scope

- Failure followed by repair; three failures; pre-dispatch counters;
  append-only attempts; exact one-to-three-cycle extension records; revision
  and stale-approval behavior.

### Prohibited scope

- No role delegation, inferred extension, automatic renewal, attempt deletion,
  cycle refund, or more than three autonomous cycles.

## Acceptance Criteria

- [ ] Repair passes only in a later reserved cycle.
- [ ] Three failures stop with `needs-human`.
- [ ] Counters persist before each dispatch and attempts remain append-only.
- [ ] Extensions add only the explicitly authorized one-to-three cycles,
      increment revision, and require matching approval.

## Verification Plan

- Run focused cycle-transition fixtures.
- Run dispatch and plan-ready validation for each material snapshot.

## Risks

Test setup must not normalize impossible state merely to reach a branch.

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
