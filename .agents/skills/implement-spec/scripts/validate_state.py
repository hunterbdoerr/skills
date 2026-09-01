#!/usr/bin/env python3
"""Deterministically validate an implement-spec persisted state package.

This module deliberately implements only the flat frontmatter subset emitted by
the canonical implement-spec assets.  It is not, and must not become, a YAML
parser: unsupported YAML is rejected instead of being interpreted loosely.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


PLAN_FIELDS = {
    "schema_version": int,
    "status": str,
    "spec": str,
    "spec_revision": str,
    "baseline_commit": str,
    "plan_revision": int,
    "approved_revision": (int, type(None)),
    "task_count": int,
    "current_task": (str, type(None)),
    "max_cycles_per_task": int,
}
TASK_FIELDS = {
    "schema_version": int,
    "id": str,
    "kind": str,
    "status": str,
    "dependencies": list,
    "cycles_used": int,
    "cycle_limit": int,
    "human_gate": bool,
    "human_gate_status": str,
    "tester_verdict": str,
}
PLAN_STATUSES = {
    "draft",
    "awaiting-approval",
    "approved",
    "in-progress",
    "needs-human",
    "completed",
    "cancelled",
}
TASK_KINDS = {"implementation", "final-verification"}
TASK_STATUSES = {"pending", "implementing", "testing", "passed", "needs-human"}
GATE_STATUSES = {"not-required", "pending", "approved"}
TESTER_VERDICTS = {"none", "pass", "fail", "blocked"}
ACTIVE_STATUSES = {"implementing", "testing"}
KEY_RE = re.compile(r"[a-z][a-z0-9_]*\Z")
PLAIN_RE = re.compile(r"[-A-Za-z0-9_./]+\Z")
TASK_ID_RE = re.compile(r"task-(?:[0-9]{3,}|final-verification)\Z")
SHA256_RE = re.compile(r"sha256:[0-9a-f]{64}\Z")


@dataclass(frozen=True)
class Diagnostic:
    path: Path
    field: str
    message: str

    def render(self) -> str:
        return f"{self.path}: {self.field}: {self.message}"


class FrontmatterError(ValueError):
    pass


def _parse_scalar(source: str, line_number: int) -> Any:
    if source == "null":
        return None
    if source == "true":
        return True
    if source == "false":
        return False
    if re.fullmatch(r"0|[1-9][0-9]*", source):
        return int(source)
    if source.startswith('"'):
        try:
            value = json.loads(source)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise FrontmatterError(
                f"line {line_number}: invalid double-quoted string ({exc.msg})"
            ) from exc
        if not isinstance(value, str):
            raise FrontmatterError(
                f"line {line_number}: quoted frontmatter values must be strings"
            )
        return value
    if PLAIN_RE.fullmatch(source):
        return source
    raise FrontmatterError(
        f"line {line_number}: unsupported YAML value {source!r}; use a canonical "
        "plain scalar, JSON-style double-quoted string, boolean, null, integer, "
        "or inline list"
    )


def _parse_value(source: str, line_number: int) -> Any:
    if source.startswith("["):
        if not source.endswith("]"):
            raise FrontmatterError(f"line {line_number}: unterminated inline list")
        inner = source[1:-1]
        if not inner:
            return []
        values = []
        # Canonical dependency lists do not contain commas inside values.
        for item in inner.split(","):
            item = item.strip()
            if not item:
                raise FrontmatterError(f"line {line_number}: inline list has an empty item")
            value = _parse_scalar(item, line_number)
            if not isinstance(value, str):
                raise FrontmatterError(
                    f"line {line_number}: inline list items must be task ID strings"
                )
            values.append(value)
        return values
    if source.startswith("{") or source in {"|", ">"}:
        raise FrontmatterError(f"line {line_number}: mappings and block scalars are unsupported")
    return _parse_scalar(source, line_number)


def parse_frontmatter(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise FrontmatterError(f"cannot read UTF-8 file: {exc}") from exc
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise FrontmatterError("line 1: expected opening '---'")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise FrontmatterError("missing closing '---'") from exc
    result: dict[str, Any] = {}
    for index, line in enumerate(lines[1:end], start=2):
        if not line.strip():
            raise FrontmatterError(f"line {index}: blank frontmatter lines are unsupported")
        if "\t" in line or line.startswith((" ", "-", "#")):
            raise FrontmatterError(
                f"line {index}: only unindented flat key/value entries are supported"
            )
        if ": " not in line:
            raise FrontmatterError(f"line {index}: expected 'key: value'")
        key, source = line.split(": ", 1)
        if not KEY_RE.fullmatch(key):
            raise FrontmatterError(f"line {index}: unsupported key {key!r}")
        if key in result:
            raise FrontmatterError(f"line {index}: duplicate key {key!r}")
        if not source:
            raise FrontmatterError(f"line {index}: missing value for {key!r}")
        result[key] = _parse_value(source, index)
    return result


def _matches_type(value: Any, expected: Any) -> bool:
    choices = expected if isinstance(expected, tuple) else (expected,)
    # bool is a subclass of int; persisted schema types are intentionally exact.
    return any(type(value) is choice for choice in choices)


def _validate_schema(path: Path, data: dict[str, Any], fields: dict[str, Any]) -> list[Diagnostic]:
    errors = []
    for field in sorted(fields.keys() - data.keys()):
        errors.append(Diagnostic(path, field, "required field is missing"))
    for field in sorted(data.keys() - fields.keys()):
        errors.append(Diagnostic(path, field, "field is not supported by schema version 1"))
    for field in sorted(fields.keys() & data.keys()):
        if not _matches_type(data[field], fields[field]):
            expected = fields[field]
            names = expected if isinstance(expected, tuple) else (expected,)
            label = " or ".join(t.__name__ for t in names)
            errors.append(Diagnostic(path, field, f"expected {label}, got {type(data[field]).__name__}"))
    if data.get("schema_version") != 1:
        errors.append(Diagnostic(path, "schema_version", "recognized value is exactly 1"))
    return errors


class PackageValidator:
    def __init__(self, package: Path):
        self.package = package.resolve()
        self.plan_path = self.package / "implementation" / "plan.md"
        self.tasks_dir = self.package / "implementation" / "tasks"
        self.plan: dict[str, Any] = {}
        self.tasks: list[tuple[Path, dict[str, Any]]] = []
        self.errors: list[Diagnostic] = []

    def error(self, path: Path, field: str, message: str) -> None:
        self.errors.append(Diagnostic(path, field, message))

    def load(self) -> None:
        if not self.package.is_dir():
            self.error(self.package, "package", "spec package directory does not exist")
            return
        try:
            self.plan = parse_frontmatter(self.plan_path)
        except FrontmatterError as exc:
            self.error(self.plan_path, "frontmatter", str(exc))
        if not self.tasks_dir.is_dir():
            self.error(self.tasks_dir, "tasks", "task directory does not exist")
            return
        for path in sorted(self.tasks_dir.glob("*.md")):
            try:
                self.tasks.append((path, parse_frontmatter(path)))
            except FrontmatterError as exc:
                self.error(path, "frontmatter", str(exc))

    def validate_common(self) -> None:
        schema_errors = _validate_schema(self.plan_path, self.plan, PLAN_FIELDS)
        self.errors.extend(schema_errors)
        for path, task in self.tasks:
            task_schema_errors = _validate_schema(path, task, TASK_FIELDS)
            schema_errors.extend(task_schema_errors)
            self.errors.extend(task_schema_errors)
        # Missing or mistyped fields make indexed validation unsafe. Unknown
        # fields and an unknown schema version can still receive further useful
        # diagnostics without attempting to interpret them.
        if any(
            error.message.startswith(("required field", "expected "))
            for error in schema_errors
        ):
            return

        plan = self.plan
        if plan["status"] not in PLAN_STATUSES:
            self.error(self.plan_path, "status", f"unknown plan state {plan['status']!r}")
        if plan["plan_revision"] < 1:
            self.error(self.plan_path, "plan_revision", "must be at least 1")
        if plan["approved_revision"] is not None and plan["approved_revision"] < 1:
            self.error(self.plan_path, "approved_revision", "must be null or at least 1")
        if plan["task_count"] < 1:
            self.error(self.plan_path, "task_count", "must be at least 1")
        if plan["max_cycles_per_task"] < 1:
            self.error(self.plan_path, "max_cycles_per_task", "must be at least 1")

        spec_path = (self.plan_path.parent / plan["spec"]).resolve()
        canonical_spec = (self.package / "spec.md").resolve()
        if spec_path != canonical_spec:
            self.error(
                self.plan_path,
                "spec",
                f"must resolve to canonical package spec {canonical_spec} (got {spec_path})",
            )
        else:
            try:
                digest = "sha256:" + hashlib.sha256(spec_path.read_bytes()).hexdigest()
            except OSError as exc:
                self.error(spec_path, "spec", f"cannot read spec bytes: {exc}")
            else:
                if not SHA256_RE.fullmatch(plan["spec_revision"]):
                    self.error(self.plan_path, "spec_revision", "must be 'sha256:' plus 64 lowercase hex digits")
                if plan["spec_revision"] != digest:
                    self.error(
                        self.plan_path,
                        "spec_revision",
                        f"digest mismatch; expected {digest} for {spec_path}",
                    )

        if plan["task_count"] != len(self.tasks):
            self.error(
                self.plan_path,
                "task_count",
                f"declares {plan['task_count']} but found {len(self.tasks)} task Markdown files",
            )

        by_id: dict[str, tuple[Path, dict[str, Any]]] = {}
        for path, task in self.tasks:
            task_id = task["id"]
            if not TASK_ID_RE.fullmatch(task_id):
                self.error(path, "id", "must match task-NNN or task-final-verification")
            if task_id in by_id:
                self.error(path, "id", f"duplicate task ID {task_id!r}; first declared in {by_id[task_id][0]}")
            else:
                by_id[task_id] = (path, task)
            if task["kind"] not in TASK_KINDS:
                self.error(path, "kind", f"unknown task kind {task['kind']!r}")
            if task["status"] not in TASK_STATUSES:
                self.error(path, "status", f"unknown task state {task['status']!r}")
            if task["human_gate_status"] not in GATE_STATUSES:
                self.error(path, "human_gate_status", f"unknown gate state {task['human_gate_status']!r}")
            if task["tester_verdict"] not in TESTER_VERDICTS:
                self.error(path, "tester_verdict", f"unknown tester verdict {task['tester_verdict']!r}")
            if len(task["dependencies"]) != len(set(task["dependencies"])):
                self.error(path, "dependencies", "contains a duplicate dependency")
            for dependency in task["dependencies"]:
                if not TASK_ID_RE.fullmatch(dependency):
                    self.error(path, "dependencies", f"invalid task ID {dependency!r}")
            if task["cycles_used"] < 0:
                self.error(path, "cycles_used", "must not be negative")
            if task["cycle_limit"] < 1:
                self.error(path, "cycle_limit", "must be at least 1")
            if task["cycles_used"] > task["cycle_limit"]:
                self.error(
                    path,
                    "cycles_used",
                    f"{task['cycles_used']} exceeds cycle_limit {task['cycle_limit']}",
                )
            if task["status"] in ACTIVE_STATUSES | {"passed"} and task["cycles_used"] < 1:
                self.error(path, "cycles_used", f"must be at least 1 while status is {task['status']!r}")
            if task["status"] == "pending" and task["cycles_used"] != 0:
                self.error(path, "cycles_used", "pending task must have zero reserved cycles")
            if task["human_gate"] and task["human_gate_status"] == "not-required":
                self.error(path, "human_gate_status", "gated task must be pending or approved")
            if not task["human_gate"] and task["human_gate_status"] != "not-required":
                self.error(path, "human_gate_status", "ungated task must use not-required")
            if task["human_gate"] and task["human_gate_status"] == "pending" and task["status"] in ACTIVE_STATUSES | {"passed"}:
                self.error(path, "human_gate_status", "pending gate prohibits implementing, testing, or passed status")
            if task["status"] == "passed" and task["tester_verdict"] != "pass":
                self.error(path, "tester_verdict", "passed task requires tester verdict pass")
            if task["tester_verdict"] == "pass" and task["status"] != "passed":
                self.error(path, "status", "tester verdict pass requires task status passed")
            if task["tester_verdict"] == "blocked" and task["status"] != "needs-human":
                self.error(path, "status", "tester verdict blocked requires needs-human status")
            if task["status"] == "pending" and task["tester_verdict"] != "none":
                self.error(path, "tester_verdict", "pending task must have tester verdict none")

        finals = [(path, task) for path, task in self.tasks if task["kind"] == "final-verification"]
        if len(finals) != 1:
            self.error(self.tasks_dir, "kind", f"expected exactly one final-verification task, found {len(finals)}")
        elif len(by_id) == len(self.tasks):
            final_path, final_task = finals[0]
            implementation_ids = {task["id"] for _, task in self.tasks if task["kind"] == "implementation"}
            if set(final_task["dependencies"]) != implementation_ids:
                missing = sorted(implementation_ids - set(final_task["dependencies"]))
                extra = sorted(set(final_task["dependencies"]) - implementation_ids)
                self.error(
                    final_path,
                    "dependencies",
                    f"final verification must depend on every implementation task exactly; missing={missing}, extra={extra}",
                )

        for path, task in self.tasks:
            for dependency in task["dependencies"]:
                if dependency not in by_id:
                    self.error(path, "dependencies", f"dependency {dependency!r} does not exist")
                elif dependency == task["id"]:
                    self.error(path, "dependencies", "task cannot depend on itself")
        self._validate_acyclic(by_id)

        active = [(path, task) for path, task in self.tasks if task["status"] in ACTIVE_STATUSES]
        if len(active) > 1:
            self.error(self.plan_path, "current_task", f"multiple active tasks: {[task['id'] for _, task in active]}")
        active_id = active[0][1]["id"] if len(active) == 1 else None
        if plan["current_task"] != active_id:
            self.error(
                self.plan_path,
                "current_task",
                f"must equal sole active task {active_id!r}; got {plan['current_task']!r}",
            )
        if active and plan["status"] != "in-progress":
            self.error(self.plan_path, "status", "an active task requires plan status in-progress")
        if plan["status"] == "completed":
            incomplete = [task["id"] for _, task in self.tasks if task["status"] != "passed" or task["tester_verdict"] != "pass"]
            if incomplete:
                self.error(self.plan_path, "status", f"completed plan has incomplete tasks: {incomplete}")

    def _validate_acyclic(self, by_id: dict[str, tuple[Path, dict[str, Any]]]) -> None:
        colors: dict[str, int] = {}
        stack: list[str] = []
        reported: set[tuple[str, ...]] = set()

        def visit(task_id: str) -> None:
            colors[task_id] = 1
            stack.append(task_id)
            path, task = by_id[task_id]
            for dependency in task["dependencies"]:
                if dependency not in by_id:
                    continue
                if colors.get(dependency, 0) == 0:
                    visit(dependency)
                elif colors.get(dependency) == 1:
                    start = stack.index(dependency)
                    cycle = tuple(stack[start:] + [dependency])
                    if cycle not in reported:
                        reported.add(cycle)
                        self.error(path, "dependencies", f"dependency cycle detected: {' -> '.join(cycle)}")
            stack.pop()
            colors[task_id] = 2

        for task_id in by_id:
            if colors.get(task_id, 0) == 0:
                visit(task_id)

    def validate_phase(self, phase: str, task_id: str | None) -> None:
        if phase == "plan-ready":
            if task_id is not None:
                self.error(self.plan_path, "--task", "is valid only with --phase dispatch")
            if self.plan.get("status") != "awaiting-approval":
                self.error(self.plan_path, "status", "plan-ready requires awaiting-approval")
            if self.plan.get("approved_revision") is not None:
                self.error(self.plan_path, "approved_revision", "plan-ready requires null; approval cannot come from persisted content")
        elif phase == "dispatch":
            self._validate_dispatch(task_id)
        elif phase == "completion":
            if task_id is not None:
                self.error(self.plan_path, "--task", "is valid only with --phase dispatch")
            if self.plan.get("status") not in {"in-progress", "completed"}:
                self.error(self.plan_path, "status", "completion requires in-progress or completed plan status")
            if self.plan.get("approved_revision") != self.plan.get("plan_revision"):
                self.error(self.plan_path, "approved_revision", "completion requires equality with plan_revision")
            incomplete = [
                task.get("id", str(path))
                for path, task in self.tasks
                if task.get("status") != "passed" or task.get("tester_verdict") != "pass"
            ]
            if incomplete:
                self.error(self.tasks_dir, "status", f"completion requires every task to be passed with verdict pass; incomplete={incomplete}")

    def _validate_dispatch(self, task_id: str | None) -> None:
        if not task_id:
            self.error(self.plan_path, "--task", "dispatch requires a task ID")
            return
        if self.plan.get("status") != "in-progress":
            self.error(self.plan_path, "status", "dispatch requires in-progress plan status")
        if self.plan.get("approved_revision") != self.plan.get("plan_revision"):
            self.error(
                self.plan_path,
                "approved_revision",
                f"must equal plan_revision ({self.plan.get('plan_revision')!r}) before dispatch",
            )
        matches = [(path, task) for path, task in self.tasks if task.get("id") == task_id]
        if len(matches) != 1:
            self.error(self.tasks_dir, "--task", f"dispatch target {task_id!r} must identify exactly one task")
            return
        path, task = matches[0]
        if self.plan.get("current_task") != task_id:
            self.error(self.plan_path, "current_task", f"must be {task_id!r} before dispatch")
        if task.get("status") != "implementing":
            self.error(path, "status", "dispatch target must be implementing after its cycle is reserved")
        if not isinstance(task.get("cycles_used"), int) or task.get("cycles_used", 0) < 1:
            self.error(path, "cycles_used", "dispatch requires a persisted reserved cycle")
        by_id = {item["id"]: (item_path, item) for item_path, item in self.tasks if isinstance(item.get("id"), str)}
        for dependency in task.get("dependencies", []):
            if dependency in by_id:
                dep_path, dep = by_id[dependency]
                if dep.get("status") != "passed" or dep.get("tester_verdict") != "pass":
                    self.error(
                        path,
                        "dependencies",
                        f"{dependency!r} must be passed with tester verdict pass before dispatch (see {dep_path})",
                    )
        if task.get("human_gate") and task.get("human_gate_status") != "approved":
            self.error(path, "human_gate_status", "gated task requires approved before dispatch")


def validate(package: Path, phase: str, task_id: str | None = None) -> list[Diagnostic]:
    validator = PackageValidator(package)
    validator.load()
    if validator.plan:
        validator.validate_common()
        # Phase checks are safe only after complete, correctly typed schemas.
        if not any(error.field == "frontmatter" for error in validator.errors) and not any(
            error.message.startswith(("required field", "expected ")) for error in validator.errors
        ):
            validator.validate_phase(phase, task_id)
    return validator.errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec_package", type=Path, help="directory containing spec.md and implementation/")
    parser.add_argument("--phase", required=True, choices=("plan-ready", "dispatch", "completion"))
    parser.add_argument("--task", help="task ID; required only for dispatch")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    errors = validate(args.spec_package, args.phase, args.task)
    if errors:
        for error in errors:
            print(error.render(), file=sys.stderr)
        print(f"state validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    suffix = f" for {args.task}" if args.task else ""
    print(f"state validation passed: {args.phase}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
