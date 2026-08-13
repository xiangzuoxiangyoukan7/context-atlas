"""test_reporting 自动化测试。"""

import json
from pathlib import Path
import unittest

from scripts.project_kb.model import Issue
from scripts.project_kb.reporting import render_json, render_text


class ReportingTests(unittest.TestCase):
    """验证 ReportingTests 相关行为。"""

    def test_json_report_has_stable_machine_contract(self) -> None:
        """验证 json_report_has_stable_machine_contract 场景。"""

        issues = [
            Issue("KB_Z", Path("z.md"), "last"),
            Issue("KB_A", Path("a.md"), "first", "line 2"),
        ]

        payload = json.loads(render_json(issues))

        self.assertEqual(payload["ok"], False)
        self.assertEqual(payload["issue_count"], 2)
        self.assertEqual(
            payload["issues"],
            [
                {
                    "code": "KB_A",
                    "path": "a.md",
                    "message": "first",
                    "location": "line 2",
                },
                {
                    "code": "KB_Z",
                    "path": "z.md",
                    "message": "last",
                    "location": None,
                },
            ],
        )

    def test_text_report_has_stable_success_message(self) -> None:
        """验证 text_report_has_stable_success_message 场景。"""

        self.assertEqual(render_text([]), "Knowledge base validation passed")
