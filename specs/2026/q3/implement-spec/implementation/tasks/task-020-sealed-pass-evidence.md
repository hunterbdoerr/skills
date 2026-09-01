---
schema_version: 1
id: task-020
kind: implementation
status: pending
dependencies: [task-019]
cycles_used: 0
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: none
---

# Task 020: Seal immutable distinct-role pass evidence

## Objective

Close only final-pass binding against synchronized role-identity and reviewed-
evidence substitution in the deterministic success fixture.

## Spec References

- Implementer
- Tester
- Orchestration Lifecycle, Execute one task
- AC-08 and AC-12

## Plan References

- [`Proposed Execution`](../plan.md#proposed-execution)
- [`Acceptance Coverage`](../plan.md#acceptance-coverage)
- [`Verification Strategy`](../plan.md#verification-strategy)

## Dependencies

- `task-019` must be passed.

## Scope

### In scope

- Edit only
  `.agents/skills/implement-spec/tests/test_success_role_ownership.py`.
- Create one structurally sealed review-evidence record from the exact
  contacted/accepted implementer identity, accepted tester identity, complete
  ordered criterion evidence, and internally captured reviewed snapshot or its
  canonical digest.
- Before pass, require nonempty distinct identities; agreement among sealed,
  persisted, and in-memory evidence; unchanged filesystem/state since review;
  an unaltered seal; coherent testing state; zero prior advancement; and no
  prior pass.
- Add synchronized identity, simultaneous persisted/in-memory substitution,
  replaced or recomputed reviewed snapshot, altered criteria/seal, post-review
  mutation, and repeated-pass regressions.

### Prohibited scope

- No reservation/contact redesign, tester-baseline capture redesign,
  downstream lifecycle work, unrelated files, or runtime-security claims
  beyond the deterministic fixture.
- No planner, live model call, network/external write, destructive action, or
  Git-history mutation.
- Spawning or delegating to a planner, helper, or sub-agent.

## Acceptance Criteria

- [ ] Exact implementer and tester identities remain distinct through pass.
- [ ] Changing both mutable identity locations to forged values is rejected.
- [ ] Reviewed evidence cannot be replaced or recomputed after mutation to
      legitimize pass.
- [ ] Persisted, in-memory, and sealed role/review evidence must agree.
- [ ] Post-review production, test, state, or evidence mutation prevents pass.
- [ ] An unmodified valid review advances once and only once.
- [ ] Every prior focused and full test remains green.

## Verification Plan

- Run focused synchronized-identity, mutable-snapshot, evidence-seal,
  post-review-mutation, and repeated-pass regressions.
- Run the full standard-library suite and isolated compilation.
- Run `git diff --check` and inspect the exact one-file scope.
- Independently review every criterion and substitution attack.

## Execution Roles

- Implementer: one direct implementer performs the bounded work itself and
  must not spawn or delegate to a planner, helper, or sub-agent.
- Tester/reviewer: one different independent direct tester remains read-only,
  performs every check itself, and must not delegate.

## Risks

- This proves deterministic fixture enforcement, not runtime cryptographic or
  process isolation; evidence and final reporting must state that boundary.

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
