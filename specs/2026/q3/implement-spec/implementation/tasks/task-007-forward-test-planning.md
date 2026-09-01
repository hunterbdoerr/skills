---
schema_version: 1
id: task-007
kind: implementation
status: passed
dependencies: [task-002, task-005, task-006]
cycles_used: 3
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: pass
---

# Task 007: Codify non-delegating task execution

## Objective

Codify one up-front planning boundary and require every approved execution task
to use one direct implementer followed by one independent direct
tester/reviewer, with neither role delegating to another agent.

## Spec References

- Decision Summary
- Role Contracts
- Orchestration Lifecycle
- Delivery Plan, Phase 4
- AC-03 and AC-08

## Plan References

- [`Proposed Execution`](../plan.md#proposed-execution)
- [`Acceptance Coverage`](../plan.md#acceptance-coverage)
- [`Execution Bounds`](../plan.md#execution-bounds)

## Dependencies

- `task-002`, `task-005`, and `task-006` must remain passed.

## Scope

### In scope

- Update `SKILL.md`, `references/role-contracts.md`,
  `references/state-contract.md`, `assets/plan.md`, and `assets/task.md` so that:
  planning occurs only during initial planning or a material amendment; task
  proposals must be small enough for one implementer; and implementers and
  testers may not delegate to planners, helpers, or sub-agents.
- Add focused static contract checks for the amended wording.
- Replace nested-agent forward-validation instructions with direct,
  deterministic disposable-fixture scenario instructions.

### Prohibited scope

- Do not remove the one read-only planning boundary.
- Do not remove independent tester/reviewer verification.
- Do not spawn a planner, helper, or sub-agent from this task.
- Do not reset cycles, rewrite prior attempts, or perform scenario work owned
  by Tasks 008–016.

## Acceptance Criteria

- [ ] The skill names exactly one planning boundary: initial planning or
      material amendment.
- [ ] Semantic plan review rejects work that is too broad or requires task-role
      delegation.
- [ ] The implementer and tester contracts explicitly prohibit spawning or
      delegating to another planner, helper, or sub-agent.
- [ ] Every task template requires enough bounded implementation and
      verification detail for one implementer and one independent tester.
- [ ] Forward-validation instructions prohibit an
      orchestrator-under-implementer topology.
- [ ] Existing approval authority, role ownership, and independent review
      remain intact.

## Verification Plan

- Run standard skill validation.
- Run the full existing validator test suite.
- Run focused static assertions for the one-planning-boundary,
  one-implementer, independent-tester, and no-delegation clauses.
- Run `git diff --check` and inspect the amended contracts for contradictions.

## Risks

Only one cycle remains. Keep this task to contract, template, and focused
static-test changes; any failure after Cycle 3 stops for an explicit extension
or other human resolution.

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

### Cycle 3

#### Reservation

- Reserved at: 2026-09-01T16:38:32Z
- Starting status: implementing
- Implementer: `/root/task_007_cycle_3_implementer`

#### Implementer Report

- Status: ready-for-test
- Change summary: Codified one read-only planning boundary for initial planning
  or material amendment; rejected oversized or delegating task proposals;
  required one direct implementer followed by one independent direct tester;
  prohibited execution-role delegation; strengthened templates; and replaced
  nested-agent forward validation with deterministic disposable fixtures.
- Files changed: `.agents/skills/implement-spec/SKILL.md`,
  `references/role-contracts.md`, `references/state-contract.md`,
  `assets/plan.md`, `assets/task.md`, and
  `tests/test_execution_contracts.py`.
- Checks and results: official skill validation passed; all 30 unittests
  passed, including five focused execution-contract tests; `git diff --check`
  passed; manual scope inspection passed.
- Residual risks or assumptions: deterministic static and fixture-oriented
  contracts do not prove live model-runtime behavior; this is the approved
  revision-2 tradeoff.
- Contract issue: none
- Blocker: none

#### Tester Report

- Tester: `/root/task_007_cycle_3_tester`
- Verdict: pass
- Checks and results: all 30 unittests and five focused contract tests passed;
  `git diff --check`, semantic diff review, and scope inspection passed. The
  tester's official skill-validator attempt was inconclusive because its
  environment lacked PyYAML; the orchestrator reran it with the previously
  authorized isolated dependency and received `Skill is valid!`.
- Criterion-by-criterion evidence: the skill and all durable contracts define
  one initial/material-amendment planning boundary; reject broad or delegating
  proposals; prohibit implementer/tester spawning or delegation; require exact
  direct-role template detail; prohibit orchestrator-under-implementer forward
  tests; and preserve approval, state, review, cycle, retry, extension, and Git
  boundaries.
- Failure attribution: none
- Residual risk: static contract tests cannot prove future live model
  compliance; deterministic fixture scenarios are the approved mitigation.
- Required next action: none

## Latest Tester Evidence

- Cycle: 3
- Verdict: pass
- Evidence: 30 tests, focused semantic inspection, scope review, whitespace
  checks, and official skill validation passed.
- Recorded at: 2026-09-01T16:51:08Z

## Human Resolutions and Extensions

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

Amendment resolution requested by the current user on 2026-09-01: supersede
the nested fresh-agent method with small non-delegating tasks while preserving
the independent review cycle. The two prior capacity blocks, consumed cycles,
reports, and evidence remain authoritative history. Revision 2 approval is
still required before Cycle 3 may be reserved.

Resolved by the current user at 2026-09-01T16:38:13Z: approve plan revision 2
exactly as disclosed, including the deterministic-fixture tradeoff and Task
007 retaining only Cycle 3. This authorizes Cycle 3 within the amended task
scope and does not authorize delegation, added cycles, or external side
effects.
