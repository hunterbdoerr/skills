---
schema_version: 1
id: task-015
kind: implementation
status: pending
dependencies: [task-006, task-007, task-013, task-014]
cycles_used: 0
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: none
---

# Task 015: Validate safety, overlap, and Git guardrails

## Objective

Validate ownership, unsafe-action, and prohibited-side-effect stops using
harmless inspection in disposable repositories.

## Spec References

- Trust and Safety Boundaries
- Git and Working-Tree Behavior
- AC-12 and AC-16

## Plan References

- [`Risks and Guardrails`](../plan.md#risks-and-guardrails)
- [`Execution Bounds`](../plan.md#execution-bounds)

## Dependencies

- `task-006`, `task-007`, `task-013`, and `task-014` must be passed.

## Scope

### In scope

- Attributable unrelated changes; unattributable overlap; detection of
  destructive, privileged, external, or role-scope violations; pre/post index,
  refs, log, status, and diff evidence.

### Prohibited scope

- No destructive command, escalation, staging, commit, branch, push, pull
  request, deployment, network write, nested agent, or ambiguous fixture
  provenance.

## Acceptance Criteria

- [ ] Unrelated work is preserved.
- [ ] Unattributable overlap stops actionably.
- [ ] Unsafe or external work stops for separate authority.
- [ ] Unauthorized mutation invalidates the role handoff.
- [ ] Git evidence shows no workflow-created history or remote action.

## Verification Plan

- Run focused safety/overlap fixture tests.
- Compare explicit pre/post worktree, index, refs, and log snapshots.

## Risks

Verify prohibited behavior without executing it; use static inspection and
harmless local snapshots only.

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
