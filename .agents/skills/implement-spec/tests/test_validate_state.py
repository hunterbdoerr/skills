from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_state.py"
SPEC = importlib.util.spec_from_file_location("validate_state", SCRIPT)
assert SPEC and SPEC.loader
validate_state = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate_state
SPEC.loader.exec_module(validate_state)


class PackageFixture:
    def __init__(self, root: Path, phase: str = "plan-ready"):
        self.root = root
        self.phase = phase
        self.root.mkdir()
        self.spec = self.root / "spec.md"
        self.spec.write_text("# Test specification\n", encoding="utf-8")
        (self.root / "implementation" / "tasks").mkdir(parents=True)
        self.tasks = {
            "task-001": self.task(),
            "task-final-verification": self.task(
                task_id="task-final-verification",
                kind="final-verification",
                dependencies=["task-001"],
            ),
        }
        self.plan = self.plan_data()
        self.write()

    def plan_data(self):
        digest = hashlib.sha256(self.spec.read_bytes()).hexdigest()
        return {
            "schema_version": 1,
            "status": "awaiting-approval",
            "spec": "../spec.md",
            "spec_revision": f"sha256:{digest}",
            "baseline_commit": "0123456789abcdef",
            "plan_revision": 1,
            "approved_revision": None,
            "task_count": 2,
            "current_task": None,
            "max_cycles_per_task": 3,
        }

    @staticmethod
    def task(task_id="task-001", kind="implementation", dependencies=None):
        return {
            "schema_version": 1,
            "id": task_id,
            "kind": kind,
            "status": "pending",
            "dependencies": [] if dependencies is None else dependencies,
            "cycles_used": 0,
            "cycle_limit": 3,
            "human_gate": False,
            "human_gate_status": "not-required",
            "tester_verdict": "none",
        }

    @staticmethod
    def scalar(value):
        if value is None:
            return "null"
        if value is True:
            return "true"
        if value is False:
            return "false"
        if isinstance(value, list):
            return "[" + ", ".join(value) + "]"
        if isinstance(value, str) and ":" in value:
            return f'"{value}"'
        return str(value)

    def render(self, data):
        fields = [f"{key}: {self.scalar(value)}" for key, value in data.items()]
        return "---\n" + "\n".join(fields) + "\n---\n\n# Body\n"

    def write(self):
        (self.root / "implementation" / "plan.md").write_text(
            self.render(self.plan), encoding="utf-8"
        )
        tasks_dir = self.root / "implementation" / "tasks"
        for old in tasks_dir.glob("*.md"):
            old.unlink()
        for filename, task in self.tasks.items():
            (tasks_dir / f"{filename}.md").write_text(self.render(task), encoding="utf-8")

    def make_dispatch(self, task_id="task-001"):
        self.plan.update(
            status="in-progress",
            approved_revision=self.plan["plan_revision"],
            current_task=task_id,
        )
        self.tasks[task_id].update(status="implementing", cycles_used=1)
        self.write()

    def make_completion(self):
        self.plan.update(status="in-progress", approved_revision=1, current_task=None)
        for task in self.tasks.values():
            task.update(status="passed", cycles_used=1, tester_verdict="pass")
        self.write()

    def errors(self, phase=None, task_id=None):
        self.write()
        return validate_state.validate(self.root, phase or self.phase, task_id)


class ValidateStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture = PackageFixture(Path(self.temp.name) / "package")

    def messages(self, errors):
        return "\n".join(error.render() for error in errors)

    def assert_invalid(self, expected, phase=None, task_id=None):
        errors = self.fixture.errors(phase, task_id)
        self.assertTrue(errors)
        self.assertIn(expected, self.messages(errors))

    def test_valid_plan_ready(self):
        self.assertEqual([], self.fixture.errors())

    def test_valid_dispatch(self):
        self.fixture.make_dispatch()
        self.assertEqual([], self.fixture.errors("dispatch", "task-001"))

    def test_valid_completion(self):
        self.fixture.make_completion()
        self.assertEqual([], self.fixture.errors("completion"))

    def test_cli_returns_nonzero_and_actionable_file_field_diagnostic(self):
        self.fixture.plan["spec_revision"] = "sha256:" + "0" * 64
        self.fixture.write()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.fixture.root), "--phase", "plan-ready"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("implementation/plan.md: spec_revision: digest mismatch", result.stderr)

    def test_malformed_and_unsupported_frontmatter(self):
        plan_path = self.fixture.root / "implementation" / "plan.md"
        plan_path.write_text("---\nschema_version: &version 1\n---\n", encoding="utf-8")
        errors = validate_state.validate(self.fixture.root, "plan-ready")
        self.assertIn("unsupported YAML value", self.messages(errors))

    def test_nested_yaml_comments_single_quotes_and_duplicate_keys_are_rejected(self):
        samples = (
            "---\nschema_version:\n  nested: 1\n---\n",
            "---\n# comment\n---\n",
            "---\nschema_version: '1'\n---\n",
            "---\nschema_version: 1\nschema_version: 1\n---\n",
        )
        path = self.fixture.root / "bad.md"
        for sample in samples:
            with self.subTest(sample=sample):
                path.write_text(sample, encoding="utf-8")
                with self.assertRaises(validate_state.FrontmatterError):
                    validate_state.parse_frontmatter(path)

    def test_required_unknown_and_wrong_type_fields(self):
        del self.fixture.plan["baseline_commit"]
        self.fixture.plan["surprise"] = "value"
        self.fixture.plan["task_count"] = "two"
        errors = self.messages(self.fixture.errors())
        self.assertIn("baseline_commit: required field is missing", errors)
        self.assertIn("surprise: field is not supported", errors)
        self.assertIn("task_count: expected int", errors)

    def test_unknown_schema_and_enums(self):
        self.fixture.plan["schema_version"] = 2
        self.fixture.plan["status"] = "running"
        self.fixture.tasks["task-001"]["kind"] = "review"
        self.fixture.tasks["task-001"]["status"] = "queued"
        self.fixture.tasks["task-001"]["human_gate_status"] = "waived"
        self.fixture.tasks["task-001"]["tester_verdict"] = "maybe"
        errors = self.messages(self.fixture.errors())
        for expected in ("recognized value is exactly 1", "unknown plan state", "unknown task kind", "unknown task state", "unknown gate state", "unknown tester verdict"):
            self.assertIn(expected, errors)

    def test_stale_spec_digest_and_noncanonical_spec_path(self):
        self.fixture.plan["spec_revision"] = "sha256:" + "0" * 64
        self.assert_invalid("digest mismatch")
        self.fixture.plan["spec"] = "../../outside.md"
        self.assert_invalid("must resolve to canonical package spec")

    def test_task_count_and_duplicate_ids(self):
        self.fixture.plan["task_count"] = 3
        self.fixture.tasks["copy"] = dict(self.fixture.tasks["task-001"])
        errors = self.messages(self.fixture.errors())
        self.assertIn("duplicate task ID", errors)

        del self.fixture.tasks["copy"]
        self.assert_invalid("declares 3 but found 2")

    def test_missing_dependency(self):
        self.fixture.tasks["task-001"]["dependencies"] = ["task-999"]
        self.assert_invalid("dependency 'task-999' does not exist")

    def test_circular_dependency(self):
        self.fixture.tasks["task-001"]["dependencies"] = ["task-final-verification"]
        self.assert_invalid("dependency cycle detected")

    def test_missing_and_multiple_final_verification(self):
        self.fixture.tasks["task-final-verification"]["kind"] = "implementation"
        self.assert_invalid("expected exactly one final-verification task, found 0")
        self.fixture.tasks["task-001"]["kind"] = "final-verification"
        self.fixture.tasks["task-final-verification"]["kind"] = "final-verification"
        self.assert_invalid("expected exactly one final-verification task, found 2")

    def test_final_depends_on_every_implementation_task(self):
        self.fixture.tasks["task-final-verification"]["dependencies"] = []
        self.assert_invalid("must depend on every implementation task exactly")

    def test_multiple_active_tasks_and_current_task_consistency(self):
        self.fixture.plan.update(status="in-progress", current_task="task-001")
        for task in self.fixture.tasks.values():
            task.update(status="implementing", cycles_used=1)
        errors = self.messages(self.fixture.errors("dispatch", "task-001"))
        self.assertIn("multiple active tasks", errors)

        self.fixture.tasks["task-final-verification"].update(status="pending", cycles_used=0)
        self.fixture.plan["current_task"] = None
        self.assert_invalid("must equal sole active task 'task-001'", "dispatch", "task-001")

    def test_dispatch_requires_matching_approval_revision(self):
        self.fixture.make_dispatch()
        self.fixture.plan["approved_revision"] = None
        self.assert_invalid("must equal plan_revision", "dispatch", "task-001")

    def test_dispatch_requires_reserved_implementing_cycle(self):
        self.fixture.make_dispatch()
        self.fixture.tasks["task-001"].update(status="pending", cycles_used=0)
        self.fixture.plan["current_task"] = None
        self.assert_invalid("dispatch target must be implementing", "dispatch", "task-001")

    def test_dispatch_requires_passed_dependencies(self):
        self.fixture.tasks["task-002"] = self.fixture.task("task-002", dependencies=["task-001"])
        self.fixture.tasks["task-final-verification"]["dependencies"] = ["task-001", "task-002"]
        self.fixture.plan["task_count"] = 3
        self.fixture.make_dispatch("task-002")
        self.assert_invalid("must be passed with tester verdict pass", "dispatch", "task-002")

    def test_dispatch_rejects_pending_human_gate(self):
        self.fixture.make_dispatch()
        self.fixture.tasks["task-001"].update(human_gate=True, human_gate_status="pending")
        self.assert_invalid("gated task requires approved before dispatch", "dispatch", "task-001")

    def test_cycle_bounds_and_state_accounting(self):
        self.fixture.tasks["task-001"].update(cycles_used=4, cycle_limit=3)
        self.assert_invalid("exceeds cycle_limit")
        self.fixture.tasks["task-001"].update(status="implementing", cycles_used=0)
        self.fixture.plan.update(status="in-progress", current_task="task-001")
        self.assert_invalid("must be at least 1 while status is 'implementing'", "dispatch", "task-001")

    def test_positive_task_limit_and_persisted_extension(self):
        self.fixture.tasks["task-001"]["cycle_limit"] = 0
        self.assert_invalid("cycle_limit: must be at least 1")
        self.fixture.tasks["task-001"]["cycle_limit"] = 6
        self.assertEqual([], self.fixture.errors())

    def test_invalid_pass_verdict_combinations(self):
        self.fixture.tasks["task-001"].update(status="passed", cycles_used=1, tester_verdict="fail")
        self.assert_invalid("passed task requires tester verdict pass")
        self.fixture.tasks["task-001"].update(status="testing", tester_verdict="pass")
        self.fixture.plan.update(status="in-progress", current_task="task-001")
        self.assert_invalid("tester verdict pass requires task status passed", "dispatch", "task-001")

    def test_plan_ready_cannot_treat_file_content_as_approval(self):
        self.fixture.plan.update(status="approved", approved_revision=1)
        errors = self.messages(self.fixture.errors())
        self.assertIn("plan-ready requires awaiting-approval", errors)
        self.assertIn("plan-ready requires null", errors)

    def test_incomplete_completion(self):
        self.fixture.plan.update(status="in-progress", approved_revision=1)
        self.assert_invalid("completion requires every task", "completion")

    def test_completed_plan_must_be_internally_complete(self):
        self.fixture.plan.update(status="completed", approved_revision=1)
        self.assert_invalid("completed plan has incomplete tasks", "completion")


if __name__ == "__main__":
    unittest.main()
