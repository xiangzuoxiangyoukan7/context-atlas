"""验证外部来源暂存箱的必处理、原子保存和保留边界。"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path

from scripts.project_kb.initializer import initialize_from_assets
from scripts.project_kb.managed_sources import apply_source_import, build_source_import_proposal
from scripts.project_kb.validator import ValidationConfig, validate
from tests.helpers import InstalledPluginTestCase


class ManagedSourceTests(InstalledPluginTestCase):
    """使用完整初始化目标验证来源文件生命周期。"""

    def setUp(self) -> None:
        """初始化带内嵌运行时的隔离知识库与暂存箱。"""

        super().setUp()
        self.target = initialize_from_assets(
            self.root, "example", self.assets_root, initialized_at="2026-08-22"
        )
        self.inbox = self.target / "Clippings"

    def test_clipping_frontmatter_is_excluded_from_formal_validation(self) -> None:
        """任意网页剪藏元数据不能破坏正式知识检查。"""

        (self.inbox / "搜索.md").write_text(
            "---\nauthor:\npublished:\ntags:\n  - clippings\n---\n正文\n",
            encoding="utf-8",
        )
        self.assertEqual(
            [], validate(self.target, ValidationConfig(schema_root=self.target / ".project-kb/schemas"))
        )

    def test_confirmed_eligible_file_is_saved_then_removed_from_inbox(self) -> None:
        """目标摘要与知识库验证成功后才能删除暂存原件。"""

        original = self.inbox / "外部说明.md"
        original.write_text("# 外部说明\n\n稳定资料。\n", encoding="utf-8")
        proposal = build_source_import_proposal(self.target)
        self.assertEqual(1, len(proposal.items))
        self.assertEqual("eligible", proposal.items[0].status)

        result = apply_source_import(
            self.target, proposal.proposal_revision, proposal.proposal_revision,
            imported_at=datetime(2026, 8, 22, tzinfo=timezone.utc),
        )

        self.assertEqual("saved", result.results[0]["status"])
        self.assertFalse(original.exists())
        item = proposal.items[0]
        managed = self.target / item.managed_path
        card = self.target / item.card_path
        self.assertTrue(managed.is_file())
        self.assertTrue(card.is_file())
        self.assertEqual(item.sha256, hashlib.sha256(managed.read_bytes()).hexdigest())
        self.assertIn("保存不表示批准", card.read_text(encoding="utf-8"))
        temporary_root = self.root / ".context-atlas-temp"
        self.assertTrue(temporary_root.is_dir())
        self.assertEqual([], list(temporary_root.iterdir()))
        self.assertEqual([], list((self.target / "05-知识治理/来源资料").glob(".importing-*")))

    def test_blocked_file_remains_and_other_file_is_saved(self) -> None:
        """部分批次不能删除阻塞文件，也不能抹去合格结果。"""

        allowed = self.inbox / "allowed.txt"
        blocked = self.inbox / "blocked.exe"
        allowed.write_text("ordinary external source\n", encoding="utf-8")
        blocked.write_bytes(b"MZ fixture")
        proposal = build_source_import_proposal(self.target)
        self.assertEqual({"eligible", "blocked"}, {item.status for item in proposal.items})

        result = apply_source_import(
            self.target, proposal.proposal_revision, proposal.proposal_revision,
            imported_at=datetime(2026, 8, 22, tzinfo=timezone.utc),
        )

        self.assertFalse(allowed.exists())
        self.assertTrue(blocked.exists())
        self.assertEqual({"saved", "blocked"}, {item["status"] for item in result.results})

    def test_symbolic_link_is_blocked_without_reading_target(self) -> None:
        """暂存箱链接不能成为绕过来源边界的读取入口。"""

        outside = self.root / "outside.txt"
        outside.write_text("external secret\n", encoding="utf-8")
        link = self.inbox / "linked.txt"
        try:
            os.symlink(outside, link)
        except OSError as exc:
            self.skipTest(f"当前环境不能创建符号链接: {exc}")

        proposal = build_source_import_proposal(self.target)

        self.assertEqual("blocked", proposal.items[0].status)
        self.assertEqual("symbolic links are not allowed", proposal.items[0].blocked_reason)
        self.assertEqual(0, proposal.items[0].size_bytes)

    def test_changed_or_unconfirmed_proposal_has_zero_moves(self) -> None:
        """修订不一致或暂存内容变化必须在写入前拒绝。"""

        original = self.inbox / "source.txt"
        original.write_text("version one\n", encoding="utf-8")
        proposal = build_source_import_proposal(self.target)
        original.write_text("version two\n", encoding="utf-8")
        with self.assertRaises(PermissionError):
            apply_source_import(
                self.target, proposal.proposal_revision, proposal.proposal_revision
            )
        self.assertTrue(original.exists())
        self.assertFalse((self.target / "05-知识治理/来源资料/files").exists())

    def test_duplicate_is_reported_without_new_managed_copy(self) -> None:
        """相同摘要复用稳定来源身份并按确认移除重复暂存副本。"""

        first = self.inbox / "first.txt"
        first.write_text("same body\n", encoding="utf-8")
        initial = build_source_import_proposal(self.target)
        apply_source_import(
            self.target, initial.proposal_revision, initial.proposal_revision,
            imported_at=datetime(2026, 8, 22, tzinfo=timezone.utc),
        )
        duplicate = self.inbox / "duplicate.txt"
        duplicate.write_text("same body\n", encoding="utf-8")
        proposal = build_source_import_proposal(self.target)
        self.assertEqual("duplicate", proposal.items[0].status)
        result = apply_source_import(
            self.target, proposal.proposal_revision, proposal.proposal_revision,
            imported_at=datetime(2026, 8, 22, tzinfo=timezone.utc),
        )
        self.assertEqual("duplicate", result.results[0]["status"])
        self.assertFalse(duplicate.exists())
        self.assertEqual(1, len(list((self.target / "05-知识治理/来源资料/files").glob("*/*"))))
