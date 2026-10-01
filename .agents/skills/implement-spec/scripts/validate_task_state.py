#!/usr/bin/env python3
"""Validate persisted implement-spec task state."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


VALID_STATUSES = {"pending", "in-progress", "blocked", "complete"}
READY_SECTIONS = {
    "Outcome",
    "Scope",
    "Service boundaries and contracts",
    "Relevant context and standards",
    "Implementation guidance",
    "Acceptance checks",
    "Verification",
    "Risks and adversarial scenarios",
    "Notes",
}


@dataclass
class Task:
    number: str
    path: Path
    text: str
    status: str | None
    dependencies: list[str]


def field(text: str, name: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(name)}:\s*(.+?)\s*$", text)
    return match.group(1) if match else None


def section(text: str, name: str) -> str | None:
    match = re.search(
        rf"(?ms)^## {re.escape(name)}\s*$\n(.*?)(?=^## |\Z)", text
    )
    return match.group(1) if match else None


def load_tasks(spec_dir: Path) -> tuple[dict[str, Task], list[str]]:
    errors: list[str] = []
    tasks: dict[str, Task] = {}
    for required_file in ("spec.md", "context.md"):
        if not (spec_dir / required_file).is_file():
            errors.append(f"missing normalized file: {spec_dir / required_file}")
    task_dir = spec_dir / "tasks"
    if not task_dir.is_dir():
        errors.append(f"missing task directory: {task_dir}")
        return {}, errors

    for path in sorted(task_dir.glob("*.md")):
        match = re.match(r"^(\d{2})-[a-z0-9-]+\.md$", path.name)
        if not match:
            errors.append(f"{path.name}: expected NN-kebab-case.md filename")
            continue
        number = match.group(1)
        text = path.read_text(encoding="utf-8")
        status = field(text, "Status")
        raw_dependencies = field(text, "Depends on")
        dependencies: list[str] = []
        if raw_dependencies and raw_dependencies != "none":
            dependencies = [item.strip() for item in raw_dependencies.split(",")]
        if number in tasks:
            errors.append(f"duplicate task number: {number}")
        tasks[number] = Task(number, path, text, status, dependencies)

    if not tasks:
        errors.append(f"no task files found in {task_dir}")
    return tasks, errors


def validate_basic(tasks: dict[str, Task], errors: list[str]) -> None:
    for task in tasks.values():
        label = task.path.name
        if task.status not in VALID_STATUSES:
            errors.append(
                f"{label}: invalid or missing status {task.status!r}; "
                f"expected one of {sorted(VALID_STATUSES)}"
            )
        if field(task.text, "Depends on") is None:
            errors.append(f"{label}: missing Depends on field")
        for dependency in task.dependencies:
            if not re.fullmatch(r"\d{2}", dependency):
                errors.append(f"{label}: invalid dependency {dependency!r}")
                continue
            if dependency not in tasks:
                errors.append(f"{label}: dependency {dependency} does not exist")
            elif (
                task.status in {"in-progress", "complete"}
                and tasks[dependency].status != "complete"
            ):
                errors.append(
                    f"{label}: dependency {dependency} must be complete before "
                    f"status {task.status}"
                )

        if task.status == "complete":
            checks = section(task.text, "Acceptance checks")
            if checks is None:
                errors.append(f"{label}: complete task lacks Acceptance checks")
            else:
                boxes = re.findall(r"(?m)^\s*- \[([ xX])\] ", checks)
                if not boxes:
                    errors.append(f"{label}: complete task has no acceptance checkboxes")
                elif any(box == " " for box in boxes):
                    errors.append(f"{label}: complete task has unchecked acceptance checks")
            notes = section(task.text, "Notes") or ""
            if not re.search(r"(?im)^Review verdict:\s*pass\s*$", notes):
                errors.append(f"{label}: complete task lacks 'Review verdict: pass'")


def validate_ready(tasks: dict[str, Task], numbers: list[str], errors: list[str]) -> None:
    for number in numbers:
        task = tasks.get(number)
        if task is None:
            errors.append(f"ready task {number} does not exist")
            continue
        label = task.path.name
        if task.status not in {"pending", "in-progress"}:
            errors.append(f"{label}: ready task must be pending or in-progress")
        for metadata in ("Primary workspace", "Planning baseline", "Scope basis"):
            if field(task.text, metadata) is None:
                errors.append(f"{label}: ready task lacks {metadata} field")
        headings = set(re.findall(r"(?m)^## (.+?)\s*$", task.text))
        for missing in sorted(READY_SECTIONS - headings):
            errors.append(f"{label}: ready task lacks ## {missing}")
        checks = section(task.text, "Acceptance checks") or ""
        if not re.search(r"(?m)^\s*- \[[ xX]\] ", checks):
            errors.append(f"{label}: ready task has no acceptance checkboxes")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec_directory", type=Path)
    parser.add_argument(
        "--ready",
        action="append",
        default=[],
        metavar="NN",
        help="also validate a task as dispatch-ready; may be repeated",
    )
    parser.add_argument(
        "--final",
        action="store_true",
        help="require every task to be complete",
    )
    args = parser.parse_args()

    tasks, errors = load_tasks(args.spec_directory.resolve())
    validate_basic(tasks, errors)
    validate_ready(tasks, args.ready, errors)
    if args.final:
        for task in tasks.values():
            if task.status != "complete":
                errors.append(
                    f"{task.path.name}: final validation requires complete, "
                    f"found {task.status!r}"
                )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(tasks)} task file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
