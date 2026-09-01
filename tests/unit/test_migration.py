"""验证旧来源编号到统一文件关系的等价转换和确认门禁。"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

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
        self.assertEqual(11, proposal.target_version)
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

    def test_legacy_contract_is_normalized_for_format_eleven(self) -> None:
        """遗留契约应转换为最新格式的待确认知识，而不是阻断升级。"""

        manifest = self._manifest()
        manifest.write_text(
            "project_id: example\nproject_version: 3.4.0\nformat_version: 9\nknowledge_revision: 1\n",
            encoding="utf-8",
        )
        contract = self.root / "02-技术基线/独立契约/CONTRACT-001.md"
        contract.parent.mkdir(parents=True)
        contract.write_text(
            "---\nid: CONTRACT-001\ntype: independent_contract\ntitle: 遗留契约\n---\n# 遗留契约\n",
            encoding="utf-8",
        )

        proposal = self._proposal()

        self.assertEqual(11, proposal.target_version)
        self.assertEqual([], list(proposal.unresolved))

        from scripts.project_kb.migration import apply_migration

        apply_migration(self.root, proposal, proposal.proposal_revision)
        converted = self.root / "03-变更与证据/待确认知识/CONTRACT-001.md"
        self.assertTrue(converted.is_file())
        self.assertIn("type: knowledge_item", converted.read_text(encoding="utf-8"))
        self.assertFalse(contract.exists())

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
        self.assertIn("format_version: 11", manifest_content)
        self.assertIn("knowledge_revision: 1", manifest_content)
        self.assertIn("created_by:", manifest_content)
        self.assertNotIn("revision:", manifest_content.replace("knowledge_revision:", ""))
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
        self.assertEqual(11, proposal.target_version)
        self.assertEqual(2, len(proposal.moves))
        self.assertEqual(2, len(proposal.removals))
        self.assertEqual([], list(proposal.unresolved))

        apply_migration(self.root, proposal, proposal.proposal_revision)

        self.assertTrue((self.root / "05-知识治理/README.md").is_file())
        self.assertTrue((self.root / "05-知识治理/AI知识采集协议.md").is_file())
        self.assertFalse((legacy / "本地开发.md").exists())
        self.assertFalse((legacy / "测试规则.md").exists())
        self.assertIn("format_version: 11", manifest.read_text(encoding="utf-8"))
        self.assertIn("05-知识治理/README.md", root_readme.read_text(encoding="utf-8"))
        self.assertNotIn("05-开发指南", root_readme.read_text(encoding="utf-8"))
        self.assertEqual(
            "# 知识治理\n",
            (self.root / "05-知识治理/README.md").read_text(encoding="utf-8"),
        )

    def test_format_four_rewrites_legacy_requirement_relation(self) -> None:
        """格式四迁移只执行可证明等价的关系改名。"""

        from scripts.project_kb.migration import apply_migration

        manifest = self._manifest()
        manifest.write_text(
            "project_id: example\nproject_version: 3.4.0\nformat_version: 4\nrevision: 1\n",
            encoding="utf-8",
        )
        feature = self.root / "01-功能基线/F01-example.md"
        feature.parent.mkdir(parents=True, exist_ok=True)
        feature.write_text(
            "---\nid: F01\ntype: feature\nrel_implements: []\n---\n# example\n",
            encoding="utf-8",
        )

        proposal = self._proposal()
        self.assertEqual([], list(proposal.unresolved))
        self.assertEqual(11, proposal.target_version)
        apply_migration(self.root, proposal, proposal.proposal_revision)

        self.assertIn("rel_satisfies: []", feature.read_text(encoding="utf-8"))
        self.assertIn("format_version: 11", manifest.read_text(encoding="utf-8"))

    def test_format_six_creates_complete_specification_workspaces_atomically(self) -> None:
        """格式六升级应创建目录说明及其模板，并拒绝提案后的目标冲突。"""

        from scripts.project_kb.migration import apply_migration

        manifest = self._manifest()
        manifest.write_text(
            "project_id: example\nproject_version: 3.4.0\nformat_version: 6\nrevision: 1\n",
            encoding="utf-8",
        )
        proposal = self._proposal()
        self.assertGreaterEqual(len(proposal.creations), 3)
        conflict = proposal.creations[0].path
        conflict.parent.mkdir(parents=True, exist_ok=True)
        conflict.write_text("conflict\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            apply_migration(self.root, proposal, proposal.proposal_revision)
        self.assertIn("format_version: 6", manifest.read_text(encoding="utf-8"))
        conflict.unlink()

        proposal = self._proposal()
        report = apply_migration(self.root, proposal, proposal.proposal_revision)
        self.assertEqual(11, report.format_version)
        self.assertTrue((self.root / "03-变更与证据/变更/README.md").is_file())
        self.assertFalse((self.root / "03-变更与证据/变更/TEMPLATE.md").exists())
        self.assertFalse((self.root / "03-变更与证据/变更/Delta/TEMPLATE.md").exists())
        change_readme = (self.root / "03-变更与证据/变更/README.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(".project-kb/templates/knowledge/specification-change.md", change_readme)
        self.assertIn(".project-kb/templates/knowledge/specification-delta.md", change_readme)
        self.assertTrue((self.root / ".project-kb/scripts/check_knowledge_base.py").is_file())
        self.assertTrue((self.root / ".project-kb/schemas/catalog.json").is_file())
        self.assertTrue((self.root / ".project-kb/rules/catalog.json").is_file())
        self.assertTrue((self.root / ".project-kb/operations/validate.json").is_file())
        self.assertTrue((self.root / ".project-kb/templates/knowledge/feature.md").is_file())

    def test_format_seven_asset_digest_drift_keeps_all_files_unchanged(self) -> None:
        """运行资产在确认前漂移时必须拒绝迁移且不产生其他写入。"""

        from scripts.project_kb.migration import apply_migration

        manifest = self._manifest()
        manifest.write_text(
            "project_id: example\nproject_version: 3.4.0\nformat_version: 6\nrevision: 1\n",
            encoding="utf-8",
        )
        proposal = self._proposal()
        asset = proposal.assets[0]
        asset.path.parent.mkdir(parents=True, exist_ok=True)
        asset.path.write_text("drift\n", encoding="utf-8")
        before = manifest.read_bytes()

        with self.assertRaises(ValueError):
            apply_migration(self.root, proposal, proposal.proposal_revision)

        self.assertEqual(before, manifest.read_bytes())
        self.assertFalse((self.root / "03-变更与证据/变更/README.md").exists())

    def test_format_seven_asset_write_failure_rolls_back_all_outputs(self) -> None:
        """运行资产写入中途失败时应恢复清单并清理全部新增文件。"""

        from scripts.project_kb import migration

        manifest = self._manifest()
        manifest.write_text(
            "project_id: example\nproject_version: 3.4.0\nformat_version: 6\nrevision: 1\n",
            encoding="utf-8",
        )
        proposal = self._proposal()
        original_writer = migration._atomic_write_bytes
        calls = 0

        def fail_after_first(path: Path, content: bytes) -> None:
            """先成功写入一个资产，再模拟后续磁盘错误。"""

            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("simulated asset write failure")
            original_writer(path, content)

        with patch.object(migration, "_atomic_write_bytes", side_effect=fail_after_first):
            with self.assertRaises(OSError):
                migration.apply_migration(self.root, proposal, proposal.proposal_revision)

        self.assertIn("format_version: 6", manifest.read_text(encoding="utf-8"))
        self.assertFalse((self.root / ".project-kb").exists())
        self.assertFalse((self.root / "03-变更与证据/变更/README.md").exists())

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

    def test_format_eleven_template_is_removed_not_moved_and_revision_is_stable(self) -> None:
        """格式十一不得为同一模板生成移动和删除计划，修订号必须稳定。"""

        self._manifest().write_text(
            "project_id: example\nproject_version: 3.4.0\n"
            "format_version: 10\nknowledge_revision: 1\n",
            encoding="utf-8",
        )
        legacy = self.root / "02-架构与契约/接口"
        legacy.mkdir(parents=True)
        template = legacy / "TEMPLATE.md"
        template.write_text("# 旧模板\n", encoding="utf-8")
        document = legacy / "API-001.md"
        document.write_text("# 接口\n", encoding="utf-8")
        old_relation = self.root / "02-架构与契约/关系目录.md"
        old_relation.write_text("# 旧关系目录\n", encoding="utf-8")
        independent = self.root / "02-架构与契约/独立契约/CONTRACT-002.md"
        independent.parent.mkdir(parents=True)
        independent.write_text(
            "---\nid: CONTRACT-002\ntype: independent_contract\ntitle: 旧独立契约\n---\n# 旧独立契约\n",
            encoding="utf-8",
        )
        acceptance = self.root / "03-变更与证据/验收契约/AC-001.md"
        acceptance.parent.mkdir(parents=True)
        acceptance.write_text(
            "---\nid: AC-001\ntype: acceptance_contract\ntitle: 旧验收契约\n---\n# 旧验收契约\n",
            encoding="utf-8",
        )

        first = self._proposal()
        second = self._proposal()

        self.assertEqual(first.proposal_revision, second.proposal_revision)
        self.assertNotIn(template.resolve(), {item.source.resolve() for item in first.moves})
        self.assertIn(template.resolve(), {item.path.resolve() for item in first.removals})
        self.assertFalse(first.unresolved)

        from scripts.project_kb.migration import apply_migration

        apply_migration(self.root, first, first.proposal_revision)
        self.assertFalse(template.exists())
        self.assertTrue((self.root / "02-技术基线/接口/API-001.md").exists())
        self.assertFalse(old_relation.exists())
        self.assertFalse(independent.exists())
        self.assertFalse(acceptance.exists())
        self.assertTrue((self.root / "03-变更与证据/待确认知识/CONTRACT-002.md").exists())
        self.assertTrue((self.root / "03-变更与证据/待确认知识/AC-001.md").exists())
