# Spec Context Packet

Use this structure for the handoff to `write-spec`. This is a decision and evidence record, not a draft specification. Omit empty or irrelevant sections and keep confirmed facts distinct from proposals and assumptions.

## Contents

- [Packet template](#packet-template)
- [Handoff rules](#handoff-rules)

## Packet template

```markdown
# <Topic> — Spec Context

## Readiness

Ready | Ready with open questions | Not ready

State why and identify any blocking decision.

## User Direction

Capture the user's requested outcome, priorities, constraints, exclusions, preferred document shape or depth, and any intentional departure from existing behavior or prior specs. Preserve important wording when paraphrasing would weaken the decision.

## Recommended Spec Shape

Product/implementation | Architecture decision | Operational workflow | Focused contract/security change | Delivery plan | Paired architecture and delivery documents

State why this shape fits and whether the spec should describe proposed work, current implementation status, or both.

## Problem and Desired Outcome

Describe the current problem, affected users or operators, desired outcome, and success signal.

## Sources Reviewed

- `<repository-relative path or link>` — relevance and any freshness concern.

## Verified Current State

| Claim | Evidence | Confidence or caveat |
|---|---|---|
| ... | `<path:line or link>` | Confirmed / Time-sensitive / Conflicting |

Summarize the current flow, entry points, ownership boundaries, data flow, and relevant constraints after the table.

## Scope

### Goals

- ...

### Non-Goals

- ...

### First Delivery Slice

Describe the smallest independently useful, verifiable scope.

## Actors and Business Requirements

List actors, permissions, source-of-truth ownership, business rules, precedence, exceptions, and invariants.

## Expected Behavior

Walk through the primary flow and meaningful alternative flows from trigger to observable outcome.

## Edge Cases and Failure Semantics

| Scenario | Expected behavior | Status |
|---|---|---|
| ... | ... | Confirmed / Proposed / Open |

## Technical Implications

### Codebase Impact Map

| Surface | Current responsibility | Likely implication | Evidence |
|---|---|---|---|
| ... | ... | ... | `<path>` |

### Data and Contracts

Describe schema, persistence, lifecycle, API, event, compatibility, or migration implications.

### Security and Privacy

Describe authorization, sensitive-data, audit, compliance, and prohibited-data implications.

### Operations and Delivery

Describe observability, rollout, deployment order, rollback, capacity, cost, and support implications.

### Test Implications

List the behaviors and failure paths that require verification at each relevant test layer.

## Decisions

| Decision | Rationale | Source or owner |
|---|---|---|
| ... | ... | ... |

## Assumptions

- Assumption — consequence if false and how to verify it.

## Open Questions

- Question — why it matters, options considered, and who can answer it.

## Deferred Follow-Ups

- Work intentionally excluded from the first delivery slice.

## Handoff Notes for `write-spec`

- Local spec conventions or representative specs to follow.
- Facts that must be re-verified because the implementation is moving.
- Whether a separate delivery/status document is warranted.
```

## Handoff rules

- Preserve repository-relative source paths and external links.
- Include rejected options only when they explain a consequential decision.
- Mark user statements as confirmed requirements only after the user affirms them or their intent is unambiguous.
- Treat repository conventions as presentation and implementation evidence, not as authority to rewrite confirmed user intent.
- Mark agent-suggested defaults as proposed until accepted.
- Preserve unresolved contradictions instead of choosing the most convenient source.
- Do not invent a technical design to fill a business-policy gap.
- Keep open questions bounded enough that `write-spec` can either resolve them through research or record them honestly.
