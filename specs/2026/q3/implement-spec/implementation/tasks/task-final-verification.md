---
schema_version: 1
id: task-final-verification
kind: final-verification
status: pending
dependencies: [task-001, task-002, task-003, task-004, task-005, task-006, task-007, task-008, task-009, task-010, task-011, task-012, task-013, task-014, task-015, task-016, task-017, task-018, task-019, task-020]
cycles_used: 0
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: none
---

# Final Verification: Verify the complete amended specification

## Objective

Independently prove every amended acceptance criterion, deterministic scenario,
repository compatibility requirement, and no-delegation boundary.

## Spec References

- Entire amended specification
- Test Strategy
- Acceptance Criteria

## Plan References

- [`Acceptance Coverage`](../plan.md#acceptance-coverage)
- [`Verification Strategy`](../plan.md#verification-strategy)
- [`Execution Bounds`](../plan.md#execution-bounds)

## Dependencies

- Every implementation task, `task-001` through `task-020`, must be passed.

## Scope

### In scope

- Complete acceptance matrix; validator and scenario suites, including Tasks
  018–020; canonical skill
  validation; role/template consistency; one-planner and no-delegation
  contracts; documentation and discovery layout; Git/external guardrails;
  completion validation.

### Prohibited scope

- No new requirements, weakened criteria, delegated agent work, out-of-scope
  repairs, Git-history or remote actions, deployment, or unrelated cleanup.

## Acceptance Criteria

- [ ] Every spec criterion has implementation and independent evidence.
- [ ] All standard-library suites, compiler checks, and skill validators pass.
- [ ] Planning occurs only at the initial/material-amendment boundary.
- [ ] Every execution task requires one direct implementer and one independent
      direct tester/reviewer, with no role delegation.
- [ ] Every deterministic scenario has durable criterion evidence.
- [ ] Exactly one final task exists and every task has a passing verdict.
- [ ] Completion validation passes and unrelated work remains unchanged.

## Verification Plan

- Compile the validator with an isolated writable cache.
- Run all `test_*.py` tests and direct validator phase smoke checks.
- Validate every canonical skill and inspect role/template consistency.
- Review all scenario evidence criterion by criterion.
- Run `git diff --check` and inspect status, index, refs, log, and symlinks.
- Run completion validation before and after the orchestrator persists
  `completed`.

## Risks

Integration defects may span earlier artifacts. Repair only when it fits this
final task's approved scope; otherwise stop for amendment.

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
