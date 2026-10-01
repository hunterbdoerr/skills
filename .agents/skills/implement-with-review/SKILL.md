---
name: implement-with-review
description: Implement a well-defined coding change through a structured multi-agent workflow with one implementer, two independent reviewers, feedback adjudication, and evidence-producing testing. Use when the user explicitly invokes this skill after establishing or referencing adequate context and wants stronger implementation quality without the planning overhead of a full specification orchestrator. Best for focused changes owned in one repository; do not use for discovery, unresolved product decisions, broad programs, or multi-task specifications.
---

# Implement With Review

Coordinate one bounded code change through implementation, two independent
reviews, feedback adjudication, and testing. Keep the workflow in the session;
do not create coordinator plans, task files, or journals in the repository.
The session agent coordinates the workflow and writes the final handoff; it does
not substitute for the implementer, reviewers, feedback assessor, or tester.

## Establish the contract

1. Read the referenced context, repository instructions, relevant code and tests,
   and the working-tree state. Load any skills required by the repository or the
   requested work.
2. Confirm that the available context defines:
   - the intended behavior and current problem;
   - included and excluded scope;
   - objective acceptance checks; and
   - the repository and runtime surface to change.
3. Stop for the smallest missing decision if proceeding would invent product
   behavior. Recommend a broader planning or specification workflow when the
   change contains multiple independently deliverable outcomes, unresolved
   architecture, or coordination across several services.
4. Record a compact contract in the conversation and plan: outcome, boundaries,
   acceptance checks, likely touchpoints, applicable instructions, focused test
   commands, and material risks. Do not ask for another approval when explicit
   invocation already authorizes the well-defined implementation.
5. Preserve unrelated work. Do not stage, commit, branch, push, open a pull
   request, deploy, or perform unrelated cleanup unless separately requested.

## Dispatch the implementer

Create one implementation subagent named `implementer` and keep it available for
all repair rounds. Give it the compact contract, source context, relevant paths,
repository instructions, current working-tree state, and exact acceptance checks.

Require the implementer to:

- inspect the actual code and nearby tests before editing;
- make the narrowest complete change directly in the shared working tree;
- add or update proportionate tests when behavior changes;
- run focused checks and report exact commands, results, changed files, and any
  residual concern; and
- avoid unrelated edits and actions not authorized by the user.

Inspect the resulting diff before review. Stop if it exceeds the contract or
overlaps unrelated user changes in a way that cannot be preserved safely.

## Run two independent reviews

After implementation, create two fresh reviewer subagents in parallel. Reviewers
must be distinct from the implementer and from each other, must not edit files,
and must review the same current diff and test evidence independently. Do not
show either reviewer the other review.

Give both reviewers the contract, referenced context, repository instructions,
current diff, and implementer evidence. Assign complementary emphases without
limiting either reviewer's ability to report any defect:

- `reviewer-1`: requirements, behavior, correctness, and edge cases.
- `reviewer-2`: regressions, test adequacy, maintainability, security, and
  repository conventions.

Require each finding to include severity, file and location, evidence or a
reproduction path, the violated acceptance check or invariant, and a bounded fix.
Require a verdict of `pass`, `changes-required`, or `blocked`. Optional cleanup
and out-of-scope improvements cannot block the change.

## Adjudicate and repair

Create a fresh, read-only subagent named `feedback-assessor`. Give it the compact
contract, current diff, test evidence, both raw review reports, and the
implementer's canonical task name. Do not ask the session agent or implementer
to merge the reviews.

Require the feedback assessor to validate the findings against the code, resolve
duplicates and contradictions, and classify each finding as:

- `required`: an evidenced in-scope correctness, regression, security, test, or
  repository-compliance issue;
- `optional`: worthwhile but outside the acceptance boundary; or
- `rejected`: unsupported, incorrect, or already satisfied.

The assessor must return one verdict: `pass`, `repair`, or `blocked`. For
`repair`, it must author a single direct repair instruction containing ordered
changes and checks, then send that instruction to the same `implementer` as a
follow-up task. If agent topology prevents direct delivery, relay the assessor's
instruction verbatim. The assessor must not edit files.

After repair, have the feedback assessor inspect the updated diff and focused
test evidence to confirm every required finding is resolved. Repeat with the same
implementer only for unresolved required findings. Do not implement optional or
rejected findings. Stop for the user when repair would expand scope or require a
missing decision.

## Test and collect evidence

Once review findings are resolved, create a fresh tester subagent. Give it the
contract, final diff, repository instructions, review disposition, and the
expected verification commands. The tester must not change implementation code.

Require the tester to verify every acceptance check and relevant regression gate
in the most realistic available environment. It must report:

- a `pass`, `fail`, or `blocked` verdict;
- each command or manual flow, its result, and the acceptance check it covers;
- concise expected-versus-actual evidence for failures; and
- durable artifact paths for screenshots, recordings, logs, reports, or other
  useful evidence.

Capture visual evidence when the changed behavior has a visible interface and a
runnable environment is available. Prefer screenshots of the changed state and
important interaction outcomes. For nonvisual work, use focused test output,
request/response examples, logs, or generated reports. Never treat a screenshot
alone as proof of behavior that should have an automated test.

On `fail`, send the tester's reproduction and evidence to the same implementer
for the narrowest repair, then have the same tester rerun the failed checks and
all affected regression checks. Continue until the tester passes or a genuine
blocker or scope decision emerges. If the same root cause survives two repair
attempts, stop cycling, summarize the evidence, and ask the user for direction.
A blocked or unexecuted required check is not a successful run.

## Hand off success

Only declare success after the tester passes every required acceptance check and
regression gate. Return:

1. a concise implementation summary and changed-file list;
2. the successful test evidence, with exact commands and results;
3. clickable paths to visual or other test artifacts when available;
4. any residual risk or unperformed optional check;
5. a concise, imperative pull request title; and
6. a ready-to-paste pull request description with `Summary`, `Testing`, and
   `Evidence / Risks` sections.

State clearly that the pull request title and description are proposed handoff
text; do not imply a pull request was created. Do not report success when required
evidence is missing.
