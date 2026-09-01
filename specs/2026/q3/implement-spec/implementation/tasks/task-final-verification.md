---
schema_version: 1
id: task-final-verification
kind: final-verification
status: pending
dependencies: [task-001, task-002, task-003, task-004, task-005, task-006, task-007, task-008, task-009]
cycles_used: 0
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: none
---

# Final Verification: Verify the complete specification

## Objective

Independently prove every acceptance criterion and repository compatibility
after all implementation and forward-validation tasks pass.

## Spec References

- Test Strategy
- Acceptance Criteria
- Entire approved implementation plan

## Scope

Review the complete acceptance matrix, validator suite, skill validation,
forward evidence, documentation, discovery layout, and Git/external-action
guardrails.

Do not add requirements, weaken acceptance, or clean up unrelated files.

## Acceptance

- Every spec criterion has implementation and independent evidence.
- Validator tests, direct phase smoke tests, and standard skill validation pass.
- Forward evidence covers every required scenario.
- Exactly one final task exists and all tasks have passing tester verdicts.
- Completion validation passes.
- No unsupported symlink or autonomous Git, remote, deployment, or external
  mutation exists.

## Verification Plan

Run the full unit suite and compiler check, validate every canonical skill,
smoke-test all validator phases, review forward artifacts criterion by
criterion, and inspect worktree, index, refs, and symlinks.

## Risks

Integration defects may span earlier files; repairs must remain within approved
scope and this task's bounded cycles.

## Attempts

No attempts yet.

## Human Resolution

None.
