from __future__ import annotations

import copy
import gc
import hashlib
import json
import tempfile
import unittest
import weakref
from dataclasses import dataclass
from pathlib import Path


CRITERIA = (
    "cycle reserved before implementer contact",
    "exactly one active task",
    "direct implementer owns code and test edits",
    "independent tester checks every criterion without edits",
    "pass advances exactly once",
)


@dataclass(frozen=True)
class RoleReport:
    role_id: str
    direct: bool
    delegated: bool
    status: str
    checked_criteria: tuple[str, ...] = ()


_CONTACTED_IMPLEMENTER_BINDINGS = weakref.WeakKeyDictionary()


class SuccessfulExecutionFixture:
    """A synthetic happy-path handoff with observable file ownership."""

    def __setattr__(self, name: str, value: object) -> None:
        if (
            name == "_contacted_implementer_anchor"
            and name in self.__dict__
            and self.__dict__[name] is not None
        ):
            raise AttributeError("contacted implementer anchor is write-once")
        object.__setattr__(self, name, value)

    def __init__(self, root: Path):
        self.root = root
        self.product = root / "product" / "feature.py"
        self.test = root / "tests" / "test_feature.py"
        self.state = root / "implementation" / "state.json"
        for path in (self.product, self.test, self.state):
            path.parent.mkdir(parents=True, exist_ok=True)
        self.product.write_text("ENABLED = False\n", encoding="utf-8")
        self.test.write_text("EXPECTED = False\n", encoding="utf-8")
        self.tasks = {
            "task-dependency": {
                "status": "passed",
                "tester_verdict": "pass",
                "dependencies": [],
                "cycles_used": 1,
            },
            "task-target": {
                "status": "pending",
                "tester_verdict": "none",
                "dependencies": ["task-dependency"],
                "cycles_used": 0,
            },
            "task-later": {
                "status": "pending",
                "tester_verdict": "none",
                "dependencies": ["task-target"],
                "cycles_used": 0,
            },
        }
        self.current_task: str | None = None
        self.events: list[str] = []
        self.advance_count = 0
        self.contacted_implementer_id: str | None = None
        self._contacted_implementer_receipt: tuple[str] | None = None
        self._contacted_implementer_anchor: str | None = None
        self.accepted_implementer_id: str | None = None
        self.accepted_tester_id: str | None = None
        self.reviewed_snapshot: tuple[tuple[str, str], ...] | None = None
        self._persist_state()

    def _state_payload(self) -> dict[str, object]:
        return {
            "current_task": self.current_task,
            "tasks": self.tasks,
            "advance_count": self.advance_count,
            "contacted_implementer_id": self.contacted_implementer_id,
            "accepted_implementer_id": self.accepted_implementer_id,
            "accepted_tester_id": self.accepted_tester_id,
        }

    @staticmethod
    def _expected_reservation_state() -> dict[str, object]:
        return {
            "current_task": "task-target",
            "tasks": {
                "task-dependency": {
                    "status": "passed",
                    "tester_verdict": "pass",
                    "dependencies": [],
                    "cycles_used": 1,
                },
                "task-target": {
                    "status": "implementing",
                    "tester_verdict": "none",
                    "dependencies": ["task-dependency"],
                    "cycles_used": 1,
                },
                "task-later": {
                    "status": "pending",
                    "tester_verdict": "none",
                    "dependencies": ["task-target"],
                    "cycles_used": 0,
                },
            },
            "advance_count": 0,
            "contacted_implementer_id": None,
            "accepted_implementer_id": None,
            "accepted_tester_id": None,
        }

    def _persist_state(self) -> None:
        self.state.write_text(
            json.dumps(self._state_payload(), sort_keys=True)
            + "\n",
            encoding="utf-8",
        )

    @classmethod
    def _expected_contacted_state(
        cls, role_id: str, *, accepted: bool = False
    ) -> dict[str, object]:
        expected = cls._expected_reservation_state()
        expected["contacted_implementer_id"] = role_id
        if accepted:
            expected["accepted_implementer_id"] = role_id
        return expected

    @classmethod
    def _matches_exact_structure(cls, actual: object, expected: object) -> bool:
        if type(actual) is not type(expected):
            return False
        if isinstance(expected, dict):
            if actual.keys() != expected.keys():
                return False
            return all(
                cls._matches_exact_structure(actual[key], expected[key])
                for key in expected
            )
        if isinstance(expected, list):
            return len(actual) == len(expected) and all(
                cls._matches_exact_structure(actual_item, expected_item)
                for actual_item, expected_item in zip(actual, expected)
            )
        return actual == expected

    def snapshot(self) -> dict[str, str]:
        snapshot = {}
        for path in sorted(self.root.rglob("*")):
            if path.is_file():
                snapshot[path.relative_to(self.root).as_posix()] = hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
        return snapshot

    @staticmethod
    def categorized_diff(
        before: dict[str, str], after: dict[str, str]
    ) -> dict[str, set[str]]:
        changed = {
            path
            for path in before.keys() | after.keys()
            if before.get(path) != after.get(path)
        }
        return {
            "production": {path for path in changed if path.startswith("product/")},
            "tests": {path for path in changed if path.startswith("tests/")},
            "orchestration": {
                path for path in changed if path.startswith("implementation/")
            },
        }

    def dependency_ready_selection(self) -> str:
        self._require_no_active_task()
        ready = []
        for task_id, task in self.tasks.items():
            if task["status"] != "pending":
                continue
            dependencies = task["dependencies"]
            if all(
                self.tasks[dependency]["status"] == "passed"
                and self.tasks[dependency]["tester_verdict"] == "pass"
                for dependency in dependencies
            ):
                ready.append(task_id)
        if ready != ["task-target"]:
            raise AssertionError(f"expected one dependency-ready task, got {ready}")
        return ready[0]

    def reserve(self, task_id: str) -> None:
        if task_id != self.dependency_ready_selection():
            raise AssertionError("task is not dependency ready")
        task = self.tasks[task_id]
        task["cycles_used"] += 1
        task["status"] = "implementing"
        self.current_task = task_id
        self.events.append("reservation persisted")
        self._persist_state()
        self._require_exactly_one_active_task()

    def contact_implementer(self, report: RoleReport) -> None:
        persisted = json.loads(self.state.read_text(encoding="utf-8"))
        expected = self._expected_reservation_state()
        if (
            not self._matches_exact_structure(self._state_payload(), expected)
            or not self._matches_exact_structure(persisted, expected)
            or self._contacted_implementer_receipt is not None
            or self._contacted_implementer_anchor is not None
            or self in _CONTACTED_IMPLEMENTER_BINDINGS
        ):
            raise AssertionError("complete reservation was not persisted before contact")
        if self.events != ["reservation persisted"]:
            raise AssertionError("implementer contacted before reservation")
        if (
            type(report.direct) is not bool
            or type(report.delegated) is not bool
            or report.direct is not True
            or report.delegated is not False
            or type(report.role_id) is not str
            or not report.role_id.strip()
        ):
            raise AssertionError("implementer must be direct and non-delegating")
        _CONTACTED_IMPLEMENTER_BINDINGS[self] = report.role_id
        self.contacted_implementer_id = report.role_id
        self._contacted_implementer_receipt = (report.role_id,)
        self._contacted_implementer_anchor = report.role_id
        self._persist_state()
        self.events.append(f"implementer contacted:{report.role_id}")

    def implement(self) -> None:
        self.product.write_text("ENABLED = True\n", encoding="utf-8")
        self.test.write_text("EXPECTED = True\n", encoding="utf-8")

    def begin_testing(self) -> None:
        if self.accepted_implementer_id is None:
            raise AssertionError("accepted implementer report is required before testing")
        if self.accepted_tester_id is not None:
            raise AssertionError("tester handoff already exists")
        if (
            type(self.accepted_implementer_id) is not str
            or not self.accepted_implementer_id.strip()
        ):
            raise AssertionError("implementer handoff state is not coherent")
        persisted = json.loads(self.state.read_text(encoding="utf-8"))
        expected = self._expected_contacted_state(
            self.accepted_implementer_id, accepted=True
        )
        bound_contacted_id = _CONTACTED_IMPLEMENTER_BINDINGS.get(self)
        if (
            not self._matches_exact_structure(self._state_payload(), expected)
            or not self._matches_exact_structure(persisted, expected)
            or self._contacted_implementer_receipt
            != (self.accepted_implementer_id,)
            or self._contacted_implementer_anchor
            != self.accepted_implementer_id
            or bound_contacted_id != self.accepted_implementer_id
        ):
            raise AssertionError("implementer handoff state is not coherent")
        self.tasks["task-target"]["status"] = "testing"
        self._persist_state()
        self._require_exactly_one_active_task()

    def accept_tester(
        self,
        tester: RoleReport,
        before: dict[str, str],
        after: dict[str, str],
    ) -> None:
        if self.accepted_implementer_id is None:
            raise AssertionError("accepted implementer report is required")
        if self.accepted_tester_id is not None:
            raise AssertionError("tester handoff may be accepted exactly once")
        if tester.role_id == self.accepted_implementer_id:
            raise AssertionError("tester must differ from implementer")
        if tester.status != "pass" or not tester.direct or tester.delegated:
            raise AssertionError("tester must be direct and non-delegating")
        if tester.checked_criteria != CRITERIA:
            raise AssertionError("tester must check every criterion exactly once in order")
        if before != after:
            raise AssertionError("tester mutation invalidates the handoff")
        task = self.tasks["task-target"]
        persisted = json.loads(self.state.read_text(encoding="utf-8"))
        persisted_task = persisted["tasks"]["task-target"]
        if (
            self.current_task != "task-target"
            or task["status"] != "testing"
            or task["cycles_used"] != 1
            or task["tester_verdict"] != "none"
            or self.advance_count != 0
            or persisted["current_task"] != self.current_task
            or persisted["tasks"] != self.tasks
            or persisted_task != task
            or persisted["advance_count"] != self.advance_count
            or persisted["accepted_implementer_id"]
            != self.accepted_implementer_id
            or persisted["accepted_tester_id"] is not None
        ):
            raise AssertionError("testing handoff metadata is not coherent")
        self.accepted_tester_id = tester.role_id
        self._persist_state()
        self.reviewed_snapshot = tuple(sorted(self.snapshot().items()))
        self.events.append(f"tester accepted:{tester.role_id}")

    def accept_implementer_diff(
        self,
        report: RoleReport,
        before: dict[str, str],
        after: dict[str, str],
    ) -> None:
        if self.accepted_implementer_id is not None:
            raise AssertionError("implementer handoff may be accepted exactly once")
        changed = {
            path
            for path in before.keys() | after.keys()
            if before.get(path) != after.get(path)
        }
        diff = self.categorized_diff(before, after)
        if diff["orchestration"]:
            raise AssertionError("implementer mutation invalidates the handoff")
        persisted = json.loads(self.state.read_text(encoding="utf-8"))
        contacted_id = self.contacted_implementer_id
        bound_contacted_id = _CONTACTED_IMPLEMENTER_BINDINGS.get(self)
        expected = (
            self._expected_contacted_state(contacted_id)
            if type(contacted_id) is str
            else None
        )
        if (
            type(report.role_id) is not str
            or type(report.direct) is not bool
            or type(report.delegated) is not bool
            or type(contacted_id) is not str
            or not contacted_id.strip()
            or report.role_id != contacted_id
            or self._contacted_implementer_receipt != (contacted_id,)
            or self._contacted_implementer_anchor != contacted_id
            or bound_contacted_id != contacted_id
            or not self._matches_exact_structure(self._state_payload(), expected)
            or not self._matches_exact_structure(persisted, expected)
        ):
            raise AssertionError(
                "implementer report identity must match contacted implementer"
            )
        allowed = {"product/feature.py", "tests/test_feature.py"}
        if changed != allowed:
            raise AssertionError(
                f"implementer changed paths outside the exact allowance: {changed - allowed}"
            )
        if not self.product.is_file() or not self.test.is_file():
            raise AssertionError("allowed product and test files must remain present")
        if (
            report.status != "ready-for-test"
            or report.direct is not True
            or report.delegated is not False
        ):
            raise AssertionError("implementer report must be direct and non-delegating")
        if diff["production"] != {"product/feature.py"}:
            raise AssertionError("expected one in-scope production edit")
        if diff["tests"] != {"tests/test_feature.py"}:
            raise AssertionError("expected one in-scope test edit")
        self.accepted_implementer_id = report.role_id
        self._persist_state()
        self.events.append(f"implementer report accepted:{report.role_id}")

    def accept_pass(self) -> None:
        task = self.tasks["task-target"]
        if task["status"] == "passed" or task["tester_verdict"] == "pass":
            raise AssertionError("pass may advance the task exactly once")
        implementer_handoffs = [
            event
            for event in self.events
            if event.startswith("implementer report accepted:")
        ]
        tester_handoffs = [
            event for event in self.events if event.startswith("tester accepted:")
        ]
        if len(implementer_handoffs) != 1 or self.accepted_implementer_id is None:
            raise AssertionError("one accepted implementer handoff is required before pass")
        if len(tester_handoffs) != 1 or self.accepted_tester_id is None:
            raise AssertionError("one accepted tester handoff is required before pass")
        if self.reviewed_snapshot is None or tuple(sorted(self.snapshot().items())) != self.reviewed_snapshot:
            raise AssertionError("filesystem changed after tester review")
        persisted = json.loads(self.state.read_text(encoding="utf-8"))
        persisted_task = persisted["tasks"]["task-target"]
        if (
            self.current_task != "task-target"
            or task["status"] != "testing"
            or task["cycles_used"] != 1
            or task["tester_verdict"] != "none"
            or self.advance_count != 0
            or persisted["current_task"] != self.current_task
            or persisted["tasks"] != self.tasks
            or persisted_task["status"] != task["status"]
            or persisted_task["cycles_used"] != task["cycles_used"]
            or persisted_task["tester_verdict"] != task["tester_verdict"]
            or persisted["advance_count"] != self.advance_count
            or persisted["contacted_implementer_id"]
            != self.contacted_implementer_id
            or self.contacted_implementer_id != self.accepted_implementer_id
            or persisted["accepted_implementer_id"]
            != self.accepted_implementer_id
            or persisted["accepted_tester_id"] != self.accepted_tester_id
        ):
            raise AssertionError("pass state is not coherent with reviewed evidence")
        task["tester_verdict"] = "pass"
        task["status"] = "passed"
        self.current_task = None
        self.advance_count += 1
        self._persist_state()

    def _require_no_active_task(self) -> None:
        active = [
            task_id
            for task_id, task in self.tasks.items()
            if task["status"] in {"implementing", "testing"}
        ]
        if self.current_task is not None or active:
            raise AssertionError("an active task already exists")

    def _require_exactly_one_active_task(self) -> None:
        active = [
            task_id
            for task_id, task in self.tasks.items()
            if task["status"] in {"implementing", "testing"}
        ]
        if active != [self.current_task]:
            raise AssertionError(f"expected exactly one active task, got {active}")


class SuccessfulExecutionOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture = SuccessfulExecutionFixture(Path(self.temp.name))
        self.implementer = RoleReport(
            role_id="direct-implementer",
            direct=True,
            delegated=False,
            status="ready-for-test",
        )
        self.tester = RoleReport(
            role_id="independent-tester",
            direct=True,
            delegated=False,
            status="pass",
            checked_criteria=CRITERIA,
        )

    def prepare_testing(self) -> None:
        self.fixture.reserve(self.fixture.dependency_ready_selection())
        self.fixture.contact_implementer(self.implementer)
        before = self.fixture.snapshot()
        self.fixture.implement()
        self.fixture.accept_implementer_diff(
            self.implementer, before, self.fixture.snapshot()
        )
        self.fixture.begin_testing()

    def complete_review(self) -> None:
        self.prepare_testing()
        before = self.fixture.snapshot()
        self.fixture.accept_tester(self.tester, before, self.fixture.snapshot())

    def test_smallest_successful_transition_and_role_diffs(self):
        before_reservation = self.fixture.snapshot()
        selected = self.fixture.dependency_ready_selection()
        self.fixture.reserve(selected)
        after_reservation = self.fixture.snapshot()
        self.assertEqual(
            {
                "production": set(),
                "tests": set(),
                "orchestration": {"implementation/state.json"},
            },
            self.fixture.categorized_diff(before_reservation, after_reservation),
        )

        self.fixture.contact_implementer(self.implementer)
        before_implementation = self.fixture.snapshot()
        self.fixture.implement()
        after_implementation = self.fixture.snapshot()
        self.fixture.accept_implementer_diff(
            self.implementer, before_implementation, after_implementation
        )
        self.assertIn(
            "implementer report accepted:direct-implementer", self.fixture.events
        )

        before_testing_transition = self.fixture.snapshot()
        self.fixture.begin_testing()
        before_testing = self.fixture.snapshot()
        self.assertEqual(
            {
                "production": set(),
                "tests": set(),
                "orchestration": {"implementation/state.json"},
            },
            self.fixture.categorized_diff(
                before_testing_transition, before_testing
            ),
        )
        tester_after = self.fixture.snapshot()
        self.fixture.accept_tester(self.tester, before_testing, tester_after)
        self.assertEqual(
            {"production": set(), "tests": set(), "orchestration": set()},
            self.fixture.categorized_diff(before_testing, tester_after),
        )
        self.assertEqual(
            {
                "production": set(),
                "tests": set(),
                "orchestration": {"implementation/state.json"},
            },
            self.fixture.categorized_diff(tester_after, self.fixture.snapshot()),
        )

        before_pass = self.fixture.snapshot()
        self.fixture.accept_pass()
        after_pass = self.fixture.snapshot()
        self.assertEqual(
            {
                "production": set(),
                "tests": set(),
                "orchestration": {"implementation/state.json"},
            },
            self.fixture.categorized_diff(before_pass, after_pass),
        )
        self.assertEqual(1, self.fixture.advance_count)
        self.assertEqual("passed", self.fixture.tasks["task-target"]["status"])
        self.assertIsNone(self.fixture.current_task)
        with self.assertRaisesRegex(AssertionError, "exactly once"):
            self.fixture.accept_pass()

    def test_implementer_cannot_mutate_orchestration_state(self):
        self.fixture.reserve(self.fixture.dependency_ready_selection())
        self.fixture.contact_implementer(self.implementer)
        before = self.fixture.snapshot()
        self.fixture.state.write_text("unauthorized\n", encoding="utf-8")

        with self.assertRaisesRegex(AssertionError, "implementer mutation"):
            self.fixture.accept_implementer_diff(
                self.implementer, before, self.fixture.snapshot()
            )

    def test_corrupted_persisted_reservation_prevents_contact(self):
        expected = SuccessfulExecutionFixture._expected_reservation_state()
        corruptions: list[tuple[str, dict[str, object]]] = []

        for root_key in expected:
            corrupted = json.loads(json.dumps(expected))
            corrupted.pop(root_key)
            corruptions.append((f"missing-root-{root_key}", corrupted))

        corrupted = json.loads(json.dumps(expected))
        corrupted["unexpected_root"] = "not allowed"
        corruptions.append(("extra-root", corrupted))

        root_values = {
            "current_task": None,
            "advance_count": 1,
            "contacted_implementer_id": "stale-contact",
            "accepted_implementer_id": "stale-acceptance",
            "accepted_tester_id": "stale-tester",
        }
        for root_key, value in root_values.items():
            corrupted = json.loads(json.dumps(expected))
            corrupted[root_key] = value
            corruptions.append((f"corrupt-root-{root_key}", corrupted))

        tasks = expected["tasks"]
        assert isinstance(tasks, dict)
        for task_id, task in tasks.items():
            assert isinstance(task, dict)
            corrupted = json.loads(json.dumps(expected))
            corrupted["tasks"].pop(task_id)
            corruptions.append((f"missing-task-{task_id}", corrupted))

            corrupted = json.loads(json.dumps(expected))
            corrupted["tasks"][task_id]["unexpected_field"] = True
            corruptions.append((f"extra-field-{task_id}", corrupted))

            for field in task:
                corrupted = json.loads(json.dumps(expected))
                corrupted["tasks"][task_id].pop(field)
                corruptions.append((f"missing-{task_id}-{field}", corrupted))

            field_values = {
                "status": "testing" if task_id == "task-target" else "implementing",
                "tester_verdict": "fail",
                "dependencies": ["stale-dependency"],
                "cycles_used": task["cycles_used"] + 1,
            }
            for field, value in field_values.items():
                corrupted = json.loads(json.dumps(expected))
                corrupted["tasks"][task_id][field] = value
                corruptions.append((f"corrupt-{task_id}-{field}", corrupted))

        corrupted = json.loads(json.dumps(expected))
        corrupted["tasks"]["task-extra"] = {
            "status": "pending",
            "tester_verdict": "none",
            "dependencies": [],
            "cycles_used": 0,
        }
        corruptions.append(("extra-task", corrupted))

        for index, (label, persisted) in enumerate(corruptions):
            with self.subTest(corruption=label):
                fixture = SuccessfulExecutionFixture(
                    Path(self.temp.name) / f"corruption-{index}"
                )
                fixture.reserve(fixture.dependency_ready_selection())
                fixture.state.write_text(
                    json.dumps(persisted, sort_keys=True) + "\n", encoding="utf-8"
                )
                before = fixture.snapshot()

                with self.assertRaisesRegex(AssertionError, "complete reservation"):
                    fixture.contact_implementer(self.implementer)
                self.assertEqual(before, fixture.snapshot())
                self.assertIsNone(fixture.contacted_implementer_id)
                self.assertIsNone(fixture._contacted_implementer_receipt)
                self.assertEqual(["reservation persisted"], fixture.events)

    def test_corrupted_in_memory_reservation_prevents_contact(self):
        corruptions = (
            ("advance", lambda fixture: setattr(fixture, "advance_count", 1)),
            (
                "dependency",
                lambda fixture: fixture.tasks["task-target"].update(
                    dependencies=["task-later"]
                ),
            ),
            (
                "additional-active",
                lambda fixture: fixture.tasks["task-later"].update(
                    status="implementing"
                ),
            ),
            (
                "extra-task",
                lambda fixture: fixture.tasks.update(
                    {
                        "task-extra": {
                            "status": "pending",
                            "tester_verdict": "none",
                            "dependencies": [],
                            "cycles_used": 0,
                        }
                    }
                ),
            ),
        )
        for index, (label, corrupt) in enumerate(corruptions):
            with self.subTest(corruption=label):
                fixture = SuccessfulExecutionFixture(
                    Path(self.temp.name) / f"memory-corruption-{index}"
                )
                fixture.reserve(fixture.dependency_ready_selection())
                before = fixture.snapshot()
                corrupt(fixture)

                with self.assertRaisesRegex(AssertionError, "complete reservation"):
                    fixture.contact_implementer(self.implementer)
                self.assertEqual(before, fixture.snapshot())
                self.assertIsNone(fixture.contacted_implementer_id)
                self.assertIsNone(fixture._contacted_implementer_receipt)

    def test_type_confused_reservation_fields_prevent_contact(self):
        expected = SuccessfulExecutionFixture._expected_reservation_state()
        corruptions: list[tuple[str, dict[str, object], object | None]] = []

        root_values = {
            "current_task": True,
            "tasks": [],
            "advance_count": False,
            "contacted_implementer_id": False,
            "accepted_implementer_id": 0,
            "accepted_tester_id": [],
        }
        for root_key, value in root_values.items():
            corrupted = json.loads(json.dumps(expected))
            corrupted[root_key] = value
            in_memory_value = value if root_key == "advance_count" else None
            corruptions.append(
                (f"root-{root_key}", corrupted, in_memory_value)
            )

        tasks = expected["tasks"]
        assert isinstance(tasks, dict)
        for task_id in tasks:
            for field, value in (
                ("status", True),
                ("tester_verdict", False),
                ("dependencies", "task-dependency"),
                ("dependencies", [True]),
                ("cycles_used", True),
                ("cycles_used", "1"),
            ):
                corrupted = json.loads(json.dumps(expected))
                corrupted["tasks"][task_id][field] = value
                corruptions.append(
                    (f"{task_id}-{field}-{type(value).__name__}", corrupted, None)
                )

        for index, (label, persisted, in_memory_advance) in enumerate(corruptions):
            with self.subTest(corruption=label):
                fixture = SuccessfulExecutionFixture(
                    Path(self.temp.name) / f"type-confusion-{index}"
                )
                fixture.reserve(fixture.dependency_ready_selection())
                fixture.state.write_text(
                    json.dumps(persisted, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                if in_memory_advance is not None:
                    fixture.advance_count = in_memory_advance
                before = fixture.snapshot()

                with self.assertRaisesRegex(AssertionError, "complete reservation"):
                    fixture.contact_implementer(self.implementer)
                self.assertEqual(before, fixture.snapshot())
                self.assertIsNone(fixture.contacted_implementer_id)
                self.assertIsNone(fixture._contacted_implementer_anchor)

    def test_contact_persists_nonempty_identity_only_after_validation(self):
        class StringSubclass(str):
            pass

        invalid_reports = (
            RoleReport("", True, False, "ready-for-test"),
            RoleReport("   ", True, False, "ready-for-test"),
            RoleReport("delegated", True, True, "ready-for-test"),
            RoleReport("indirect", False, False, "ready-for-test"),
            RoleReport(1, True, False, "ready-for-test"),
            RoleReport(True, True, False, "ready-for-test"),
            RoleReport(StringSubclass("subclass"), True, False, "ready-for-test"),
            RoleReport("integer-direct", 1, False, "ready-for-test"),
            RoleReport("integer-delegated", True, 0, "ready-for-test"),
        )
        for index, report in enumerate(invalid_reports):
            with self.subTest(report=report):
                fixture = SuccessfulExecutionFixture(
                    Path(self.temp.name) / f"invalid-contact-{index}"
                )
                fixture.reserve(fixture.dependency_ready_selection())
                before = fixture.snapshot()

                with self.assertRaisesRegex(AssertionError, "direct and non-delegating"):
                    fixture.contact_implementer(report)
                self.assertEqual(before, fixture.snapshot())
                self.assertIsNone(fixture.contacted_implementer_id)

        self.fixture.reserve(self.fixture.dependency_ready_selection())
        before = self.fixture.snapshot()
        self.fixture.contact_implementer(self.implementer)
        persisted = json.loads(self.fixture.state.read_text(encoding="utf-8"))
        self.assertNotEqual(before, self.fixture.snapshot())
        self.assertEqual(self.implementer.role_id, self.fixture.contacted_implementer_id)
        self.assertEqual(
            self.implementer.role_id, persisted["contacted_implementer_id"]
        )
        self.assertIsNone(persisted["accepted_implementer_id"])
        self.assertEqual(
            self.implementer.role_id,
            self.fixture._contacted_implementer_anchor,
        )

    def test_accepted_report_rejects_type_confused_role_fields(self):
        class StringSubclass(str):
            pass

        reports = (
            RoleReport(
                StringSubclass(self.implementer.role_id),
                True,
                False,
                "ready-for-test",
            ),
            RoleReport(self.implementer.role_id, 1, False, "ready-for-test"),
            RoleReport(self.implementer.role_id, True, 0, "ready-for-test"),
        )
        for index, report in enumerate(reports):
            with self.subTest(report=report):
                fixture = SuccessfulExecutionFixture(
                    Path(self.temp.name) / f"type-confused-report-{index}"
                )
                fixture.reserve(fixture.dependency_ready_selection())
                fixture.contact_implementer(self.implementer)
                before = fixture.snapshot()
                fixture.implement()
                after = fixture.snapshot()

                with self.assertRaisesRegex(
                    AssertionError, "identity must match contacted"
                ):
                    fixture.accept_implementer_diff(report, before, after)
                self.assertEqual(after, fixture.snapshot())
                self.assertIsNone(fixture.accepted_implementer_id)

    def test_implementer_unknown_path_invalidates_handoff(self):
        self.fixture.reserve(self.fixture.dependency_ready_selection())
        self.fixture.contact_implementer(self.implementer)
        before = self.fixture.snapshot()
        self.fixture.implement()
        unknown = self.fixture.root / "unexpected.txt"
        unknown.write_text("out of scope\n", encoding="utf-8")

        with self.assertRaisesRegex(AssertionError, "outside the exact allowance"):
            self.fixture.accept_implementer_diff(
                self.implementer, before, self.fixture.snapshot()
            )

    def test_deleted_allowed_file_invalidates_implementer_handoff(self):
        self.fixture.reserve(self.fixture.dependency_ready_selection())
        self.fixture.contact_implementer(self.implementer)
        before = self.fixture.snapshot()
        self.fixture.implement()
        self.fixture.product.unlink()

        with self.assertRaisesRegex(AssertionError, "must remain present"):
            self.fixture.accept_implementer_diff(
                self.implementer, before, self.fixture.snapshot()
            )

    def test_event_string_substitution_cannot_authorize_implementation_report(self):
        self.fixture.reserve(self.fixture.dependency_ready_selection())
        self.fixture.events.append(
            f"implementer contacted:{self.implementer.role_id}"
        )
        before = self.fixture.snapshot()
        self.fixture.implement()
        after = self.fixture.snapshot()

        with self.assertRaisesRegex(AssertionError, "identity must match contacted"):
            self.fixture.accept_implementer_diff(self.implementer, before, after)
        self.assertIsNone(self.fixture.accepted_implementer_id)
        with self.assertRaisesRegex(AssertionError, "accepted implementer report"):
            self.fixture.begin_testing()

    def test_report_identity_must_match_contacted_implementer(self):
        self.fixture.reserve(self.fixture.dependency_ready_selection())
        self.fixture.contact_implementer(self.implementer)
        before = self.fixture.snapshot()
        self.fixture.implement()
        after = self.fixture.snapshot()
        substituted_report = RoleReport(
            role_id="substituted-implementer",
            direct=True,
            delegated=False,
            status="ready-for-test",
        )

        with self.assertRaisesRegex(AssertionError, "identity must match contacted"):
            self.fixture.accept_implementer_diff(substituted_report, before, after)
        self.assertEqual(after, self.fixture.snapshot())
        self.assertIsNone(self.fixture.accepted_implementer_id)

    def test_contacted_identity_substitution_cannot_authorize_testing(self):
        substitutions = ("persisted", "memory", "memory-and-persisted")
        for index, substitution in enumerate(substitutions):
            with self.subTest(substitution=substitution):
                fixture = SuccessfulExecutionFixture(
                    Path(self.temp.name) / f"contact-substitution-{index}"
                )
                fixture.reserve(fixture.dependency_ready_selection())
                fixture.contact_implementer(self.implementer)
                persisted = json.loads(fixture.state.read_text(encoding="utf-8"))
                if substitution in {"persisted", "memory-and-persisted"}:
                    persisted["contacted_implementer_id"] = "substituted-implementer"
                    fixture.state.write_text(
                        json.dumps(persisted, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )
                if substitution in {"memory", "memory-and-persisted"}:
                    fixture.contacted_implementer_id = "substituted-implementer"

                report = RoleReport(
                    role_id=(
                        "substituted-implementer"
                        if substitution != "persisted"
                        else self.implementer.role_id
                    ),
                    direct=True,
                    delegated=False,
                    status="ready-for-test",
                )
                before = fixture.snapshot()
                fixture.implement()

                with self.assertRaisesRegex(
                    AssertionError, "identity must match contacted"
                ):
                    fixture.accept_implementer_diff(
                        report, before, fixture.snapshot()
                    )
                self.assertIsNone(fixture.accepted_implementer_id)
                with self.assertRaisesRegex(
                    AssertionError, "accepted implementer report"
                ):
                    fixture.begin_testing()

    def test_coordinated_identity_and_receipt_replacement_cannot_reanchor_contact(self):
        self.fixture.reserve(self.fixture.dependency_ready_selection())
        self.fixture.contact_implementer(self.implementer)
        with self.assertRaisesRegex(AttributeError, "write-once"):
            self.fixture._contacted_implementer_anchor = "substituted-implementer"

        self.fixture.contacted_implementer_id = "substituted-implementer"
        self.fixture._contacted_implementer_receipt = ("substituted-implementer",)
        persisted = json.loads(self.fixture.state.read_text(encoding="utf-8"))
        persisted["contacted_implementer_id"] = "substituted-implementer"
        self.fixture.state.write_text(
            json.dumps(persisted, sort_keys=True) + "\n", encoding="utf-8"
        )
        substituted_report = RoleReport(
            role_id="substituted-implementer",
            direct=True,
            delegated=False,
            status="ready-for-test",
        )
        before = self.fixture.snapshot()
        self.fixture.implement()

        with self.assertRaisesRegex(AssertionError, "identity must match contacted"):
            self.fixture.accept_implementer_diff(
                substituted_report, before, self.fixture.snapshot()
            )
        self.assertIsNone(self.fixture.accepted_implementer_id)

    def test_coordinated_identity_replacement_cannot_begin_testing(self):
        self.fixture.reserve(self.fixture.dependency_ready_selection())
        self.fixture.contact_implementer(self.implementer)
        before = self.fixture.snapshot()
        self.fixture.implement()
        self.fixture.accept_implementer_diff(
            self.implementer, before, self.fixture.snapshot()
        )

        substituted = "substituted-implementer"
        self.fixture.contacted_implementer_id = substituted
        self.fixture.accepted_implementer_id = substituted
        self.fixture._contacted_implementer_receipt = (substituted,)
        persisted = json.loads(self.fixture.state.read_text(encoding="utf-8"))
        persisted["contacted_implementer_id"] = substituted
        persisted["accepted_implementer_id"] = substituted
        self.fixture.state.write_text(
            json.dumps(persisted, sort_keys=True) + "\n", encoding="utf-8"
        )
        before_testing = self.fixture.snapshot()

        with self.assertRaisesRegex(AssertionError, "not coherent"):
            self.fixture.begin_testing()
        self.assertEqual(before_testing, self.fixture.snapshot())
        self.assertEqual("implementing", self.fixture.tasks["task-target"]["status"])

    def test_external_contact_binding_rejects_all_instance_reanchoring_paths(self):
        substituted = "substituted-implementer"
        tamper_paths = (
            "delete-and-recreate",
            "object-setattr",
            "direct-dict",
            "mirrors-only",
            "shallow-copy",
        )
        for index, tamper_path in enumerate(tamper_paths):
            with self.subTest(tamper_path=tamper_path):
                original = SuccessfulExecutionFixture(
                    Path(self.temp.name) / f"external-binding-{index}"
                )
                original.reserve(original.dependency_ready_selection())
                original.contact_implementer(self.implementer)
                fixture = copy.copy(original) if tamper_path == "shallow-copy" else original

                if tamper_path == "delete-and-recreate":
                    del fixture._contacted_implementer_anchor
                    fixture._contacted_implementer_anchor = substituted
                elif tamper_path == "object-setattr":
                    object.__setattr__(
                        fixture, "_contacted_implementer_anchor", substituted
                    )
                elif tamper_path in {"direct-dict", "shallow-copy"}:
                    fixture.__dict__["_contacted_implementer_anchor"] = substituted

                fixture.contacted_implementer_id = substituted
                fixture._contacted_implementer_receipt = (substituted,)
                persisted = json.loads(fixture.state.read_text(encoding="utf-8"))
                persisted["contacted_implementer_id"] = substituted
                fixture.state.write_text(
                    json.dumps(persisted, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                substituted_report = RoleReport(
                    role_id=substituted,
                    direct=True,
                    delegated=False,
                    status="ready-for-test",
                )
                before = fixture.snapshot()
                fixture.implement()

                with self.assertRaisesRegex(
                    AssertionError, "identity must match contacted"
                ):
                    fixture.accept_implementer_diff(
                        substituted_report, before, fixture.snapshot()
                    )
                self.assertIsNone(fixture.accepted_implementer_id)

                fixture.accepted_implementer_id = substituted
                persisted = json.loads(fixture.state.read_text(encoding="utf-8"))
                persisted["accepted_implementer_id"] = substituted
                fixture.state.write_text(
                    json.dumps(persisted, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                before_testing = fixture.snapshot()
                with self.assertRaisesRegex(AssertionError, "not coherent"):
                    fixture.begin_testing()
                self.assertEqual(before_testing, fixture.snapshot())
                self.assertEqual(
                    "implementing", fixture.tasks["task-target"]["status"]
                )

                if tamper_path == "shallow-copy":
                    self.assertNotIn(fixture, _CONTACTED_IMPLEMENTER_BINDINGS)
                self.assertEqual(
                    self.implementer.role_id,
                    _CONTACTED_IMPLEMENTER_BINDINGS.get(original),
                )

    def test_external_contact_binding_is_lifecycle_safe(self):
        initial_bindings = len(_CONTACTED_IMPLEMENTER_BINDINGS)
        fixture = SuccessfulExecutionFixture(
            Path(self.temp.name) / "lifecycle-binding"
        )
        fixture.reserve(fixture.dependency_ready_selection())
        fixture.contact_implementer(self.implementer)
        fixture_reference = weakref.ref(fixture)
        self.assertEqual(initial_bindings + 1, len(_CONTACTED_IMPLEMENTER_BINDINGS))

        del fixture
        gc.collect()

        self.assertIsNone(fixture_reference())
        self.assertEqual(initial_bindings, len(_CONTACTED_IMPLEMENTER_BINDINGS))

    def test_shallow_copy_of_accepted_handoff_cannot_begin_testing(self):
        self.fixture.reserve(self.fixture.dependency_ready_selection())
        self.fixture.contact_implementer(self.implementer)
        before = self.fixture.snapshot()
        self.fixture.implement()
        self.fixture.accept_implementer_diff(
            self.implementer, before, self.fixture.snapshot()
        )
        copied_fixture = copy.copy(self.fixture)
        self.assertNotIn(copied_fixture, _CONTACTED_IMPLEMENTER_BINDINGS)
        before_testing = copied_fixture.snapshot()

        with self.assertRaisesRegex(AssertionError, "not coherent"):
            copied_fixture.begin_testing()
        self.assertEqual(before_testing, copied_fixture.snapshot())
        self.assertEqual(
            "implementing", copied_fixture.tasks["task-target"]["status"]
        )

    def test_accepted_report_persists_exact_contacted_identity(self):
        self.fixture.reserve(self.fixture.dependency_ready_selection())
        self.fixture.contact_implementer(self.implementer)
        before = self.fixture.snapshot()
        self.fixture.implement()
        self.fixture.accept_implementer_diff(
            self.implementer, before, self.fixture.snapshot()
        )
        persisted = json.loads(self.fixture.state.read_text(encoding="utf-8"))

        self.assertEqual(
            self.implementer.role_id,
            self.fixture.contacted_implementer_id,
        )
        self.assertEqual(
            self.fixture.contacted_implementer_id,
            self.fixture.accepted_implementer_id,
        )
        self.assertEqual(
            self.fixture.contacted_implementer_id,
            persisted["contacted_implementer_id"],
        )
        self.assertEqual(
            self.fixture.contacted_implementer_id,
            persisted["accepted_implementer_id"],
        )
        self.fixture.events[:] = ["implementer contacted:substituted-event"]
        self.fixture.begin_testing()
        self.assertEqual("testing", self.fixture.tasks["task-target"]["status"])

    def test_reservation_rejects_existing_active_tasks_without_persisting(self):
        before = self.fixture.snapshot()
        self.fixture.tasks["task-dependency"]["status"] = "implementing"
        self.fixture.tasks["task-later"]["status"] = "testing"
        self.fixture.current_task = "task-dependency"

        with self.assertRaisesRegex(AssertionError, "active task already exists"):
            self.fixture.reserve("task-target")

        self.assertEqual(before, self.fixture.snapshot())
        self.assertEqual(0, self.fixture.tasks["task-target"]["cycles_used"])
        self.assertEqual("pending", self.fixture.tasks["task-target"]["status"])

    def test_pass_requires_an_accepted_tester_handoff(self):
        self.fixture.reserve(self.fixture.dependency_ready_selection())
        self.fixture.contact_implementer(self.implementer)
        before_implementation = self.fixture.snapshot()
        self.fixture.implement()
        self.fixture.accept_implementer_diff(
            self.implementer, before_implementation, self.fixture.snapshot()
        )
        self.fixture.begin_testing()
        before_pass = self.fixture.snapshot()

        with self.assertRaisesRegex(AssertionError, "accepted tester handoff"):
            self.fixture.accept_pass()

        self.assertEqual(before_pass, self.fixture.snapshot())
        self.assertEqual(0, self.fixture.advance_count)

    def test_testing_and_pass_require_an_accepted_implementer_report(self):
        self.fixture.reserve(self.fixture.dependency_ready_selection())
        self.fixture.contact_implementer(self.implementer)
        self.fixture.implement()
        before = self.fixture.snapshot()

        with self.assertRaisesRegex(AssertionError, "implementer report"):
            self.fixture.begin_testing()
        self.assertEqual(before, self.fixture.snapshot())

        self.fixture.tasks["task-target"]["status"] = "testing"
        with self.assertRaisesRegex(AssertionError, "implementer handoff"):
            self.fixture.accept_pass()

    def test_actual_implementer_cannot_be_substituted_as_tester(self):
        self.prepare_testing()
        actual_implementer_as_tester = RoleReport(
            role_id=self.implementer.role_id,
            direct=True,
            delegated=False,
            status="pass",
            checked_criteria=CRITERIA,
        )
        before = self.fixture.snapshot()

        with self.assertRaisesRegex(AssertionError, "differ from implementer"):
            self.fixture.accept_tester(
                actual_implementer_as_tester, before, self.fixture.snapshot()
            )

    def test_implementer_and_tester_handoffs_are_accepted_once(self):
        self.fixture.reserve(self.fixture.dependency_ready_selection())
        self.fixture.contact_implementer(self.implementer)
        before = self.fixture.snapshot()
        self.fixture.implement()
        after = self.fixture.snapshot()
        self.fixture.accept_implementer_diff(self.implementer, before, after)
        with self.assertRaisesRegex(AssertionError, "exactly once"):
            self.fixture.accept_implementer_diff(self.implementer, before, after)

        self.fixture.begin_testing()
        before_tester = self.fixture.snapshot()
        self.fixture.accept_tester(
            self.tester, before_tester, self.fixture.snapshot()
        )
        with self.assertRaisesRegex(AssertionError, "exactly once"):
            self.fixture.accept_tester(
                self.tester, before_tester, before_tester
            )

    def test_post_review_file_mutation_prevents_pass(self):
        mutations = ("product", "test", "orchestration")
        for index, mutation in enumerate(mutations):
            with self.subTest(mutation=mutation):
                self.fixture = SuccessfulExecutionFixture(
                    Path(self.temp.name) / f"post-review-{index}"
                )
                self.complete_review()
                if mutation == "product":
                    self.fixture.product.write_text("CHANGED = True\n", encoding="utf-8")
                elif mutation == "test":
                    self.fixture.test.write_text("CHANGED = True\n", encoding="utf-8")
                else:
                    self.fixture.state.write_text("corrupted\n", encoding="utf-8")

                with self.assertRaisesRegex(AssertionError, "changed after tester"):
                    self.fixture.accept_pass()

    def test_corrupted_persisted_pass_state_rejects_even_with_matching_snapshot(self):
        corruptions = (
            ("current_task", None),
            ("status", "pending"),
            ("cycles_used", 2),
            ("tester_verdict", "fail"),
            ("advance_count", 1),
            ("accepted_implementer_id", "other"),
            ("accepted_tester_id", "other"),
        )
        for index, (field, value) in enumerate(corruptions):
            with self.subTest(field=field):
                self.fixture = SuccessfulExecutionFixture(
                    Path(self.temp.name) / f"persisted-pass-{index}"
                )
                self.complete_review()
                persisted = json.loads(
                    self.fixture.state.read_text(encoding="utf-8")
                )
                if field in {"status", "cycles_used", "tester_verdict"}:
                    persisted["tasks"]["task-target"][field] = value
                else:
                    persisted[field] = value
                self.fixture.state.write_text(
                    json.dumps(persisted, sort_keys=True) + "\n", encoding="utf-8"
                )
                self.fixture.reviewed_snapshot = tuple(
                    sorted(self.fixture.snapshot().items())
                )

                with self.assertRaisesRegex(AssertionError, "not coherent"):
                    self.fixture.accept_pass()

    def test_altered_in_memory_pass_state_is_rejected(self):
        corruptions = (
            ("current_task", None),
            ("status", "pending"),
            ("cycles_used", 2),
            ("tester_verdict", "fail"),
            ("advance_count", 1),
        )
        for index, (field, value) in enumerate(corruptions):
            with self.subTest(field=field):
                self.fixture = SuccessfulExecutionFixture(
                    Path(self.temp.name) / f"memory-pass-{index}"
                )
                self.complete_review()
                if field in {"status", "cycles_used", "tester_verdict"}:
                    self.fixture.tasks["task-target"][field] = value
                else:
                    setattr(self.fixture, field, value)

                with self.assertRaisesRegex(AssertionError, "not coherent"):
                    self.fixture.accept_pass()

    def test_tester_must_be_independent_complete_and_non_mutating(self):
        self.prepare_testing()
        before = self.fixture.snapshot()

        bad_reports = (
            RoleReport(
                role_id="direct-implementer",
                direct=True,
                delegated=False,
                status="pass",
                checked_criteria=CRITERIA,
            ),
            RoleReport(
                role_id="independent-tester",
                direct=True,
                delegated=True,
                status="pass",
                checked_criteria=CRITERIA,
            ),
            RoleReport(
                role_id="independent-tester",
                direct=True,
                delegated=False,
                status="pass",
                checked_criteria=CRITERIA[:-1],
            ),
            RoleReport(
                role_id="independent-tester",
                direct=True,
                delegated=False,
                status="pass",
                checked_criteria=CRITERIA + (CRITERIA[-1],),
            ),
        )
        for report in bad_reports:
            with self.subTest(report=report):
                with self.assertRaises(AssertionError):
                    self.fixture.accept_tester(report, before, self.fixture.snapshot())

        self.fixture.product.write_text("ENABLED = 'tester edit'\n", encoding="utf-8")
        with self.assertRaisesRegex(AssertionError, "tester mutation"):
            self.fixture.accept_tester(self.tester, before, self.fixture.snapshot())


if __name__ == "__main__":
    unittest.main()
