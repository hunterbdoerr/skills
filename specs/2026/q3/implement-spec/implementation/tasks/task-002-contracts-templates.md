---
schema_version: 1
id: task-002
kind: implementation
status: passed
dependencies: [task-001]
cycles_used: 2
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: pass
---

# Task 002: Define state, role, and output contracts

## Objective

Encode the approved state model and agent report contracts in reusable
references and canonical Markdown templates.

## Spec References

- Persisted State Contract
- Approval Semantics
- Role Contracts
- Retry and Stop Policy
- AC-03 through AC-05, AC-08, AC-11, and AC-13

## Scope

Create `state-contract.md`, `role-contracts.md`, `plan.md`, and `task.md` with
the required fields, states, transitions, approval authority, append-only
evidence, human gates, and report schemas.

Do not implement executable validation or dispatch behavior.

## Acceptance

- Templates contain every required field and human-readable section.
- The plan template is sufficient for normal approval without task files.
- The task template supports attempts, evidence, resolutions, and extensions.
- Critical review requires a plan summary and exact task-heading link.
- Role permissions remain disjoint and explicit.

## Verification Plan

Compare fields against the spec, instantiate temporary sample documents, and
search for contradictory approval or mutation language.

## Risks

Duplicated contract text may drift; vague report fields may weaken tester
independence.

## Attempts

### Cycle 1

- Implementation summary: Added detailed state and role contracts plus canonical plan and task assets.
- Files changed: `references/state-contract.md`, `references/role-contracts.md`, `assets/plan.md`, and `assets/task.md`.
- Checks run: Template frontmatter parsing, required fields/sections/enums, in-memory instantiation, initial task state, whitespace, and progressive-disclosure checks passed.
- Tester verdict: fail
- Verification evidence: Plan/task recovery transitions were incomplete and extension authorization conflicted with orchestrator persistence permissions.

Tester verdict: fail. Plan transitions were not fully defined, recovery from
`needs-human` was missing, and the shared prohibition on expanding cycle
limits contradicted the orchestrator's duty to persist an explicitly
human-authorized extension.

### Cycle 2

- Implementation summary: Added explicit plan/task transition graphs and clarified that humans authorize extensions while the orchestrator only persists exact authorized values.
- Files changed: `references/state-contract.md`, `references/role-contracts.md`, `assets/plan.md`, and `assets/task.md`.
- Checks run: Frontmatter, explicit transition/recovery, approval-versus-persistence, and whitespace assertions passed.
- Tester verdict: pass
- Verification evidence: Retest passed all schema, transition, recovery, extension authority, append-only evidence, final verification, critical-link, and role-separation criteria.

## Human Resolution

None.
