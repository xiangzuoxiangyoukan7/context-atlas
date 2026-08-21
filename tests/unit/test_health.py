"""验证知识库健康检查的只读发现能力。"""

from __future__ import annotations

from datetime import date
from pathlib import Path
import tempfile
import unittest

from scripts.project_kb.health import inspect_health


class HealthTests(unittest.TestCase):
    """确保七类健康问题可定位且检查不修改文件。"""

    def test_health_reports_deterministic_findings_without_writes(self) -> None:
        """重复、断链、陈旧、冲突、来源和权威缺口应进入只读报告。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "knowledge-base.yaml").write_text(
                "protocol_version: 1.0\nauthority:\n  overview: README.md\n",
                encoding="utf-8",
            )
            first = root / "first.md"
            second = root / "second.md"
            first.write_text(
                "---\nid: ITEM-001\ntype: knowledge_item\nstatus: conflicted\n"
                "last_updated: 2020-01-01\nrel_depends_on: [[[missing|ITEM-404]]]\n---\n",
                encoding="utf-8",
            )
            second.write_text(
                "---\nid: ITEM-001\ntype: knowledge_item\nstatus: approved\nlast_updated: 2026-08-22\n---\n",
                encoding="utf-8",
            )
            before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}

            report = inspect_health(root, today=date(2026, 8, 22))

            codes = {finding.code for finding in report.findings}
            self.assertTrue(
                {
                    "KB_HEALTH_DUPLICATE_ID",
                    "KB_HEALTH_DANGLING_RELATION",
                    "KB_HEALTH_STALE",
                    "KB_HEALTH_UNRESOLVED_CONFLICT",
                    "KB_HEALTH_UNVERIFIED_SOURCE",
                    "KB_HEALTH_AUTHORITY_GAP",
                }.issubset(codes)
            )
            self.assertFalse(report.writes_performed)
            self.assertEqual(before, {path: path.read_bytes() for path in root.rglob("*") if path.is_file()})


if __name__ == "__main__":
    unittest.main()
