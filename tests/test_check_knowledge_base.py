"""test_check_knowledge_base 自动化测试。"""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from scripts.check_knowledge_base import Issue, validate


class KnowledgeBaseValidationTests(unittest.TestCase):
    """验证 KnowledgeBaseValidationTests 相关行为。"""

    def setUp(self) -> None:
        """初始化当前测试所需的隔离环境。"""

        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "doc-context-atlas-template"
        self.root.mkdir()

    def tearDown(self) -> None:
        """清理当前测试创建的隔离资源。"""

        self.tmp.cleanup()

    def write(self, relative: str, text: str) -> Path:
        """提供 write 测试辅助行为。"""

        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def metadata(self, relative: str, **fields: object) -> Path:
        """提供 metadata 测试辅助行为。"""

        lines = ["---"]
        for key, value in fields.items():
            if isinstance(value, list):
                lines.append(f"{key}: [{', '.join(str(item) for item in value)}]")
            else:
                lines.append(f"{key}: {value}")
        lines.extend(["---", "# Document", ""])
        return self.write(relative, "\n".join(lines))

    def valid_feature(self, *, status: str = "baselined", acceptance: list[str] | None = None) -> None:
        """提供 valid_feature 测试辅助行为。"""

        self.metadata(
            "01-功能基线/F01.md",
            id="F01", type="feature", title="Feature", status=status,
            phase="mvp", priority="P0", current_slice="included",
            depends_on=[], acceptance=acceptance or ["F01-AC-01"], adr=[],
            last_updated="2026-08-07",
        )

    def valid_current(self) -> None:
        """提供 valid_current 测试辅助行为。"""

        self.write("03-变更与证据/CURRENT.md", "# 当前任务\n\n- 当前任务：无可执行开发任务\n")

    def matrix(self, rows: str) -> None:
        """提供 matrix 测试辅助行为。"""

        self.write(
            "03-变更与证据/验收矩阵.md",
            "| 验收编号 | 对象 | 条件摘要 | 结果 | 证据位置 | 对应版本 |\n"
            "| --- | --- | --- | --- | --- | --- |\n" + rows,
        )

    def codes(self, issues: list[Issue]) -> set[str]:
        """提供 codes 测试辅助行为。"""

        return {issue.code for issue in issues}

    def test_rejects_invalid_metadata_and_duplicate_ids(self) -> None:
        """验证 rejects_invalid_metadata_and_duplicate_ids 场景。"""

        self.metadata("01-功能基线/F01.md", id="F01", type="feature", status="wrong")
        self.metadata("01-功能基线/F01-copy.md", id="F01", type="feature", status="wrong")

        codes = self.codes(validate(self.root))

        self.assertIn("KB_ID_DUPLICATE", codes)
        self.assertIn("KB_SCHEMA_REQUIRED", codes)

    def test_rejects_empty_or_duplicate_acceptance(self) -> None:
        """验证 rejects_empty_or_duplicate_acceptance 场景。"""

        self.valid_feature(acceptance=[])
        self.metadata(
            "03-变更与证据/任务包/TASK-F01-001.md", id="TASK-F01-001", type="task",
            title="Task", feature="F01", status="ready",
            acceptance=["F01-AC-01", "F01-AC-01"], last_updated="2026-08-07",
        )
        self.valid_current()

        codes = self.codes(validate(self.root))

        self.assertIn("KB_SCHEMA_LIST", codes)

    def test_rejects_illegal_acceptance_result_and_passed_without_evidence(self) -> None:
        """验证 rejects_illegal_acceptance_result_and_passed_without_evidence 场景。"""

        self.valid_feature()
        self.valid_current()
        self.matrix("| F01-AC-01 | Feature | condition | failed | — | — |\n")

        self.assertIn("KB_ACCEPTANCE_RESULT", self.codes(validate(self.root)))

        self.matrix("| F01-AC-01 | Feature | condition | passed | — | — |\n")
        self.assertIn("KB_ACCEPTANCE_EVIDENCE", self.codes(validate(self.root)))

    def test_rejects_missing_or_duplicate_matrix_rows(self) -> None:
        """验证 rejects_missing_or_duplicate_matrix_rows 场景。"""

        self.valid_feature(acceptance=["F01-AC-01", "F01-AC-02"])
        self.valid_current()
        self.matrix("| F01-AC-01 | Feature | condition | not_started | — | — |\n| F01-AC-01 | Feature | duplicate | not_started | — | — |\n")

        codes = self.codes(validate(self.root))

        self.assertIn("KB_MATRIX_IDS", codes)
        self.assertIn("KB_MATRIX_DUPLICATE", codes)

    def test_current_is_optional_and_does_not_control_task_execution(self) -> None:
        """验证 current_is_optional_and_does_not_control_task_execution 场景。"""

        self.valid_feature()
        self.matrix("| F01-AC-01 | Feature | condition | not_started | — | — |\n")
        self.assertNotIn("KB_CURRENT_REQUIRED", self.codes(validate(self.root)))

        self.valid_current()
        self.write(
            "03-变更与证据/CURRENT.md",
            "- 当前任务：无可执行开发任务\n- 任务包：[task](./任务包/TASK-F01-001.md)\n",
        )
        self.assertNotIn("KB_CURRENT_STATE", self.codes(validate(self.root)))

    def test_rejects_broken_relative_link(self) -> None:
        """验证 rejects_broken_relative_link 场景。"""

        self.valid_current()
        self.write("00-项目总览/README.md", "[missing](./missing.md)\n")

        self.assertIn("KB_LINK_BROKEN", self.codes(validate(self.root)))

    def test_ignores_workspace_excalidraw_documents(self) -> None:
        """验证 ignores_workspace_excalidraw_documents 场景。"""

        self.valid_current()
        self.write("Excalidraw/Drawing.md", "---\nnot valid metadata\n---\n")

        self.assertEqual([], validate(self.root))


if __name__ == "__main__":
    unittest.main()
