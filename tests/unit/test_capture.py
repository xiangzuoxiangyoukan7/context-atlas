"""验证主动检查点只捕获待确认知识提案并执行去重。"""

from __future__ import annotations

from pathlib import Path

from tests.helpers import TempDirectoryTestCase


class CaptureTests(TempDirectoryTestCase):
    """验证自动捕获不会直接修改需求、接口或数据库正式知识。"""

    def _candidate(self, **overrides: object) -> object:
        """创建测试使用的结构化知识候选。"""

        from scripts.project_kb.capture import CaptureCandidate

        values: dict[str, object] = {
            "checkpoint": "user_decision",
            "summary": "订单状态新增 3=已取消",
            "target_ids": ("TABLE-ORDER", "RULE-ORDER-002"),
            "source_type": "user_statement",
            "source_reference": "当前用户明确决定",
            "differences": ("状态值域新增 3=已取消",),
            "impact_ids": ("FEATURE-ORDER",),
            "unknowns": (),
            "conflicts": (),
            "proposed_by": "PERSON-001",
            "operated_by": "AGENT-CODEX",
            "project_version": "3.4.0",
        }
        values.update(overrides)
        return CaptureCandidate(**values)

    def test_capture_creates_only_proposed_queue_item(self) -> None:
        """检查点捕获只能创建 proposed 提案，不能创建正式目标文件。"""

        from scripts.project_kb.capture import capture_candidate

        report = capture_candidate(
            self.root, self._candidate(), captured_at="2026-08-13T10:30:00+08:00", user_requested=True
        )

        self.assertEqual("created", report.status)
        self.assertTrue(report.path.is_file())
        content = report.path.read_text(encoding="utf-8")
        self.assertIn("status: proposed", content)
        self.assertIn("checkpoint: user_decision", content)
        self.assertIn("proposed_by: PERSON-001", content)
        self.assertIn("operated_by: AGENT-CODEX", content)
        self.assertIn("订单状态新增 3=已取消", content)
        self.assertFalse((self.root / "TABLE-ORDER.md").exists())

    def test_same_target_and_content_is_deduplicated(self) -> None:
        """同一任务中的同目标同内容候选不得重复生成文件。"""

        from scripts.project_kb.capture import capture_candidate

        first = capture_candidate(
            self.root, self._candidate(), captured_at="2026-08-13T10:30:00+08:00", user_requested=True
        )
        second = capture_candidate(
            self.root, self._candidate(), captured_at="2026-08-13T10:31:00+08:00", user_requested=True
        )

        self.assertEqual("duplicate", second.status)
        self.assertEqual(first.path, second.path)
        self.assertEqual(
            1,
            len(list((self.root / "03-变更与证据/待确认知识").glob("PROP-*.md"))),
        )

    def test_supported_checkpoints_are_controlled(self) -> None:
        """八类自然检查点可捕获，未知触发名称必须拒绝。"""

        from scripts.project_kb.capture import CHECKPOINTS, capture_candidate

        self.assertEqual(
            {
                "user_decision",
                "requirement_change",
                "contract_change",
                "before_plan",
                "before_delivery",
                "after_acceptance",
                "before_release",
                "session_end",
            },
            CHECKPOINTS,
        )
        candidate = self._candidate(checkpoint="background_monitor")

        with self.assertRaises(ValueError):
            capture_candidate(self.root, candidate, captured_at="2026-08-13T10:30:00+08:00", user_requested=True)

    def test_plugin_process_file_is_referenced_but_not_copied(self) -> None:
        """其他插件产物只作为来源路径，提案不能复制其完整内容。"""

        from scripts.project_kb.capture import capture_candidate

        process_file = self.root / "docs/superpowers/plans/large-plan.md"
        process_file.parent.mkdir(parents=True)
        secret_marker = "PROCESS-FILE-BODY-MUST-NOT-BE-COPIED"
        process_file.write_text(secret_marker, encoding="utf-8")
        candidate = self._candidate(
            checkpoint="before_plan",
            source_type="existing_document",
            source_reference="docs/superpowers/plans/large-plan.md",
        )

        report = capture_candidate(
            self.root, candidate, captured_at="2026-08-13T10:30:00+08:00", user_requested=True
        )
        content = report.path.read_text(encoding="utf-8")

        self.assertIn("docs/superpowers/plans/large-plan.md", content)
        self.assertNotIn(secret_marker, content)

    def test_roles_and_confirmation_are_not_conflated(self) -> None:
        """自动提案记录提出者和操作方，但确认者必须保持待确认。"""

        from scripts.project_kb.capture import capture_candidate

        report = capture_candidate(
            self.root,
            self._candidate(proposed_by="AGENT-CODEX"),
            captured_at="2026-08-13T10:30:00+08:00",
            user_requested=True,
        )
        content = report.path.read_text(encoding="utf-8")

        self.assertIn("proposed_by: AGENT-CODEX", content)
        self.assertIn("operated_by: AGENT-CODEX", content)
        self.assertIn("confirmed_by: pending", content)
        self.assertIn("git_commit: pending", content)

    def test_capture_requires_explicit_user_request(self) -> None:
        """普通开发发现候选时不得自动创建待确认知识文件。"""

        from scripts.project_kb.capture import capture_candidate

        with self.assertRaisesRegex(ValueError, "explicit user request"):
            capture_candidate(
                self.root,
                self._candidate(),
                captured_at="2026-08-13T10:30:00+08:00",
            )
        self.assertFalse((self.root / "03-变更与证据/待确认知识").exists())
