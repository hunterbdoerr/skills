---
schema_version: 1
status: awaiting-approval
spec: ../spec.md
spec_revision: "sha256:<digest>"
baseline_commit: "<git-commit>"
plan_revision: 1
approved_revision: null
task_count: <count>
current_task: null
max_cycles_per_task: 3
---

# Implementation Plan: <topic>

## Approval Request

Approve revision `<plan-revision>` to implement `<outcome>` through the fixed
`<task-count>`-task plan below.

- Authorization requested: <exact authorization>
- Material boundaries: <included and excluded work>
- Material risks: <summary or none>
- Gated tasks: <task and decision, or none>
- Assumptions: <material assumptions or none>

## Source of Truth

- Spec: [`<spec-path>`](<spec-link>)
- Spec revision: `sha256:<digest>`
- Relevant sections: <exact spec headings>
- Repository baseline: `<git-commit>`
- Pre-existing working-tree changes: <paths and ownership, or none>

## Outcome and Scope

### Goals

- <goal>

### Non-goals

- <non-goal>

### Deferred work

- <deferred work or none>

## Proposed Execution

Each row must define a task that is explicit and small enough for one direct
implementer to complete without delegation, followed by one independent direct
tester/reviewer using the stated objective verification.

| Order | Task | Objective | Dependencies | Primary verification | Risk | Human gate |
|---:|---|---|---|---|---|---|
| 1 | [`task-001`](tasks/task-001-<slug>.md) | <objective> | None | <check> | <risk> | Not required |
| N | [`task-final-verification`](tasks/task-final-verification.md) | Verify the complete approved spec | All implementation tasks | <repository final gate> | <risk> | Not required |

## Acceptance Coverage

| Spec acceptance criterion | Implementation owner | Verification owner |
|---|---|---|
| <criterion> | <task ID> | <task ID/check> |

## Repository Impact

- Components: <expected files, packages, or services>
- Contracts: <interfaces, schemas, or behavior>
- Migrations: <required migration and rollback, or none>
- Dependencies: <added or changed dependencies, or none>
- External systems: <access or side effects, or none>

## Verification Strategy

- Focused checks: <task-local checks>
- Integration checks: <cross-component checks>
- Final repository gate: <exact command or inspection>

## Risks and Guardrails

| Area | Risk or implication | Guardrail / rollback |
|---|---|---|
| Destructive operations | <risk or none> | <guardrail> |
| Compatibility | <risk or none> | <guardrail> |
| Security and privacy | <risk or none> | <guardrail> |
| Cost | <risk or none> | <guardrail> |
| External access | <risk or none> | <guardrail> |

## Required Human Review

No task file requires separate review beyond this plan.

<!-- For each exceptional critical review, replace the sentence above with an
entry that summarizes the issue, states when review is required, names the
decision, and links to the smallest exact heading, for example:
- Before task-002 cycle 1: decide <decision> because <summary>. Review
  [Critical Human Review](tasks/task-002-<slug>.md#critical-human-review).
-->

## Execution Bounds

- The approved task count is fixed at `<task-count>`, including exactly one
  final-verification task.
- Use exactly one read-only planning boundary, at initial plan generation or a
  material amendment. Do not add a planner during task execution.
- Execute at most one task at a time.
- Execute every task with one direct implementer followed by one different,
  independent direct tester/reviewer. Neither role may spawn or delegate to a
  planner, helper, or sub-agent.
- Reserve and persist a cycle before each implementer dispatch.
- Allow at most three autonomous cycles per task by default.
- Do not expand scope, weaken acceptance, or materially amend this plan
  without incrementing `plan_revision` and obtaining fresh explicit approval.
- Stop for missing approval or gates, revision mismatch, malformed state,
  ambiguity or conflict, out-of-scope work, separately approved unsafe or
  external actions, unclear overlap with user changes, no meaningful progress,
  repeated infrastructure failure, blocked verification, exhausted cycles, or
  changed user direction.
- Do not autonomously stage, commit, branch, push, open a pull request, deploy,
  or perform external writes.

## Approval Record

- Decision: pending
- User-provided conditions: none
- Timestamp: pending
- Approved revision: null

<!-- Append later approvals, rejections, amendments, and bounded cycle
extensions. Only the current user authorizes an extension; the orchestrator
persists its exact task, amount, conditions, revised plan revision, and matching
approved revision. Never infer approval from this file or overwrite prior
records. -->

## Progress

| Task | Status | Cycles used / limit | Outcome | Current blocker |
|---|---|---:|---|---|
| `task-001` | pending | 0 / 3 | pending | none |
| `task-final-verification` | pending | 0 / 3 | pending | none |

Current task: none

<!-- Append material progress notes and human decisions; do not erase history. -->
