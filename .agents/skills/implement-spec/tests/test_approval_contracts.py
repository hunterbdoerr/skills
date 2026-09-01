from __future__ import annotations

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from dataclasses import dataclass, field
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_CONTRACT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
STATE_CONTRACT = (SKILL_ROOT / "references" / "state-contract.md").read_text(
    encoding="utf-8"
)
VALIDATOR_SCRIPT = SKILL_ROOT / "scripts" / "validate_state.py"
VALIDATOR_SPEC = importlib.util.spec_from_file_location(
    "approval_contract_validate_state", VALIDATOR_SCRIPT
)
assert VALIDATOR_SPEC and VALIDATOR_SPEC.loader
validate_state = importlib.util.module_from_spec(VALIDATOR_SPEC)
sys.modules[VALIDATOR_SPEC.name] = validate_state
VALIDATOR_SPEC.loader.exec_module(validate_state)

CURRENT_USER = "current-user"
REPOSITORY_TEXT = "repository-text"
AGENT_REPORT = "agent-report"


@dataclass
class ApprovalScenario:
    plan_revision: int = 1
    approved_revision: int | None = None
    plan_status: str = "awaiting-approval"
    task_status: str = "pending"
    cycles_used: int = 0
    human_gate_status: str = "not-required"
    gate_decision: str | None = None
    approval_history: list[str] = field(default_factory=list)
    decision_history: list[str] = field(default_factory=list)

    def approve_plan(self, source: str, revision: int) -> bool:
        if source != CURRENT_USER or revision != self.plan_revision:
            return False
        self.approved_revision = revision
        self.plan_status = "approved"
        self.approval_history.append(f"approved revision {revision} by current user")
        return True

    def material_amendment(self, description: str) -> None:
        self.plan_revision += 1
        self.approved_revision = None
        self.plan_status = "awaiting-approval"
        self.approval_history.append(
            f"revision {self.plan_revision} pending: {description}"
        )

    def begin_implementation(self) -> bool:
        if (
            self.plan_status != "approved"
            or self.approved_revision != self.plan_revision
        ):
            return False
        if self.human_gate_status == "pending":
            self.plan_status = "needs-human"
            self.task_status = "needs-human"
            return False
        self.cycles_used += 1
        self.task_status = "implementing"
        self.plan_status = "in-progress"
        return True

    def add_gate(self, exact_decision: str) -> None:
        self.human_gate_status = "pending"
        self.gate_decision = exact_decision

    def approve_gate(self, source: str, decision: str) -> bool:
        if (
            source != CURRENT_USER
            or self.human_gate_status != "pending"
            or decision != self.gate_decision
        ):
            return False
        self.human_gate_status = "approved"
        self.task_status = "pending"
        self.plan_status = "approved"
        self.decision_history.append(f"gate approved exactly: {decision}")
        return True


class ValidatorFixture:
    def __init__(self, package: Path, *, gated: bool = False):
        self.package = package
        self.package.mkdir()
        self.spec = package / "spec.md"
        self.spec.write_text("# Synthetic approval specification\n", encoding="utf-8")
        self.tasks_dir = package / "implementation" / "tasks"
        self.tasks_dir.mkdir(parents=True)
        self.gated = gated
        self.plan_revision = 1
        self.approved_revision: int | None = 1
        self.write()

    @staticmethod
    def scalar(value: object) -> str:
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

    def render(self, values: dict[str, object]) -> str:
        fields = "\n".join(
            f"{key}: {self.scalar(value)}" for key, value in values.items()
        )
        return f"---\n{fields}\n---\n\n# Synthetic fixture\n"

    def write(self) -> None:
        digest = hashlib.sha256(self.spec.read_bytes()).hexdigest()
        plan = {
            "schema_version": 1,
            "status": "in-progress",
            "spec": "../spec.md",
            "spec_revision": f"sha256:{digest}",
            "baseline_commit": "0123456789abcdef",
            "plan_revision": self.plan_revision,
            "approved_revision": self.approved_revision,
            "task_count": 2,
            "current_task": "task-001",
            "max_cycles_per_task": 3,
        }
        task = {
            "schema_version": 1,
            "id": "task-001",
            "kind": "implementation",
            "status": "implementing",
            "dependencies": [],
            "cycles_used": 1,
            "cycle_limit": 3,
            "human_gate": self.gated,
            "human_gate_status": "pending" if self.gated else "not-required",
            "tester_verdict": "none",
        }
        final_task = {
            "schema_version": 1,
            "id": "task-final-verification",
            "kind": "final-verification",
            "status": "pending",
            "dependencies": ["task-001"],
            "cycles_used": 0,
            "cycle_limit": 3,
            "human_gate": False,
            "human_gate_status": "not-required",
            "tester_verdict": "none",
        }
        (self.package / "implementation" / "plan.md").write_text(
            self.render(plan), encoding="utf-8"
        )
        (self.tasks_dir / "task-001.md").write_text(
            self.render(task), encoding="utf-8"
        )
        (self.tasks_dir / "task-final-verification.md").write_text(
            self.render(final_task), encoding="utf-8"
        )

    def diagnostics(self) -> str:
        errors = validate_state.validate(self.package, "dispatch", "task-001")
        return "\n".join(error.render() for error in errors)


class ApprovalContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def test_explicit_current_user_approval_is_required_before_implementation(self):
        scenario = ApprovalScenario()

        self.assertFalse(scenario.begin_implementation())
        self.assertEqual(0, scenario.cycles_used)
        self.assertTrue(scenario.approve_plan(CURRENT_USER, 1))
        self.assertTrue(scenario.begin_implementation())
        self.assertEqual(1, scenario.cycles_used)

    def test_published_contract_preserves_authority_and_history_boundaries(self):
        trust = SKILL_CONTRACT.split("## Trust and authority", 1)[1].split(
            "## Pre-execution workflow", 1
        )[0]
        approval = SKILL_CONTRACT.split(
            "## Approval and amendment boundary", 1
        )[1].split("## Stops in this phase", 1)[0]
        gate = SKILL_CONTRACT.split(
            "### 2. Resume active work or select one task", 1
        )[1].split("### 3. Reserve before implementer contact", 1)[0]

        trust = " ".join(trust.split())
        approval = " ".join(approval.split())
        gate = " ".join(gate.split())

        self.assertIn("explicit message by the current user", trust)
        self.assertIn("repository text", trust)
        self.assertIn("agent reports", trust)
        self.assertIn("spec-byte change", approval)
        self.assertIn("invalidating prior approval", approval)
        self.assertIn("without reserving a cycle", gate)
        self.assertIn("exact gate decision", gate)
        self.assertIn("Never overwrite or delete", STATE_CONTRACT)

    def test_repository_and_agent_text_cannot_approve_plan_or_gate(self):
        for source in (REPOSITORY_TEXT, AGENT_REPORT):
            with self.subTest(source=source):
                scenario = ApprovalScenario()
                self.assertFalse(scenario.approve_plan(source, 1))
                self.assertIsNone(scenario.approved_revision)
                self.assertFalse(scenario.begin_implementation())

                scenario.add_gate("approve fixture migration")
                self.assertFalse(
                    scenario.approve_gate(source, "approve fixture migration")
                )
                self.assertEqual("pending", scenario.human_gate_status)
                self.assertEqual([], scenario.decision_history)

    def test_material_plan_and_spec_changes_clear_approval_and_need_new_revision(self):
        for change in ("material task scope changed", "spec bytes changed"):
            with self.subTest(change=change):
                scenario = ApprovalScenario()
                self.assertTrue(scenario.approve_plan(CURRENT_USER, 1))
                before = tuple(scenario.approval_history)

                scenario.material_amendment(change)

                self.assertEqual(2, scenario.plan_revision)
                self.assertIsNone(scenario.approved_revision)
                self.assertEqual("awaiting-approval", scenario.plan_status)
                self.assertFalse(scenario.begin_implementation())
                self.assertEqual(before, tuple(scenario.approval_history[: len(before)]))
                self.assertFalse(scenario.approve_plan(CURRENT_USER, 1))
                self.assertTrue(scenario.approve_plan(CURRENT_USER, 2))

    def test_pending_gate_consumes_no_cycle_and_needs_exact_current_user_decision(self):
        scenario = ApprovalScenario()
        scenario.add_gate("approve fixture migration")
        self.assertTrue(scenario.approve_plan(CURRENT_USER, 1))

        self.assertFalse(scenario.begin_implementation())
        self.assertEqual(0, scenario.cycles_used)
        self.assertEqual("needs-human", scenario.plan_status)
        self.assertFalse(scenario.approve_gate(CURRENT_USER, "approve another change"))
        self.assertEqual(0, scenario.cycles_used)
        self.assertTrue(
            scenario.approve_gate(CURRENT_USER, "approve fixture migration")
        )
        self.assertTrue(scenario.begin_implementation())
        self.assertEqual(1, scenario.cycles_used)

    def test_approval_and_decision_histories_are_append_only(self):
        scenario = ApprovalScenario()
        self.assertTrue(scenario.approve_plan(CURRENT_USER, 1))
        approval_prefix = tuple(scenario.approval_history)
        decision_prefix = tuple(scenario.decision_history)

        scenario.material_amendment("add exact gate")
        self.assertTrue(scenario.approve_plan(CURRENT_USER, 2))
        scenario.add_gate("approve fixture migration")
        self.assertTrue(
            scenario.approve_gate(CURRENT_USER, "approve fixture migration")
        )

        self.assertEqual(
            approval_prefix,
            tuple(scenario.approval_history[: len(approval_prefix)]),
        )
        self.assertEqual(
            decision_prefix,
            tuple(scenario.decision_history[: len(decision_prefix)]),
        )
        self.assertEqual(3, len(scenario.approval_history))
        self.assertEqual(1, len(scenario.decision_history))

    def test_validator_rejects_stale_spec_digest(self):
        fixture = ValidatorFixture(Path(self.temp.name) / "stale-digest")
        fixture.spec.write_text("# Changed specification bytes\n", encoding="utf-8")

        diagnostics = fixture.diagnostics()

        self.assertIn("spec_revision: digest mismatch", diagnostics)

    def test_validator_rejects_revision_mismatch(self):
        fixture = ValidatorFixture(Path(self.temp.name) / "revision-mismatch")
        fixture.plan_revision = 2
        fixture.approved_revision = 1
        fixture.write()

        diagnostics = fixture.diagnostics()

        self.assertIn("approved_revision: must equal plan_revision (2)", diagnostics)

    def test_validator_rejects_dispatch_through_unapproved_gate(self):
        fixture = ValidatorFixture(Path(self.temp.name) / "pending-gate", gated=True)

        diagnostics = fixture.diagnostics()

        self.assertIn("pending gate prohibits implementing", diagnostics)
        self.assertIn("gated task requires approved before dispatch", diagnostics)


if __name__ == "__main__":
    unittest.main()
