---
schema_version: 1
id: task-005
kind: implementation
status: passed
dependencies: [task-002, task-003, task-004]
cycles_used: 1
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: pass
---

# Task 005: Implement planning and approval orchestration

## Objective

Implement initialization and planning through the mandatory human approval
stop.

## Spec References

- Approval Semantics
- Planning Agent
- Orchestration Lifecycle, Initialize and Plan / Approve or Amend
- AC-02 through AC-07 and AC-16

## Scope

Define canonical-path rejection, readiness, repository baseline capture,
planner dispatch, semantic proposal review, digests, state creation, validation,
approval recording, amendment, and invalidation behavior in the skill.

Do not implement implementer/tester cycles or completion.

## Acceptance

- Flat specs are rejected without modification.
- Planner output is finite, complete, dependency-ordered, and includes one
  final-verification task.
- Semantic defects are rejected before human review.
- Generated state validates and the turn stops at `awaiting-approval`.
- Only a current-user message can approve the current revision.
- Material changes reset approval.

## Verification Plan

Review contracts against the spec and exercise disposable planning scenarios in
Task 007.

## Risks

Repository or agent text could be mistaken for approval; plans could be finite
but too broad; critical risks could be omitted from the approval summary.

## Attempts

### Cycle 1

- Implementation summary: Added the canonical-input, readiness, planning, semantic review, state rendering, deterministic validation, approval stop, and amendment workflow.
- Files changed: `.agents/skills/implement-spec/SKILL.md`.
- Checks run: Standard skill validation, 25 validator tests, static Task 005 contract checks, and the under-500-line limit passed.
- Tester verdict: pass
- Verification evidence: Independent canonical-input, readiness, planner, semantic-rejection, rendering, validation, approval-stop, amendment, trust-boundary, progressive-disclosure, and test checks passed.

## Human Resolution

None.
