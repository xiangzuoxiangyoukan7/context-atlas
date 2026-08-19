"""test_skill_package 自动化测试。"""

import json
from pathlib import Path
import re
import tempfile
import unittest


SKILL_ROOTS = (
    Path("skills/context-atlas-init"),
    Path("skills/context-atlas-update"),
)
ASSETS_ROOT = Path("assets")
REFERENCES_ROOT = Path("references")
REFERENCES = (
    "初始化协议.md",
    "执行状态机.md",
    "知识采集与确认.md",
    "更新冲突与归档.md",
    "验证与结果报告.md",
    "关系与影响分析.md",
    "数据库知识.md",
    "兼容与迁移.md",
    "身份与主动采集.md",
    "宿主执行与运行时探测.md",
)


class SkillPackageTests(unittest.TestCase):
    """验证 SkillPackageTests 相关行为。"""

    def test_skill_has_required_progressive_disclosure_files(self) -> None:
        """验证 skill_has_required_progressive_disclosure_files 场景。"""

        for skill_root in SKILL_ROOTS:
            self.assertTrue((skill_root / "SKILL.md").is_file())
            self.assertTrue((skill_root / "agents/openai.yaml").is_file())
            self.assertFalse((skill_root / "README.md").exists())
        for name in REFERENCES:
            self.assertTrue((REFERENCES_ROOT / name).is_file(), name)

    def test_installed_skill_contains_all_runtime_assets(self) -> None:
        """验证 installed_skill_contains_all_runtime_assets 场景。"""

        assets = ASSETS_ROOT
        manifest = json.loads((assets / "manifest.json").read_text(encoding="utf-8"))
        missing = [path for path in manifest["files"] if not (assets / path).is_file()]

        self.assertEqual(missing, [])

    def test_skill_assets_match_canonical_sources(self) -> None:
        """验证 skill_assets_match_canonical_sources 场景。"""

        from scripts.sync_skill_assets import sync_assets

        mismatches = sync_assets(Path.cwd(), Path.cwd(), check=True)

        self.assertEqual(mismatches, [])

    def test_skill_declares_required_behavior_boundaries(self) -> None:
        """验证 skill_declares_required_behavior_boundaries 场景。"""

        content = "\n".join((root / "SKILL.md").read_text(encoding="utf-8") for root in SKILL_ROOTS)
        required = (
            "doc-<项目目录名>",
            "显式确认",
            "目标已存在",
            "AGENTS.md",
            "CLAUDE.md",
            "../../references/初始化协议.md",
            "../../references/执行状态机.md",
            "../../references/知识采集与确认.md",
            "../../references/更新冲突与归档.md",
            "../../references/验证与结果报告.md",
        )
        for phrase in required:
            self.assertIn(phrase, content)

        for command in (
            "$context-atlas-init",
            "$context-atlas-update",
            "Formal writes require explicit invocation",
        ):
            self.assertIn(command, content)

    def test_skill_resolves_python_three_portably(self) -> None:
        """Skill 必须优先使用平台原生 Python 3 启动方式并报告探测结果。"""

        runtime_contract = (REFERENCES_ROOT / "宿主执行与运行时探测.md").read_text(
            encoding="utf-8"
        )
        for skill_root in SKILL_ROOTS:
            skill_content = (skill_root / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("../../references/宿主执行与运行时探测.md", skill_content)
            content = skill_content + "\n" + runtime_contract
            for phrase in (
                "py -3",
                "python3",
                "Windows Store",
                "exit code 9009",
                "zero formal writes",
                "只记录候选命令",
            ):
                self.assertIn(phrase, content, f"{skill_root.name}: {phrase}")

    def test_agent_host_fallback_is_scoped_and_auditable(self) -> None:
        """无 Python 时必须暂存、限制写入范围并降低验证声明。"""

        contract = (REFERENCES_ROOT / "宿主执行与运行时探测.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "agent_host",
            ".context-atlas-staging-<revision-prefix>",
            "不得直接写正式目标",
            "写入范围只包含暂存目录",
            "deterministic_validation: not_run",
            "不得表述为“确定性验证通过”",
        ):
            self.assertIn(phrase, contract)

        for skill_root in SKILL_ROOTS:
            content = (skill_root / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("../../references/宿主执行与运行时探测.md", content)
            self.assertIn("agent_host", content)

    def test_relation_and_impact_reference_explains_human_decision_boundary(self) -> None:
        """Skill 必须解释统一链接、三级结果和人工确认边界。"""

        content = (REFERENCES_ROOT / "关系与影响分析.md").read_text(
            encoding="utf-8"
        )

        for phrase in (
            "rel_<type>",
            "[[相对/目标文件#可选锚点|TARGET-ID]]",
            "必须处理",
            "需要复核",
            "仅供参考",
            "不得控制开发任务是否执行",
        ):
            self.assertIn(phrase, content)

    def test_relation_and_impact_templates_are_packaged(self) -> None:
        """初始化资产必须包含关系目录和影响分析记录模板。"""

        assets = ASSETS_ROOT / "templates" / "core" / "doc-project"

        self.assertTrue((assets / "02-架构与契约/关系目录.md").is_file())
        self.assertTrue((assets / "03-实施与验收/影响分析/TEMPLATE.md").is_file())

    def test_database_reference_and_four_entity_templates_are_packaged(self) -> None:
        """Skill 必须解释数据库产品层级并包含四类实体模板。"""

        reference = (REFERENCES_ROOT / "数据库知识.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "Oracle",
            "KingbaseES",
            "PostgreSQL",
            "MySQL",
            "逻辑外键",
            "物理外键",
            "值域",
            "数据库作为基础知识",
        ):
            self.assertIn(phrase, reference)
        database_root = (
            ASSETS_ROOT / "templates/core/doc-project/02-架构与契约/数据库"
        )
        for relative in (
            "数据源/TEMPLATE.md",
            "数据库单元/TEMPLATE.md",
            "数据命名空间/TEMPLATE.md",
            "数据表/TEMPLATE.md",
        ):
            self.assertTrue((database_root / relative).is_file(), relative)

    def test_skill_state_machine_has_confirmation_and_revision_gates(self) -> None:
        """验证 skill_state_machine_has_confirmation_and_revision_gates 场景。"""

        content = (REFERENCES_ROOT / "执行状态机.md").read_text(
            encoding="utf-8"
        )
        states = (
            "inspect",
            "propose",
            "await_confirmation",
            "apply",
            "validate",
            "report",
        )

        for state in states:
            self.assertIn(state, content)
        self.assertIn("proposal_revision == confirmed_revision", content)
        self.assertIn("zero formal writes", content)
        self.assertIn("目标已存在", content)
        self.assertIn("更新流程", content)
        self.assertIn("不决定外部任务是否执行", content)

    def test_identity_capture_and_migration_references_explain_runtime_protocol(self) -> None:
        """Skill 必须给 Agent 明确的身份、检查点和轻量迁移调用协议。"""

        identity = (REFERENCES_ROOT / "身份与主动采集.md").read_text(
            encoding="utf-8"
        )
        migration = (REFERENCES_ROOT / "兼容与迁移.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "Git 邮箱摘要",
            "PERSON-UNKNOWN",
            "user_decision",
            "before_delivery",
            "session_end",
            "status: proposed",
            "不控制开发任务",
            "agent_kb_operation.py capture",
            "identify-contributor",
        ):
            self.assertIn(phrase, identity)
        for phrase in (
            "format_version",
            "project_version",
            "migrate-propose",
            "migrate-apply",
            "proposal_revision",
            "旧字段",
            "rel_supported_by",
        ):
            self.assertIn(phrase, migration)

    def test_proposal_and_report_references_use_state_machine_contract(self) -> None:
        """验证 proposal_and_report_references_use_state_machine_contract 场景。"""

        proposal = (REFERENCES_ROOT / "知识采集与确认.md").read_text(
            encoding="utf-8"
        )
        report = (REFERENCES_ROOT / "验证与结果报告.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("proposal_revision", proposal)
        self.assertIn("confirmed_revision", proposal)
        self.assertIn("Confirmation state", report)
        self.assertIn("Validation result", report)
        self.assertIn("not_validated", report)

    def test_capture_protocol_has_one_runtime_authority_and_thin_skills(self) -> None:
        """知识采集完整执行语义必须集中在 references，Skill 只做薄编排。"""

        protocol = (REFERENCES_ROOT / "知识采集与确认.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "single normative protocol source",
            "thin adapters",
            "durable governance explanation",
            "not the plugin runtime specification",
            "Schemas are the machine authority",
        ):
            self.assertIn(phrase, protocol)

        for skill_root in SKILL_ROOTS:
            skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("../../references/知识采集与确认.md", skill)
            self.assertNotIn("## Source types", skill)
            self.assertNotIn("## Proposal contract", skill)

    def test_skill_ui_metadata_is_readable_and_legacy_assets_are_absent(self) -> None:
        """验证 skill_ui_metadata_is_readable_and_legacy_assets_are_absent 场景。"""

        metadata = "\n".join((root / "agents/openai.yaml").read_text(encoding="utf-8") for root in SKILL_ROOTS)
        manifest = json.loads(
            (ASSETS_ROOT / "manifest.json").read_text(encoding="utf-8")
        )

        self.assertIn('display_name: "context-atlas-init"', metadata)
        self.assertIn('display_name: "context-atlas-update"', metadata)
        self.assertIn("$context-atlas-init", metadata)
        self.assertIn("$context-atlas-update", metadata)
        self.assertFalse(Path("skills/project-knowledge-context").exists())
        self.assertFalse(Path("profiles").exists())
        self.assertFalse(any(path.startswith("profiles/") for path in manifest["files"]))

    def test_skill_frontmatter_matches_official_constraints(self) -> None:
        """验证 skill_frontmatter_matches_official_constraints 场景。"""

        for skill_root in SKILL_ROOTS:
            content = (skill_root / "SKILL.md").read_text(encoding="utf-8")
            match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            self.assertIsNotNone(match)
            assert match is not None
            fields = dict(line.split(":", 1) for line in match.group(1).splitlines() if ":" in line)
            self.assertEqual(set(fields), {"name", "description"})
            name = fields["name"].strip()
            self.assertEqual(skill_root.name, name)
            self.assertNotIn("TODO", content)
            self.assertLess(len(content.splitlines()), 500)

    def test_sync_rejects_escape_and_preserves_undeclared_files(self) -> None:
        """验证 sync_rejects_escape_and_preserves_undeclared_files 场景。"""

        from scripts.sync_skill_assets import sync_assets

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            skill = root / "skill"
            assets = skill / "assets"
            source.mkdir()
            assets.mkdir(parents=True)
            (assets / "manifest.json").write_text(
                json.dumps({"files": ["../outside.txt"]}), encoding="utf-8"
            )

            with self.assertRaises(ValueError):
                sync_assets(source, skill)

            (source / "declared.txt").write_text("declared\n", encoding="utf-8")
            (assets / "manifest.json").write_text(
                json.dumps({"files": ["declared.txt"]}), encoding="utf-8"
            )
            extra = assets / "keep-me.txt"
            extra.write_text("user file\n", encoding="utf-8")

            self.assertEqual(sync_assets(source, skill), ["declared.txt"])
            self.assertTrue(extra.is_file())

    def test_sync_treats_crlf_target_as_matching_lf_canonical_text(self) -> None:
        """验证 sync_treats_crlf_target_as_matching_lf_canonical_text 场景。"""

        from scripts.sync_skill_assets import sync_assets

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            skill = root / "skill"
            assets = skill / "assets"
            source.mkdir()
            assets.mkdir(parents=True)
            (source / "document.md").write_bytes(b"first line\nsecond line\n")
            (assets / "manifest.json").write_text(
                json.dumps({"files": ["document.md"]}), encoding="utf-8"
            )
            (assets / "document.md").write_bytes(b"first line\r\nsecond line\r\n")

            self.assertEqual(sync_assets(source, skill, check=True), [])

    def test_sync_handles_invalid_utf8_text_target_as_mismatch(self) -> None:
        """验证 sync_handles_invalid_utf8_text_target_as_mismatch 场景。"""

        from scripts.sync_skill_assets import sync_assets

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            skill = root / "skill"
            assets = skill / "assets"
            source.mkdir()
            assets.mkdir(parents=True)
            canonical = b"canonical line\n"
            (source / "document.md").write_bytes(canonical)
            (assets / "manifest.json").write_text(
                json.dumps({"files": ["document.md"]}), encoding="utf-8"
            )
            target = assets / "document.md"
            target.write_bytes(b"invalid \xff\n")

            self.assertEqual(sync_assets(source, skill, check=True), ["document.md"])
            self.assertEqual(sync_assets(source, skill, check=False), ["document.md"])
            self.assertEqual(target.read_bytes(), canonical)


if __name__ == "__main__":
    unittest.main()
