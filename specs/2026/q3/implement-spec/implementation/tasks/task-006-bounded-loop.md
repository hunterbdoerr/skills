---
schema_version: 1
id: task-006
kind: implementation
status: passed
dependencies: [task-003, task-005]
cycles_used: 1
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: pass
---

# Task 006: Implement the bounded execution loop

## Objective

Complete sequential implement/test execution, stopping, resume, and final
completion behavior.

## Spec References

- Implementer and Tester
- Orchestration Lifecycle, Execute / Final Verification / Resume
- Retry and Stop Policy
- Git and Working-Tree Behavior
- AC-08 through AC-16

## Scope

Define dependency selection, distinct roles, pre-dispatch cycle persistence,
reports, verdict transitions, one infrastructure retry, gates, bounded human
extensions, overlap detection, stop rules, resume, final verification, and
completion.

Do not add parallel mutation, autonomous Git actions, deployments, external
writes, or future specialist roles.

## Acceptance

- At most one task is active and dependencies/gates block dispatch.
- Cycles persist before contact and stop at three without human extension.
- Tester remains non-mutating and returns one valid verdict.
- Pass, fail, blocked, infrastructure failure, and extension transitions match
  the spec.
- Resume preserves state and final completion requires every pass verdict.

## Verification Plan

Walk every transition, expand validator tests if a mechanical gap appears, and
run Tasks 008 and 009 forward scenarios.

## Risks

Filesystem role isolation is prompt-enforced; narrow prompts, post-agent diff
inspection, persisted state, and conservative stops are required.

## Attempts

### Cycle 1

- Implementation summary: Added post-approval reconstruction, sequential dispatch, persisted cycle accounting, independent testing, bounded retries/extensions, resume, final verification, completion, and actionable stop behavior.
- Files changed: `.agents/skills/implement-spec/SKILL.md`.
- Checks run: Standard skill validation passed in the approved temporary environment; 25 validator tests passed; live Task 006 dispatch validation passed; static transition checks passed; SKILL.md remains under 500 lines.
- Tester verdict: pass
- Verification evidence: Independent reconstruction, selection, cycle, role, diff, transition, retry, extension, resume, final-completion, handoff, authority, validation, and Git-boundary checks passed.

Infrastructure note: the first implementer dispatch failed before any edits
because the workspace was out of agent credits. The current user resumed the
workflow, authorizing no scope change. One safe same-cycle retry remains.

## Human Resolution

None.
