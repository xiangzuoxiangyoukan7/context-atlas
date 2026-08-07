from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from scripts.check_knowledge_base import Issue, validate


class KnowledgeBaseValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "doc-project-knowledge-base-template"
        self.root.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, relative: str, text: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def metadata(self, relative: str, **fields: object) -> Path:
        lines = ["---"]
        for key, value in fields.items():
            if isinstance(value, list):
                lines.append(f"{key}: [{', '.join(str(item) for item in value)}]")
            else:
                lines.append(f"{key}: {value}")
        lines.extend(["---", "# Document", ""])
        return self.write(relative, "\n".join(lines))

    def valid_feature(self, *, status: str = "baselined", acceptance: list[str] | None = None) -> None:
        self.metadata(
            "01-功能基线/F01.md",
            id="F01", type="feature", title="Feature", status=status,
            phase="mvp", priority="P0", current_slice="included",
            depends_on=[], acceptance=acceptance or ["F01-AC-01"], contracts=[], adr=[],
            last_updated="2026-08-07",
        )

    def valid_current(self) -> None:
        self.write("03-实施与验收/CURRENT.md", "# 当前任务\n\n- 当前任务：无可执行开发任务\n")

    def matrix(self, rows: str) -> None:
        self.write(
            "03-实施与验收/验收矩阵.md",
            "| 验收编号 | 对象 | 条件摘要 | 结果 | 证据位置 | 对应版本 |\n"
            "| --- | --- | --- | --- | --- | --- |\n" + rows,
        )

    def codes(self, issues: list[Issue]) -> set[str]:
        return {issue.code for issue in issues}

    def test_rejects_invalid_metadata_and_duplicate_ids(self) -> None:
        self.metadata("01-功能基线/F01.md", id="F01", type="feature", status="wrong")
        self.metadata("01-功能基线/F01-copy.md", id="F01", type="feature", status="wrong")

        codes = self.codes(validate(self.root))

        self.assertIn("KB001", codes)
        self.assertIn("KB003", codes)

    def test_rejects_empty_or_duplicate_acceptance(self) -> None:
        self.valid_feature(acceptance=[])
        self.metadata(
            "03-实施与验收/任务包/TASK-F01-001.md", id="TASK-F01-001", type="task",
            title="Task", feature="F01", status="ready",
            acceptance=["F01-AC-01", "F01-AC-01"], last_updated="2026-08-07",
        )
        self.valid_current()

        codes = self.codes(validate(self.root))

        self.assertIn("KB003", codes)

    def test_rejects_illegal_acceptance_result_and_passed_without_evidence(self) -> None:
        self.valid_feature()
        self.valid_current()
        self.matrix("| F01-AC-01 | Feature | condition | failed | — | — |\n")

        self.assertIn("KB005", self.codes(validate(self.root)))

        self.matrix("| F01-AC-01 | Feature | condition | passed | — | — |\n")
        self.assertIn("KB007", self.codes(validate(self.root)))

    def test_rejects_missing_or_duplicate_matrix_rows(self) -> None:
        self.valid_feature(acceptance=["F01-AC-01", "F01-AC-02"])
        self.valid_current()
        self.matrix("| F01-AC-01 | Feature | condition | not_started | — | — |\n| F01-AC-01 | Feature | duplicate | not_started | — | — |\n")

        codes = self.codes(validate(self.root))

        self.assertIn("KB004", codes)

    def test_rejects_missing_current_and_mixed_current_states(self) -> None:
        self.valid_feature()
        self.matrix("| F01-AC-01 | Feature | condition | not_started | — | — |\n")
        self.assertIn("KB006", self.codes(validate(self.root)))

        self.valid_current()
        self.write(
            "03-实施与验收/CURRENT.md",
            "- 当前任务：无可执行开发任务\n- 任务包：[task](./任务包/TASK-F01-001.md)\n",
        )
        self.assertIn("KB006", self.codes(validate(self.root)))

    def test_rejects_broken_relative_link(self) -> None:
        self.valid_current()
        self.write("00-项目总览/README.md", "[missing](./missing.md)\n")

        self.assertIn("KB009", self.codes(validate(self.root)))

    def test_rejects_profile_core_override(self) -> None:
        self.valid_current()
        profiles = self.root.parent / "profiles" / "bad"
        profiles.mkdir(parents=True)
        (profiles / "README.md").write_text("profile_id: bad\n允许修改核心 status\n", encoding="utf-8")

        self.assertIn("KB008", self.codes(validate(self.root)))

    def test_ignores_workspace_excalidraw_documents(self) -> None:
        self.valid_current()
        self.write("Excalidraw/Drawing.md", "---\nnot valid metadata\n---\n")

        self.assertEqual([], validate(self.root))


if __name__ == "__main__":
    unittest.main()
