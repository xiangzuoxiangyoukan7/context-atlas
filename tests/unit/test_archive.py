"""历史归档提案、确认和回滚测试。"""

from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.project_kb.archive import ArchiveProposal, apply_archive, build_archive_proposal
from tests.helpers import materialize_core_template


OLD = """---
id: KB-OLD
type: knowledge_item
title: 旧知识
status: superseded
version: 1.0.0
last_updated: 2026-08-20
superseded_by: KB-NEW
sources:
  - type: user_statement
    reference: test
    observed_at: 2026-08-20
    confirmation_status: confirmed
    confirmed_at: 2026-08-20
---
# 旧知识
"""

NEW = """---
id: KB-NEW
type: knowledge_item
title: 新知识
status: approved
version: 2.0.0
last_updated: 2026-08-20
approved_by: owner
approved_at: 2026-08-20
supersedes: [KB-OLD]
sources:
  - type: user_statement
    reference: test
    observed_at: 2026-08-20
    confirmation_status: confirmed
    confirmed_at: 2026-08-20
---
# 新知识
"""


class ArchiveTests(unittest.TestCase):
    """验证归档操作的提案门禁、并发保护和原子写入行为。"""

    def setUp(self) -> None:
        """建立包含运行时 Schema 及一组双向替代知识的隔离目录。"""

        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = materialize_core_template(Path(self.temporary.name), "archive")
        shutil.copytree(Path("schemas"), self.root / ".project-kb" / "schemas")
        self.old = self.root / "02-架构与契约" / "旧知识.md"
        self.new = self.root / "02-架构与契约" / "新知识.md"
        self.old.write_text(OLD, encoding="utf-8")
        self.new.write_text(NEW, encoding="utf-8")

    def proposal(self) -> ArchiveProposal:
        """返回当前隔离知识库对应的归档提案。"""

        return build_archive_proposal(
            self.root, "02-架构与契约/旧知识.md", "90-历史归档/正式知识/旧知识.md",
            "KB-NEW", "2026-08-20", "已被新知识替代", "用户确认",
        )

    def test_proposal_is_read_only_and_confirmation_is_exact(self) -> None:
        """验证提案不写盘且错误确认号不会产生修改。"""

        proposal = self.proposal()
        self.assertTrue(self.old.exists())
        with self.assertRaises(PermissionError):
            apply_archive(self.root, proposal, "wrong")
        self.assertTrue(self.old.exists())

    def test_apply_moves_changes_status_and_updates_index(self) -> None:
        """验证确认后移动文件、改变状态并登记索引。"""

        proposal = self.proposal()
        report = apply_archive(self.root, proposal, proposal.proposal_revision)
        target = self.root / proposal.target_path
        self.assertFalse(self.old.exists())
        self.assertIn("status: archived", target.read_text(encoding="utf-8"))
        self.assertIn("KB-OLD", (self.root / "90-历史归档" / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(report.validator_exit_code, 0)

    def test_changed_source_rejects_stale_proposal(self) -> None:
        """验证源文件变化会让旧提案失效。"""

        proposal = self.proposal()
        self.old.write_text(OLD + "changed\n", encoding="utf-8")
        with self.assertRaises(PermissionError):
            apply_archive(self.root, proposal, proposal.proposal_revision)

    def test_other_current_reference_blocks_proposal(self) -> None:
        """验证除后继替代关系外的当前引用会阻止归档。"""

        self.new.write_text(NEW.replace("supersedes: [KB-OLD]", "supersedes: [KB-OLD]\ndepends_on: [KB-OLD]"), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.proposal()


if __name__ == "__main__":
    unittest.main()
