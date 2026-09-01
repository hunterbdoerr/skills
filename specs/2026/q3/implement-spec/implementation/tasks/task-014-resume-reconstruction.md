---
schema_version: 1
id: task-014
kind: implementation
status: pending
dependencies: [task-002, task-006, task-007, task-011, task-012, task-020]
cycles_used: 0
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: none
---

# Task 014: Validate resume and reconstruction

## Objective

Prove interruption recovery from persisted repository state alone.

## Spec References

- Orchestration Lifecycle, Resume
- Persisted State Contract
- AC-13

## Plan References

- [`Verification Strategy`](../plan.md#verification-strategy)
- [`Execution Bounds`](../plan.md#execution-bounds)

## Dependencies

- `task-002`, `task-006`, `task-007`, `task-011`, `task-012`, and `task-020`
  must be passed.

## Scope

### In scope

- Interrupted `implementing` and `testing` fixtures; replacement-role handoff;
  passed-task, cycle, approval, decision, and attempt preservation; malformed
  state stops.

### Prohibited scope

- No nested agents, conversation history as authority, repeated passed task,
  counter reset, evidence deletion, or direct recovery to pass.

## Acceptance Criteria

- [ ] Reconstruction identifies exactly one valid continuation or stops.
- [ ] Passed work is never redispatched.
- [ ] An active reserved cycle is not incremented twice.
- [ ] Replacement roles receive complete persisted history.
- [ ] Malformed or contradictory state stops actionably.

## Verification Plan

- Run focused resume fixture tests and before/after state comparisons.
- Run dispatch validation for reconstructed active-task fixtures.

## Risks

Fixtures must distinguish a resumed reservation from a new cycle.

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
