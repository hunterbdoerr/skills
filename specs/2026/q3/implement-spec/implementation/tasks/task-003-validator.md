---
schema_version: 1
id: task-003
kind: implementation
status: passed
dependencies: [task-002]
cycles_used: 1
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: pass
---

# Task 003: Implement deterministic state validation

## Objective

Implement and unit-test a standard-library validator for `plan-ready`,
`dispatch`, and `completion`.

## Spec References

- Deterministic Validator
- Delivery Plan, Phase 1
- Validator Tests
- AC-07, AC-09 through AC-11, AC-14, and AC-15

## Scope

Implement constrained frontmatter parsing, all documented mechanical
invariants, actionable diagnostics, and focused temporary-package tests.

Do not judge semantic coverage, evidence quality, scope overlap, risk, or human
approval intent.

## Acceptance

- All three validation phases work without third-party dependencies.
- Every documented invariant has passing and failing test coverage.
- Unsupported YAML is rejected safely.
- Failures return non-zero and identify the corrective condition.

## Verification Plan

Run `py_compile`, `unittest discover`, and direct valid/invalid smoke cases for
all phases.

## Risks

Python has no standard-library YAML parser; only the canonical restricted
syntax may be accepted.

## Attempts

### Cycle 1

- Implementation summary: Added a restricted-frontmatter validator supporting plan-ready, dispatch, and completion phases with focused invariant tests.
- Files changed: `.agents/skills/implement-spec/scripts/validate_state.py` and `.agents/skills/implement-spec/tests/test_validate_state.py`.
- Checks run: Unit discovery passed 25 tests; direct valid and invalid CLI smoke cases passed. `py_compile` requires a writable `PYTHONPYCACHEPREFIX` in the root sandbox.
- Tester verdict: pass
- Verification evidence: Independent compile, 25-test suite, direct valid/invalid phase smoke tests, invariant matrix, diagnostic, and standard-library import checks passed.

## Human Resolution

None.
