"""永久删除知识的叶子门禁、关系清理、确认和回滚测试。"""

from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
import json
import shutil
import tempfile
import unittest

from scripts.project_kb.deletion import apply_delete, build_delete_proposal
from scripts.agent_kb_operation import main
from tests.helpers import materialize_core_template


OLD = """---
id: KB-OLD
type: knowledge_item
title: 无审计价值的旧知识
status: superseded
version: 1.0.0
last_updated: 2026-09-03
superseded_by: KB-NEW
sources:
  - type: user_statement
    reference: owner deletion decision
    observed_at: 2026-09-03
    confirmation_status: confirmed
    confirmed_at: 2026-09-03
rel_classified_under:
  - "[[02-技术基线/README|IDX-TECHNICAL-BASELINE]]"
---
# 旧知识
"""

NEW = """---
id: KB-NEW
type: knowledge_item
title: 新知识
status: approved
version: 2.0.0
last_updated: 2026-09-03
approved_by: owner
approved_at: 2026-09-03
supersedes: [KB-OLD]
sources:
  - type: user_statement
    reference: owner deletion decision
    observed_at: 2026-09-03
    confirmation_status: confirmed
    confirmed_at: 2026-09-03
rel_classified_under:
  - "[[02-技术基线/README|IDX-TECHNICAL-BASELINE]]"
---
# 新知识
"""


class DeletionTests(unittest.TestCase):
    """验证物理删除只作用于叶子知识并完整清理跨类型关系。"""

    def setUp(self) -> None:
        """建立含替代关系和运行时 Schema 的隔离知识库。"""
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = materialize_core_template(Path(self.temporary.name), "delete")
        shutil.copytree(Path("schemas"), self.root / ".project-kb" / "schemas")
        self.old = self.root / "02-技术基线" / "旧知识.md"
        self.new = self.root / "02-技术基线" / "新知识.md"
        self.old.write_text(OLD, encoding="utf-8")
        self.new.write_text(NEW, encoding="utf-8")
        self.plan = Path(self.temporary.name) / "delete-plan.json"
        self.write_plan(NEW.replace("supersedes: [KB-OLD]\n", ""))

    def write_plan(self, replacement: str, deletion_path: str = "02-技术基线/旧知识.md") -> None:
        """写入一份可调整删除路径与关系清理内容的候选计划。"""
        self.plan.write_text(json.dumps({
            "source_reference": "项目责任人确认无审计价值",
            "deletions": [{"path": deletion_path, "reason": "内容已完整承接且无需历史保留"}],
            "replacements": [{"path": "02-技术基线/新知识.md", "content": replacement}],
        }, ensure_ascii=False), encoding="utf-8")

    def test_propose_is_read_only_and_apply_requires_exact_confirmation(self) -> None:
        """提案保持零写入，错误确认修订不能进入正式删除。"""
        proposal = build_delete_proposal(self.root, self.plan)
        self.assertEqual("passed", proposal.preflight_status)
        self.assertIn("KB-NEW:supersedes->KB-OLD", proposal.affected_relations)
        self.assertTrue(self.old.exists())
        with self.assertRaises(PermissionError):
            apply_delete(self.root, self.plan, proposal.proposal_revision, "wrong")
        self.assertTrue(self.old.exists())

    def test_apply_deletes_leaf_and_cleans_incoming_relation(self) -> None:
        """正确确认后同时删除叶子并移除后继项的替代关系。"""
        proposal = build_delete_proposal(self.root, self.plan)
        report = apply_delete(self.root, self.plan, proposal.proposal_revision, proposal.proposal_revision)
        self.assertEqual("deleted", report.operation)
        self.assertFalse(self.old.exists())
        self.assertNotIn("KB-OLD", self.new.read_text(encoding="utf-8"))

    def test_readme_and_classification_parent_are_not_deletable(self) -> None:
        """结构 README 与存在分类子节点的知识均被确定性拒绝。"""
        self.write_plan(NEW, "02-技术基线/README.md")
        with self.assertRaises(ValueError):
            build_delete_proposal(self.root, self.plan)
        child = self.root / "02-技术基线" / "子知识.md"
        child.write_text(NEW.replace("supersedes: [KB-OLD]\n", "").replace("KB-NEW", "KB-CHILD").replace(
            '[[02-技术基线/README|IDX-TECHNICAL-BASELINE]]',
            '[[02-技术基线/旧知识|KB-OLD]]'), encoding="utf-8")
        self.write_plan(NEW.replace("supersedes: [KB-OLD]\n", ""))
        with self.assertRaisesRegex(ValueError, "不是分类树叶子"):
            build_delete_proposal(self.root, self.plan)

    def test_missing_relation_cleanup_is_rejected(self) -> None:
        """存活文件的任一入向关系未纳入替换计划时拒绝提案。"""
        self.plan.write_text(json.dumps({
            "source_reference": "owner",
            "deletions": [{"path": "02-技术基线/旧知识.md", "reason": "no audit value"}],
            "replacements": [],
        }), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "未改写入向关系"):
            build_delete_proposal(self.root, self.plan)

    def test_cli_exposes_delete_propose_as_json(self) -> None:
        """共享 Agent 入口能以 JSON 暴露只读删除提案和预演结果。"""

        output = StringIO()
        with redirect_stdout(output):
            code = main(["delete-propose", str(self.root), "--plan", str(self.plan)])
        payload = json.loads(output.getvalue())
        self.assertEqual(0, code)
        self.assertTrue(payload["ok"])
        self.assertEqual("passed", payload["preflight_status"])


if __name__ == "__main__":
    unittest.main()
