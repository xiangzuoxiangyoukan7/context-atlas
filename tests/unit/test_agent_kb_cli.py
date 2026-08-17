"""验证 Agent 可使用统一命令入口执行知识诊断、捕获与迁移。"""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path

from scripts.agent_kb_operation import main
from tests.helpers import TempDirectoryTestCase


ROOT = Path(__file__).resolve().parents[2]


class AgentKnowledgeCliTests(TempDirectoryTestCase):
    """验证命令输出是可判定的 JSON，并保留确认门禁。"""

    def _run(self, *arguments: str) -> tuple[int, dict[str, object]]:
        """运行命令并解析标准输出中的结构化报告。"""

        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(list(arguments))
        return exit_code, json.loads(output.getvalue())

    def test_diagnose_format_reports_current_compatibility(self) -> None:
        """格式诊断应明确当前版本是否可写及是否需要转换。"""

        (self.root / "knowledge-base.yaml").write_text(
            "project_version: 1.0.0\nformat_version: 2\n", encoding="utf-8"
        )

        exit_code, payload = self._run(
            "diagnose-format",
            str(self.root),
            "--compatibility",
            str(ROOT / "compatibility.json"),
        )

        self.assertEqual(0, exit_code)
        self.assertEqual("compatible", payload["status"])
        self.assertFalse(payload["write_blocked"])

    def test_init_is_an_explicit_alias_for_initialize(self) -> None:
        """init 命令应执行正式初始化并返回结构化报告。"""

        exit_code, payload = self._run(
            "init",
            str(self.root),
            "--proposal-revision",
            "proposal-init-1",
            "--confirmed-revision",
            "proposal-init-1",
        )

        self.assertEqual(0, exit_code)
        self.assertEqual("initialized", payload["operation"])
        self.assertTrue((self.root / f"doc-{self.root.name}").exists())

    def test_update_applies_confirmed_file_changes_and_validates(self) -> None:
        """update 命令应只在同一修订号确认后应用文件变更。"""

        from scripts.project_kb.initializer import initialize_from_assets

        target = initialize_from_assets(
            self.root,
            assets_root=ROOT / "skills/context-atlas/assets",
        )
        content_file = self.root / "replacement.md"
        content_file.write_text("# 已确认更新\n", encoding="utf-8")

        exit_code, payload = self._run(
            "update",
            str(target),
            "--proposal-revision",
            "proposal-update-1",
            "--confirmed-revision",
            "proposal-update-1",
            "--file",
            "README.md",
            "--content-file",
            str(content_file),
        )

        self.assertEqual(0, exit_code)
        self.assertEqual("updated", payload["operation"])
        self.assertEqual("# 已确认更新\n", (target / "README.md").read_text(encoding="utf-8"))

    def test_capture_creates_proposed_knowledge_only(self) -> None:
        """捕获命令应写入待确认队列并返回提案路径。"""

        exit_code, payload = self._run(
            "capture",
            str(self.root),
            "--checkpoint",
            "user_decision",
            "--summary",
            "订单状态新增已取消",
            "--target-id",
            "TABLE-ORDER",
            "--source-type",
            "user_statement",
            "--source-reference",
            "当前用户明确决定",
            "--difference",
            "状态值域发生变化",
            "--impact-id",
            "FEATURE-ORDER",
            "--proposed-by",
            "PERSON-001",
            "--operated-by",
            "AGENT-CLAUDE-CODE",
            "--project-version",
            "1.2.0",
            "--captured-at",
            "2026-08-13T10:30:00+08:00",
        )

        self.assertEqual(0, exit_code)
        self.assertEqual("created", payload["status"])
        proposal = Path(str(payload["path"]))
        self.assertTrue(proposal.is_file())
        self.assertIn("status: proposed", proposal.read_text(encoding="utf-8"))

    def test_identify_contributor_returns_stable_person_candidate(self) -> None:
        """身份命令应使用知识库人员表，并仅返回邮箱摘要。"""

        import subprocess

        from scripts.project_kb.identity import email_digest

        people_dir = self.root / "doc-example/00-项目总览"
        people_dir.mkdir(parents=True)
        (people_dir / "协作人员.md").write_text(
            "# 协作人员\n\n"
            "| 人员编号 | 显示名称 | 所属团队 | 状态 | Git 用户名别名 | Git 邮箱摘要 |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            f"| PERSON-001 | Fixture | 测试组 | active | fixture | "
            f"{email_digest('fixture@example.com')} |\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "init", "--quiet"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "config", "--local", "user.name", "fixture"],
            cwd=self.root,
            check=True,
        )
        subprocess.run(
            ["git", "config", "--local", "user.email", "fixture@example.com"],
            cwd=self.root,
            check=True,
        )

        exit_code, payload = self._run(
            "identify-contributor", str(self.root), str(self.root / "doc-example")
        )

        self.assertEqual(0, exit_code)
        self.assertEqual("PERSON-001", payload["person_id"])
        self.assertNotIn("fixture@example.com", json.dumps(payload))

    def test_migration_requires_same_confirmed_revision(self) -> None:
        """迁移应用命令必须使用只读提案返回的同一修订号。"""

        (self.root / "knowledge-base.yaml").write_text(
            "project_version: 1.2.0\n", encoding="utf-8"
        )
        source_dir = self.root / "00-项目总览"
        source_dir.mkdir()
        (source_dir / "SRC-001.md").write_text(
            "---\nid: SRC-001\ntype: source\ntitle: 用户确认\n"
            "source_type: user_statement\nreference: test\nlast_updated: 2026-08-13\n"
            "---\n# 来源\n",
            encoding="utf-8",
        )
        target_dir = self.root / "01-功能基线"
        target_dir.mkdir()
        target = target_dir / "REQ-001.md"
        target.write_text(
            "---\nid: REQ-001\ntype: knowledge_item\ntitle: 需求\n"
            "status: approved\nversion: 1.0.0\nsources: [SRC-001]\n"
            "approved_by: owner\napproved_at: 2026-08-13\n"
            "last_updated: 2026-08-13\n---\n# 需求\n",
            encoding="utf-8",
        )
        compatibility = str(ROOT / "compatibility.json")

        propose_code, proposal = self._run(
            "migrate-propose", str(self.root), "--compatibility", compatibility
        )
        apply_code, report = self._run(
            "migrate-apply",
            str(self.root),
            "--compatibility",
            compatibility,
            "--proposal-revision",
            str(proposal["proposal_revision"]),
            "--confirmed-revision",
            str(proposal["proposal_revision"]),
        )

        self.assertEqual(0, propose_code)
        self.assertEqual(0, apply_code)
        self.assertEqual("migrated", report["status"])
        self.assertIn("rel_supported_by", target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    import unittest

    unittest.main()
