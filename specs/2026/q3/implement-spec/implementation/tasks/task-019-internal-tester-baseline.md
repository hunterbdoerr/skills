---
schema_version: 1
id: task-019
kind: implementation
status: pending
dependencies: [task-018]
cycles_used: 0
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: none
---

# Task 019: Capture the tester baseline internally

## Objective

Close only tester non-mutation and caller-baseline laundering in the
deterministic success fixture.

## Spec References

- Tester
- Orchestration Lifecycle, Execute one task
- AC-08 and AC-12

## Plan References

- [`Proposed Execution`](../plan.md#proposed-execution)
- [`Acceptance Coverage`](../plan.md#acceptance-coverage)
- [`Verification Strategy`](../plan.md#verification-strategy)

## Dependencies

- `task-018` must be passed.

## Scope

### In scope

- Edit only
  `.agents/skills/implement-spec/tests/test_success_role_ownership.py`.
- At the transition into testing, internally capture the authoritative
  pre-tester filesystem/state snapshot after the orchestrator-owned transition
  and before tester work.
- Remove caller authority to provide or replace the trusted baseline; tester
  acceptance compares the internal baseline with current state before
  persisting accepted evidence.
- Add product, test, orchestration-state, deletion, addition, and identical
  post-mutation before/after laundering regressions.
- Preserve direct/non-delegating, exact-distinct-role, exact-criterion, and
  single-acceptance guards.

### Prohibited scope

- No reservation-schema expansion, final pass sealing, unrelated test or
  contract changes, or downstream lifecycle work.
- No planner, live model call, network/external write, destructive action, or
  Git-history mutation.
- Spawning or delegating to a planner, helper, or sub-agent.

## Acceptance Criteria

- [ ] Testing cannot begin without Task 018's accepted implementer identity.
- [ ] One authoritative pre-tester baseline is captured internally exactly
      once.
- [ ] Tester acceptance accepts no caller-supplied baseline as authority.
- [ ] Identical post-mutation snapshots cannot conceal product, test, state,
      added-path, or deleted-path mutation.
- [ ] A genuinely non-mutating independent tester remains accepted.
- [ ] Every prior focused and full test remains green.

## Verification Plan

- Run focused internal-baseline and laundering regressions.
- Run the full standard-library test suite and isolated compilation.
- Run `git diff --check`; inspect all API call sites and the exact one-file
  diff.
- Independently compare pre/post hashes and mutation outcomes.

## Execution Roles

- Implementer: one direct implementer performs the bounded work itself and
  must not spawn or delegate to a planner, helper, or sub-agent.
- Tester/reviewer: one different independent direct tester remains read-only,
  performs every check itself, and must not delegate.

## Risks

- Snapshot timing must distinguish the orchestrator-owned testing transition
  from tester mutation and be explicit in both code and tests.

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
