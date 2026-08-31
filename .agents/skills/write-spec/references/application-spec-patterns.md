# Application Specification Patterns

Use these patterns to select a document shape for the application repository. They are distilled from recent specs; they are not mandatory templates.

Explicit user direction wins over these patterns. Use them to match repository vocabulary and make decisions reviewable, never to add scope, reverse a requested policy, or force sections that do not help the requested artifact.

## Contents

- [Shared characteristics](#shared-characteristics)
- [Product or implementation spec](#product-or-implementation-spec)
- [Architecture decision](#architecture-decision)
- [Delivery plan](#delivery-plan)
- [Operational workflow](#operational-workflow)
- [Focused contract or security change](#focused-contract-or-security-change)
- [Selection rules](#selection-rules)

## Shared characteristics

Strong application specs tend to:

- lead with an overview, summary decision, or decision summary rather than process narration;
- make goals and non-goals explicit when scope could expand;
- describe verified current state using concrete repository paths, symbols, routes, or integrations;
- define ownership and source-of-truth boundaries, not just components to edit;
- make replacement, failure, retry, ordering, authorization, privacy, and compatibility semantics explicit when relevant;
- use tables for exact mappings, contracts, ownership, risks, or current/target comparisons;
- keep implementation status truthful with status sections or checked items only when work has actually landed;
- pair delivery steps with acceptance or verification;
- end with acceptance, success, completion, or architecture exit criteria that describe observable outcomes.

Headings vary. Preserve the local document's vocabulary and include only sections that carry decisions.

## Product or implementation spec

Use for a user or operational capability spanning behavior, data, and multiple system boundaries.

Typical shape:

1. Summary or Overview
2. Product Context and related specs
3. Terminology, when domain terms affect behavior
4. Goals and Non-Goals
5. Current State
6. Required Behavior, often as an end-to-end numbered flow
7. Domain-specific contracts: data model, API, projection, UI, configuration
8. Failure, concurrency, replacement, and ownership rules
9. Incremental Delivery
10. Acceptance Criteria
11. Test Strategy
12. Observability and Rollout
13. Decided Questions, Caveats, or bounded Open Questions

Calibrate against `specs/2026/q3/cost_transparency.md` and `specs/2026/q2/patient_drive_folder_creation_async.md`.

## Architecture decision

Use when the central output is a stable boundary, ownership model, or migration strategy.

Typical shape:

1. Decision Summary or Status / Problem / Decision
2. Context and related work
3. Goals and Non-Goals
4. Current and Target State
5. Problems Being Solved or Design Principles
6. Public contracts, ownership boundaries, and configuration/data identity
7. Compatibility or transition approach
8. Risks and Guardrails
9. Open Decisions that do not invalidate the core architecture
10. Architecture Exit or Completion Criteria

Use current/target tables and precise contract sketches when they make the boundary reviewable. Calibrate against `specs/2026/q3/agent_runtime_consolidation.md` and `specs/2026/q3/explicit_database_migration_strategy.md`.

## Delivery plan

Use when stable decisions already exist and the document's job is sequencing, status, and mergeability. Link to the architecture or product spec as the source of truth.

Typical shape:

1. Purpose and source-of-truth link
2. Current Status with a phase table
3. One section per phase
4. Objective, Work, and Acceptance for each phase or suggested PR
5. Explicit migration order and atomic changes
6. Deferred work
7. Delivery Guardrails
8. Delivery Completion

Keep landed work and proposed work visually distinct. Calibrate against `specs/2026/q3/agent_runtime_consolidation_delivery.md`.

## Operational workflow

Use when the main design is how operators notice, interpret, and act on system state.

Typical shape:

1. Overview and Problem Statement
2. Guiding Decisions
3. Operator workflow and definition of completion or acknowledgement
4. Retention, alerting, thresholds, and alert content
5. In Scope and Out of Scope
6. Implementation Shape by backend, UI, and configuration
7. Acceptance Criteria
8. Follow-On Questions

State who owns the action and distinguish urgent response from routine review. Calibrate against `specs/2026/q2/river/river_failure_review.md`.

## Focused contract or security change

Use for a bounded API, audit, authorization, privacy, or compatibility change.

Typical shape:

1. Overview
2. Decision
3. Goals and Non-Goals
4. Concrete request/event/permission contract
5. User or operator experience
6. Audit, authorization, privacy, or prohibited-data behavior
7. Compatibility
8. Implementation Sequence and Verification
9. Success Criteria

Name prohibited behavior explicitly when sensitive data or privilege is involved. Calibrate against `specs/2026/q3/smh_data_redaction_provenance_audit.md` and `specs/2026/q3/pfc_patient_caregiver_app_access.md`.

## Selection rules

- Choose the archetype by the document's primary decision, not by the team requesting it.
- If the user supplies an outline, length constraint, or document purpose, honor it and borrow only the useful characteristics of the nearest archetype.
- Combine patterns when one document remains coherent, such as a product spec with a focused security section.
- Split architecture from delivery when the decision should remain stable while phase status and suggested PRs will change.
- Prefer a focused contract spec over a broad implementation template for a small, security-sensitive change.
- Prefer an operational workflow over a component-by-component design when human review and remediation are the core outcome.
- If an existing related spec already owns the architecture, update or link it instead of restating its decisions in a new delivery plan.
