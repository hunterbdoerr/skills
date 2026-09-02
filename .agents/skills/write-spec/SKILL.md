---
name: write-spec
description: Turn a spec context packet, resolved discovery session, ticket, or document set into a repository-grounded implementation-ready specification in Markdown. Use when asked to create, revise, or review a technical/product spec, architecture decision, operational workflow, implementation proposal, delivery plan, or acceptance criteria. Use build-spec-context first when material business rules, scope, edge cases, ownership, or failure policy are still unresolved. Match the repository's existing spec archetype and keep implementation separate unless code changes are also requested.
---

# Write Spec

Produce a decision-dense specification that reflects the repository's actual state, makes the intended behavior implementable, and gives reviewers and implementers observable completion criteria.

## Instruction Priority and Proportionality

- Follow the user's latest explicit direction for the intended outcome, scope, audience, format, and level of detail.
- Preserve confirmed decisions from the context packet or discovery session unless the user changes them.
- Use repository instructions and verified facts to identify constraints, feasibility issues, and current state. Do not let current implementation or an older spec silently veto a requested target state.
- Use existing specs as presentation and reasoning precedent, not as a source of unrequested product requirements. If the user intentionally changes an earlier decision, name the superseded decision and describe the compatibility or migration consequence.
- Scale the artifact to the work. A focused, low-risk change may need only a concise decision, behavior, affected surface, verification, and acceptance criteria; a cross-boundary or high-risk change needs deeper contracts and delivery treatment.

## Workflow

### 1. Establish the request and destination

- Identify the requested outcome, audience, scope, and whether the task is to create, revise, or review a spec.
- If a spec context packet or discovery session exists, treat it as the requirements handoff: preserve its decisions, assumptions, source links, and open questions while re-verifying repository facts that may have changed.
- Honor user-requested structure and length when they can still support an implementation-ready result. Treat local archetypes as defaults, not mandatory outlines.
- Check handoff readiness. If a material product rule, ownership boundary, source of truth, security decision, or failure policy is missing, use `build-spec-context` before drafting. Proceed with bounded open questions only when they do not force the design to be invented.
- Read repository instructions and locate existing specs, design docs, issue templates, and relevant engineering guidance.
- Sample several recent specs of the same kind. Follow their location, naming, tone, decision density, and section choices rather than copying one outline mechanically.
- Unless the user or repository specifies another location, use the existing flat destination convention: `specs/<year>/q<quarter>/<topic>.md`.
- Read [references/application-spec-patterns.md](references/application-spec-patterns.md) when working in the application repository or when its archetypes fit the target repository. Otherwise use [references/spec-structure.md](references/spec-structure.md) as a fallback.
- Decide whether one document is sufficient. Separate a stable architecture/behavior decision from a mutable delivery/status plan when they have different audiences or update lifecycles.
- Ask a question only when the missing answer would materially change the scope or architecture and cannot be discovered. Otherwise state a bounded assumption or record an open question.
- When the user requests an exploratory or decision-framing document, do not convert it into an implementation commitment. Make the decision status and remaining choices explicit.

### 2. Ground the spec in evidence

- Inspect the relevant source, configuration, migrations, tests, documentation, and adjacent specs before proposing a design.
- Trace the current behavior through its real entry points and boundaries. Search for definitions and call sites; do not infer architecture from filenames alone.
- Verify every named file, symbol, command, dependency, and current-state claim.
- Distinguish observed current state, requested behavior, proposed decisions, and unresolved questions.
- Reconcile the handoff against repository evidence. Preserve product decisions, but flag any technical premise that the current code contradicts.
- Read external documentation only when the design depends on a third-party contract or current behavior. Prefer primary sources.

### 3. Define the design

- Lead with a concise summary or decision that tells the reader what will change, for whom, and why.
- Define goals and explicit non-goals to bound the work.
- Describe the proposed behavior end to end, including ownership boundaries and data flow.
- Make contracts concrete where relevant: inputs, outputs, persistence, APIs, schemas, states, failure semantics, concurrency, security, privacy, observability, compatibility, and rollback.
- Explain consequential choices and rejected alternatives. Avoid narrating obvious mechanics.
- Preserve explicit invariants: data or behavior that must not be lost, duplicated, exposed, reordered, or overwritten.
- Break delivery into reviewable, dependency-ordered slices when the change is too large for one safe change. Give each phase or PR its objective, work, and acceptance boundary.
- Add diagrams only when they clarify a multi-component relationship or sequence better than prose.

### 4. Make completion verifiable

- Define a test strategy at the appropriate layers, including failure paths and boundary behavior.
- Define rollout, migration, monitoring, and rollback when production state or compatibility can change.
- Write acceptance criteria as observable outcomes. Each criterion must be decidable from code, tests, runtime behavior, or an explicit manual check.
- Map acceptance criteria back to goals, business rules, failure semantics, and rollout constraints; do not reduce them to a file-change checklist.
- Keep deferred work out of the committed scope and identify it as a follow-up.

### 5. Write and review the artifact

- Use the repository's terminology and Markdown style.
- Prefer concise prose, tables for exact mappings, and code blocks only for contracts or commands that benefit from precision.
- Omit irrelevant or empty template sections. Add domain-specific sections when the risk requires them.
- Prefer the shortest document that preserves the consequential decisions, contracts, risks, and proof of completion.
- Use status checklists only for verified implementation state. Never mark proposed work complete because a similar implementation exists.
- Preserve useful existing content when revising; reconcile contradictions rather than replacing the document wholesale.
- Do not modify production code, configuration, or migrations unless the user separately requests implementation.
- Run a final review against the checklist below, then report the spec path, major decisions, assumptions, and open questions.

## Quality Checklist

- The problem, intended outcome, goals, and non-goals agree.
- The artifact follows explicit user constraints and does not import requirements solely from repository precedent.
- The chosen spec archetype fits the work; architecture decisions and delivery tracking are separated when their lifecycles differ.
- Current-state claims are supported by repository evidence and are clearly separated from the target state.
- The design identifies ownership and behavior across every affected boundary.
- Contracts define validation, state transitions, replacement/merge semantics, ordering, and idempotency where relevant.
- Failure, security/privacy, compatibility, migration, and operational concerns are addressed when applicable.
- Delivery steps are ordered, independently reviewable where practical, and do not hide prerequisites.
- Tests map to requirements and include meaningful negative cases.
- Acceptance criteria are specific, observable, and collectively cover the goals.
- Open questions name the decision needed and its impact; they do not substitute for discoverable facts.
- The spec contains no invented paths, symbols, commands, APIs, or completed work.

## Reference

Read [references/spec-structure.md](references/spec-structure.md) when creating a new spec or when the target repository has no clear structure. Use it as a menu, not a requirement to include every section.
