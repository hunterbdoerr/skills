---
schema_version: 1
id: task-009
kind: implementation
status: pending
dependencies: [task-006, task-007, task-008]
cycles_used: 0
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: none
---

# Task 009: Forward-test resume and completion safety

## Objective

Prove reconstruction, unsafe-state handling, overlap detection, and final
completion in disposable repositories.

## Spec References

- Resume
- Trust and Safety Boundaries
- Git and Working-Tree Behavior
- Delivery Plan, Phase 4
- AC-07, AC-08, and AC-12 through AC-16

## Scope

Exercise interruption and reconstruction, spec changes, pre-existing overlap,
unsafe actions, successful final verification, and prohibited Git/external
side effects.

Do not add new workflow capabilities.

## Acceptance

- Resume never repeats passed work or resets counters and evidence.
- Digest mismatch, unattributable overlap, and unsafe actions stop actionably.
- Completion requires final verification.
- Fixture Git evidence shows no workflow-created stage, commit, branch, push,
  deployment, or external write.

## Verification Plan

Restart with fresh agents using persisted files, compare pre/post Git state, and
run completion validation on incomplete and passing packages.

## Risks

Fixture setup actions must be distinguishable from workflow side effects.

## Attempts

No attempts yet.

## Human Resolution

None.
