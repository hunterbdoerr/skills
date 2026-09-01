---
schema_version: 1
id: task-004
kind: implementation
status: passed
dependencies: [task-001]
cycles_used: 1
cycle_limit: 3
human_gate: false
human_gate_status: not-required
tester_verdict: pass
---

# Task 004: Add orchestration packaging to write-spec

## Objective

Make orchestration-ready spec packaging opt-in while preserving ordinary
flat-spec behavior, and document the Codex-only skill.

## Spec References

- Spec Packaging
- Delivery Plan, Phase 2
- Compatibility Tests
- AC-01 and AC-17

## Scope

Update `.agents/skills/write-spec/SKILL.md` with explicit destination rules and
update `README.md` to distinguish portable and Codex-only skills.

Do not convert legacy specs, change the ordinary default, create implementation
state from `write-spec`, or add Claude/Copilot links.

## Acceptance

- Explicit orchestration requests target `<topic>/spec.md`.
- Ordinary specs retain `<topic>.md`.
- `write-spec` creates only the spec document.
- README accurately describes discovery and portability.
- All canonical skills validate.

## Verification Plan

Validate every skill and inspect the two mutually exclusive destination rules;
forward behavior is covered by Task 007.

## Risks

Trigger wording could redirect ordinary specs or imply unsupported portability.

## Attempts

### Cycle 1

- Implementation summary: Added explicit opt-in orchestration packaging while preserving ordinary flat specs and documented Codex-only discovery.
- Files changed: `.agents/skills/write-spec/SKILL.md` and `README.md`.
- Checks run: All three canonical skills passed standard validation; `git diff --check` passed.
- Tester verdict: pass
- Verification evidence: Independent destination-rule, state-ownership, legacy-preservation, README, symlink, three-skill validation, and diff checks passed.

## Human Resolution

None.
