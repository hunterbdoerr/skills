---
schema_version: 1
id: task-018
kind: implementation
status: needs-human
dependencies: [task-003, task-006, task-007, task-011]
cycles_used: 3
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: fail
---

# Task 018: Bind reservation and contacted implementer identity

## Objective

Close only the reservation-through-accepted-implementer integrity boundary in
the deterministic success fixture.

## Spec References

- Persisted State Contract
- Implementer
- Orchestration Lifecycle, Execute one task
- AC-08, AC-09, and AC-12

## Plan References

- [`Proposed Execution`](../plan.md#proposed-execution)
- [`Acceptance Coverage`](../plan.md#acceptance-coverage)
- [`Execution Bounds`](../plan.md#execution-bounds)

## Dependencies

- `task-003`, `task-006`, `task-007`, and `task-011` must be passed.

## Scope

### In scope

- Edit only
  `.agents/skills/implement-spec/tests/test_success_role_ownership.py`.
- Replace partial pre-contact checks with a complete structural comparison of
  persisted and expected reservation state: exact root keys, complete task
  records, dependencies, statuses, verdicts, cycle counts, sole active/current
  task, zero advancement, and absent pre-contact role evidence.
- Persist a separate nonempty `contacted_implementer_id` only after validating
  a direct non-delegating contacted role.
- Require the accepted implementer report and persisted/in-memory handoff state
  to match that exact contacted identity.
- Add missing/extra/field-corruption, additional-active, event-string
  substitution, contacted-identity substitution, and report-identity mismatch
  regressions.

### Prohibited scope

- No tester-baseline capture, final pass sealing, downstream lifecycle
  scenarios, product contract changes, or other test files.
- No planner, live model call, network/external write, destructive action, or
  Git-history mutation.
- Spawning or delegating to a planner, helper, or sub-agent.

## Acceptance Criteria

- [ ] Any missing, extra, stale, or corrupted reservation field prevents
      implementer contact.
- [ ] Complete reservation validation occurs before contacted-role state
      changes.
- [ ] Contacted implementer identity is structurally persisted rather than
      inferred from mutable event text.
- [ ] Accepted implementer identity exactly matches the contacted identity in
      memory and persisted state.
- [ ] Event-string or identity substitution cannot authorize testing.
- [ ] The existing happy path and every prior Task 011 regression remain green.

## Verification Plan

- Run focused reservation-schema and identity-substitution regressions.
- Run the full standard-library test suite and isolated compilation.
- Run `git diff --check` and inspect the diff for exact one-file scope.
- Independently compare pre/post fixture state for every criterion.

## Execution Roles

- Implementer: one direct implementer performs the bounded work itself and
  must not spawn or delegate to a planner, helper, or sub-agent.
- Tester/reviewer: one different independent direct tester remains read-only,
  performs every check itself, and must not delegate.

## Risks

- Keep refactoring strictly before tester-baseline and pass-evidence concerns;
  Tasks 019–020 own those later boundaries.

## Critical Human Review

Not required.

## Attempts

### Cycle 1

#### Reservation

- Reserved at: 2026-09-01T23:20:48Z
- Starting status: implementing
- Implementer: `/root/task_018_cycle_1_implementer`

#### Implementer Report

- Status: ready-for-test
- Change summary: Added exact expected-versus-persisted reservation validation,
  separately persisted nonempty contacted identity with an in-memory receipt,
  exact accepted-report/testing identity binding, and exhaustive reservation/
  active/event/identity mismatch regressions.
- Files changed:
  `.agents/skills/implement-spec/tests/test_success_role_ownership.py`.
- Checks and results: all 20 focused and all 83 implement-spec tests passed;
  isolated compilation, Task 018 dispatch validation, `git diff --check`, and
  one-file scope/hash inspection passed.
- Residual risks or assumptions: tester-baseline capture and final pass-
  evidence sealing remain deferred to Tasks 019–020.
- Contract issue: none
- Blocker: none

#### Tester Report

- Tester: `/root/task_018_cycle_1_tester`
- Verdict: fail
- Checks and results: all 20 focused and all 83 implement-spec tests passed;
  malformed shape/event probes rejected safely. Strict-type probes accepted
  `cycles_used=True` as integer `1` and integer direct/delegated flags;
  coordinated persisted/in-memory contacted-ID plus receipt substitution
  authorized testing. Compilation, scope, whitespace, and hashes passed.
- Criterion-by-criterion evidence: pre-mutation validation, separate persisted
  identity, and prior regressions passed; strict complete reservation,
  exact accepted identity, and substitution-resistant testing authorization
  remain unsatisfied under the two bypass classes.
- Failure attribution: value-equality is not type-strict and the contact receipt
  can be recomputed/replaced with both identity copies.
- Residual risk: the green suite misses type-confused reservation data and
  coordinated contact substitution.
- Required next action: add strict field/flag type validation and bind the
  originally contacted identity to an authoritative receipt that coordinated
  mutable-field substitution cannot recompute.

### Cycle 2

#### Reservation

- Reserved at: 2026-09-01T23:29:17Z
- Starting status: implementing
- Implementer: `/root/task_018_cycle_1_implementer`

#### Implementer Report

- Status: ready-for-test
- Change summary: Added recursive exact-type reservation validation, exact
  Boolean flags and nonempty string identity validation, a write-once original-
  contact anchor, and strict-type/coordinated-substitution regressions.
- Files changed:
  `.agents/skills/implement-spec/tests/test_success_role_ownership.py`.
- Checks and results: all 24 focused, 4 targeted, and 87 implement-spec tests
  passed; isolated compilation, Task 018 dispatch validation,
  `git diff --check`, and scope/hash inspection passed.
- Residual risks or assumptions: the anchor covers contacted-implementer
  identity only; Tasks 019–020 own tester baseline and final pass sealing.
- Contract issue: none
- Blocker: none

#### Tester Report

- Tester: `/root/task_018_cycle_1_tester`
- Verdict: fail
- Checks and results: all 24 focused and all 87 implement-spec tests passed;
  recursive type probes passed. Deletion/recreation, `object.__setattr__`,
  direct `__dict__` replacement, and copied-instance manipulation replaced the
  fixture-local anchor and authorized a substituted report/testing path.
  Compilation, scope, whitespace, and hashes passed.
- Criterion-by-criterion evidence: complete typed reservation, pre-mutation
  validation, separate persisted identity, and prior regressions passed;
  exact original contacted identity and substitution-resistant testing remain
  unsatisfied.
- Failure attribution: the contact anchor lives on the same replaceable fixture
  instance and is protected only from ordinary reassignment.
- Residual risk: green tests overstate original-contact integrity under normal
  Python object-state replacement/copying.
- Required next action: bind original contact outside replaceable instance
  state, reject copied instances lacking that binding, and add all four
  substitution regressions through the full report-to-testing path.

### Cycle 3

#### Reservation

- Reserved at: 2026-09-01T23:35:19Z
- Starting status: implementing
- Implementer: `/root/task_018_cycle_1_implementer`

#### Implementer Report

- Status: ready-for-test
- Change summary: Added a module-owned weak-key original-contact binding,
  required report/testing transitions to consult it, rejected all instance
  re-anchoring and shallow-copy paths, and added lifecycle cleanup plus full-
  path regressions while preserving strict validation.
- Files changed:
  `.agents/skills/implement-spec/tests/test_success_role_ownership.py`.
- Checks and results: all 27 focused, 4 targeted, and 90 implement-spec tests
  passed; isolated compilation, Task 018 dispatch validation,
  `git diff --check`, and scope/hash inspection passed.
- Residual risks or assumptions: the external binding covers contacted-
  implementer authority only; Tasks 019–020 own later boundaries.
- Contract issue: none
- Blocker: none

#### Tester Report

- Tester: `/root/task_018_cycle_1_tester`
- Verdict: fail
- Checks and results: all 27 focused and all 90 implement-spec tests passed;
  strict types, ordinary state substitution, copies/reconstruction, and
  lifecycle cleanup passed. An equal/hash-alias subclass consumed another
  instance's weak-key binding, and fixture-bound method globals exposed a
  mutable registry whose forged entry authorized substituted testing.
- Criterion-by-criterion evidence: complete typed reservation, pre-mutation
  validation, separate persisted identity, and prior regressions passed;
  exact instance-specific accepted identity and substitution-resistant testing
  remain unsatisfied under weak-key aliasing and registry forgery.
- Failure attribution: `WeakKeyDictionary` uses referent equality/hash rather
  than identity-only lookup, and its module registry remains mutable and
  reachable through Python globals introspection.
- Residual risk: the suite overstates original-contact authority under the two
  adversarial registry paths.
- Required next action: human must authorize an exact bounded extension or a
  material amendment. Repair requires identity-checked binding and an explicit
  threat boundary for internal-registry access, with equal/hash alias and
  permitted-interface registry-mutation regressions.

## Latest Tester Evidence

- Cycle: 3
- Verdict: fail
- Evidence: all 90 tests pass, but weak-key equality/hash aliasing and mutable
  globals-reachable registry forgery still authorize substituted identity.
- Recorded at: 2026-09-01T23:40:25Z

## Human Resolutions and Extensions

Cycle 3 exhausted the approved autonomous limit at
`2026-09-01T23:40:25Z`. Current-user authorization is required for an exact
one-to-three-cycle Task 018 extension or a material amendment. No cycle is
refunded and no later task may be dispatched while this stop remains
unresolved.
