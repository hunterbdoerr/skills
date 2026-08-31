---
name: build-spec-context
description: Build a repository-grounded requirements and decision handoff for write-spec. Use when an idea, ticket, conversation, or document set still needs clarification of business rules, user outcomes, scope, edge cases, technical implications, risks, or open decisions before a specification can be written. Investigate facts in the codebase, interview the user adaptively about intent and policy, stress-test the proposal, and produce a structured spec context packet rather than a finished spec.
---

# Build Spec Context

Turn an early idea or scattered evidence into a decision-rich context packet that `write-spec` can convert into an implementation-ready specification without repeating discovery.

## Operating Principles

- Treat the user's latest explicit intent as the primary source for desired outcomes, scope, priorities, and product policy. Repository evidence describes the current system and its constraints; it does not override the user's requested target state.
- When user direction conflicts with an existing spec or convention, surface the conflict and its consequences. Confirm only when the conflict appears accidental, unsafe, or makes the requested outcome incoherent; otherwise preserve the user's direction and identify what it supersedes.
- Collaborate as a technical discovery partner, not a form. Ask focused questions, reflect what changed, and follow important threads.
- Inspect the repository before asking the user about facts the code, tests, docs, configuration, or history can answer.
- Ask the user about intent, policy, priorities, exceptions, and tradeoffs that repository evidence cannot decide.
- Surface implications and contradictions proactively. Do not merely record the user's first answer.
- Separate confirmed facts, repository evidence, proposed decisions, assumptions, and unresolved questions.
- Separate requirements from technical implications. Do not silently promote a likely implementation into a business requirement.
- Scale discovery to the change's ambiguity and risk. A small, well-bounded request may need one evidence pass and a compact handoff; do not force every discovery lens or packet section into every task.
- Do not write the final specification or implement code unless the user explicitly asks to transition to that work.

## Workflow

### 1. Establish the discovery target

- Identify the initial idea, problem, ticket, transcript, or document set and the repository in scope.
- Capture any user-requested output shape, level of detail, constraints, exclusions, and decisions that intentionally depart from current behavior or precedent.
- Summarize the starting point in a few sentences and state the largest visible uncertainty.
- Read [references/discovery-lenses.md](references/discovery-lenses.md) before beginning a new discovery interview.
- Select the working mode:
  - **Idea discovery**: investigate the repository, then interview the user.
  - **Document synthesis**: reconcile supplied sources, then ask only about conflicts and gaps.
  - **Session closeout**: extract decisions and evidence already established, then test readiness.

### 2. Build an evidence map

- Read repository instructions and relevant existing specs, product docs, source, tests, configuration, schemas, and migrations.
- Trace the current behavior through real entry points, ownership boundaries, data flows, and external integrations.
- Extract claims from supplied documents with their source paths or links. Flag disagreements, stale claims, and missing evidence.
- Share a concise current-state summary with the user before asking detailed questions. Include the evidence that materially changes the framing.

For the first discovery response, provide:

1. the current understanding of the problem;
2. the most relevant repository findings;
3. the highest-risk implication or ambiguity;
4. one to three questions that unlock the next decision.

### 3. Conduct adaptive discovery

- Ask one to three related questions per turn. Prefer the smallest question set that can unlock the next useful investigation.
- Explain briefly why a question matters when its consequence is not obvious.
- Offer concrete options with tradeoffs when the repository suggests likely choices; allow the user to reject the framing.
- After each answer, update the working model, investigate newly relevant code, and probe consequences or exceptions.
- Cover the relevant lenses from the reference, but skip inapplicable prompts and avoid repeating settled questions.
- Follow the user's emphasis. Probe edge cases and technical consequences to improve their decision, not to redirect the task toward whatever the repository already does.
- When the user is unsure, propose a bounded default and label it as a proposal rather than silently converting it into a requirement.
- Do not ask the user to choose code-level details until the business behavior or system constraint makes that choice necessary.

### 4. Stress-test the emerging requirements

- Walk through the primary success path from trigger to observable outcome.
- Test boundary cases, invalid inputs, partial state, retries, concurrency, permissions, historical data, compatibility, and operational failure where applicable.
- Look for business-rule collisions: precedence, exceptions, timing, ownership, lifecycle transitions, and what must never happen.
- Map each proposed behavior to likely codebase surfaces and identify hidden coupling, migrations, deployment ordering, or test impact.
- Challenge scope that cannot be delivered or verified independently; separate later work from the first useful slice.
- Identify invariants explicitly, especially data that must not be lost, duplicated, exposed, or overwritten.

### 5. Maintain checkpoints

Periodically summarize:

- what is confirmed;
- what repository evidence supports it;
- what decisions were made and why;
- what assumptions remain;
- what is explicitly out of scope;
- what questions still block a safe spec.

Ask the user to correct the checkpoint instead of waiting until the final handoff to discover misunderstandings.
Use a checkpoint after a meaningful decision cluster or when the framing changes; do not repeat a ledger after every answer.

### 6. Produce the handoff

- Read [references/context-packet.md](references/context-packet.md) and produce a proportionate context packet in the conversation by default. Compress related sections for small changes; retain the distinctions among user direction, verified evidence, proposals, assumptions, and open questions.
- If the user needs cross-session or cross-agent transfer, write the packet to a user-approved Markdown path.
- Preserve source paths, links, decisions, dissent, assumptions, and unresolved questions. Do not erase uncertainty to make the packet look complete.
- Mark readiness as **ready**, **ready with open questions**, or **not ready**. Explain any blocker and the decision needed.
- Recommend the likely spec shape: product/implementation, architecture decision, operational workflow, focused contract/security change, delivery plan, or a paired architecture document and delivery plan.
- When the user wants to proceed, apply the `write-spec` skill to the packet and repository evidence. Do not make the user restate the discovery.

## Readiness Gate

A context packet is ready for specification when it contains enough information to state:

- the problem, affected users or operators, and desired outcome;
- goals, non-goals, and a bounded first delivery slice;
- important business rules and exception behavior;
- verified current-state architecture and affected boundaries;
- expected behavior, data or contract implications, and failure semantics;
- security, privacy, compatibility, rollout, and observability implications where relevant;
- testable success signals;
- decisions already made and unresolved questions that can safely remain open.

Mark the packet **not ready** when a missing product rule, ownership decision, security boundary, source-of-truth decision, or failure policy would force `write-spec` to invent the design. Do not require false certainty: a packet may be **ready with open questions** when the questions are bounded and do not prevent a coherent first slice.

Do not treat a decision as blocking when the user deliberately excludes the behavior it governs from the current slice. Record the boundary and the consequence of expanding scope later.
