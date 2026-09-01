---
schema_version: 1
id: task-007
kind: implementation
status: needs-human
dependencies: [task-004, task-005]
cycles_used: 2
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: blocked
---

# Task 007: Forward-test planning and approval

## Objective

Validate packaging, planning, approval, amendments, and critical gates with
fresh agents and disposable repositories.

## Spec References

- Delivery Plan, Phase 4
- Skill Behavior Tests
- AC-01 through AC-07 and AC-17

## Scope

Exercise ordinary versus packaged output, flat-spec rejection, plan generation,
approval stop, amendment/reapproval, critical gates, and changed specs.

Do not exercise the full retry, blocked tester, resume, or completion suite.

## Acceptance

- Fresh agents follow the skill from raw requests and artifacts.
- Every scenario reaches the expected persisted state and stop.
- No repository or agent text grants approval.
- Repairs are rerun from uncontaminated fixtures.

## Verification Plan

Use fresh sub-agents and disposable local Git repositories; capture plans,
reports, validator output, Git state, and dispatch evidence.

## Risks

Forward tests are nondeterministic and reused fixtures can leak expected state.

## Attempts

### Cycle 1

- Implementation summary: Created eight baseline-committed disposable fixtures
  and exercised fresh-agent routing, flat-spec rejection, and the first canonical
  approval scenario. Ordinary `write-spec` routed to a flat spec, explicit
  orchestration mode routed to `<topic>/spec.md`, and `implement-spec` rejected
  a flat legacy spec without mutation. The canonical approval scenario stopped
  after both permitted planner-dispatch attempts hit the shared agent limit;
  no implementation state, product files, or implementer dispatch resulted.
- Files changed: Source repository unchanged. Disposable fixtures and evidence
  exist under `/tmp/implement-spec-task007-20260901`.
- Checks run: Inspected fixture Git status, validator/dispatch evidence, raw
  prompts, and fresh-agent reports for the three completed scenarios and the
  blocked approval scenario.
- Tester verdict: blocked
- Verification evidence:
  `/tmp/implement-spec-task007-20260901/evidence/README.md` and
  `/tmp/implement-spec-task007-20260901/evidence/status-and-dispatch.md`.
  Amendment/reapproval, critical-gate, spec-drift, plan-completeness/link, and
  trust-text scenarios remain unexecuted and were not simulated.

### Cycle 2

#### Reservation

- Reserved at: 2026-09-01T14:34:35Z
- Starting status: implementing
- Implementer: `/root/implement_task_007_retry`

#### Implementer Report

- Status: blocked
- Change summary: Recreated the canonical approval scenario from an
  uncontaminated baseline and dispatched a fresh agent with only the raw
  user-like request. Its two planner-dispatch attempts hit the shared agent
  limit. After attempting to release a completed slot, the one permitted
  side-effect-free infrastructure retry reproduced the same two failures.
- Files changed: Source repository none. Disposable evidence only under
  `/tmp/implement-spec-task007-retry-20260901/evidence`.
- Checks and results: Fixture status, staged diff, and unstaged diff were
  empty at baseline commit `442cb8d7fe2085ebfa2f1940d5311f4cc6b8ce61`;
  spec digest was
  `d0fdff569d64904a7f28ae2662ee79eff3768bf98be14a108b03c90ec5bef0ed`.
  Plan-ready validation could not run because the planner block correctly
  occurred before any `implementation/` state was rendered.
- Residual risks or assumptions: Plan completeness/approval stop,
  amendment/reapproval, critical gate/link, spec drift, and trust-text
  scenarios remain unexecuted and were not simulated.
- Contract issue: none
- Blocker: Shared nested-agent capacity prevents a fresh orchestrator under
  test from spawning its mandatory planner, including after the one allowed
  no-side-effect retry.

#### Tester Report

- Tester: not dispatched because the implementer report was blocked
- Verdict: blocked
- Checks and results: not run
- Criterion-by-criterion evidence: canonical forward-test criteria remain
  unverifiable without planner capacity
- Failure attribution: environment
- Residual risk: the remaining Task 007 scenarios lack canonical evidence
- Required next action: provide enough nested-agent capacity for one fresh
  orchestrator under test plus its planner

## Human Resolution

Human input is required to retry Task 007 after enough shared sub-agent capacity
is available for each fresh orchestrator to spawn its required planner. The
preserved fixtures may be reused only as clean baselines; each repaired or
retried scenario must run from an uncontaminated copy.

Resolved by the current user at 2026-09-01T14:34:35Z: retry Task 007 after
sub-agent capacity became available. This authorizes no scope, acceptance,
cycle-limit, or repository-side-effect change.

Cycle 2 stopped after the repeated capacity failure. A further retry requires
new current-user direction and still must remain within the one remaining
approved cycle.
