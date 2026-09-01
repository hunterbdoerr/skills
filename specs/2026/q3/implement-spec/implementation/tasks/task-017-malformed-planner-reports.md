---
schema_version: 1
id: task-017
kind: implementation
status: passed
dependencies: [task-009]
cycles_used: 2
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: pass
---

# Task 017: Harden malformed planner-report parsing

## Objective

Make malformed planner-report parsing deterministic and exception-safe for the
small residual input surface transferred from Task 009.

## Spec References

- Planning Agent
- Orchestration Lifecycle, Initialize and Plan
- Trust and Safety Boundaries
- AC-03, AC-04, AC-06, and AC-12

## Plan References

- [`Proposed Execution`](../plan.md#proposed-execution)
- [`Acceptance Coverage`](../plan.md#acceptance-coverage)
- [`Verification Strategy`](../plan.md#verification-strategy)

## Dependencies

- `task-009` must be passed.

## Scope

### In scope

- Clarify only the explicit-`none` planner-report grammar in
  `.agents/skills/implement-spec/references/role-contracts.md` when needed to
  make the expected valid blocked-report representation unambiguous.
- Harden the focused parser fixture and add tests only in
  `.agents/skills/implement-spec/tests/test_planning_contracts.py`.
- Cover empty and whitespace-only `Status:` and `Blocker:` scalars, blank Task
  list and Acceptance coverage sections, exact `- none` blocked-report
  representations, and deterministic malformed-input/no-exception cases.

### Prohibited scope

- No changes to `validate_state.py`, canonical plan/task templates, the spec,
  persisted plan/task state other than orchestrator-owned bookkeeping, or
  unrelated product code/tests.
- No changes to Task 009's original semantic/report-authority behavior.
- No planner, live model call, external write, or destructive/Git-history
  action.
- Spawning or delegating to a planner, helper, or sub-agent.

## Acceptance Criteria

- [ ] Empty or whitespace-only `Status:` and `Blocker:` values produce
      structured validation errors and never raise exceptions.
- [ ] Missing, duplicate, invalid, or status-inconsistent scalar values are
      rejected.
- [ ] Blank Task list or Acceptance coverage sections are rejected.
- [ ] A blocked report may use exact `- none` in the transferred sections; a
      ready report may not use that representation.
- [ ] Deterministic malformed cases, including a fixed-seed bounded fuzz set,
      never raise an exception and never create state, request approval, or
      dispatch implementation.
- [ ] Existing valid ready and explicit-`none` blocked paths continue to work.

## Verification Plan

- Run the focused planning-contract scenario tests.
- Run all standard-library `test_*.py` discovery for the skill.
- Inspect the diff to confirm changes are limited to the two allowed files.
- Run `git diff --check`.

## Execution Roles

- Implementer: one direct implementer performs the bounded work itself and
  must not spawn or delegate to a planner, helper, or sub-agent.
- Tester/reviewer: one different, independent direct tester performs the
  verification itself, remains read-only, and must not spawn or delegate to a
  planner, helper, or sub-agent.

## Risks

- The fixture parser is test infrastructure rather than the production state
  validator; keep the repair limited to the transferred report-input boundary
  and preserve valid report behavior.

## Critical Human Review

Not required.

## Attempts

### Cycle 1

#### Reservation

- Reserved at: 2026-09-01T20:31:44Z
- Starting status: implementing
- Implementer: `/root/task_017_cycle_1_implementer`

#### Implementer Report

- Status: ready-for-test
- Change summary: Hardened planner-report fixture parsing so malformed scalar
  values, blank required sections, and invalid explicit-`none` usage return
  structured errors without exceptions or side effects; defined the exact
  blocked-report `- none` grammar; added deterministic malformed and fixed-seed
  fuzz cases while preserving valid ready and blocked paths.
- Files changed:
  `.agents/skills/implement-spec/references/role-contracts.md` and
  `.agents/skills/implement-spec/tests/test_planning_contracts.py`.
- Checks and results: all 18 focused and all 53 implement-spec tests passed;
  isolated module compilation, `git diff --check`, and static two-file scope
  inspection passed.
- Residual risks or assumptions: The hardened parser remains fixture test
  infrastructure rather than the production state validator, as required.
- Contract issue: none
- Blocker: none

#### Tester Report

- Tester: `/root/task_017_cycle_1_tester`
- Verdict: fail
- Checks and results: all 18 focused and all 53 implement-spec tests passed;
  isolated compilation, `git diff --check`, scope inspection, and pre/post
  hashes passed. An independent adversarial probe showed that leading-space
  ` - none` and trailing-space `- none ` were accepted in both transferred
  sections because the parser strips the raw section before comparison.
- Criterion-by-criterion evidence: empty/whitespace, missing, duplicate,
  invalid, and inconsistent scalars reject safely; blank required sections
  reject; deterministic and fixed-seed malformed inputs have no exception or
  side effect; valid ready and exact blocked paths work. The exact-`- none`
  criterion is unsatisfied because whitespace-altered near matches also pass.
- Failure attribution: implementation defect and missing near-match test in
  `report_structure_errors()`.
- Residual risk: no additional defect observed; the parser remains fixture
  infrastructure rather than the production validator.
- Required next action: compare raw section content exactly, reject leading or
  trailing whitespace variants, add focused tests for both sections and both
  whitespace directions, and rerun focused/full suites.

### Cycle 2

#### Reservation

- Reserved at: 2026-09-01T20:38:33Z
- Starting status: implementing
- Implementer: `/root/task_017_cycle_1_implementer`

#### Implementer Report

- Status: ready-for-test
- Change summary: Required raw transferred-section content to equal the sole
  exact bullet `- none`; added regression coverage rejecting leading- and
  trailing-whitespace near matches in both Task list and Acceptance coverage;
  preserved canonical blocked, valid ready, and prior Task 017 behavior.
- Files changed:
  `.agents/skills/implement-spec/tests/test_planning_contracts.py`.
- Checks and results: the direct near-match regression, all 19 focused tests,
  all 54 implement-spec tests, isolated compilation, `git diff --check`, and
  scope/hash inspection passed. `role-contracts.md` remained unchanged.
- Residual risks or assumptions: The parser remains fixture test
  infrastructure rather than the production state validator, as required.
- Contract issue: none
- Blocker: none

#### Tester Report

- Tester: `/root/task_017_cycle_1_tester`
- Verdict: pass
- Checks and results: all 19 focused and all 54 implement-spec tests passed;
  isolated compilation, `git diff --check`, static scope review, and unchanged
  pre/post hashes passed. Independent exactness probes covered spaces, tabs,
  blank lines, extra bullets, casing, bare `none`, and CRLF boundaries without
  exceptions or side effects.
- Criterion-by-criterion evidence: empty/whitespace, missing, duplicate,
  invalid, and inconsistent scalars reject structurally; blank required
  sections reject; exact `- none` is blocked-only; the 96-input fixed-seed fuzz
  set and deterministic near matches produce no exception/state/approval/
  dispatch; valid ready and exact blocked paths remain correct.
- Failure attribution: none
- Residual risk: The parser is fixture infrastructure rather than the
  production validator; noncanonical CRLF reports reject safely.
- Required next action: none.

## Latest Tester Evidence

- Cycle: 2
- Verdict: pass
- Evidence: all six criteria passed through 19 focused and 54 total tests,
  independent boundary probes, compilation, scope inspection, and unchanged
  file/diff hashes.
- Recorded at: 2026-09-01T20:42:05Z

## Human Resolutions and Extensions

None.
