from pathlib import Path
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]


class ExecutionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (SKILL_ROOT / "SKILL.md").read_text()
        cls.roles = (SKILL_ROOT / "references" / "role-contracts.md").read_text()
        cls.state = (SKILL_ROOT / "references" / "state-contract.md").read_text()
        cls.plan = (SKILL_ROOT / "assets" / "plan.md").read_text()
        cls.task = (SKILL_ROOT / "assets" / "task.md").read_text()

    def test_single_planning_boundary_is_explicit(self):
        for document in (self.skill, self.roles, self.state, self.plan):
            normalized = " ".join(document.split())
            self.assertIn("one read-only planning boundary", normalized)
            self.assertIn(
                "initial plan generation or a material amendment", normalized
            )

    def test_semantic_review_rejects_oversized_or_delegating_tasks(self):
        semantic_review = self.skill.split(
            "### 4. Reject semantically unsafe proposals", 1
        )[1].split("### 5. Render canonical state", 1)[0]
        self.assertIn(
            "not explicit and bounded enough for one direct implementer",
            semantic_review,
        )
        self.assertIn("helper, or sub-agent", semantic_review)
        self.assertIn("too broad for one direct implementer", self.roles)

    def test_execution_roles_are_direct_independent_and_non_delegating(self):
        for document in (self.skill, self.roles, self.state, self.plan, self.task):
            self.assertIn("direct implementer", document)
            self.assertIn("independent direct tester", document)
            self.assertIn("planner, helper, or sub-agent", document)

        implementer = self.roles.split("## Implementer", 1)[1].split("## Tester", 1)[0]
        tester = self.roles.split("## Tester", 1)[1].split(
            "## Human handoff contract", 1
        )[0]
        self.assertIn("must not spawn or delegate", implementer)
        self.assertIn("must not spawn or delegate", tester)

    def test_task_template_supplies_direct_role_detail(self):
        self.assertIn("## Execution Roles", self.task)
        self.assertIn("exact allowed files, code, tests, and behavior", self.task)
        self.assertIn("exact focused command or inspection", self.task)
        self.assertIn("task-local planning pass", self.task)

    def test_forward_validation_forbids_nested_orchestrator(self):
        guidance = self.skill.split("## Forward-validation guidance", 1)[1].split(
            "## Approval and amendment boundary", 1
        )[0]
        self.assertIn("disposable local fixtures", guidance)
        self.assertIn("Do not place an orchestrator under an implementer", guidance)
        self.assertIn("Do not use live nested-agent capacity", guidance)


if __name__ == "__main__":
    unittest.main()
