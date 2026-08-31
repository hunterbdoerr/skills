# Discovery Lenses

Use these lenses as a prompt catalog, not a questionnaire. Select only questions that are relevant and not already answered by repository evidence or supplied documents.

## Problem and outcome

- What observable problem exists today, and who experiences it?
- What event triggers the workflow and what outcome ends it?
- What happens if nothing changes?
- How will the business or user recognize success?

## Users, actors, and ownership

- Which users, roles, services, or external systems participate?
- Who may initiate, view, change, retry, override, or cancel the behavior?
- Who owns the source of truth and who owns projections or downstream effects?
- Are internal users, customers, administrators, and automated actors treated differently?

## Business rules

- Which conditions allow, deny, defer, or alter the behavior?
- When rules conflict, which rule wins?
- What exceptions exist by customer, role, jurisdiction, lifecycle state, product tier, or time?
- Are defaults safe, and who can override them?
- Must historical decisions remain reproducible after rules change?

## Scope and sequencing

- What is the smallest independently valuable first slice?
- What is explicitly excluded even if it is adjacent or desirable?
- Which dependencies or consumers must change first?
- Which manual steps are acceptable initially, and which must be automated?
- What follow-up work should remain possible without redesigning the first slice?

## Scenarios and edge cases

- What are the happy path and the most common alternative paths?
- What happens for missing, malformed, stale, duplicated, or conflicting input?
- What happens when state changes between read and write?
- What happens on retry, timeout, partial success, duplicate delivery, or out-of-order events?
- What happens at empty, minimum, maximum, and high-volume boundaries?
- How are legacy records, partially migrated records, and new records handled?
- What must never happen, even during failure or rollback?

## Codebase and architecture

- Where does the current flow enter, and which component owns each decision or side effect?
- Which APIs, events, schemas, database models, jobs, configuration, flags, and UI states may change?
- Which existing pattern should the design preserve, and where would that pattern be insufficient?
- Are there hidden consumers, caches, generated code, background workers, or external integrations?
- Does the change create a new source of truth, coupling, or consistency boundary?

## Data, contracts, and lifecycle

- What data is read, written, derived, retained, or deleted?
- Which fields are required, optional, immutable, sensitive, or versioned?
- What are the lifecycle states and valid transitions?
- How are contract changes kept backward and forward compatible?
- Is migration, backfill, reconciliation, or provenance required?

## Failure and recovery

- Which failures are user-correctable, retryable, terminal, or ignorable?
- What state remains after partial failure?
- Is the operation idempotent, and what identifies duplicate work?
- How are errors surfaced to users and operators without leaking sensitive data?
- What recovery, reconciliation, rollback, or manual remediation path exists?

## Security, privacy, and compliance

- Who is authorized at each boundary, and is access scoped to a resource or tenant?
- Does the change expose, log, transmit, or retain sensitive data?
- What data must be explicitly prohibited from logs, metrics, events, or prompts?
- Are auditability, consent, retention, residency, or least-privilege requirements relevant?
- Could an external or untrusted input influence privileged behavior?

## Operations and delivery

- What must be observable before and after rollout?
- Which metrics, logs, traces, audits, dashboards, or alerts prove correct behavior?
- Is a feature flag, staged rollout, compatibility window, or deployment order needed?
- What is the rollback trigger and what state must remain compatible during rollback?
- What capacity, latency, cost, rate-limit, or support burden could change?

## Verification

- Which outcomes can be proven with unit, integration, contract, system, or manual tests?
- Which negative and recovery cases are important enough to require explicit coverage?
- What acceptance criteria are observable rather than implementation instructions?
- Which production signal confirms that the original problem is actually solved?
