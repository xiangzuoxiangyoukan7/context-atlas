"""验证旧来源编号到统一文件关系的等价转换和确认门禁。"""

from __future__ import annotations

from pathlib import Path

from scripts.project_kb.discovery import discover_records
from tests.helpers import TempDirectoryTestCase


ROOT = Path(__file__).resolve().parents[2]


class MigrationTests(TempDirectoryTestCase):
    """验证迁移只处理表达逻辑差异，不改变项目业务版本。"""

    def _manifest(self) -> Path:
        """写入没有格式字段的旧知识库清单。"""

        path = self.root / "knowledge-base.yaml"
        path.write_text(
            "project_id: example\nproject_version: 3.4.0\nrevision: 1\n",
            encoding="utf-8",
        )
        return path

    def _source(self) -> None:
        """写入可唯一定位的旧来源实体。"""

        directory = self.root / "00-项目总览"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "SRC-001.md").write_text(
            "---\nid: SRC-001\ntype: source\ntitle: 用户确认\n"
            "source_type: user_statement\nreference: fixture\nlast_updated: 2026-08-13\n"
            "---\n# SRC-001 用户确认\n",
            encoding="utf-8",
        )

    def _knowledge(self, source: str = "SRC-001") -> Path:
        """写入只含旧裸来源编号的正式知识。"""

        directory = self.root / "01-功能基线"
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "REQ-001.md"
        path.write_text(
            "---\nid: REQ-001\ntype: knowledge_item\ntitle: 示例需求\n"
            f"status: approved\nversion: 1.0.0\nsources: [{source}]\n"
            "approved_by: example-owner\napproved_at: 2026-08-13\n"
            "last_updated: 2026-08-13\n---\n# REQ-001 示例需求\n",
            encoding="utf-8",
        )
        return path

    def _proposal(self) -> object:
        """发现记录并生成到当前格式的转换提案。"""

        from scripts.project_kb.compatibility import CompatibilityPolicy
        from scripts.project_kb.migration import build_migration_proposal

        records, issues = discover_records(self.root, frozenset())
        self.assertEqual([], issues)
        policy = CompatibilityPolicy.load(ROOT / "compatibility.json")
        return build_migration_proposal(self.root, records, policy)

    def test_proposal_lists_equivalent_source_link_without_writing(self) -> None:
        """生成迁移提案只能读文件并列出确定的一对一转换。"""

        manifest = self._manifest()
        self._source()
        knowledge = self._knowledge()
        before = {manifest: manifest.read_bytes(), knowledge: knowledge.read_bytes()}

        proposal = self._proposal()

        self.assertEqual(1, proposal.source_version)
        self.assertEqual(4, proposal.target_version)
        self.assertEqual([], list(proposal.unresolved))
        self.assertIn(
            '"reference": "fixture"',
            proposal.changes[0].links[0],
        )
        self.assertEqual(before[manifest], manifest.read_bytes())
        self.assertEqual(before[knowledge], knowledge.read_bytes())

    def test_ambiguous_or_missing_source_prevents_conversion(self) -> None:
        """来源无法唯一定位时只报告待确认项，不猜测目标文件。"""

        self._manifest()
        knowledge = self._knowledge("SRC-999")
        before = knowledge.read_bytes()

        proposal = self._proposal()

        self.assertEqual(1, len(proposal.unresolved))
        self.assertEqual([], list(proposal.changes))
        self.assertEqual(before, knowledge.read_bytes())

    def test_confirmation_gate_applies_links_and_only_format_version(self) -> None:
        """确认同修订后才写链接，并保持项目版本不变。"""

        from scripts.project_kb.migration import apply_migration

        manifest = self._manifest()
        self._source()
        knowledge = self._knowledge()
        proposal = self._proposal()

        with self.assertRaises(PermissionError):
            apply_migration(self.root, proposal, "wrong-revision")
        self.assertIn("sources: [SRC-001]", knowledge.read_text(encoding="utf-8"))

        report = apply_migration(self.root, proposal, proposal.proposal_revision)

        content = knowledge.read_text(encoding="utf-8")
        manifest_content = manifest.read_text(encoding="utf-8")
        self.assertIn("sources:", content)
        self.assertIn("  - type: \"user_statement\"", content)
        self.assertIn("    reference: \"fixture\"", content)
        self.assertIn("    confirmation_status: \"confirmed\"", content)
        self.assertNotIn("SRC-001", content)
        self.assertFalse((self.root / "00-项目总览/SRC-001.md").exists())
        self.assertTrue((self.root / "05-知识治理/公共来源/SRC-001.md").exists())
        self.assertIn("format_version: 4", manifest_content)
        self.assertIn("project_version: 3.4.0", manifest_content)
        self.assertEqual("migrated", report.status)

    def test_unresolved_proposal_cannot_be_applied(self) -> None:
        """即使修订号确认，存在歧义的提案也必须保持零写入。"""

        from scripts.project_kb.migration import apply_migration

        manifest = self._manifest()
        knowledge = self._knowledge("SRC-999")
        proposal = self._proposal()
        before = {manifest: manifest.read_bytes(), knowledge: knowledge.read_bytes()}

        with self.assertRaises(ValueError):
            apply_migration(self.root, proposal, proposal.proposal_revision)

        self.assertEqual(before[manifest], manifest.read_bytes())
        self.assertEqual(before[knowledge], knowledge.read_bytes())

    def test_format_two_moves_governance_and_removes_only_pristine_placeholders(self) -> None:
        """格式二升级后不再保留开发指南产品边界。"""

        from scripts.project_kb.compatibility import CompatibilityPolicy
        from scripts.project_kb.migration import LEGACY_PLACEHOLDERS, apply_migration, build_migration_proposal

        manifest = self._manifest()
        manifest.write_text(
            "project_id: example\nproject_version: 3.4.0\nformat_version: 2\nrevision: 1\n",
            encoding="utf-8",
        )
        legacy = self.root / "05-开发指南"
        legacy.mkdir()
        (legacy / "README.md").write_text("# 开发指南\n", encoding="utf-8")
        (legacy / "AI知识采集协议.md").write_text("# AI 知识采集协议\n", encoding="utf-8")
        root_readme = self.root / "README.md"
        root_readme.write_text(
            "# 示例知识库\n\n[开发指南](./05-开发指南/README.md)\n",
            encoding="utf-8",
        )
        for name, content in LEGACY_PLACEHOLDERS.items():
            (legacy / name).write_text(content + "\n", encoding="utf-8")

        records, issues = discover_records(self.root, frozenset())
        self.assertEqual([], issues)
        proposal = build_migration_proposal(
            self.root, records, CompatibilityPolicy.load(ROOT / "compatibility.json")
        )

        self.assertEqual(2, proposal.source_version)
        self.assertEqual(4, proposal.target_version)
        self.assertEqual(2, len(proposal.moves))
        self.assertEqual(2, len(proposal.removals))
        self.assertEqual([], list(proposal.unresolved))

        apply_migration(self.root, proposal, proposal.proposal_revision)

        self.assertTrue((self.root / "05-知识治理/README.md").is_file())
        self.assertTrue((self.root / "05-知识治理/AI知识采集协议.md").is_file())
        self.assertFalse((legacy / "本地开发.md").exists())
        self.assertFalse((legacy / "测试规则.md").exists())
        self.assertIn("format_version: 4", manifest.read_text(encoding="utf-8"))
        self.assertIn("05-知识治理/README.md", root_readme.read_text(encoding="utf-8"))
        self.assertNotIn("05-开发指南", root_readme.read_text(encoding="utf-8"))
        self.assertEqual(
            "# 知识治理\n",
            (self.root / "05-知识治理/README.md").read_text(encoding="utf-8"),
        )

    def test_format_two_preserves_custom_development_content_as_unresolved(self) -> None:
        """旧开发文档有实质内容时不得静默删除。"""

        from scripts.project_kb.compatibility import CompatibilityPolicy
        from scripts.project_kb.migration import build_migration_proposal

        manifest = self._manifest()
        manifest.write_text(
            "project_id: example\nproject_version: 3.4.0\nformat_version: 2\nrevision: 1\n",
            encoding="utf-8",
        )
        legacy = self.root / "05-开发指南"
        legacy.mkdir()
        custom = legacy / "本地开发.md"
        custom.write_text("# 本地开发\n\n`make release`\n", encoding="utf-8")
        records, issues = discover_records(self.root, frozenset())
        self.assertEqual([], issues)

        proposal = build_migration_proposal(
            self.root, records, CompatibilityPolicy.load(ROOT / "compatibility.json")
        )

        self.assertEqual(1, len(proposal.unresolved))
        self.assertIn("技术栈或技术契约", proposal.unresolved[0].reason)
        self.assertTrue(custom.is_file())
