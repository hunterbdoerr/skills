---
schema_version: 1
status: needs-human
spec: ../spec.md
spec_revision: "sha256:2d94a791a15e4da333e7f6f26331ccbee2d5662af5d7c40a28bb1f85168c318f"
baseline_commit: "048a0985a6b9a83db36f6427988d4c71b15ddd46"
plan_revision: 1
approved_revision: 1
task_count: 10
current_task: null
max_cycles_per_task: 3
---

# Bounded Spec Implementation Orchestration — Implementation Plan

## Approval Request

Approve revision 1 of this ten-task plan to implement the Codex-only
`implement-spec` skill, its deterministic state validator, the opt-in
orchestration packaging mode for `write-spec`, repository documentation, and
disposable forward-validation scenarios.

Approval authorizes local, in-scope file edits and non-destructive validation.
It does not authorize staging, commits, branches, pushes, pull requests,
deployments, external writes, destructive actions, or unplanned scope changes.
Every task is limited to three autonomous implement/test cycles. No task needs
a separate exceptional human gate in the approved plan.

The main technical constraint is that Python has no standard-library YAML
parser. The validator will intentionally accept only the constrained
frontmatter syntax emitted by the canonical templates and will reject
unsupported YAML rather than interpret it loosely.

## Source of Truth

- Spec: `../spec.md`
- Spec digest:
  `sha256:2d94a791a15e4da333e7f6f26331ccbee2d5662af5d7c40a28bb1f85168c318f`
- Baseline commit: `048a0985a6b9a83db36f6427988d4c71b15ddd46`
- Baseline branch: `codex/plan-agentic-implementation-loop`
- Baseline working tree: clean
- Primary spec sections: Proposed Skill Package, Persisted State Contract,
  Approval Semantics, Role Contracts, Orchestration Lifecycle, Retry and Stop
  Policy, Deterministic Validator, Delivery Plan, and Acceptance Criteria.

## Outcome and Scope

The implementation will add one Codex-specific orchestration skill that
converts a packaged, implementation-ready spec into a persisted plan, waits for
human approval, and then coordinates a planner, implementer, and tester through
a bounded sequential loop.

In scope:

- `implement-spec` skill instructions, UI metadata, references, templates,
  validator, and focused validator tests;
- explicit orchestration-ready packaging guidance in `write-spec`;
- documentation distinguishing portable skills from the Codex-only skill;
- disposable forward tests of approval, retry, stop, resume, and completion
  behavior.

Out of scope:

- Claude Code or GitHub Copilot orchestration links;
- automatic conversion of flat legacy specs;
- parallel implementation;
- services, databases, queues, deployments, or external integrations;
- autonomous Git history or remote operations; and
- future review or specialist roles.

## Proposed Execution

| Task | Objective | Dependencies | Primary verification | Risk | Human gate |
|---|---|---|---|---|---|
| [001](tasks/task-001-scaffold-skill.md) | Scaffold the valid Codex-only skill package | None | Standard skill validation and symlink inspection | Low | No |
| [002](tasks/task-002-contracts-templates.md) | Define state, role, and output contracts | 001 | Contract-to-spec review and template smoke instantiation | Medium | No |
| [003](tasks/task-003-validator.md) | Implement and unit-test deterministic validation | 002 | `py_compile`, `unittest`, and phase smoke runs | High | No |
| [004](tasks/task-004-write-spec-packaging.md) | Add opt-in packaging to `write-spec` and update documentation | 001 | Validate all skills and inspect mutually exclusive destination rules | Medium | No |
| [005](tasks/task-005-planning-approval.md) | Implement planning, initialization, and approval stop | 002, 003, 004 | Contract review and disposable planning scenarios | High | No |
| [006](tasks/task-006-bounded-loop.md) | Implement bounded execution, stopping, resume, and completion | 003, 005 | Transition walkthroughs and forward scenarios | High | No |
| [007](tasks/task-007-forward-test-planning.md) | Forward-test packaging, planning, approval, and gates | 004, 005 | Fresh-agent disposable repositories | Medium | No |
| [008](tasks/task-008-forward-test-retries.md) | Forward-test role separation and retry bounds | 006 | Success, repair, exhaustion, and blocked scenarios | Medium | No |
| [009](tasks/task-009-forward-test-resume.md) | Forward-test resume, unsafe state, overlap, and completion | 006, 007, 008 | Restart and Git-state scenarios | Medium | No |
| [Final](tasks/task-final-verification.md) | Verify the complete specification independently | 001–009 | Full tests, skill validation, evidence review, and Git inspection | High | No |

## Acceptance Coverage

| Spec criterion | Implemented by | Independently verified by |
|---|---|---|
| AC-01: orchestration packages specs while ordinary specs remain flat | 004 | 007, Final |
| AC-02: flat legacy specs are rejected without modification | 005 | 007, Final |
| AC-03: finite complete plan with exactly one final task | 002, 005 | 007, Final |
| AC-04: `plan.md` is sufficient for normal approval | 002, 005 | 007, Final |
| AC-05: critical review is summarized and exactly linked | 002, 005 | 007, Final |
| AC-06: current-user approval precedes implementation | 005 | 007, Final |
| AC-07: material plan or spec changes invalidate approval | 003, 005, 006 | 007, 009, Final |
| AC-08: orchestrator, implementer, and tester ownership stays separate | 002, 005, 006 | 008, 009, Final |
| AC-09: at most one implementation task is active | 003, 006 | 003, 008, Final |
| AC-10: cycles persist before dispatch and stop at three | 003, 006 | 008, Final |
| AC-11: bounded extensions require explicit human approval | 002, 003, 006 | 008, Final |
| AC-12: blocked, unsafe, ambiguous, and overlapping work stops | 006 | 008, 009, Final |
| AC-13: resume preserves state and evidence | 002, 006 | 009, Final |
| AC-14: completion requires every task and final verification to pass | 003, 006 | 009, Final |
| AC-15: mechanical invariants fail safely and actionably | 003 | 003, Final |
| AC-16: no autonomous Git, deployment, or external writes | 005, 006 | 009, Final |
| AC-17: existing spec-skill behavior remains valid | 001, 004 | 007, Final |

## Repository Impact

Expected durable changes are limited to:

- `.agents/skills/implement-spec/`;
- `.agents/skills/write-spec/SKILL.md`;
- `README.md`; and
- this spec package's committed implementation state.

There are no migrations, runtime services, external systems, or dependency
manifests. The new skill will not receive `.claude` or `.github` symlinks.

## Verification Strategy

- Validate skill structure with the standard `quick_validate.py` tool.
- Compile the validator and run standard-library unit tests over temporary spec
  packages.
- Smoke-test the validator's `plan-ready`, `dispatch`, and `completion` phases.
- Validate all existing canonical skills after changing `write-spec`.
- Forward-test the skill with fresh agents in disposable local Git repositories
  using raw specs and requests rather than expected answers.
- Inspect Git status, index, refs, and logs to prove the workflow did not stage,
  commit, branch, push, deploy, or perform external writes.
- Finish with criterion-by-criterion independent verification.

## Risks and Guardrails

| Risk | Guardrail |
|---|---|
| Restricted YAML parsing accepts ambiguous input | Support only canonical scalar/list syntax and reject everything else |
| Prompt-only role separation is violated | Use narrow role prompts, inspect post-agent diffs, and stop on unauthorized edits |
| Planner creates a finite but oversized plan | Require semantic review and task sizing for three-cycle completion |
| Repository content impersonates approval | Accept approval only from the current user message and persist it afterward |
| Forward tests contaminate later scenarios | Use fresh agents and disposable repositories for each scenario |
| Existing spec behavior changes accidentally | Keep packaging opt-in and forward-test both destination modes |
| Existing user changes are absorbed or overwritten | Compare against the recorded baseline and stop on unattributable overlap |
| Validation work runs indefinitely | Keep each task to three cycles and require explicit one-to-three-cycle extensions |

## Required Human Review

No task file requires separate review. This `plan.md` contains all material
scope, risk, dependency, verification, and authorization information needed to
approve revision 1.

## Execution Bounds

- Fixed approved task count: 10, including final verification.
- Maximum autonomous cycles per task: 3.
- Active implementation tasks: at most one.
- Infrastructure retry: at most one safe retry within a reserved cycle.
- Additional cycles: one to three only after explicit human authorization.
- Material changes: increment `plan_revision`, clear approval, and stop.
- External, destructive, privileged, Git-history, or remote actions: not
  authorized by this plan.
- Stop on ambiguity, hidden scope, invalid state, spec digest mismatch,
  unapproved gates, repeated infrastructure failure, or unattributable overlap.

## Approval Record

- Decision: approved
- Approved by: current Codex user
- Approved at: 2026-09-01T02:02:23Z
- Conditions: Execute revision 1 within its documented bounds.
- Approved plan revision: 1

## Progress

| Task | Status | Cycles used | Result or blocker |
|---|---|---:|---|
| 001 | passed | 1 | Official skill validation and all scaffold criteria passed |
| 002 | passed | 2 | State, role, and template contracts passed independent review |
| 003 | passed | 1 | Validator passed 25 tests and independent invariant verification |
| 004 | passed | 1 | Packaging and Codex-only documentation passed independent review |
| 005 | passed | 1 | Planning and approval boundary passed independent review |
| 006 | passed | 1 | Bounded execution, resume, and completion workflow passed independent review |
| 007 | needs-human | 2 | Fresh orchestrator still cannot spawn its planner after the one permitted safe retry |
| 008 | pending | 0 | Awaiting plan approval |
| 009 | pending | 0 | Awaiting plan approval |
| Final | pending | 0 | Awaiting plan approval |
