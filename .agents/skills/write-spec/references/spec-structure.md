# Specification Structure

Use this as a fallback when the target repository has no clear convention. For the application repository, use [application-spec-patterns.md](application-spec-patterns.md) instead. Adapt the structure to the size and risk of the change; omit sections that add no value.

If the user requests a particular structure, audience, or level of detail, start there. Use this reference only to catch missing decisions that materially affect implementation or verification.

## Placement and naming

When the repository has no stronger convention:

- Store specs at `specs/<year>/q<quarter>/<snake_case_topic>.md`.
- Use a concise title in title case.
- Add a status near the top when implementation may already be underway.
- Link related repository specs and docs with relative paths.

## Core structure

```markdown
# <Title>

## Status

Draft, accepted, partially implemented, implemented, or superseded. Describe known completed and pending work when useful.

## Summary

State the proposed outcome, affected actor, and central decision in a few sentences.

## Context / Problem

Explain the user, product, engineering, or operational problem. Include relevant current behavior and constraints.

## Goals

- Define the outcomes this work must achieve.

## Non-Goals

- Define adjacent work this specification intentionally excludes.

## Current State

Describe the verified repository baseline, important entry points, and ownership boundaries. Note that implementers must re-verify time-sensitive details.

## Proposed Design / Required Behavior

Describe the end-to-end behavior and decisions. Add subsections for contracts, data model, APIs, UI, state transitions, or component boundaries as needed.

State invariants and source-of-truth ownership explicitly.

## Failure and Edge-Case Behavior

Define validation, partial failure, retries, idempotency, concurrency, and recovery where relevant.

## Security and Privacy

Define authorization, sensitive-data boundaries, audit behavior, and prohibited data where relevant.

## Alternatives Considered

Record viable alternatives and why the chosen design is preferred.

## Implementation / Delivery Plan

Order reviewable slices by dependency. State the objective, work, and completion condition for each slice.

## Test Strategy

Cover focused unit tests, integration or boundary tests, end-to-end behavior, and explicit manual verification where appropriate.

## Migration, Rollout, and Observability

Define compatibility constraints, deployment order, feature gating, monitoring, success signals, and rollback when applicable.

## Acceptance Criteria

- [ ] Write observable, binary completion criteria that collectively cover the goals.

## Open Questions

- Name only unresolved decisions, their owner when known, and the consequence of each answer.
```

## Selection guidance

- Use **Overview** instead of **Summary** when that matches the local corpus.
- Add **Terminology** when overloaded terms or domain language affect the design.
- Add **Decision** or **Guiding Decisions** near the top for architecture-decision specs.
- Add explicit contract sections for event schemas, APIs, persistence, or agent/runtime boundaries.
- Use **Phase Plan**, **Milestones**, or **Incremental Delivery** when sequencing is central.
- Use **Risks and Mitigations** when uncertainty or operational impact warrants explicit treatment.
- Use **Consequences** for architecture decisions with meaningful positive and negative tradeoffs.
- Use **Success Criteria** or **Completion Criteria** only when the repository favors those names; keep the criteria observable.

## Writing rules

- Lead with decisions and behavior, not a diary of investigation.
- Mark facts, proposals, assumptions, and open questions distinctly.
- Prefer repository-relative links and exact verified identifiers.
- Explain why for consequential constraints, especially security, data integrity, compatibility, and rollout order.
- Keep future work clearly separated from the implementation-ready scope.
- Avoid estimates unless the user requests them or the repository convention requires them.
