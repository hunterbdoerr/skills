---
schema_version: 1
id: task-016
kind: implementation
status: pending
dependencies: [task-003, task-006, task-007, task-008, task-009, task-010, task-011, task-012, task-013, task-014, task-015, task-017, task-018, task-019, task-020]
cycles_used: 0
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: none
---

# Task 016: Validate final and completion transitions

## Objective

Exercise incomplete and complete packages through the sole final task without
delegated roles.

## Spec References

- Orchestration Lifecycle, Final verification
- Deterministic Validator
- AC-14

## Plan References

- [`Acceptance Coverage`](../plan.md#acceptance-coverage)
- [`Verification Strategy`](../plan.md#verification-strategy)

## Dependencies

- `task-003`, `task-006`, `task-007` through `task-015`, and `task-017`
  through `task-020` must be passed.

## Scope

### In scope

- Final-task dependency readiness; incomplete completion rejection; final-task
  reservation; direct implementer report; independent direct tester verdict;
  complete acceptance matrix; persisted completion validation.

### Prohibited scope

- No second final task, reopened passed work, nested roles, weakened
  acceptance, or premature `completed` status.

## Acceptance Criteria

- [ ] Final verification cannot be selected early.
- [ ] Exactly one final task exists.
- [ ] Incomplete completion fails actionably.
- [ ] Every implementation task and the final task must pass.
- [ ] Completion validation succeeds before and after persisting `completed`.

## Verification Plan

- Run focused completion fixture tests.
- Run direct failing and passing `validate_state.py --phase completion` cases.

## Risks

Passing fixtures must satisfy every invariant rather than bypass the validator.

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
