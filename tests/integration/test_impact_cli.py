"""验证影响分析命令行的 JSON 输出、只读性和退出码。"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from tests.helpers import TempDirectoryTestCase


ROOT = Path(__file__).resolve().parents[2]


class ImpactCliTests(TempDirectoryTestCase):
    """验证用户可以直接对知识库稳定编号执行影响分析。"""

    def _write_graph(self) -> None:
        """写入一个合法的表与读取模块关系图。"""

        (self.root / "表.md").write_text(
            "---\nid: TABLE-001\ntype: relation_fixture\n---\n# 表\n",
            encoding="utf-8",
        )
        (self.root / "模块.md").write_text(
            "---\nid: MODULE-001\ntype: relation_fixture\n"
            "rel_reads:\n  - \"[[表|TABLE-001]]\"\n---\n# 模块\n",
            encoding="utf-8",
        )

    def _run(self, changed_id: str) -> subprocess.CompletedProcess[str]:
        """运行 JSON 格式影响分析并返回进程结果。"""

        return subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "analyze_knowledge_impact.py"),
                str(self.root),
                "--schema-root",
                str(ROOT / "schemas"),
                "--changed-id",
                changed_id,
                "--change-type",
                "field_removed",
                "--format",
                "json",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    def test_json_analysis_succeeds_without_modifying_knowledge(self) -> None:
        """存在必改影响仍返回成功，因为结果只是人工决策输入。"""

        self._write_graph()
        before = {path.name: path.read_bytes() for path in self.root.glob("*.md")}

        result = self._run("TABLE-001")
        payload = json.loads(result.stdout)
        after = {path.name: path.read_bytes() for path in self.root.glob("*.md")}

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("required", payload["impacts"][0]["level"])
        self.assertEqual(before, after)

    def test_unknown_changed_id_returns_configuration_exit_code(self) -> None:
        """不存在的稳定编号应以退出码二明确提示输入错误。"""

        self._write_graph()

        result = self._run("TABLE-999")

        self.assertEqual(2, result.returncode)
        self.assertIn("TABLE-999", result.stderr)
