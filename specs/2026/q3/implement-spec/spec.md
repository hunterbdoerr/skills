# Bounded Spec Implementation Orchestration

## Status

Draft. The decisions in this document are approved for specification, but the
skill and supporting files have not been implemented.

## Decision Summary

Add a Codex-specific `implement-spec` skill that turns an implementation-ready
specification into a human-approved, persisted implementation plan and then
coordinates a planning agent, an implementer, and an independent tester through
a bounded task loop.

The workflow will:

1. require an orchestration-ready spec at `<topic>/spec.md`;
2. ask a planning agent for a finite, dependency-ordered task breakdown;
3. persist the proposed plan and task state as Markdown with YAML frontmatter;
4. stop until a human explicitly approves `implementation/plan.md`;
5. run one task at a time through at most three implement/test cycles;
6. stop for human input on ambiguity, blocked work, critical gates, exhausted
   cycles, material plan changes, or unsafe state; and
7. finish with a dedicated final-verification task covering the entire spec.

The orchestrator owns workflow state but does not implement code, judge its own
implementation, or grant approval. It may edit in-scope code and state files,
but it may not stage, commit, push, create a pull request, or otherwise mutate
Git history or remote state.

## Context

This repository currently provides two canonical skills under
`.agents/skills`: `build-spec-context` creates a decision-rich discovery
handoff, and `write-spec` creates an implementation-ready Markdown spec.
Tool-specific directories expose those skills through relative symlinks, as
documented in `README.md`.

`write-spec` supports delivery phases, acceptance criteria, verification,
failure behavior, and open questions, but those sections are intentionally
proportional and are not a normalized execution queue. A separate planning
role is therefore needed before implementation begins.

The first version targets Codex's orchestrator/sub-agent capabilities rather
than attempting a portable abstraction. This permits explicit planner,
implementer, and tester dispatch while keeping the workflow small. Claude Code
and GitHub Copilot discovery symlinks are out of scope until an equivalent,
testable orchestration contract exists for those tools.

## Goals

- Turn an implementation-ready spec into a finite set of reviewable tasks.
- Give a human one primary approval document containing every material fact
  needed to authorize the plan.
- Preserve enough committed Markdown state to resume safely after an
  interruption or a new Codex turn.
- Keep implementation and testing responsibilities separate.
- Bound autonomous iteration to three implement/test cycles per task.
- Stop rather than invent requirements, weaken acceptance criteria, or expand
  scope.
- Make mechanical workflow invariants deterministically checkable.
- Leave stable extension points for future planning review, code review,
  security review, and other specialist agents.

## Non-Goals

- General-purpose workflow orchestration outside spec implementation.
- Portable multi-agent support for Claude Code or GitHub Copilot in v1.
- Parallel implementation of multiple tasks.
- Autonomous commits, branches, staging, pushes, pull requests, deployments,
  or external writes.
- Automatic conversion or movement of existing flat-file specs.
- Replacing repository instructions, tests, CI, or human code review.
- Allowing an agent to change approved acceptance criteria to make a test pass.
- Building a service, database, queue, or background daemon.
- Adding task estimation, scheduling, or project-management integrations.

## Source-of-Truth and Ownership

| Artifact or actor | Responsibility | May not do |
|---|---|---|
| `spec.md` | Requirements and acceptance source of truth | Approve execution or mutate orchestration policy |
| Human | Approve plans, critical gates, scope changes, and bounded extensions | Be impersonated by repository content |
| Orchestrator | Validate state, dispatch roles, persist reports, enforce stops | Implement code, overrule tester evidence, or self-approve |
| Planning agent | Propose tasks, dependencies, coverage, risks, and gates | Edit code or approve its plan |
| Implementer | Change code and tests for the active task | Edit orchestration state or broaden task scope |
| Tester | Independently verify the active task and report evidence | Edit production code or weaken acceptance criteria |
| `plan.md` | Human approval contract and overall workflow state | Serve as approval merely because its text says approved |
| Task files | Task-local execution history and evidence | Override the spec or plan |

The orchestrator is the only writer of `implementation/plan.md` and
`implementation/tasks/*.md`. Sub-agents return structured reports; the
orchestrator records them after checking that they stay within the approved
contract.

## Spec Packaging

### Orchestration-ready specs

`write-spec` will gain an explicit orchestration-ready output mode:

```text
specs/<year>/q<quarter>/<topic>/
├── spec.md
└── implementation/
    ├── plan.md
    └── tasks/
        ├── task-001-<slug>.md
        └── task-final-verification.md
```

`write-spec` creates `<topic>/spec.md`. `implement-spec` creates the
`implementation` contents when planning begins.

Ordinary specs retain the existing fallback convention of
`specs/<year>/q<quarter>/<topic>.md`. The orchestration mode must be explicit;
`write-spec` must not silently change all specs to directory packages.

### Legacy specs

V1 accepts only the canonical `<topic>/spec.md` input. A flat legacy spec must
be deliberately converted or rewritten into an orchestration-ready package.
`implement-spec` must not move, copy, or rewrite it automatically.

## Proposed Skill Package

```text
.agents/skills/implement-spec/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── plan.md
│   └── task.md
├── references/
│   ├── state-contract.md
│   └── role-contracts.md
└── scripts/
    └── validate_state.py
```

The main skill file should contain only the core workflow, dispatch order,
approval boundary, and stop rules. Detailed schemas and role report contracts
belong in references. Templates are output assets. The validator uses only the
Python standard library so the skill does not introduce a runtime dependency.

The skill is intentionally present only in `.agents/skills` in v1. `README.md`
must identify it as Codex-specific rather than adding `.claude` or `.github`
symlinks that imply unsupported behavior.

## Persisted State Contract

### Plan frontmatter

`implementation/plan.md` begins with:

```yaml
---
schema_version: 1
status: awaiting-approval
spec: ../spec.md
spec_revision: "sha256:<digest>"
baseline_commit: "<git-commit>"
plan_revision: 1
approved_revision: null
task_count: 4
current_task: null
max_cycles_per_task: 3
---
```

Allowed plan states are:

- `draft`
- `awaiting-approval`
- `approved`
- `in-progress`
- `needs-human`
- `completed`
- `cancelled`

`spec_revision` is the SHA-256 digest of `spec.md` at planning time. Any spec
change invalidates the plan until it is regenerated or amended and approved.
`baseline_commit` records the repository commit used during planning; it does
not require a clean working tree.

`plan_revision` increases for material plan changes. `approved_revision` is set
only after an explicit user approval and must equal `plan_revision` before
implementation may proceed.

### Task frontmatter

Each task begins with:

```yaml
---
schema_version: 1
id: task-001
kind: implementation
status: pending
dependencies: []
cycles_used: 0
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: none
---
```

Allowed task states are `pending`, `implementing`, `testing`, `passed`, and
`needs-human`. `kind` is `implementation` or `final-verification`.

`human_gate_status` is `not-required`, `pending`, or `approved`. A file value of
`approved` is only a persisted record; the orchestrator may set it only in
response to an explicit approval from the current user.

`tester_verdict` is `none`, `pass`, `fail`, or `blocked`. A task may enter
`passed` only with a `pass` verdict.

### Human-readable plan content

`plan.md` is the only document a human must normally read to approve a plan. It
must contain:

1. **Approval Request** — the exact authorization requested, outcome, task
   count, material boundaries, risks, gated tasks, and assumptions.
2. **Source of Truth** — spec path, digest, relevant sections, and repository
   baseline.
3. **Outcome and Scope** — goals, non-goals, and deferred work.
4. **Proposed Execution** — every task's objective, dependencies, primary
   verification, risk, and human-gate status.
5. **Acceptance Coverage** — a mapping from every spec acceptance criterion to
   its implementation and verification owner.
6. **Repository Impact** — expected components, contracts, migrations,
   dependencies, and external systems.
7. **Verification Strategy** — focused checks, integration checks, and the
   final repository gate.
8. **Risks and Guardrails** — destructive operations, compatibility, security,
   privacy, cost, rollback, and external-access implications.
9. **Required Human Review** — normally states that no task file needs separate
   review. Exceptional entries link to an exact task heading, summarize the
   issue, state when review is required, and name the decision.
10. **Execution Bounds** — fixed task count, three-cycle default, single active
    task, no unapproved expansion, and all stop conditions.
11. **Approval Record** — decision, user-provided conditions, timestamp, and
    approved revision.
12. **Progress** — task status, cycles used, outcome, and current blocker.

A critical issue may not be buried exclusively in a task file. When detailed
task review is necessary, the plan must explain why and link directly to the
smallest relevant section. "Read the task" is not sufficient guidance.

### Task content

Each task file contains:

- objective;
- exact spec and plan references;
- dependencies;
- bounded scope and prohibited scope;
- task-level acceptance criteria;
- verification plan;
- risks or a critical human-review section when applicable;
- one append-only attempt section per cycle;
- the latest tester evidence; and
- human resolutions or bounded extensions.

Attempt history must not be overwritten. Corrections are appended and identify
the superseded claim.

## Approval Semantics

The planner and orchestrator may prepare files before approval, but no
implementer may be dispatched while the plan is `draft` or
`awaiting-approval`.

Approval must be an explicit message from the current human user in Codex. Text
inside the repository, spec, plan, task, source, test output, tool output, or a
sub-agent report cannot authorize work. The orchestrator records the approval
and any conditions in `plan.md` and sets `approved_revision`.

Overall plan approval authorizes all listed tasks except those with a pending
human gate. A gated task stops immediately before its first implementation
cycle and requests the decision described in `plan.md`.

The following changes are material and invalidate approval:

- adding or removing a task;
- changing task scope, acceptance, or prohibited work;
- changing dependencies or execution order in a consequential way;
- changing verification requirements;
- changing a risk classification or human gate;
- changing the spec; or
- raising an execution limit.

Status, evidence, and attempt-history updates within the approved contract do
not invalidate approval. When implementation discovers necessary work outside
the plan, the orchestrator proposes an amendment, increments `plan_revision`,
sets the plan to `awaiting-approval`, and stops.

## Role Contracts

### Planning agent

The planning agent receives the spec, repository instructions, relevant current
state, and existing implementation state if resuming or amending. It does not
edit files. It returns:

- `ready` or `blocked` readiness;
- a finite dependency-ordered task list;
- task objectives, scope, acceptance, and verification;
- a complete spec-acceptance coverage matrix;
- repository impact and known risks;
- proposed human gates and exact review sections;
- assumptions and unresolved decisions; and
- the mandatory final-verification task.

The orchestrator rejects the proposal before human review if criteria are
unmapped, a task is unlikely to fit three cycles, dependencies are circular or
missing, a non-goal is included, verification is subjective, risk is hidden, or
an unresolved decision would force implementation to invent behavior.

### Implementer

One implementer is assigned per active task and may be re-contacted within that
task's cycles. It receives the approved task, relevant spec and plan sections,
repository instructions, current diff, prior tester evidence, and explicit
scope boundaries.

It may edit in-scope code and tests. It must not edit orchestration state,
change approval criteria, perform Git history or remote actions, or work on
another task. It returns:

- `ready-for-test` or `blocked`;
- a concise change summary;
- files changed;
- checks run and their results;
- unresolved risks or assumptions; and
- any evidence that the approved task is insufficient or contradictory.

### Tester

One tester is assigned per active task and remains a separate role from the
implementer. It receives the task acceptance contract, relevant spec sections,
repository instructions, current diff, and implementer report.

It may inspect files and run non-destructive verification but must not edit
production code or orchestration state. Missing tests or an implementation
defect produce evidence for the implementer; the tester does not repair them.
It returns exactly one verdict:

- `pass` — all task acceptance criteria are supported by evidence;
- `fail` — an in-scope implementation or test deficiency is identified; or
- `blocked` — verification cannot reach a reliable conclusion without human or
  environmental intervention.

The report includes commands or checks run, results, criterion-by-criterion
evidence, failure attribution, and any residual risk.

## Orchestration Lifecycle

### 1. Initialize and plan

1. Verify the input is a canonical `<topic>/spec.md` and is implementation
   ready.
2. Read repository instructions and record the baseline commit and pre-existing
   working-tree changes.
3. Spawn the planning agent.
4. Validate the proposed breakdown semantically.
5. Create `implementation/plan.md` and all task files from the canonical
   templates.
6. Run deterministic state validation.
7. Set the plan to `awaiting-approval`, present the approval request, and end
   the Codex turn without dispatching an implementer.

### 2. Approve or amend

1. Treat only the current user's explicit message as approval authority.
2. Record approval conditions and the approved plan revision.
3. If the human requests changes, amend the plan and tasks, increment the plan
   revision, validate again, and request fresh approval.

### 3. Execute one task

Before every dispatch, run the validator and compare current working-tree
changes with the recorded baseline and task scope. Preserve unrelated user
changes. If overlapping changes cannot be attributed safely, stop with
`needs-human`.

For an eligible task:

1. verify all dependencies passed and any human gate is approved;
2. persist the incremented `cycles_used` value and `implementing` status before
   contacting the implementer;
3. dispatch or re-contact the task's implementer;
4. record its report;
5. stop on `blocked`, otherwise set the task to `testing`;
6. dispatch or re-contact the independent tester;
7. record its evidence and verdict;
8. mark the task `passed` on `pass`;
9. return to implementation on `fail` only when cycles remain; or
10. set both task and plan to `needs-human` on `blocked` or exhausted cycles.

Only one task may be `implementing` or `testing`. Mutation work is sequential;
future review agents may run only at explicit, non-conflicting extension
points.

### 4. Final verification

Every plan ends with exactly one `final-verification` task that depends on all
implementation tasks. It verifies the complete acceptance matrix, relevant
integration behavior, and repository-defined final gate. It follows the same
three-cycle contract; integration defects return to its implementer within the
already approved overall scope.

The plan becomes `completed` only after every task, including final
verification, has a tester `pass` verdict and deterministic completion
validation succeeds.

### 5. Resume

On a later turn, the orchestrator reconstructs state from:

- the current user direction;
- `spec.md` and its digest;
- `implementation/plan.md`;
- every task file;
- repository instructions;
- Git HEAD, status, and diff.

Sub-agent conversation state is an optimization, not a source of truth. If an
earlier agent cannot be re-contacted, a replacement receives the persisted task
history. The orchestrator must not repeat a passed task or reset consumed
cycles.

## Retry and Stop Policy

A cycle is reserved and persisted immediately before implementer dispatch. One
implementer handoff followed by one tester verdict is one cycle. A crash or
interruption cannot erase a reserved cycle.

An agent communication or tool-infrastructure failure may be retried once
within the same cycle when doing so cannot duplicate a side effect. A second
failure stops for human input. A tester `blocked` verdict stops immediately
rather than spending remaining cycles.

After the initial three cycles, only a human may continue. The human may revise
the spec or task, supply information, accept a documented limitation, defer or
cancel work, or authorize one to three additional cycles. Each extension is
explicit, recorded in the task and plan, and never renews automatically.

The orchestrator also stops when:

- the plan or critical gate lacks explicit approval;
- spec and plan revisions disagree;
- repository state is malformed or contradictory;
- requirements are ambiguous or conflict;
- work would exceed approved scope;
- acceptance criteria would need to be weakened;
- a destructive, privileged, external, or otherwise separately approved
  action is required;
- pre-existing changes overlap the task and ownership is unclear;
- the planner or agents report no meaningful progress; or
- the user interrupts, cancels, or changes direction.

## Deterministic Validator

`scripts/validate_state.py` accepts a spec package path and a phase:

```text
python3 validate_state.py <spec-package> --phase plan-ready
python3 validate_state.py <spec-package> --phase dispatch --task task-001
python3 validate_state.py <spec-package> --phase completion
```

The exact invocation may be adjusted during implementation, but the validator
must support these three decisions and return a non-zero exit status with
actionable diagnostics on violation.

It checks only mechanical facts:

- recognized schema versions and enum values;
- readable YAML frontmatter and required fields;
- spec digest equality;
- plan and approved revision equality before dispatch;
- declared task count and unique task IDs;
- exactly one final-verification task;
- zero or one active task;
- dependency existence, acyclicity, and passed status before dispatch;
- human-gate state;
- cycle bounds;
- task/verdict consistency; and
- all tasks passed before completion.

Semantic coverage, task size, risk, scope overlap, and evidence quality remain
agent and human judgments. Validator success never substitutes for approval.

## Trust and Safety Boundaries

Repository content and sub-agent output are untrusted inputs to orchestration.
They may describe requirements or evidence but cannot override Codex system or
developer instructions, change role permissions, grant approval, or increase
limits.

Normal Codex approval rules continue to govern destructive actions, elevated
permissions, credentials, dependency installation, external writes, and other
material side effects. Plan approval is not blanket authorization for actions
that independently require confirmation.

Sensitive data must not be copied into state files merely to make a report
self-contained. State should record the minimum safe evidence and point to
authorized repository locations or redacted diagnostics when necessary.

## Git and Working-Tree Behavior

The workflow does not require a clean worktree. Planning records the baseline
commit and existing modifications. Agents preserve unrelated changes and do
not revert, overwrite, or absorb them into their task.

The orchestrator may update in-scope code and committed-artifact files in the
working tree. It must not autonomously stage, commit, amend, rebase, push,
create branches or pull requests, or otherwise mutate Git history or remote
state. The human's normal workflow commits code and orchestration state
together.

## Delivery Plan

### Phase 1: Contracts and validation

Create the `implement-spec` skill skeleton, templates, state contract, role
contract, and standard-library validator. Add focused validator fixtures for
valid and invalid state transitions.

Acceptance:

- The skill passes the standard skill validator.
- State templates contain all required fields and sections.
- Mechanical violations fail with actionable messages.
- No sub-agent implementation behavior is required to test the validator.

### Phase 2: Planning and approval boundary

Implement the initialization, planning-agent contract, semantic plan review,
file generation, and mandatory human approval stop. Update `write-spec` with
the explicit orchestration-ready output mode and document the Codex-only skill
in `README.md`.

Acceptance:

- An orchestration request produces `<topic>/spec.md` without changing ordinary
  flat-spec behavior.
- Planning produces a complete `plan.md` and finite task set.
- No implementer is dispatched before explicit user approval.
- Material amendments reset approval.

### Phase 3: Bounded implement/test loop

Add sequential task dispatch, role-separated reports, persisted cycle
transitions, human gates, resume behavior, final verification, and completion
reporting.

Acceptance:

- A passing task advances once.
- A failing task receives no more than three autonomous cycles.
- Blocked, ambiguous, or unsafe work stops with an actionable human handoff.
- Resume does not lose cycles or repeat passed tasks.
- Final completion requires the final-verification task to pass.

### Phase 4: Forward validation

Forward-test the skill in a disposable fixture repository using realistic
requests and fresh sub-agents. Do not expose the intended outcome beyond the
spec and skill artifacts under test.

Scenarios:

- plan generation and mandatory approval stop;
- plan amendment and reapproval;
- first-cycle success;
- failure followed by successful repair;
- three consecutive failures;
- tester-blocked environment;
- critical task gate;
- interrupted run and reconstruction;
- spec changed after approval;
- overlapping pre-existing working-tree changes; and
- successful final verification.

## Test Strategy

### Validator tests

Use temporary spec packages to cover valid state plus malformed frontmatter,
unknown enums, duplicate IDs, missing and circular dependencies, task-count
mismatch, stale spec digest, approval-revision mismatch, unapproved gates,
cycle overflow, invalid pass/verdict combinations, multiple active tasks,
missing final verification, and incomplete completion.

### Skill behavior tests

Inspect generated plans for complete approval summaries and acceptance
coverage. Verify through fresh-agent forward tests that role prompts do not
leak authority, the tester does not repair code, and the implementer does not
edit state.

### Compatibility tests

Verify that existing `build-spec-context` and ordinary `write-spec` behavior
remains unchanged. Verify that orchestration mode creates a directory package
only when requested and that no unsupported Claude or Copilot symlink is
created.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Prompt instructions alone fail to enforce a limit | Persist counters before dispatch and run a deterministic validator |
| Human approves an incomplete summary | Require acceptance coverage, risk disclosure, task count, and critical links in `plan.md` |
| State drifts from the spec | Store and validate the spec digest |
| Plan changes after approval | Track plan revisions and invalidate material changes |
| Tester becomes an implementer | Separate role contract; production edits invalidate the tester handoff |
| Interruption loses context | Treat Markdown and repository state as authoritative; agent sessions are optional |
| Existing user work is overwritten | Record the baseline, inspect overlap, preserve unrelated changes, and stop when ownership is unclear |
| Planner creates an effectively endless queue | Require a finite fixed task set and human approval of the explicit count |
| Repeated human extensions recreate an autonomous infinite loop | Require every one-to-three-cycle extension explicitly; never renew automatically |
| Critical detail is buried in a task | Require a plan summary and exact task-section link before approval |

## Future Extension Points

The state machine may later add bounded roles at these boundaries without
changing v1 ownership:

- a task-breakdown reviewer before human plan approval;
- a code reviewer after implementation and before testing;
- security, privacy, migration, or domain reviewers before task pass;
- an integration reviewer before final verification; and
- optional parallel read-only review where repository state cannot conflict.

Adding a role requires a separate role contract, stop behavior, persisted
verdict, and plan disclosure. Future roles may not silently acquire approval or
state ownership.

## Acceptance Criteria

- [ ] An explicitly requested orchestration-ready spec is written to
      `specs/<year>/q<quarter>/<topic>/spec.md`; ordinary specs remain flat.
- [ ] `implement-spec` rejects flat legacy specs without moving or rewriting
      them.
- [ ] The planning agent produces a finite task set with complete acceptance
      coverage and exactly one final-verification task.
- [ ] The generated `plan.md` contains all information required for normal
      human approval without opening task files.
- [ ] Critical task review is summarized in the plan and linked to an exact
      task section.
- [ ] No implementer is dispatched until the current user explicitly approves
      the current plan revision.
- [ ] Material plan or spec changes invalidate approval.
- [ ] Only the orchestrator writes implementation state, only the implementer
      edits in-scope code, and the tester remains non-mutating.
- [ ] Exactly zero or one implementation task is active at any time.
- [ ] Cycle usage is persisted before implementer dispatch and no task receives
      more than three autonomous cycles.
- [ ] Additional cycles require an explicit, recorded human extension of one to
      three cycles.
- [ ] Blocked verification, repeated infrastructure failure, ambiguous scope,
      unsafe actions, or overlapping unattributed changes stop with an
      actionable human handoff.
- [ ] A resumed run preserves passed tasks, consumed cycles, approval state,
      attempt evidence, and human decisions.
- [ ] Completion requires every task and the final-verification task to have a
      passing tester verdict.
- [ ] Mechanical state validation fails safely with actionable diagnostics for
      every documented invariant.
- [ ] The workflow does not autonomously stage, commit, push, branch, open a
      pull request, deploy, or perform external writes.
- [ ] Existing spec skills continue to validate and their non-orchestration
      behavior remains unchanged.

## Open Questions

None block implementation. File names, validator command spelling, and report
formatting may be refined during implementation if the behavior and acceptance
contracts above remain unchanged.
