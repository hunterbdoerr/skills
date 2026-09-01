---
schema_version: 1
id: task-008
kind: implementation
status: pending
dependencies: [task-006]
cycles_used: 0
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: none
---

# Task 008: Forward-test role and retry bounds

## Objective

Prove the implement/test loop under success, repair, exhaustion, blocked
verification, and infrastructure failure.

## Spec References

- Retry and Stop Policy
- Delivery Plan, Phase 4
- AC-08 through AC-12

## Scope

Exercise first-cycle success, failure then repair, three failures, tester
blocked, one safe infrastructure retry, role mutation boundaries, and
append-only attempt history.

Do not exercise resume, overlap, or final completion.

## Acceptance

- Pass advances once and failures consume no more than three autonomous cycles.
- Blocked testing stops immediately and a second infrastructure failure stops.
- Unauthorized edits prevent acceptance.
- Attempt history remains append-only.

## Verification Plan

Use fresh-agent disposable repositories and inspect counters before dispatch,
attempt records, verdicts, and diffs.

## Risks

A fixture may accidentally avoid the intended failure branch; outcomes must be
observable without leaking the expected result.

## Attempts

No attempts yet.

## Human Resolution

None.
