from __future__ import annotations

import re
import subprocess
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
WRITE_SPEC_SKILL = REPOSITORY_ROOT / ".agents" / "skills" / "write-spec" / "SKILL.md"
IMPLEMENT_SPEC_SKILL = (
    REPOSITORY_ROOT / ".agents" / "skills" / "implement-spec" / "SKILL.md"
)


class GitFixture:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir()
        subprocess.run(
            ["git", "init", "--quiet", str(self.root)],
            check=True,
            capture_output=True,
            text=True,
        )

    def write(self, relative_path: str, content: str) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def tree(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                path.relative_to(self.root).as_posix()
                for path in self.root.rglob("*")
                if ".git" not in path.relative_to(self.root).parts
            )
        )

    def status(self) -> tuple[str, ...]:
        result = subprocess.run(
            ["git", "status", "--short", "--untracked-files=all"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        return tuple(result.stdout.splitlines())


class PackagingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.write_spec_contract = WRITE_SPEC_SKILL.read_text(encoding="utf-8")
        cls.implement_spec_contract = IMPLEMENT_SPEC_SKILL.read_text(
            encoding="utf-8"
        )

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def fixture(self, name: str) -> GitFixture:
        return GitFixture(Path(self.temp.name) / name)

    def destination_contracts(self) -> tuple[str, str]:
        destination_section = self.write_spec_contract.split(
            "### 1. Establish the request and destination", 1
        )[1].split("### 2. Ground the spec in evidence", 1)[0]
        paths = re.findall(
            r"`(specs/<year>/q<quarter>/<topic>(?:/spec)?\.md)`",
            destination_section,
        )
        self.assertEqual(
            2, len(paths), "write-spec must define exactly two output shapes"
        )
        return paths[0], paths[1]

    @staticmethod
    def concrete_path(template: str, topic: str) -> str:
        return (
            template.replace("<year>", "2026")
            .replace("<quarter>", "3")
            .replace("<topic>", topic)
        )

    def render_synthetic_spec(
        self, fixture: GitFixture, *, topic: str, orchestration_requested: bool
    ) -> Path:
        ordinary, orchestration = self.destination_contracts()
        destination = orchestration if orchestration_requested else ordinary
        return fixture.write(
            self.concrete_path(destination, topic),
            "# Synthetic specification\n",
        )

    def resolve_implement_spec_input(self, candidate: Path) -> Path | None:
        validation_section = self.implement_spec_contract.split(
            "### 1. Validate the input without writing", 1
        )[1].split("### 2. Establish readiness and repository context", 1)[0]
        self.assertIn("basename is exactly `spec.md`", validation_section)
        self.assertIn(
            "Accept only the canonical `<topic>/spec.md` shape", validation_section
        )
        self.assertIn("Reject a flat legacy spec", validation_section)
        if candidate.name != "spec.md":
            return None
        return candidate

    def test_ordinary_write_spec_output_remains_flat_and_creates_no_state(self):
        fixture = self.fixture("ordinary")
        fixture.write("briefs/widget.md", "# Ordinary spec brief\n")
        before_tree = fixture.tree()
        before_status = fixture.status()

        output = self.render_synthetic_spec(
            fixture, topic="widget", orchestration_requested=False
        )

        self.assertEqual(fixture.root / "specs/2026/q3/widget.md", output)
        self.assertTrue(output.is_file())
        self.assertFalse((fixture.root / "specs/2026/q3/widget").exists())
        self.assertFalse(
            any(path.endswith("implementation") for path in fixture.tree())
        )
        self.assertEqual(
            before_tree
            + (
                "specs",
                "specs/2026",
                "specs/2026/q3",
                "specs/2026/q3/widget.md",
            ),
            fixture.tree(),
        )
        self.assertEqual(
            before_status + ("?? specs/2026/q3/widget.md",), fixture.status()
        )

    def test_explicit_orchestration_output_is_only_topic_spec(self):
        fixture = self.fixture("orchestration")
        fixture.write("briefs/widget.md", "# Orchestration-ready spec brief\n")
        before_tree = fixture.tree()
        before_status = fixture.status()

        output = self.render_synthetic_spec(
            fixture, topic="widget", orchestration_requested=True
        )

        self.assertEqual(fixture.root / "specs/2026/q3/widget/spec.md", output)
        self.assertTrue(output.is_file())
        self.assertFalse((fixture.root / "specs/2026/q3/widget.md").exists())
        self.assertFalse((output.parent / "implementation").exists())
        self.assertEqual(
            before_tree
            + (
                "specs",
                "specs/2026",
                "specs/2026/q3",
                "specs/2026/q3/widget",
                "specs/2026/q3/widget/spec.md",
            ),
            fixture.tree(),
        )
        self.assertEqual(
            before_status + ("?? specs/2026/q3/widget/spec.md",), fixture.status()
        )

    def test_flat_legacy_input_is_rejected_without_fixture_mutation(self):
        fixture = self.fixture("legacy")
        legacy = fixture.write("specs/2026/q3/widget.md", "# Legacy flat spec\n")
        before_tree = fixture.tree()
        before_status = fixture.status()

        resolved = self.resolve_implement_spec_input(legacy)

        self.assertIsNone(resolved)
        self.assertEqual(before_tree, fixture.tree())
        self.assertEqual(before_status, fixture.status())
        self.assertEqual("# Legacy flat spec\n", legacy.read_text(encoding="utf-8"))
        self.assertFalse((fixture.root / "specs/2026/q3/widget").exists())

    def test_canonical_input_is_accepted_without_creating_state(self):
        fixture = self.fixture("canonical")
        canonical = fixture.write(
            "specs/2026/q3/widget/spec.md", "# Canonical packaged spec\n"
        )
        before_tree = fixture.tree()
        before_status = fixture.status()

        resolved = self.resolve_implement_spec_input(canonical)

        self.assertEqual(canonical, resolved)
        self.assertEqual(before_tree, fixture.tree())
        self.assertEqual(before_status, fixture.status())
        self.assertFalse((canonical.parent / "implementation").exists())

    def test_unsupported_implement_spec_discovery_symlinks_are_absent(self):
        claude_link = REPOSITORY_ROOT / ".claude/skills/implement-spec"
        github_link = REPOSITORY_ROOT / ".github/skills/implement-spec"
        self.assertFalse(claude_link.exists())
        self.assertFalse(claude_link.is_symlink())
        self.assertFalse(github_link.exists())
        self.assertFalse(github_link.is_symlink())


if __name__ == "__main__":
    unittest.main()
