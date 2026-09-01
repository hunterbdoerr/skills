---
schema_version: 1
id: task-<NNN>
kind: implementation
status: pending
dependencies: []
cycles_used: 0
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: none
---

# Task <NNN>: <title>

## Objective

<One bounded outcome that one direct implementer can complete without
delegation or a task-local planning pass.>

## Spec References

- [`<exact spec heading>`](../../spec.md#<heading-anchor>)

## Plan References

- [`Proposed Execution`](../plan.md#proposed-execution)
- [`Acceptance Coverage`](../plan.md#acceptance-coverage)
- <other exact plan heading>

## Dependencies

- <task ID and required passed outcome, or none>

## Scope

### In scope

- <exact allowed files, code, tests, and behavior; include enough detail for
  direct implementation without delegation>

### Prohibited scope

- <explicitly excluded work and side effects>
- Spawning or delegating to a planner, helper, or sub-agent.

## Acceptance Criteria

- [ ] <objective, verifiable task criterion>

## Verification Plan

- <exact focused command or inspection that one independent direct tester can
  run without delegation>
- <required integration evidence, if any>

## Execution Roles

- Implementer: one direct implementer performs the bounded work itself and
  must not spawn or delegate to a planner, helper, or sub-agent.
- Tester/reviewer: one different, independent direct tester performs the
  verification itself, remains read-only, and must not spawn or delegate to a
  planner, helper, or sub-agent.

## Risks

- <task risk and guardrail, or none>

<!-- When human_gate is true, include this section and link to this exact
heading from plan.md. Summarize the issue in the plan as well. -->
## Critical Human Review

Not required.

<!-- For a gated task, replace the line above with:
- Review timing: before cycle 1
- Issue: <critical issue>
- Decision required: <one exact decision>
- Safe default while pending: stop without implementation
-->

## Attempts

None.

<!-- Replace "None" by appending one complete section for each cycle
immediately after reserving it. Never overwrite attempts. Append corrections
and name the superseded claim.

### Cycle <N>

#### Reservation

- Reserved at: <timestamp>
- Starting status: implementing
- Implementer: <agent identifier>

#### Implementer Report

- Status: pending
- Change summary: pending
- Files changed: pending
- Checks and results: pending
- Residual risks or assumptions: pending
- Contract issue: none
- Blocker: none

#### Tester Report

- Tester: pending
- Verdict: none
- Checks and results: pending
- Criterion-by-criterion evidence: pending
- Failure attribution: none
- Residual risk: pending
- Required next action: pending
-->

## Latest Tester Evidence

- Cycle: none
- Verdict: none
- Evidence: none
- Recorded at: none

## Human Resolutions and Extensions

None.

<!-- Append each human decision. For a bounded extension record the current
user's explicit authorization, timestamp, prior cycle_limit, added cycles
(one to three), new cycle_limit, conditions, and the plan approval record that
also captures the extension. The human authorizes; the orchestrator persists
the exact authorized values. Never renew an extension automatically. -->
