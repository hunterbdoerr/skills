---
schema_version: 1
status: needs-human
spec: ../spec.md
spec_revision: "sha256:1af2331cb83cfc5a94f85ef74816ad12693cc9658159c940378be19e0b934e6d"
baseline_commit: "d42efa9562fda591899bfdc9cbc83d0b1e73a921"
plan_revision: 7
approved_revision: 7
task_count: 21
current_task: null
max_cycles_per_task: 3
---

# Bounded Spec Implementation Orchestration — Implementation Plan

## Approval Request

Approve revision 7 to continue the Codex-only `implement-spec` work through a
fixed twenty-one-task plan. Tasks 001–010 and 017 remain passed. Task 011
preserves all three consumed cycles and every report.

- Authorization requested: give Task 011 exactly one no-change closure cycle,
  raising its limit from `3` to `4`, so a fresh independent tester can confirm
  the already-demonstrated basic success-transition boundary.
- Scope transfer: move only complete reservation/contacted-implementer
  integrity to Task 018, internally captured tester-baseline integrity to Task
  019, and immutable distinct-role/pass evidence to Task 020.
- Unchanged contract: one read-only planner is allowed only for initial plan
  generation or material amendment; each execution task has one direct,
  non-delegating implementer and one different independent direct tester.
- Material boundaries: no code or test edits in Task 011 Cycle 4; no reset or
  refund of consumed cycles; no replay of passed tasks; Tasks 018–020 may edit
  only `tests/test_success_role_ownership.py`; no Git-history, remote,
  deployment, destructive, or external writes.
- Material risks: the plan gains three tasks and one narrowly bounded closure
  cycle; Task 011 is not recorded as passed without a fresh tester verdict;
  sequential tasks share one fixture file and must preserve prior guards.
- Overall spec acceptance criteria: unchanged.
- Gated tasks: none.

## Source of Truth

- Spec: [`../spec.md`](../spec.md)
- Spec revision:
  `sha256:1af2331cb83cfc5a94f85ef74816ad12693cc9658159c940378be19e0b934e6d`
- Relevant sections: Decision Summary, Goals, Source-of-Truth and Ownership,
  Role Contracts, Orchestration Lifecycle, Delivery Plan Phase 4, Test
  Strategy, Risks and Mitigations, and Acceptance Criteria.
- Amendment baseline: `d42efa9562fda591899bfdc9cbc83d0b1e73a921`
- Original revision-1 baseline: `048a0985a6b9a83db36f6427988d4c71b15ddd46`
- Pre-existing working-tree changes: none before this amendment; current
  changes are the user-requested spec and orchestration-state amendment.

## Outcome and Scope

### Goals

- Preserve one bounded planning pass for initial plan creation or material
  amendment.
- Require every execution task to be explicit and small enough for one direct
  implementer without delegation.
- Preserve one independent direct tester/reviewer after each implementer
  cycle.
- Replace nested-agent forward validation with small deterministic disposable
  fixture scenarios and objective state, validator, and Git evidence.
- Preserve all passed work, consumed cycles, attempt reports, and human
  decisions.

### Non-goals

- Removing the initial/material-amendment planning boundary.
- Allowing an orchestrator, implementer, or tester to self-approve or weaken
  acceptance.
- Replaying Tasks 001–006 or resetting Task 007.
- Adding parallel mutation, autonomous Git actions, deployments, network
  access, services, or external integrations.

### Deferred work

- Live end-to-end model-runtime forward testing outside the bounded shared
  agent environment.

## Proposed Execution

| Order | Task | Objective | Dependencies | Primary verification | Risk | Human gate |
|---:|---|---|---|---|---|---|
| 1 | [`task-001`](tasks/task-001-scaffold-skill.md) | Preserve passed skill scaffold | None | Final structure review | Low | Not required |
| 2 | [`task-002`](tasks/task-002-contracts-templates.md) | Preserve passed state and role contracts | 001 | Final contract review | Low | Not required |
| 3 | [`task-003`](tasks/task-003-validator.md) | Preserve passed deterministic validator | 002 | Full validator suite | Low | Not required |
| 4 | [`task-004`](tasks/task-004-write-spec-packaging.md) | Preserve passed packaging behavior | 001 | Task 008 and final checks | Low | Not required |
| 5 | [`task-005`](tasks/task-005-planning-approval.md) | Preserve passed initial planning and approval boundary | 002, 003, 004 | Tasks 009–010 | Low | Not required |
| 6 | [`task-006`](tasks/task-006-bounded-loop.md) | Preserve passed bounded implement/review loop | 003, 005 | Tasks 011–016 | Low | Not required |
| 7 | [`task-007`](tasks/task-007-forward-test-planning.md) | Codify one planning boundary and non-delegating execution roles | 002, 005, 006 | Contract assertions and skill validation | Medium | Not required |
| 8 | [`task-008`](tasks/task-008-forward-test-retries.md) | Validate packaging and canonical-input behavior | 004, 007 | Focused disposable-fixture tests | Low | Not required |
| 9 | [`task-009`](tasks/task-009-forward-test-resume.md) | Validate plan generation and approval-summary contracts | 003, 005, 007 | Fixed planner-report fixtures | Medium | Not required |
| 10 | [`task-017`](tasks/task-017-malformed-planner-reports.md) | Harden malformed planner-report parsing | 009 | Focused malformed-input and no-exception fixtures | Medium | Not required |
| 11 | [`task-010`](tasks/task-010-approval-amendments-gates.md) | Validate approval, amendments, gates, trust text, and spec drift | 005, 006, 007, 009, 017 | Approval-state fixtures and validator checks | Medium | Not required |
| 12 | [`task-011`](tasks/task-011-success-role-ownership.md) | Close the amended basic success transition | 003, 006, 007 | No-change fixture and evidence review | Medium | Not required |
| 13 | [`task-018`](tasks/task-018-reservation-implementer-identity.md) | Bind complete reservation and contacted implementer identity | 003, 006, 007, 011 | Reservation/identity regressions | Medium | Not required |
| 14 | [`task-019`](tasks/task-019-internal-tester-baseline.md) | Capture the tester baseline internally | 018 | Baseline-laundering regressions | Medium | Not required |
| 15 | [`task-020`](tasks/task-020-sealed-pass-evidence.md) | Seal immutable distinct-role pass evidence | 019 | Identity/evidence-seal regressions | Medium | Not required |
| 16 | [`task-012`](tasks/task-012-repair-exhaustion-extensions.md) | Validate repair, exhaustion, and bounded extensions | 003, 006, 007, 011, 020 | Cycle-transition fixture suite | Medium | Not required |
| 17 | [`task-013`](tasks/task-013-blocked-infrastructure-stops.md) | Validate blocked testing and infrastructure stops | 006, 007, 011, 020 | Stop-branch fixtures | Low | Not required |
| 18 | [`task-014`](tasks/task-014-resume-reconstruction.md) | Validate interruption and state reconstruction | 002, 006, 007, 011, 012, 020 | Resume fixture suite | Medium | Not required |
| 19 | [`task-015`](tasks/task-015-safety-overlap-git.md) | Validate safety, overlap, Git, and external-action guardrails | 006, 007, 013, 014 | Harmless pre/post Git inspection | High | Not required |
| 20 | [`task-016`](tasks/task-016-completion-transitions.md) | Validate final-task and completion transitions | 003, 006, 007–015, 017–020 | Completion fixture suite | Medium | Not required |
| 21 | [`task-final-verification`](tasks/task-final-verification.md) | Verify the complete amended spec | 001–020 | Full repository gate | High | Not required |

## Acceptance Coverage

| Spec acceptance criterion | Implementation owner | Verification owner |
|---|---|---|
| AC-01: explicit packages and ordinary flat specs | 004 | 008, Final |
| AC-02: flat legacy specs rejected without mutation | 005 | 008, Final |
| AC-03: one planning boundary yields finite complete tasks and one final task | 002, 005, 007, 017 | 009, 017, Final |
| AC-04: `plan.md` is sufficient for normal approval | 002, 005, 017 | 009, 017, Final |
| AC-05: critical review is summarized and exactly linked | 002, 005 | 009, 010, Final |
| AC-06: current-user approval precedes implementation | 005, 017 | 009, 010, 017, Final |
| AC-07: material changes invalidate approval | 003, 005, 006 | 010, Final |
| AC-08: one non-delegating implementer and independent tester per task | 002, 005, 006, 007, 018, 019, 020 | 011, 018, 019, 020, Final |
| AC-09: zero or one active task | 003, 006, 018 | 011, 018, Final |
| AC-10: cycles persist before dispatch and stop at three | 003, 006 | 012, Final |
| AC-11: extensions require explicit current-user authorization | 002, 003, 006 | 012, Final |
| AC-12: blocked, malformed, unsafe, ambiguous, mutation-tainted, and overlapping work stops | 006, 017, 018, 019, 020 | 013, 015, 017, 018, 019, 020, Final |
| AC-13: resume preserves state and evidence | 002, 006 | 014, Final |
| AC-14: completion requires all tasks and final verification to pass | 003, 006 | 016, Final |
| AC-15: validator failures are safe and actionable | 003 | 003, Final |
| AC-16: no autonomous Git, deployment, or external writes | 005, 006 | 015, Final |
| AC-17: existing spec-skill behavior remains valid | 001, 004 | 008, Final |

## Repository Impact

- Components: `.agents/skills/implement-spec/`, focused standard-library
  tests, `spec.md`, and implementation plan/task state.
- Contracts: one planning boundary; task semantic review must reject delegated
  or oversized work; implementer and tester roles are direct and
  non-delegating; independent tester review remains mandatory.
- Migrations: none.
- Dependencies: none; Python standard library only.
- External systems: none; live external model calls and nested-agent scenario
  execution are excluded from Tasks 007–020.

## Verification Strategy

- Focused checks: one small standard-library scenario module per task family,
  canonical template/static contract assertions, validator phase checks, and
  disposable Git fixture comparisons.
- Integration checks: full unit discovery, skill validation, role/template
  consistency, complete acceptance mapping, and scenario evidence review.
- Final repository gate: compile the validator with an isolated bytecode cache;
  run all `test_*.py` tests; validate every canonical skill; run direct
  `plan-ready`, `dispatch`, and `completion` smoke cases; run
  `git diff --check`; inspect status, index, refs, logs, and symlinks.

## Risks and Guardrails

| Area | Risk or implication | Guardrail / rollback |
|---|---|---|
| Validation realism | Deterministic fixtures do not prove live model-runtime behavior | Preserve realistic state/Git fixtures and independent review; defer live runtime testing |
| Task 011 closure | A no-change fourth cycle could be mistaken for a fabricated pass | Preserve all failures and require a fresh independent pass on the narrowed boundary |
| Shared fixture | Tasks 018–020 edit the same test module sequentially | Chain dependencies, exact one-file scope, full regression suite, and independent review per task |
| Evidence claim | Synthetic immutability could be overstated as runtime security | Require exact substitution regressions and describe fixture enforcement precisely |
| Existing changes | Later work could overwrite attributed prior work | Compare pre/post status, hashes, and diffs; stop on unattributable overlap |
| Destructive/external effects | Safety tests could accidentally perform prohibited work | Use synthetic local fixtures; prohibit escalation, network, Git history, and external writes |

## Required Human Review

No task file requires a separate critical gate. Approval of revision 7 must
explicitly authorize the fixed twenty-one-task count, Task 011's no-change
Cycle 4 and `3` to `4` limit, and transfer of the remaining integrity surface
to Tasks 018–020.

## Execution Bounds

- The approved task count is fixed at 21, including exactly one final task.
- Execute at most one task at a time.
- Planning occurs only at initial plan creation or material amendment.
- Every execution task uses one direct implementer and one different direct
  tester/reviewer; neither may delegate or spawn a planner/sub-agent.
- Reserve and persist a cycle before each implementer dispatch.
- Keep the default three-cycle limit; passed Task 007 retains all 3 / 3 used.
- Passed Task 009 retains all 7 / 7 consumed cycles; no further Task 009 cycle
  is authorized.
- Task 011 retains three consumed cycles and may use exactly one revision-7
  no-change closure cycle, for a limit of 4.
- Do not reset cycles, replay passed work, weaken acceptance, or amend scope
  without a new plan revision and explicit approval.
- Do not autonomously stage, commit, branch, push, open a pull request, deploy,
  access external systems, or perform destructive actions.

## Approval Record

- Revision 1: approved by the current user at `2026-09-01T02:02:23Z` with the
  condition to execute within documented bounds.
- Revision 1 execution stop: Task 007 reached `needs-human` after two
  nested-agent capacity blocks; no product or fixture state was accepted as a
  passing result.
- Revision 2 decision: approved by the current user.
- Revision 2 user-provided conditions: none beyond the disclosed revision-2
  contract.
- Revision 2 timestamp: `2026-09-01T16:38:13Z`.
- Approved revision: 2.
- Revision 3 extension: approved by the current user at
  `2026-09-01T17:42:03Z`; add exactly one Task 009 cycle, raising its limit
  from 3 to 4, with no scope, acceptance, dependency, or side-effect change.
- Approved revision: 3.
- Revision 4 extension: approved by the current user at
  `2026-09-01T17:53:54Z`; add exactly one Task 009 cycle, raising its limit
  from 4 to 5, with scope limited to impact-specific risk matching and strict
  malformed-section rejection.
- Approved revision: 4.
- Revision 5 extension: approved by the current user at
  `2026-09-01T19:20:21Z`; add exactly one Task 009 cycle, raising its limit
  from 5 to 6, restricted to task-kind/ID/file validation, complete-document
  consumption, and explicit impact-to-risk identity.
- Approved revision: 5.
- Revision 6 decision: approved by the current user at
  `2026-09-01T20:27:24Z`.
- Revision 6 conditions: Task 009 no-change closure cycle, Task 017 transfer,
  fixed task count 18, and unchanged spec acceptance.
- Revision 6 authorization: "I approve plan revision 6, including Task 009's
  no-change Cycle 7 and the new Task 017."
- Approved revision: 6.
- Revision 7 decision: approved by the current user at
  `2026-09-01T23:17:10Z`.
- Revision 7 requested conditions: preserve Task 011's three cycles and all
  evidence; authorize its no-change Cycle 4; add Tasks 018–020; fixed task
  count 21; unchanged spec acceptance.
- Revision 7 authorization: "I approve plan revision 7, including Task 011's
  no-change Cycle 4, Tasks 018–020, and the fixed 21-task count."
- Approved revision: 7.

## Progress

| Task | Status | Cycles used / limit | Outcome | Current blocker |
|---|---|---:|---|---|
| `task-001` | passed | 1 / 3 | scaffold passed | none |
| `task-002` | passed | 2 / 3 | contracts/templates passed | none |
| `task-003` | passed | 1 / 3 | validator passed | none |
| `task-004` | passed | 1 / 3 | packaging passed | none |
| `task-005` | passed | 1 / 3 | planning/approval boundary passed | none |
| `task-006` | passed | 1 / 3 | bounded loop passed | none |
| `task-007` | passed | 3 / 3 | no-delegation contract passed independent review | none |
| `task-008` | passed | 1 / 3 | packaging/canonical-input scenarios passed | none |
| `task-009` | passed | 7 / 7 | amended planning/approval-summary boundary passed fresh independent review | none |
| `task-017` | passed | 2 / 3 | malformed planner-report parsing passed independent review | none |
| `task-010` | passed | 1 / 3 | approval/amendment/gate scenarios passed independent review | none |
| `task-011` | passed | 4 / 4 | amended basic success transition passed fresh independent review | none |
| `task-018` | needs-human | 3 / 3 | identity binding aliases equal/hash objects and registry is forgeable | cycles exhausted; extension or amendment required |
| `task-019` | pending | 0 / 3 | internal tester baseline pending | task-018 |
| `task-020` | pending | 0 / 3 | sealed pass evidence pending | task-019 |
| `task-012` | pending | 0 / 3 | pending | dependencies |
| `task-013` | pending | 0 / 3 | pending | dependencies |
| `task-014` | pending | 0 / 3 | pending | dependencies |
| `task-015` | pending | 0 / 3 | pending | dependencies |
| `task-016` | pending | 0 / 3 | pending | dependencies |
| `task-final-verification` | pending | 0 / 3 | pending | all implementation tasks |

Current task: none.

- Amendment note: the nested-capacity validation method is superseded, not
  erased. Task 007 retains both blocked attempts and their evidence.
- Execution stop at `2026-09-01T17:39:37Z`: Task 009 exhausted all three
  cycles. Its final tester found that accepted external-system, additional-risk,
  assumption-none, and final-verification values do not yet round-trip safely
  into the approval plan. No later task was dispatched.
- Extension at `2026-09-01T17:42:03Z`: the current user authorized exactly one
  additional Task 009 cycle. Plan revision 3 records and approves the new
  `4`-cycle limit; all other revision-2 terms remain unchanged.
- Execution stop at `2026-09-01T17:47:26Z`: Task 009 Cycle 4 failed because
  same-category but unrelated migration risks and malformed non-bullet section
  content can still be accepted and omitted from the approval plan.
- Extension at `2026-09-01T17:53:54Z`: the current user authorized exactly one
  additional Task 009 cycle. Plan revision 4 records and approves the new
  `5`-cycle limit; all other terms remain unchanged.
- Execution stop at `2026-09-01T17:59:16Z`: Task 009 Cycle 5 failed because
  task kinds are not enum-validated, unmatched top-level report prose is not
  rejected, and migration/dependency risk matching remains heuristic.
- Extension at `2026-09-01T19:20:21Z`: the current user authorized exactly one
  additional Task 009 cycle. Plan revision 5 records and approves the new
  `6`-cycle limit; all other terms remain unchanged.
- Execution stop at `2026-09-01T19:25:28Z`: Task 009 Cycle 6 failed because
  empty Status/Blocker scalars can crash parsing and blank required task or
  coverage sections can be accepted on blocked reports.
- Revision 6 amendment prepared: preserve Task 009 history, authorize one
  no-change closure cycle, and transfer the remaining malformed-input surface
  to new Task 017 without weakening overall acceptance.
- Revision 6 approved at `2026-09-01T20:27:24Z` by the current user exactly as
  disclosed, including Task 009's no-change Cycle 7 and new Task 017.
- Task 009 Cycle 7 reserved at `2026-09-01T20:27:24Z` for a no-change
  readiness check by `/root/task_009_cycle_1_implementer` followed by fresh
  independent review.
- Task 009 passed Cycle 7 at `2026-09-01T20:31:21Z`; all amended criteria
  passed without code/test changes, and the transferred malformed-input
  surface remains pending in Task 017.
- Task 017 Cycle 1 reserved at `2026-09-01T20:31:44Z` for direct implementation
  by `/root/task_017_cycle_1_implementer`.
- Task 017 Cycle 1 failed review at `2026-09-01T20:38:33Z` because whitespace-
  altered `- none` forms were accepted; Cycle 2 was reserved for the exact
  raw-section comparison and missing near-match tests.
- Task 017 passed Cycle 2 at `2026-09-01T20:42:05Z`; all malformed-scalar,
  blank-section, exact-`none`, deterministic-fuzz, and valid-path criteria
  passed independent review.
- Task 010 Cycle 1 reserved at `2026-09-01T20:42:25Z` for direct implementation
  by `/root/task_010_cycle_1_implementer`.
- Task 010 passed Cycle 1 and Task 011 Cycle 1 was reserved at
  `2026-09-01T20:49:31Z` for direct implementation by
  `/root/task_011_cycle_1_implementer`.
- Task 011 Cycle 1 failed review and Cycle 2 was reserved at
  `2026-09-01T20:56:53Z` for complete reservation, path, criterion, active-
  state, and tester-gated-pass enforcement.
- Task 011 Cycle 2 failed review and final Cycle 3 was reserved at
  `2026-09-01T21:01:53Z` for bound role identity, immutable reviewed snapshot,
  required file presence, and coherent pass-state validation.
- Execution stopped at `2026-09-01T21:09:24Z`: Task 011 exhausted Cycle 3.
  Complete reservation validation, structurally bound contacted identity,
  internally captured tester baseline, and immutable distinct-role evidence
  remain unsatisfied. No later task was dispatched.
- Revision 7 amendment prepared at the current user's direction: preserve all
  Task 011 history, authorize one no-change closure cycle, and split the four
  remaining integrity classes into Tasks 018–020 without weakening acceptance.
- Revision 7 approved at `2026-09-01T23:17:10Z` by the current user exactly as
  disclosed, including Task 011's no-change Cycle 4, Tasks 018–020, and the
  fixed 21-task count.
- Task 011 Cycle 4 reserved at `2026-09-01T23:17:33Z` for a no-change readiness
  check by `/root/task_011_cycle_1_implementer` followed by fresh independent
  review.
- Task 011 passed Cycle 4 at `2026-09-01T23:20:29Z`; all amended criteria
  passed without source changes and the remaining integrity work remains
  exclusively assigned to Tasks 018–020.
- Task 018 Cycle 1 reserved at `2026-09-01T23:20:48Z` for direct implementation
  by `/root/task_018_cycle_1_implementer`.
- Task 018 Cycle 1 failed review and Cycle 2 was reserved at
  `2026-09-01T23:29:17Z` for strict reservation/role types and authoritative
  contacted-identity receipt validation.
- Task 018 Cycle 2 failed review and final Cycle 3 was reserved at
  `2026-09-01T23:35:19Z` for an original-contact binding outside replaceable
  fixture state and copied-instance rejection.
- Execution stopped at `2026-09-01T23:40:25Z`: Task 018 exhausted Cycle 3.
  Strict reservation/type and ordinary substitution cases pass, but weak-key
  equality/hash aliasing and globals-reachable registry forgery remain. No
  later task was dispatched.
