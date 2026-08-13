"""test_agent_operation 自动化测试。"""

from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

from scripts.project_kb.agent_operation import execute_initialize


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "skills" / "context-atlas" / "assets"


class AgentOperationTests(unittest.TestCase):
    """验证 AgentOperationTests 相关行为。"""

    def test_revision_mismatch_refuses_before_any_write(self) -> None:
        """验证 revision_mismatch_refuses_before_any_write 场景。"""

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            before = set(project.iterdir())

            with self.assertRaises(PermissionError):
                execute_initialize(project, "example", "proposal-2", "proposal-1", ASSETS)

            self.assertEqual(before, set(project.iterdir()))

    def test_existing_target_is_preserved(self) -> None:
        """验证 existing_target_is_preserved 场景。"""

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            target = project / "doc-example"
            target.mkdir()
            sentinel = target / "keep.txt"
            sentinel.write_text("unchanged", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                execute_initialize(project, "example", "proposal-1", "proposal-1", ASSETS)

            self.assertEqual("unchanged", sentinel.read_text(encoding="utf-8"))
            self.assertEqual([sentinel], list(target.iterdir()))

    def test_confirmed_initialize_validates_and_returns_safe_report(self) -> None:
        """验证 confirmed_initialize_validates_and_returns_safe_report 场景。"""

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)

            report = execute_initialize(
                project,
                "example",
                "proposal-1",
                "proposal-1",
                ASSETS,
            )

            self.assertEqual("initialized", report.operation)
            self.assertEqual(project / "doc-example", report.target)
            self.assertTrue(report.target.is_dir())
            self.assertGreater(len(report.changed_files), 10)
            self.assertEqual(0, report.validator_exit_code)
            self.assertEqual((), report.issues)
            self.assertTrue((report.target / ".project-kb" / "schemas").is_dir())
            payload = json.dumps(asdict(report), ensure_ascii=False, default=str)
            for forbidden in ("email", "token", "conversation", "session"):
                self.assertNotIn(forbidden, payload.lower())


if __name__ == "__main__":
    unittest.main()
