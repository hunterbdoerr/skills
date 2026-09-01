from __future__ import annotations

import hashlib
import importlib.util
import random
import re
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
PLAN_TEMPLATE = (SKILL_ROOT / "assets" / "plan.md").read_text(encoding="utf-8")
TASK_TEMPLATE = (SKILL_ROOT / "assets" / "task.md").read_text(encoding="utf-8")
ROLE_CONTRACT = (SKILL_ROOT / "references" / "role-contracts.md").read_text(
    encoding="utf-8"
)
VALIDATOR_SCRIPT = SKILL_ROOT / "scripts" / "validate_state.py"
VALIDATOR_SPEC = importlib.util.spec_from_file_location(
    "planning_contract_validate_state", VALIDATOR_SCRIPT
)
assert VALIDATOR_SPEC and VALIDATOR_SPEC.loader
validate_state = importlib.util.module_from_spec(VALIDATOR_SPEC)
sys.modules[VALIDATOR_SPEC.name] = validate_state
VALIDATOR_SPEC.loader.exec_module(validate_state)

CRITERIA = ("AC-03", "AC-04", "AC-05", "AC-06")
PLANNER_FIELDS = (
    "Status",
    "Task list",
    "Acceptance coverage",
    "Repository impact",
    "Risks and guardrails",
    "Assumptions",
    "Unresolved decisions",
    "Final verification",
    "Blocker",
)


@dataclass
class TaskProposal:
    task_id: str
    kind: str
    title: str
    objective: str
    dependencies: tuple[str, ...]
    criteria: tuple[str, ...]
    verification: str
    bounded: bool = True
    delegates: bool = False
    risk: str = "low; local fixture only"
    human_gate: bool = False


@dataclass
class PlannerProposal:
    tasks: list[TaskProposal]
    coverage: dict[str, tuple[str, str]]
    disclosed_risks: tuple[str, ...]
    assumptions: tuple[str, ...]
    unresolved_decisions: tuple[str, ...]
    critical_review: tuple[str, str, str, str] | None
    repository_impact: dict[str, str] = field(default_factory=dict)
    final_verification: dict[str, str] = field(default_factory=dict)
    status: str = "ready"
    blocker: str = "none"
    report: str = ""


def planner_report(proposal: PlannerProposal) -> str:
    repository = proposal.repository_impact
    final_verification = proposal.final_verification
    task_lines = []
    for task in proposal.tasks:
        review = proposal.critical_review
        if task.human_gate and review:
            review_evidence = (
                f"required; task={review[0]}; timing={review[1]}; "
                f"decision={review[2]}; link={review[3]}"
            )
        elif task.human_gate:
            review_evidence = "required; missing"
        else:
            review_evidence = "not required"
        task_lines.extend(
            (
                f"- {task.task_id}, {task.kind}, {task.title}, {task.objective}",
                f"  Dependencies: {', '.join(task.dependencies) or 'none'}",
                "  In-scope and prohibited work: "
                f"bounded for one direct implementer={'yes' if task.bounded else 'no'}; "
                f"direct execution only={'no' if task.delegates else 'yes'}; "
                "local fixture tests; no external calls",
                f"  Task acceptance criteria: {', '.join(task.criteria)}",
                f"  Primary verification: {task.verification}",
                f"  Risk classification: {task.risk}",
                f"  Human gate and exact review section: {review_evidence}",
            )
        )
    coverage = "\n".join(
        f"- {criterion}: {owners[0]}; {owners[1]}"
        for criterion, owners in proposal.coverage.items()
    )
    risks = "\n".join(f"- {risk}" for risk in proposal.disclosed_risks) or "- none"
    assumptions = "\n".join(f"- {item}" for item in proposal.assumptions) or "- none"
    decisions = (
        "\n".join(f"- {item}" for item in proposal.unresolved_decisions) or "- none"
    )
    return f"""Status: {proposal.status}

Task list:
{chr(10).join(task_lines)}

Acceptance coverage:
{coverage}

Repository impact:
- Components and contracts: {repository['Components and contracts']}
- Migrations and dependencies: {repository['Migrations and dependencies']}
- External systems: {repository['External systems']}
- Pre-existing working-tree considerations: {repository['Pre-existing working-tree considerations']}

Risks and guardrails:
{risks}

Assumptions:
{assumptions}

Unresolved decisions:
{decisions}

Final verification:
- Complete-spec coverage: {final_verification['Complete-spec coverage']}
- Integration checks: {final_verification['Integration checks']}
- Repository final gate: {final_verification['Repository final gate']}

Blocker: {proposal.blocker}
"""


def conforming_proposal() -> PlannerProposal:
    tasks = [
        TaskProposal(
            "task-001",
            "implementation",
            "Render canonical state",
            "Render the approved fixture package",
            (),
            ("AC-03", "AC-04"),
            "inspect canonical files",
        ),
        TaskProposal(
            "task-002",
            "implementation",
            "Record critical review",
            "Expose the exceptional decision before execution",
            ("task-001",),
            ("AC-05", "AC-06"),
            "inspect exact plan-to-task link",
            human_gate=True,
        ),
        TaskProposal(
            "task-final-verification",
            "final-verification",
            "Final verification",
            "Verify the complete approved fixture",
            ("task-001", "task-002"),
            CRITERIA,
            "python -m unittest discover",
        ),
    ]
    proposal = PlannerProposal(
        tasks=tasks,
        coverage={
            criterion: (
                "task-001" if criterion in {"AC-03", "AC-04"} else "task-002",
                "task-final-verification",
            )
            for criterion in CRITERIA
        },
        disclosed_risks=(
            "Impact reference: none; Risk: local fixture rendering; Mitigation: temporary directory rollback; Required approval: plan approval",
        ),
        assumptions=(
            "Assumption: Python 3 standard library is available; Supporting source: repository test contract",
        ),
        unresolved_decisions=(),
        critical_review=(
            "task-002",
            "before cycle 1",
            "approve or reject fixture-only execution",
            "tasks/task-002-record-critical-review.md#critical-human-review",
        ),
        repository_impact={
            "Components and contracts": "test-only fixture state",
            "Migrations and dependencies": "none",
            "External systems": "none",
            "Pre-existing working-tree considerations": "preserve existing changes",
        },
        final_verification={
            "Complete-spec coverage": "task-final-verification covers AC-03 through AC-06",
            "Integration checks": "canonical plan, task, and critical-review linkage",
            "Repository final gate": "python -m unittest discover",
        },
    )
    proposal.report = planner_report(proposal)
    return proposal


TASK_BLOCK_RE = re.compile(
    r"^- (?P<id>[^,\n]+), (?P<kind>[^,\n]+), "
    r"(?P<title>[^,\n]+), (?P<objective>[^\n]+)\n"
    r"  Dependencies: (?P<dependencies>[^\n]+)\n"
    r"  In-scope and prohibited work: bounded for one direct implementer="
    r"(?P<bounded>yes|no); direct execution only=(?P<direct>yes|no); "
    r"local fixture tests; no external calls\n"
    r"  Task acceptance criteria: (?P<criteria>[^\n]+)\n"
    r"  Primary verification: (?P<verification>[^\n]+)\n"
    r"  Risk classification: (?P<risk>[^\n]+)\n"
    r"  Human gate and exact review section: (?P<gate>[^\n]+)$",
    re.MULTILINE,
)


def report_section(report: str, heading: str, next_heading: str) -> str:
    start = f"{heading}:\n"
    end = f"\n\n{next_heading}:"
    if start not in report:
        return ""
    remainder = report.split(start, 1)[1]
    if end not in remainder:
        return ""
    return remainder.split(end, 1)[0]


def bullet_values(section: str, heading: str) -> tuple[tuple[str, ...], list[str]]:
    values = []
    errors = []
    for line in section.splitlines():
        if not line.strip():
            continue
        if not line.startswith("- ") or not line[2:].strip():
            errors.append(f"malformed planner report: unstructured {heading} line")
            continue
        values.append(line[2:])
    if "none" in values and len(values) != 1:
        errors.append(f"malformed planner report: {heading} mixes none with values")
    return (() if values == ["none"] else tuple(values)), errors


def required_prefixed_lines(
    report: str, heading: str, next_heading: str, prefixes: tuple[str, ...]
) -> list[str]:
    section = report_section(report, heading, next_heading)
    errors = []
    for prefix in prefixes:
        matches = [line for line in section.splitlines() if line.startswith(prefix)]
        if len(matches) != 1 or not matches[0][len(prefix) :].strip():
            errors.append(f"malformed planner report: {heading} missing {prefix}")
    for line in section.splitlines():
        if line.strip() and not any(line.startswith(prefix) for prefix in prefixes):
            errors.append(f"malformed planner report: unstructured {heading} line")
    return errors


def prefixed_values(
    report: str, heading: str, next_heading: str, labels: tuple[str, ...]
) -> dict[str, str]:
    section = report_section(report, heading, next_heading)
    values = {}
    for label in labels:
        prefix = f"- {label}: "
        matches = [line for line in section.splitlines() if line.startswith(prefix)]
        if len(matches) == 1:
            values[label] = matches[0][len(prefix) :]
    return values


def parse_planner_report(report: str) -> tuple[PlannerProposal | None, list[str]]:
    errors = report_structure_errors(report)
    if errors:
        return None, errors

    task_section = report_section(report, "Task list", "Acceptance coverage")
    raw_blocks = []
    if task_section.strip() != "- none":
        raw_blocks = [
            block.strip()
            for block in re.split(r"(?m)(?=^- task-)", task_section.strip())
            if block.strip()
        ]
    tasks: list[TaskProposal] = []
    critical_review = None
    for raw_block in raw_blocks:
        match = TASK_BLOCK_RE.fullmatch(raw_block)
        if not match:
            errors.append("malformed planner report: incomplete task subfields")
            continue
        dependencies = (
            ()
            if match["dependencies"] == "none"
            else tuple(item.strip() for item in match["dependencies"].split(","))
        )
        criteria = tuple(item.strip() for item in match["criteria"].split(","))
        gate = match["gate"]
        human_gate = gate != "not required"
        if gate == "required; missing":
            pass
        elif human_gate:
            gate_match = re.fullmatch(
                r"required; task=([^;]+); timing=([^;]+); "
                r"decision=([^;]*); link=(.+)",
                gate,
            )
            if not gate_match:
                errors.append("malformed planner report: incomplete critical review")
            else:
                review = gate_match.groups()
                if critical_review is not None and critical_review != review:
                    errors.append("malformed planner report: conflicting critical reviews")
                critical_review = review
        tasks.append(
            TaskProposal(
                match["id"],
                match["kind"],
                match["title"],
                match["objective"],
                dependencies,
                criteria,
                match["verification"],
                bounded=match["bounded"] == "yes",
                delegates=match["direct"] == "no",
                risk=match["risk"],
                human_gate=human_gate,
            )
        )

    coverage: dict[str, tuple[str, str]] = {}
    coverage_section = report_section(
        report, "Acceptance coverage", "Repository impact"
    )
    if coverage_section.strip() != "- none":
        for line in coverage_section.splitlines():
            match = re.fullmatch(r"- ([^:]+): ([^;]+); (.+)", line)
            if not match:
                errors.append("malformed planner report: invalid acceptance coverage")
                continue
            if match[1] in coverage:
                errors.append("malformed planner report: duplicate acceptance coverage")
            coverage[match[1]] = (match[2], match[3])

    repository_labels = (
        "Components and contracts",
        "Migrations and dependencies",
        "External systems",
        "Pre-existing working-tree considerations",
    )
    final_labels = (
        "Complete-spec coverage",
        "Integration checks",
        "Repository final gate",
    )
    errors.extend(
        required_prefixed_lines(
            report,
            "Repository impact",
            "Risks and guardrails",
            tuple(f"- {label}: " for label in repository_labels),
        )
    )
    errors.extend(
        required_prefixed_lines(
            report,
            "Final verification",
            "Blocker",
            tuple(f"- {label}: " for label in final_labels),
        )
    )
    repository_impact = prefixed_values(
        report, "Repository impact", "Risks and guardrails", repository_labels
    )
    final_verification = prefixed_values(
        report, "Final verification", "Blocker", final_labels
    )

    risks, risk_errors = bullet_values(
        report_section(report, "Risks and guardrails", "Assumptions"),
        "Risks and guardrails",
    )
    assumptions, assumption_errors = bullet_values(
        report_section(report, "Assumptions", "Unresolved decisions"),
        "Assumptions",
    )
    decisions, decision_errors = bullet_values(
        report_section(report, "Unresolved decisions", "Final verification"),
        "Unresolved decisions",
    )
    errors.extend(risk_errors + assumption_errors + decision_errors)
    status_match = re.search(r"(?m)^Status: (.*)$", report)
    blocker_match = re.search(r"(?m)^Blocker: (.*)$", report)
    if status_match is None or blocker_match is None:
        return None, errors or ["malformed planner report: invalid scalar syntax"]
    status = status_match.group(1)
    blocker = blocker_match.group(1).strip()
    if errors:
        return None, errors
    return (
        PlannerProposal(
            tasks=tasks,
            coverage=coverage,
            disclosed_risks=risks,
            assumptions=assumptions,
            unresolved_decisions=decisions,
            critical_review=critical_review,
            repository_impact=repository_impact,
            final_verification=final_verification,
            status=status,
            blocker=blocker,
            report=report,
        ),
        [],
    )


def semantic_errors(proposal: PlannerProposal) -> list[str]:
    errors: list[str] = []
    ids = [task.task_id for task in proposal.tasks]
    if len(ids) != len(set(ids)):
        errors.append("duplicate task ID")
    id_set = set(ids)
    positions = {task_id: index for index, task_id in enumerate(ids)}
    for task in proposal.tasks:
        if task.kind not in {"implementation", "final-verification"}:
            errors.append(f"unsupported task kind: {task.kind}")
        if task.kind == "implementation":
            if not re.fullmatch(r"task-[0-9]{3,}", task.task_id):
                errors.append(f"noncanonical implementation task ID: {task.task_id}")
            if not re.fullmatch(
                r"task-[0-9]{3,}-[a-z0-9]+(?:-[a-z0-9]+)*\.md",
                task_filename(task),
            ):
                errors.append(f"noncanonical task file: {task_filename(task)}")
        elif task.kind == "final-verification":
            if task.task_id != "task-final-verification":
                errors.append(f"noncanonical final task ID: {task.task_id}")
            if task_filename(task) != "task-final-verification.md":
                errors.append(f"noncanonical final task file: {task_filename(task)}")
        if not task.bounded:
            errors.append(f"oversized task: {task.task_id}")
        if task.delegates:
            errors.append(f"delegated task: {task.task_id}")
        for dependency in task.dependencies:
            if dependency not in id_set:
                errors.append(f"missing dependency: {dependency}")
            elif positions[dependency] >= positions[task.task_id]:
                errors.append(
                    f"dependency order: {dependency} must precede {task.task_id}"
                )

    graph = {task.task_id: task.dependencies for task in proposal.tasks}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            errors.append("circular dependency")
            return
        if task_id in visited or task_id not in graph:
            return
        visiting.add(task_id)
        for dependency in graph[task_id]:
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in ids:
        visit(task_id)

    finals = [task for task in proposal.tasks if task.kind == "final-verification"]
    if len(finals) != 1:
        errors.append("exactly one final-verification task required")
    else:
        implementations = {
            task.task_id for task in proposal.tasks if task.kind == "implementation"
        }
        if set(finals[0].dependencies) != implementations:
            errors.append("final task must depend on every implementation task")

    for criterion in CRITERIA:
        owners = proposal.coverage.get(criterion)
        if not owners or not all(owner in id_set for owner in owners):
            errors.append(f"unmapped criterion: {criterion}")
            continue
        implementation_owner = next(
            task for task in proposal.tasks if task.task_id == owners[0]
        )
        verification_owner = next(
            task for task in proposal.tasks if task.task_id == owners[1]
        )
        if criterion not in implementation_owner.criteria:
            errors.append(f"coverage contradiction: {criterion} implementation owner")
        if criterion not in verification_owner.criteria:
            errors.append(f"coverage contradiction: {criterion} verification owner")
    parsed_risks = []
    for risk in proposal.disclosed_risks:
        match = re.fullmatch(
            r"Impact reference: ([^;]+); Risk: (.+); Mitigation: (.+); Required approval: (.+)",
            risk,
        )
        if not match:
            errors.append("malformed risk disclosure")
        else:
            parsed_risks.append(tuple(part.strip() for part in match.groups()))
    if not parsed_risks:
        errors.append("hidden risk")
    external_systems = proposal.repository_impact["External systems"]
    if external_systems != "none" and not any(
        normalize_impact_identity(reference)
        == normalize_impact_identity(external_systems)
        and approval.lower() not in {"none", "not required", "not-required"}
        for reference, _risk, _mitigation, approval in parsed_risks
    ):
        errors.append("external systems lack disclosed risk and required approval")
    migrations = proposal.repository_impact["Migrations and dependencies"]
    if migrations != "none":
        if not any(
            normalize_impact_identity(reference)
            == normalize_impact_identity(migrations)
            and approval.lower() not in {"none", "not required", "not-required"}
            for reference, _risk, _mitigation, approval in parsed_risks
        ):
            errors.append("material impact lacks matching risk and required approval")
    if proposal.unresolved_decisions:
        errors.append("unresolved decision")
    for assumption in proposal.assumptions:
        if not re.fullmatch(r"Assumption: .+; Supporting source: .+", assumption):
            errors.append("malformed assumption disclosure")
    for decision in proposal.unresolved_decisions:
        if not re.fullmatch(
            r"Decision: .+; Impact: .+; Required human input: .+", decision
        ):
            errors.append("malformed unresolved decision disclosure")
    gated = [task for task in proposal.tasks if task.human_gate]
    review = proposal.critical_review
    if gated and review is None:
        errors.append("missing critical review")
    elif review is not None:
        task_id, timing, decision, link = review
        expected_task = gated[0].task_id if len(gated) == 1 else None
        if task_id != expected_task:
            errors.append("critical review task mismatch")
        if timing != "before cycle 1":
            errors.append("critical review timing mismatch")
        if not decision.strip():
            errors.append("critical review decision missing")
        review_task = next((task for task in gated if task.task_id == task_id), None)
        expected_link = (
            f"tasks/{task_filename(review_task)}#critical-human-review"
            if review_task
            else None
        )
        if link != expected_link:
            errors.append("critical review exact link mismatch")
    return errors


def report_structure_errors(report: str) -> list[str]:
    role_schema = ROLE_CONTRACT.split("### Report schema", 1)[1].split(
        "## Implementer", 1
    )[0]
    if not all(f"{field}:" in role_schema for field in PLANNER_FIELDS):
        return ["role contract schema mismatch"]
    positions = []
    errors = []
    for field in PLANNER_FIELDS:
        matches = list(re.finditer(rf"(?m)^{re.escape(field)}:", report))
        if len(matches) != 1:
            errors.append(f"malformed planner report: {field} count {len(matches)}")
        else:
            positions.append(matches[0].start())
    if len(positions) == len(PLANNER_FIELDS) and positions != sorted(positions):
        errors.append("malformed planner report: field order")
    status_match = re.search(r"(?m)^Status: (.*)$", report)
    blocker_match = re.search(r"(?m)^Blocker: (.*)$", report)
    task_heading = re.search(r"(?m)^Task list:$", report)
    if status_match and report[: status_match.start()].strip():
        errors.append("malformed planner report: unmatched preamble")
    if status_match and task_heading and report[status_match.end() : task_heading.start()].strip():
        errors.append("malformed planner report: unmatched status/task text")
    if blocker_match and report[blocker_match.end() :].strip():
        errors.append("malformed planner report: unmatched postamble")
    status = status_match.group(1) if status_match else None
    blocker = blocker_match.group(1).strip() if blocker_match else None
    if status is None or not status.strip():
        errors.append("malformed planner report: empty Status value")
    elif status not in {"ready", "blocked"}:
        errors.append("malformed planner report: invalid status")
    if blocker is None or not blocker:
        errors.append("malformed planner report: empty Blocker value")
    if status_match and blocker_match:
        if status == "ready" and blocker != "none":
            errors.append("malformed planner report: ready report has blocker")
        if status == "blocked" and blocker == "none":
            errors.append("malformed planner report: blocked report lacks blocker")
    if len(positions) == len(PLANNER_FIELDS) and positions == sorted(positions):
        task_section = report_section(report, "Task list", "Acceptance coverage")
        coverage_section = report_section(
            report, "Acceptance coverage", "Repository impact"
        )
        for heading, section in (
            ("Task list", task_section),
            ("Acceptance coverage", coverage_section),
        ):
            value = section.strip()
            if not value:
                errors.append(f"malformed planner report: blank {heading}")
            elif value == "- none":
                if section != "- none":
                    errors.append(
                        f"malformed planner report: {heading} none bullet must be exact"
                    )
                elif status != "blocked":
                    errors.append(
                        f"malformed planner report: {heading} uses none for non-blocked status"
                    )
    return errors


def normalize_impact_identity(value: str) -> str:
    return " ".join(value.casefold().split())


def task_filename(task: TaskProposal) -> str:
    if task.kind == "final-verification":
        return "task-final-verification.md"
    return f"{task.task_id}-{task.title.lower().replace(' ', '-')}.md"


def strip_template_comments(text: str) -> str:
    return re.sub(r"\n?<!--.*?-->\n?", "\n", text, flags=re.DOTALL)


def render_task(
    task: TaskProposal, critical_review: tuple[str, str, str, str] | None
) -> str:
    text = TASK_TEMPLATE.replace("kind: implementation", f"kind: {task.kind}", 1)
    dependency_value = "[" + ", ".join(task.dependencies) + "]"
    text = text.replace("dependencies: []", f"dependencies: {dependency_value}", 1)
    replacements = {
        "task-<NNN>": task.task_id,
        "<NNN>": task.task_id.removeprefix("task-"),
        "<title>": task.title,
        "<One bounded outcome that one direct implementer can complete without\ndelegation or a task-local planning pass.>": task.objective,
        "[`<exact spec heading>`](../../spec.md#<heading-anchor>)": "[`Acceptance Criteria`](../../spec.md#acceptance-criteria)",
        "<other exact plan heading>": "[`Required Human Review`](../plan.md#required-human-review)",
        "<task ID and required passed outcome, or none>": ", ".join(task.dependencies) or "none",
        "<exact allowed files, code, tests, and behavior; include enough detail for\n  direct implementation without delegation>": "Temporary fixture package files and deterministic standard-library checks only.",
        "<explicitly excluded work and side effects>": "Live agents, external calls, inferred approval, and repository writes.",
        "<objective, verifiable task criterion>": "; ".join(task.criteria),
        "<exact focused command or inspection that one independent direct tester can\n  run without delegation>": task.verification,
        "<required integration evidence, if any>": "Validator plan-ready result for the complete fixture.",
        "<task risk and guardrail, or none>": task.risk,
    }
    for source, replacement in replacements.items():
        text = text.replace(source, replacement)
    text = strip_template_comments(text)
    if task.human_gate:
        text = text.replace("human_gate: false", "human_gate: true").replace(
            "human_gate_status: not-required", "human_gate_status: pending"
        )
        assert critical_review and critical_review[0] == task.task_id
        text = text.replace(
            "Not required.",
            f"- Review timing: {critical_review[1]}\n"
            "- Issue: fixture-only execution boundary\n"
            f"- Decision required: {critical_review[2]}\n"
            "- Safe default while pending: stop without implementation",
        )
    return text


def render_plan(proposal: PlannerProposal, digest: str) -> str:
    text = PLAN_TEMPLATE
    execution_rows = "\n".join(
        "| {order} | [`{id}`](tasks/{filename}) | {objective} | {dependencies} | "
        "{verification} | {risk} | {gate} |".format(
            order=index,
            id=task.task_id,
            filename=task_filename(task),
            objective=task.objective,
            dependencies=", ".join(task.dependencies) or "None",
            verification=task.verification,
            risk=task.risk,
            gate="Required" if task.human_gate else "Not required",
        )
        for index, task in enumerate(proposal.tasks, 1)
    )
    coverage_rows = "\n".join(
        f"| {criterion} | {owners[0]} | {owners[1]} |"
        for criterion, owners in proposal.coverage.items()
    )
    progress_rows = "\n".join(
        f"| `{task.task_id}` | pending | 0 / 3 | pending | none |"
        for task in proposal.tasks
    )
    critical = proposal.critical_review
    risk_summary = " | ".join(proposal.disclosed_risks) or "none"
    assumption_summary = " | ".join(proposal.assumptions) or "none"
    repository = proposal.repository_impact
    final_verification = proposal.final_verification
    review = (
        "No task file requires separate review beyond this plan."
        if critical is None
        else f"- Before {critical[0]} cycle 1: decide {critical[2]} because it "
        "exercises a synthetic package. Review "
        f"[Critical Human Review]({critical[3]})."
    )
    replacements = {
        'spec_revision: "sha256:<digest>"': f'spec_revision: "sha256:{digest}"',
        'baseline_commit: "<git-commit>"': 'baseline_commit: "0123456789abcdef"',
        "task_count: <count>": f"task_count: {len(proposal.tasks)}",
        "# Implementation Plan: <topic>": "# Implementation Plan: Fixture planning",
        "`<plan-revision>`": "`1`",
        "`<outcome>`": "`validate deterministic planning contracts`",
        "`<task-count>`": f"`{len(proposal.tasks)}`",
        "<exact authorization>": "Create deterministic local fixture state and stop for approval.",
        "<included and excluded work>": "Local temporary files only; no live agents or external calls.",
        "<summary or none>": risk_summary,
        "<task and decision, or none>": (
            f"{critical[0]}; {critical[2]}" if critical else "none"
        ),
        "<material assumptions or none>": assumption_summary,
        "[`<spec-path>`](<spec-link>)": "[`spec.md`](../spec.md)",
        "`sha256:<digest>`": f"`sha256:{digest}`",
        "<exact spec headings>": "Acceptance Criteria, Orchestration Lifecycle",
        "`<git-commit>`": "`0123456789abcdef`",
        "<paths and ownership, or none>": repository[
            "Pre-existing working-tree considerations"
        ],
        "<goal>": "Validate canonical planning state and the approval boundary.",
        "<non-goal>": "Live planner or implementer dispatch.",
        "<deferred work or none>": "none",
        "| 1 | [`task-001`](tasks/task-001-<slug>.md) | <objective> | None | <check> | <risk> | Not required |\n| N | [`task-final-verification`](tasks/task-final-verification.md) | Verify the complete approved spec | All implementation tasks | <repository final gate> | <risk> | Not required |": execution_rows,
        "| <criterion> | <task ID> | <task ID/check> |": coverage_rows,
        "<expected files, packages, or services>": repository[
            "Components and contracts"
        ],
        "<interfaces, schemas, or behavior>": repository[
            "Components and contracts"
        ],
        "<required migration and rollback, or none>": repository[
            "Migrations and dependencies"
        ],
        "<added or changed dependencies, or none>": repository[
            "Migrations and dependencies"
        ],
        "<access or side effects, or none>": repository["External systems"],
        "<task-local checks>": final_verification["Complete-spec coverage"],
        "<cross-component checks>": final_verification["Integration checks"],
        "<exact command or inspection>": final_verification[
            "Repository final gate"
        ],
        "<risk or none>": risk_summary,
        "<guardrail>": f"Honor disclosed mitigations and approvals: {risk_summary}",
        review if review == "No task file requires separate review beyond this plan." else "No task file requires separate review beyond this plan.": review,
        "`<task-count>`": f"`{len(proposal.tasks)}`",
        "| `task-001` | pending | 0 / 3 | pending | none |\n| `task-final-verification` | pending | 0 / 3 | pending | none |": progress_rows,
    }
    for source, replacement in replacements.items():
        text = text.replace(source, replacement)
    return strip_template_comments(text)


class PlanningScenario:
    def __init__(self, package: Path):
        self.package = package
        self.human_review_requested = False
        self.implementer_dispatches: list[str] = []
        self.blocker_evidence: str | None = None

    def initialize(self, report: str) -> list[str]:
        proposal, parse_errors = parse_planner_report(report)
        if parse_errors:
            return parse_errors
        assert proposal is not None
        if proposal.status == "blocked":
            self.blocker_evidence = proposal.blocker
            return [f"planner blocked: {proposal.blocker}"]
        errors = semantic_errors(proposal)
        if errors:
            return errors
        self.package.mkdir()
        spec = self.package / "spec.md"
        spec.write_text("# Fixture spec\n\n## Acceptance Criteria\n\nAC-03 through AC-06.\n")
        digest = hashlib.sha256(spec.read_bytes()).hexdigest()
        tasks_dir = self.package / "implementation" / "tasks"
        tasks_dir.mkdir(parents=True)
        (self.package / "implementation" / "plan.md").write_text(
            render_plan(proposal, digest), encoding="utf-8"
        )
        for task in proposal.tasks:
            filename = task_filename(task)
            (tasks_dir / filename).write_text(
                render_task(task, proposal.critical_review), encoding="utf-8"
            )
        self.human_review_requested = True
        return []


class PlanningContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.scenario = PlanningScenario(Path(self.temp.name) / "fixture")

    def assert_safe_rejection(self, name: str, report: str) -> list[str]:
        scenario = PlanningScenario(Path(self.temp.name) / name)
        errors = scenario.initialize(report)
        self.assertTrue(errors)
        self.assertFalse(scenario.package.exists())
        self.assertFalse(scenario.human_review_requested)
        self.assertEqual([], scenario.implementer_dispatches)
        return errors

    def test_conforming_report_renders_canonical_plan_ready_state(self):
        proposal = conforming_proposal()

        self.assertEqual([], self.scenario.initialize(proposal.report))
        errors = validate_state.validate(self.scenario.package, "plan-ready")
        self.assertEqual([], errors, "\n".join(error.render() for error in errors))

        implementation = self.scenario.package / "implementation"
        plan = (implementation / "plan.md").read_text(encoding="utf-8")
        tasks = sorted((implementation / "tasks").glob("*.md"))
        self.assertEqual(3, len(tasks))
        self.assertEqual(
            1,
            sum("kind: final-verification" in path.read_text() for path in tasks),
        )
        canonical_headings = re.findall(r"^## .+$", PLAN_TEMPLATE, re.MULTILINE)
        self.assertEqual(canonical_headings, re.findall(r"^## .+$", plan, re.MULTILINE))
        self.assertNotRegex(plan, r"<[^>]+>")
        for path in tasks:
            body = path.read_text(encoding="utf-8")
            self.assertEqual(
                re.findall(r"^## .+$", TASK_TEMPLATE, re.MULTILINE),
                re.findall(r"^## .+$", body, re.MULTILINE),
            )
            self.assertNotRegex(body, r"<[^>]+>")

        result = subprocess.run(
            [
                sys.executable,
                str(VALIDATOR_SCRIPT),
                str(self.scenario.package),
                "--phase",
                "plan-ready",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("state validation passed: plan-ready", result.stdout)

    def test_plan_alone_contains_approval_facts_and_exact_critical_review_link(self):
        proposal = conforming_proposal()
        self.assertEqual([], self.scenario.initialize(proposal.report))
        plan = (self.scenario.package / "implementation" / "plan.md").read_text()

        for fact in (
            "fixed\n`3`-task plan",
            "Material boundaries",
            "Material risks",
            "Gated tasks",
            "Assumptions",
            "task-001",
            "task-002",
            "task-final-verification",
            "AC-03",
            "AC-04",
            "AC-05",
            "AC-06",
            "External systems: none",
            "no live agents or external calls",
        ):
            self.assertIn(fact, plan)
        self.assertIn("Before task-002 cycle 1", plan)
        link = "tasks/task-002-record-critical-review.md#critical-human-review"
        self.assertIn(link, plan)
        target = self.scenario.package / "implementation" / link.split("#", 1)[0]
        task = target.read_text()
        self.assertIn("## Critical Human Review", task)
        self.assertIn(f"Review timing: {proposal.critical_review[1]}", task)
        self.assertIn(f"Decision required: {proposal.critical_review[2]}", task)
        self.assertIn(f"link={proposal.critical_review[3]}", proposal.report)

    def test_report_schema_status_and_blocker_contract(self):
        report = conforming_proposal().report
        self.assertEqual([], report_structure_errors(report))

        malformed = {
            "missing-field": report.replace("Assumptions:\n", "", 1),
            "duplicate-field": report + "\nBlocker: none\n",
            "field-order": report.replace(
                "Task list:\n", "", 1
            ).replace("Blocker: none", "Task list:\n- misplaced\n\nBlocker: none"),
            "invalid-status": report.replace("Status: ready", "Status: waiting", 1),
            "ready-with-blocker": report.replace(
                "Blocker: none", "Blocker: repository decision required", 1
            ),
            "blocked-without-blocker": report.replace(
                "Status: ready", "Status: blocked", 1
            ),
        }
        for name, candidate in malformed.items():
            with self.subTest(name=name):
                self.assertTrue(report_structure_errors(candidate))

        blocked = report.replace("Status: ready", "Status: blocked", 1).replace(
            "Blocker: none", "Blocker: repository decision required", 1
        )
        self.assertEqual([], report_structure_errors(blocked))

    def test_empty_missing_duplicate_invalid_and_inconsistent_scalars_reject_safely(self):
        report = conforming_proposal().report
        cases = {
            "empty-status": report.replace("Status: ready", "Status: ", 1),
            "whitespace-status": report.replace("Status: ready", "Status:    ", 1),
            "empty-blocker": report.replace("Blocker: none", "Blocker: ", 1),
            "whitespace-blocker": report.replace("Blocker: none", "Blocker:    ", 1),
            "missing-status": report.replace("Status: ready\n\n", "", 1),
            "missing-blocker": report.replace("\nBlocker: none", "", 1),
            "duplicate-status": "Status: ready\n" + report,
            "duplicate-blocker": report + "Blocker: none\n",
            "invalid-status": report.replace("Status: ready", "Status: waiting", 1),
            "ready-with-blocker": report.replace(
                "Blocker: none", "Blocker: ownership decision required", 1
            ),
            "blocked-without-blocker": report.replace(
                "Status: ready", "Status: blocked", 1
            ),
        }
        for name, candidate in cases.items():
            with self.subTest(name=name):
                errors = self.assert_safe_rejection(f"scalar-{name}", candidate)
                self.assertTrue(
                    any("malformed planner report" in error for error in errors),
                    errors,
                )

    def test_blank_task_and_coverage_sections_reject_without_side_effects(self):
        report = conforming_proposal().report
        sections = (
            ("Task list", "Acceptance coverage"),
            ("Acceptance coverage", "Repository impact"),
        )
        for heading, next_heading in sections:
            with self.subTest(heading=heading):
                body = report_section(report, heading, next_heading)
                candidate = report.replace(f"{heading}:\n{body}", f"{heading}:\n", 1)
                errors = self.assert_safe_rejection(f"blank-{heading}", candidate)
                self.assertIn(
                    f"malformed planner report: blank {heading}", errors
                )

    def test_explicit_none_sections_are_blocked_only(self):
        report = conforming_proposal().report
        for heading, next_heading in (
            ("Task list", "Acceptance coverage"),
            ("Acceptance coverage", "Repository impact"),
        ):
            body = report_section(report, heading, next_heading)
            report = report.replace(f"{heading}:\n{body}", f"{heading}:\n- none", 1)

        ready_errors = self.assert_safe_rejection("ready-none", report)
        self.assertTrue(
            any("uses none for non-blocked status" in error for error in ready_errors),
            ready_errors,
        )

        blocked = report.replace("Status: ready", "Status: blocked", 1).replace(
            "Blocker: none", "Blocker: spec lacks the ownership decision", 1
        )
        scenario = PlanningScenario(Path(self.temp.name) / "blocked-none")
        self.assertEqual(
            ["planner blocked: spec lacks the ownership decision"],
            scenario.initialize(blocked),
        )
        self.assertEqual("spec lacks the ownership decision", scenario.blocker_evidence)
        self.assertFalse(scenario.package.exists())
        self.assertFalse(scenario.human_review_requested)
        self.assertEqual([], scenario.implementer_dispatches)

    def test_explicit_none_section_whitespace_near_matches_reject_safely(self):
        report = conforming_proposal().report
        for heading, next_heading in (
            ("Task list", "Acceptance coverage"),
            ("Acceptance coverage", "Repository impact"),
        ):
            body = report_section(report, heading, next_heading)
            report = report.replace(f"{heading}:\n{body}", f"{heading}:\n- none", 1)
        report = report.replace("Status: ready", "Status: blocked", 1).replace(
            "Blocker: none", "Blocker: spec lacks the ownership decision", 1
        )

        for heading, altered in (
            ("Task list", " - none"),
            ("Task list", "- none "),
            ("Acceptance coverage", " - none"),
            ("Acceptance coverage", "- none "),
        ):
            with self.subTest(heading=heading, altered=repr(altered)):
                candidate = report.replace(f"{heading}:\n- none", f"{heading}:\n{altered}", 1)
                errors = self.assert_safe_rejection(
                    f"none-near-match-{heading}-{len(altered)}-{altered[0] == ' '}",
                    candidate,
                )
                self.assertIn(
                    f"malformed planner report: {heading} none bullet must be exact",
                    errors,
                )

    def test_fixed_seed_malformed_scalar_fuzz_never_raises_or_mutates_state(self):
        report = conforming_proposal().report
        generator = random.Random(1701)
        alphabet = "abcdefghijklmnopqrstuvwxyz0123456789 !@#$%^&*()[]{}"
        corpus = []
        for index in range(96):
            payload = "".join(
                generator.choice(alphabet) for _ in range(generator.randrange(0, 33))
            )
            if payload in {"ready", "blocked"}:
                payload += "!"
            target = "Status" if index % 2 == 0 else "Blocker"
            if target == "Status":
                candidate = report.replace("Status: ready", f"Status: {payload}", 1)
            else:
                candidate = report.replace("Blocker: none", f"Blocker: {payload}", 1)
            corpus.append(candidate)

        for index, candidate in enumerate(corpus):
            with self.subTest(index=index):
                self.assert_safe_rejection(f"fuzz-{index}", candidate)

    def test_task_kind_id_and_canonical_file_constraints(self):
        report = conforming_proposal().report
        cases = {
            "unsupported-kind": (
                report.replace(
                    "- task-001, implementation,",
                    "- task-001, research,",
                    1,
                ),
                "unsupported task kind: research",
            ),
            "malformed-id": (
                report.replace("- task-001, implementation,", "- task-alpha, implementation,", 1),
                "noncanonical implementation task ID: task-alpha",
            ),
            "malformed-file": (
                report.replace(
                    "Render canonical state, Render the approved fixture package",
                    "../Escape, Render the approved fixture package",
                    1,
                ),
                "noncanonical task file",
            ),
            "malformed-final-id": (
                report.replace(
                    "- task-final-verification, final-verification,",
                    "- task-999, final-verification,",
                    1,
                ),
                "noncanonical final task ID: task-999",
            ),
        }
        for name, (candidate, expected) in cases.items():
            with self.subTest(name=name):
                scenario = PlanningScenario(Path(self.temp.name) / f"canonical-{name}")
                errors = scenario.initialize(candidate)
                self.assertTrue(any(expected in error for error in errors), errors)
                self.assertFalse(scenario.package.exists())

    def test_parser_rejects_unconsumed_document_text(self):
        report = conforming_proposal().report
        cases = {
            "preamble": "unmatched preamble\n" + report,
            "postamble": report + "unmatched postamble\n",
            "status-task": report.replace(
                "Status: ready\n\nTask list:",
                "Status: ready\nunmatched status text\n\nTask list:",
                1,
            ),
            "inter-section": report.replace(
                "\n\nRisks and guardrails:",
                "\nunmatched repository text\n\nRisks and guardrails:",
                1,
            ),
        }
        for name, candidate in cases.items():
            with self.subTest(name=name):
                scenario = PlanningScenario(Path(self.temp.name) / f"document-{name}")
                errors = scenario.initialize(candidate)
                self.assertTrue(
                    any("malformed planner report" in error for error in errors),
                    errors,
                )
                self.assertFalse(scenario.package.exists())

    def test_report_is_authoritative_and_task_subfields_are_exhaustive(self):
        proposal = conforming_proposal()
        authoritative_report = proposal.report
        proposal.tasks.clear()
        proposal.coverage.clear()

        scenario = PlanningScenario(Path(self.temp.name) / "report-authority")
        self.assertEqual([], scenario.initialize(authoritative_report))
        rendered_tasks = list(
            (scenario.package / "implementation" / "tasks").glob("*.md")
        )
        self.assertEqual(3, len(rendered_tasks))

        task_section = report_section(
            authoritative_report, "Task list", "Acceptance coverage"
        )
        first_block = next(TASK_BLOCK_RE.finditer(task_section)).group(0)
        required_lines = first_block.splitlines()
        self.assertEqual(7, len(required_lines))
        for index, line in enumerate(required_lines):
            with self.subTest(omitted_task_subfield=index):
                malformed = authoritative_report.replace(line + "\n", "", 1)
                rejected = PlanningScenario(
                    Path(self.temp.name) / f"missing-subfield-{index}"
                )
                errors = rejected.initialize(malformed)
                self.assertTrue(
                    any("incomplete task subfields" in error for error in errors),
                    errors,
                )
                self.assertFalse(rejected.package.exists())

    def test_report_task_dependency_and_coverage_contradictions_are_rejected(self):
        report = conforming_proposal().report
        task_section = report_section(report, "Task list", "Acceptance coverage")
        first_block = next(TASK_BLOCK_RE.finditer(task_section)).group(0)
        cases = {
            "omitted-task": report.replace(first_block + "\n", "", 1),
            "dependency-contradiction": report.replace(
                "  Dependencies: task-001\n",
                "  Dependencies: task-999\n",
                1,
            ),
            "coverage-contradiction": report.replace(
                "- AC-06: task-002; task-final-verification",
                "- AC-06: task-999; task-final-verification",
                1,
            ),
            "coverage-owner-mismatch": report.replace(
                "- AC-06: task-002; task-final-verification",
                "- AC-06: task-001; task-final-verification",
                1,
            ),
            "omitted-repository-field": report.replace(
                "- External systems: none\n", "", 1
            ),
            "omitted-final-field": report.replace(
                "- Integration checks: canonical plan, task, and critical-review linkage\n",
                "",
                1,
            ),
        }
        expected = {
            "omitted-task": "missing dependency: task-001",
            "dependency-contradiction": "missing dependency: task-999",
            "coverage-contradiction": "unmapped criterion: AC-06",
            "coverage-owner-mismatch": "coverage contradiction: AC-06",
            "omitted-repository-field": "Repository impact missing",
            "omitted-final-field": "Final verification missing",
        }
        for name, candidate in cases.items():
            with self.subTest(name=name):
                scenario = PlanningScenario(Path(self.temp.name) / name)
                errors = scenario.initialize(candidate)
                self.assertTrue(any(expected[name] in error for error in errors), errors)
                self.assertFalse(scenario.package.exists())
                self.assertFalse(scenario.human_review_requested)
                self.assertEqual([], scenario.implementer_dispatches)

    def test_blocked_planner_report_stops_without_state_or_dispatch(self):
        proposal = conforming_proposal()
        proposal.status = "blocked"
        proposal.blocker = "spec lacks the ownership decision"
        proposal.report = planner_report(proposal)
        scenario = PlanningScenario(Path(self.temp.name) / "blocked")

        self.assertEqual(
            ["planner blocked: spec lacks the ownership decision"],
            scenario.initialize(proposal.report),
        )
        self.assertEqual("spec lacks the ownership decision", scenario.blocker_evidence)
        self.assertFalse(scenario.package.exists())
        self.assertFalse(scenario.human_review_requested)
        self.assertEqual([], scenario.implementer_dispatches)

    def test_repository_risks_assumptions_and_final_details_round_trip(self):
        proposal = conforming_proposal()
        proposal.repository_impact["External systems"] = "fixture audit API"
        proposal.disclosed_risks += (
            "Impact reference: fixture audit API; Risk: external fixture audit API access; Mitigation: fake local adapter; Required approval: current user",
        )
        proposal.assumptions = (
            "Assumption: Python 3 standard library is available; Supporting source: repository test contract",
            "Assumption: fixture audit API is synthetic and local; Supporting source: fixture definition",
        )
        proposal.final_verification = {
            "Complete-spec coverage": "verify every synthetic acceptance mapping",
            "Integration checks": "round-trip report values into canonical state",
            "Repository final gate": "python -m unittest fixture_round_trip",
        }
        proposal.report = planner_report(proposal)
        parsed, errors = parse_planner_report(proposal.report)
        self.assertEqual([], errors)
        self.assertEqual(proposal.repository_impact, parsed.repository_impact)
        self.assertEqual(proposal.disclosed_risks, parsed.disclosed_risks)
        self.assertEqual(proposal.assumptions, parsed.assumptions)
        self.assertEqual(proposal.final_verification, parsed.final_verification)

        scenario = PlanningScenario(Path(self.temp.name) / "round-trip")
        self.assertEqual([], scenario.initialize(proposal.report))
        plan = (scenario.package / "implementation" / "plan.md").read_text()
        for accepted_value in (
            *proposal.disclosed_risks,
            *proposal.assumptions,
            "fixture audit API",
            *proposal.final_verification.values(),
        ):
            self.assertIn(accepted_value, plan)
        no_assumptions = conforming_proposal()
        no_assumptions.assumptions = ()
        no_assumptions.report = planner_report(no_assumptions)
        empty_scenario = PlanningScenario(Path(self.temp.name) / "no-assumptions")
        self.assertEqual([], empty_scenario.initialize(no_assumptions.report))
        empty_plan = (
            empty_scenario.package / "implementation" / "plan.md"
        ).read_text()
        self.assertIn("- Assumptions: none", empty_plan)

        no_risks = conforming_proposal()
        no_risks.disclosed_risks = ()
        no_risks.assumptions = ()
        rendered = render_plan(no_risks, "0" * 64)
        self.assertIn("- Material risks: none", rendered)
        self.assertIn("- Assumptions: none", rendered)

    def test_material_repository_impact_requires_risk_and_approval(self):
        cases = {}
        external = conforming_proposal()
        external.repository_impact["External systems"] = "fixture audit API"
        external.report = planner_report(external)
        cases["external"] = (
            external.report,
            "external systems lack disclosed risk and required approval",
        )

        migration = conforming_proposal()
        migration.repository_impact[
            "Migrations and dependencies"
        ] = "fixture schema migration"
        migration.report = planner_report(migration)
        cases["migration"] = (
            migration.report,
            "material impact lacks matching risk and required approval",
        )

        unrelated = conforming_proposal()
        unrelated.repository_impact[
            "Migrations and dependencies"
        ] = "fixture schema migration"
        unrelated.disclosed_risks += (
            "Impact reference: package lock dependency upgrade; Risk: fixture schema migration shares coincidental words; Mitigation: restore lockfile; Required approval: current user",
        )
        unrelated.report = planner_report(unrelated)
        cases["unrelated-migration"] = (
            unrelated.report,
            "material impact lacks matching risk and required approval",
        )

        missing_reference = conforming_proposal()
        missing_reference.repository_impact[
            "Migrations and dependencies"
        ] = "fixture schema migration"
        missing_reference.disclosed_risks += (
            "Risk: fixture schema migration data loss; Mitigation: restore fixture; Required approval: current user",
        )
        missing_reference.report = planner_report(missing_reference)
        cases["missing-impact-reference"] = (
            missing_reference.report,
            "malformed risk disclosure",
        )

        no_approval = conforming_proposal()
        no_approval.repository_impact["External systems"] = "fixture audit API"
        no_approval.disclosed_risks += (
            "Impact reference: fixture audit API; Risk: external fixture audit API access; Mitigation: fake local adapter; Required approval: none",
        )
        no_approval.report = planner_report(no_approval)
        cases["approval"] = (
            no_approval.report,
            "external systems lack disclosed risk and required approval",
        )

        for name, (report, expected) in cases.items():
            with self.subTest(name=name):
                scenario = PlanningScenario(Path(self.temp.name) / f"impact-{name}")
                errors = scenario.initialize(report)
                self.assertIn(expected, errors)
                self.assertFalse(scenario.package.exists())
                self.assertFalse(scenario.human_review_requested)

        matched = conforming_proposal()
        matched.repository_impact[
            "Migrations and dependencies"
        ] = "fixture schema migration"
        matched.disclosed_risks += (
            "Impact reference: FIXTURE   SCHEMA MIGRATION; Risk: fixture schema migration data loss; Mitigation: disposable fixture rollback; Required approval: current user",
        )
        matched.report = planner_report(matched)
        accepted = PlanningScenario(Path(self.temp.name) / "impact-matched")
        self.assertEqual([], accepted.initialize(matched.report))
        plan = (accepted.package / "implementation" / "plan.md").read_text()
        self.assertIn("fixture schema migration", plan)
        self.assertIn(matched.disclosed_risks[-1], plan)

    def test_unstructured_lines_in_required_report_sections_are_rejected(self):
        report = conforming_proposal().report
        cases = {
            "task-list": report.replace(
                "Task list:\n", "Task list:\nunstructured task content\n", 1
            ),
            "acceptance-coverage": report.replace(
                "Acceptance coverage:\n",
                "Acceptance coverage:\nunstructured coverage content\n",
                1,
            ),
            "repository-impact": report.replace(
                "Repository impact:\n",
                "Repository impact:\nunstructured repository content\n",
                1,
            ),
            "risks": report.replace(
                "Risks and guardrails:\n",
                "Risks and guardrails:\nunstructured risk content\n",
                1,
            ),
            "malformed-risk-bullet": report.replace(
                "Risks and guardrails:\n",
                "Risks and guardrails:\n- risk without required fields\n",
                1,
            ),
            "assumptions": report.replace(
                "Assumptions:\n",
                "Assumptions:\nunstructured assumption content\n",
                1,
            ),
            "malformed-assumption-bullet": report.replace(
                "Assumptions:\n",
                "Assumptions:\n- assumption without supporting source\n",
                1,
            ),
            "unresolved-decisions": report.replace(
                "Unresolved decisions:\n",
                "Unresolved decisions:\nunstructured decision content\n",
                1,
            ),
            "malformed-decision-bullet": report.replace(
                "Unresolved decisions:\n",
                "Unresolved decisions:\n- decision without impact or human input\n",
                1,
            ),
            "final-verification": report.replace(
                "Final verification:\n",
                "Final verification:\nunstructured final content\n",
                1,
            ),
        }
        for name, candidate in cases.items():
            with self.subTest(name=name):
                scenario = PlanningScenario(Path(self.temp.name) / f"line-{name}")
                errors = scenario.initialize(candidate)
                self.assertTrue(
                    any(
                        "malformed" in error
                        or "invalid acceptance coverage" in error
                        for error in errors
                    ),
                    errors,
                )
                self.assertFalse(scenario.package.exists())
                self.assertFalse(scenario.human_review_requested)

    def test_nonconforming_reports_are_rejected_before_human_review(self):
        cases = {}
        oversized = conforming_proposal()
        oversized.tasks[0].bounded = False
        oversized.report = planner_report(oversized)
        self.assertIn("bounded for one direct implementer=no", oversized.report)
        cases["oversized"] = (oversized, "oversized task")

        unmapped = conforming_proposal()
        del unmapped.coverage["AC-06"]
        unmapped.report = planner_report(unmapped)
        cases["unmapped"] = (unmapped, "unmapped criterion: AC-06")

        circular = conforming_proposal()
        circular.tasks[0].dependencies = ("task-002",)
        circular.report = planner_report(circular)
        cases["circular"] = (circular, "circular dependency")

        misordered = conforming_proposal()
        misordered.tasks[0], misordered.tasks[1] = (
            misordered.tasks[1],
            misordered.tasks[0],
        )
        misordered.report = planner_report(misordered)
        cases["dependency-order"] = (misordered, "dependency order")

        missing = conforming_proposal()
        missing.tasks[1].dependencies = ("task-999",)
        missing.report = planner_report(missing)
        cases["missing"] = (missing, "missing dependency: task-999")

        hidden_risk = conforming_proposal()
        hidden_risk.disclosed_risks = ()
        hidden_risk.report = planner_report(hidden_risk)
        cases["hidden-risk"] = (hidden_risk, "hidden risk")

        unresolved = conforming_proposal()
        unresolved.unresolved_decisions = (
            "Decision: choose an execution environment; Impact: fixture behavior is undefined; Required human input: select the environment",
        )
        unresolved.report = planner_report(unresolved)
        cases["unresolved"] = (unresolved, "unresolved decision")

        delegated = conforming_proposal()
        delegated.tasks[0].delegates = True
        delegated.report = planner_report(delegated)
        self.assertIn("direct execution only=no", delegated.report)
        cases["delegated"] = (delegated, "delegated task")

        for name, (proposal, expected) in cases.items():
            with self.subTest(name=name):
                package = Path(self.temp.name) / name
                scenario = PlanningScenario(package)
                errors = scenario.initialize(deepcopy(proposal).report)
                self.assertTrue(any(expected in error for error in errors), errors)
                self.assertFalse(package.exists())
                self.assertFalse(scenario.human_review_requested)
                self.assertEqual([], scenario.implementer_dispatches)

    def test_invalid_critical_review_source_is_rejected_before_rendering(self):
        cases = {}
        missing = conforming_proposal()
        missing.critical_review = None
        missing.report = planner_report(missing)
        cases["missing"] = (missing, "missing critical review")

        timing = conforming_proposal()
        timing.critical_review = (
            timing.critical_review[0],
            "during implementation",
            timing.critical_review[2],
            timing.critical_review[3],
        )
        timing.report = planner_report(timing)
        cases["timing"] = (timing, "critical review timing mismatch")

        decision = conforming_proposal()
        decision.critical_review = (
            decision.critical_review[0],
            decision.critical_review[1],
            "",
            decision.critical_review[3],
        )
        decision.report = planner_report(decision)
        cases["decision"] = (decision, "critical review decision missing")

        task = conforming_proposal()
        task.critical_review = (
            "task-001",
            task.critical_review[1],
            task.critical_review[2],
            "tasks/task-001-render-canonical-state.md#critical-human-review",
        )
        task.report = planner_report(task)
        cases["task"] = (task, "critical review task mismatch")

        link = conforming_proposal()
        link.critical_review = (
            link.critical_review[0],
            link.critical_review[1],
            link.critical_review[2],
            "tasks/task-002-record-critical-review.md#risks",
        )
        link.report = planner_report(link)
        cases["exact-link"] = (link, "critical review exact link mismatch")

        for name, (proposal, expected) in cases.items():
            with self.subTest(name=name):
                scenario = PlanningScenario(Path(self.temp.name) / f"review-{name}")
                errors = scenario.initialize(proposal.report)
                self.assertIn(expected, errors)
                self.assertFalse(scenario.package.exists())
                self.assertFalse(scenario.human_review_requested)

    def test_awaiting_approval_is_a_mandatory_dispatch_stop(self):
        self.assertEqual([], self.scenario.initialize(conforming_proposal().report))
        plan_path = self.scenario.package / "implementation" / "plan.md"
        plan_data = validate_state.parse_frontmatter(plan_path)

        self.assertEqual("awaiting-approval", plan_data["status"])
        self.assertIsNone(plan_data["approved_revision"])
        self.assertIsNone(plan_data["current_task"])
        self.assertTrue(self.scenario.human_review_requested)
        self.assertEqual([], self.scenario.implementer_dispatches)
        dispatch_errors = validate_state.validate(
            self.scenario.package, "dispatch", "task-001"
        )
        messages = "\n".join(error.render() for error in dispatch_errors)
        self.assertIn("dispatch requires in-progress plan status", messages)
        self.assertIn("must equal plan_revision", messages)
        self.assertIn("dispatch target must be implementing", messages)


if __name__ == "__main__":
    unittest.main()
