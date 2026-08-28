"""test_skill_package 自动化测试。"""

import json
from pathlib import Path
import re
import tempfile
import unittest


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
    "规格审查与SDD适配.md",
    "单来源摄取与路由.md",
)


class SkillPackageTests(unittest.TestCase):
    """验证 SkillPackageTests 相关行为。"""

    @classmethod
    def setUpClass(cls) -> None:
        """构建一次安装形态，所有运行资产断言只读取构建产物。"""

        from scripts.build_plugin import build

        cls.installation = tempfile.TemporaryDirectory()
        cls.plugin_root = build(Path(cls.installation.name) / "context-atlas", "codex")
        cls.assets_root = cls.plugin_root / "assets"
        cls.references_root = cls.plugin_root / "references"
        cls.skill_roots = (
            cls.plugin_root / "skills/context-atlas-init",
            cls.plugin_root / "skills/context-atlas-navigate",
            cls.plugin_root / "skills/context-atlas-review",
            cls.plugin_root / "skills/context-atlas-ingest",
            cls.plugin_root / "skills/context-atlas-add",
            cls.plugin_root / "skills/context-atlas-revise",
            cls.plugin_root / "skills/context-atlas-retire",
            cls.plugin_root / "skills/context-atlas-upgrade",
            cls.plugin_root / "skills/context-atlas-work",
        )
        cls.write_skill_roots = (
            cls.plugin_root / "skills/context-atlas-init",
            cls.plugin_root / "skills/context-atlas-add",
            cls.plugin_root / "skills/context-atlas-revise",
            cls.plugin_root / "skills/context-atlas-retire",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """清理本测试类生成的安装形态。"""

        cls.installation.cleanup()

    def test_skill_has_required_progressive_disclosure_files(self) -> None:
        """验证 skill_has_required_progressive_disclosure_files 场景。"""

        for skill_root in self.skill_roots:
            self.assertTrue((skill_root / "SKILL.md").is_file())
            self.assertTrue((skill_root / "agents/openai.yaml").is_file())
            self.assertFalse((skill_root / "README.md").exists())
        for name in REFERENCES:
            self.assertTrue((self.references_root / name).is_file(), name)

    def test_installed_skill_contains_all_runtime_assets(self) -> None:
        """验证 installed_skill_contains_all_runtime_assets 场景。"""

        assets = self.assets_root
        manifest = json.loads((assets / "manifest.json").read_text(encoding="utf-8"))
        missing = [path for path in manifest["files"] if not (assets / path).is_file()]

        self.assertEqual(missing, [])

    def test_development_repository_does_not_store_generated_runtime_copies(self) -> None:
        """开发仓库 assets 只保留清单，运行副本仅存在于构建产物。"""

        development_assets = Path("assets")
        self.assertEqual(
            [path.name for path in development_assets.iterdir() if path.is_file()],
            ["manifest.json"],
        )
        generated_files = [
            path for path in development_assets.rglob("*") if path.is_file()
        ]
        self.assertEqual(generated_files, [development_assets / "manifest.json"])

    def test_skill_declares_required_behavior_boundaries(self) -> None:
        """验证 skill_declares_required_behavior_boundaries 场景。"""

        content = "\n".join((root / "SKILL.md").read_text(encoding="utf-8") for root in self.write_skill_roots)
        required = (
            "doc-<项目目录名>",
            "显式确认",
            "if exactly one current knowledge base exists",
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
            "$context-atlas-add",
            "$context-atlas-revise",
            "$context-atlas-retire",
            "Formal writes require explicit invocation",
        ):
            self.assertIn(command, content)

    def test_init_skill_requires_interactive_workspace_profile_selection(self) -> None:
        """交互式初始化不得在用户未选择时静默使用 standard。"""

        skill = (
            self.plugin_root / "skills/context-atlas-init/SKILL.md"
        ).read_text(encoding="utf-8")
        protocol = (self.references_root / "初始化协议.md").read_text(encoding="utf-8")
        for phrase in (
            "proactively offer exactly these two user-facing choices",
            "Do not silently choose `standard`",
            "Always include the selected `project.workspace_profile`",
        ):
            self.assertIn(phrase, skill)
        for phrase in (
            "proactively present `standard`",
            "Do not silently default the interactive workflow",
            "Always record the selected value in `project.workspace_profile`",
        ):
            self.assertIn(phrase, protocol)

    def test_skill_resolves_python_three_portably(self) -> None:
        """Skill 必须优先使用平台原生 Python 3 启动方式并报告探测结果。"""

        runtime_contract = (self.references_root / "宿主执行与运行时探测.md").read_text(
            encoding="utf-8"
        )
        for skill_root in self.write_skill_roots:
            skill_content = (skill_root / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("../../references/宿主执行与运行时探测.md", skill_content)
            content = skill_content + "\n" + runtime_contract
            for phrase in (
                "py -3",
                "python3",
                "Windows Store",
                "9009",
                "zero formal writes",
                "只记录候选命令",
            ):
                self.assertIn(phrase, content, f"{skill_root.name}: {phrase}")

    def test_agent_host_fallback_is_scoped_and_auditable(self) -> None:
        """无 Python 时必须暂存、限制写入范围并降低验证声明。"""

        contract = (self.references_root / "宿主执行与运行时探测.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "agent_host",
            ".context-atlas-tmp/",
            "initialize-<revision-prefix>/",
            "不得在项目根散落其他临时目录",
            "不得直接写正式目标",
            "写入范围只包含暂存目录",
            "deterministic_validation: not_run",
            "不得表述为“确定性验证通过”",
        ):
            self.assertIn(phrase, contract)

        for skill_root in self.write_skill_roots:
            content = (skill_root / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("../../references/宿主执行与运行时探测.md", content)
            self.assertIn("agent_host", content)

    def test_relation_and_impact_reference_explains_human_decision_boundary(self) -> None:
        """Skill 必须解释统一链接、三级结果和人工确认边界。"""

        content = (self.references_root / "关系与影响分析.md").read_text(
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

        assets = self.assets_root / "templates" / "core" / "doc-project"

        self.assertTrue((assets / "02-架构与契约/关系目录.md").is_file())
        self.assertTrue((assets / "03-变更与证据/影响记录/TEMPLATE.md").is_file())
        self.assertFalse((assets / "03-变更与证据/任务包").exists())

    def test_scenario_guide_is_packaged_with_the_core_template(self) -> None:
        """安装形态必须携带目标知识库可持久读取的场景指南。"""

        guide = (
            self.assets_root
            / "templates/core/doc-project/05-知识治理/使用场景.md"
        )

        self.assertTrue(guide.is_file())
        content = guide.read_text(encoding="utf-8")
        self.assertIn("最多 20 个分别定位的来源", content)
        self.assertIn("Proposal 确认边界", content)

    def test_database_reference_and_simplified_templates_are_packaged(self) -> None:
        """Skill 必须解释数据库细节并包含数据源与数据表模板。"""

        reference = (self.references_root / "数据库知识.md").read_text(
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
            self.assets_root / "templates/core/doc-project/02-架构与契约/数据库"
        )
        for relative in ("数据源模板/TEMPLATE.md", "数据表模板/TEMPLATE.md"):
            self.assertTrue((database_root / relative).is_file(), relative)

    def test_skill_state_machine_has_confirmation_and_revision_gates(self) -> None:
        """验证 skill_state_machine_has_confirmation_and_revision_gates 场景。"""

        content = (self.references_root / "执行状态机.md").read_text(
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

        identity = (self.references_root / "身份与主动采集.md").read_text(
            encoding="utf-8"
        )
        migration = (self.references_root / "兼容与迁移.md").read_text(
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
            "upgrade-propose",
            "upgrade-apply",
            "proposal_revision",
            "内嵌来源对象",
            "公共来源",
        ):
            self.assertIn(phrase, migration)

    def test_proposal_and_report_references_use_state_machine_contract(self) -> None:
        """验证 proposal_and_report_references_use_state_machine_contract 场景。"""

        proposal = (self.references_root / "知识采集与确认.md").read_text(
            encoding="utf-8"
        )
        report = (self.references_root / "验证与结果报告.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("proposal_revision", proposal)
        self.assertIn("confirmed_revision", proposal)
        self.assertIn("只展示分类数量、摘要、哈希", proposal)
        self.assertIn("暂不处理", proposal)
        self.assertIn("confirmation_status: observed", proposal)
        self.assertIn("Confirmation state", report)
        self.assertIn("Validation result", report)
        self.assertIn("not_validated", report)
        self.assertIn("Post-initialization smoke", report)

    def test_initialization_skill_guards_real_world_review_failures(self) -> None:
        """初始化 Skill 必须约束完整展示、延后项、敏感配置与使用冒烟。"""

        skill = (self.skill_roots[0] / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "count-only summary",
            "temporary JSON path",
            "postpones them",
            "never invent `confirmed_at`",
            "credential-bearing configuration",
            "bounded `graph`",
        ):
            self.assertIn(phrase, skill)

        ingest = (self.skill_roots[3] / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("supplies no source", ingest)
        self.assertIn("source_count: 0", ingest)

    def test_capture_protocol_has_one_runtime_authority_and_thin_skills(self) -> None:
        """知识采集完整执行语义必须集中在 references，Skill 只做薄编排。"""

        protocol = (self.references_root / "知识采集与确认.md").read_text(
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

        for skill_root in self.write_skill_roots:
            skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("../../references/知识采集与确认.md", skill)
            self.assertNotIn("## Source types", skill)
            self.assertNotIn("## Proposal contract", skill)

    def test_skill_ui_metadata_is_readable_and_legacy_assets_are_absent(self) -> None:
        """验证 skill_ui_metadata_is_readable_and_legacy_assets_are_absent 场景。"""

        metadata = "\n".join((root / "agents/openai.yaml").read_text(encoding="utf-8") for root in self.skill_roots)
        manifest = json.loads(
            (self.assets_root / "manifest.json").read_text(encoding="utf-8")
        )

        self.assertIn('display_name: "context-atlas-work"', metadata)
        self.assertIn('display_name: "context-atlas-init"', metadata)
        self.assertIn('display_name: "context-atlas-navigate"', metadata)
        self.assertIn('display_name: "context-atlas-review"', metadata)
        self.assertIn('display_name: "context-atlas-ingest"', metadata)
        self.assertIn('display_name: "context-atlas-add"', metadata)
        self.assertIn('display_name: "context-atlas-revise"', metadata)
        self.assertIn('display_name: "context-atlas-retire"', metadata)
        self.assertIn('display_name: "context-atlas-upgrade"', metadata)
        self.assertIn("$context-atlas-work", metadata)
        self.assertIn("$context-atlas-init", metadata)
        self.assertIn("$context-atlas-navigate", metadata)
        self.assertIn("$context-atlas-review", metadata)
        self.assertIn("$context-atlas-ingest", metadata)
        self.assertIn("$context-atlas-add", metadata)
        self.assertIn("$context-atlas-revise", metadata)
        self.assertIn("$context-atlas-retire", metadata)
        self.assertIn("$context-atlas-upgrade", metadata)

        for name in ("context-atlas-init", "context-atlas-add", "context-atlas-revise", "context-atlas-retire"):
            skill_metadata = (
                self.plugin_root / f"skills/{name}/agents/openai.yaml"
            ).read_text(encoding="utf-8")
            self.assertIn("allow_implicit_invocation: false", skill_metadata)
        self.assertFalse(Path("skills/project-knowledge-context").exists())
        self.assertFalse(Path("profiles").exists())
        self.assertFalse(any(path.startswith("profiles/") for path in manifest["files"]))

    def test_maintenance_and_upgrade_skills_have_separate_responsibilities(self) -> None:
        """三类项目知识维护、混合编排与格式升级必须具有互斥职责。"""

        add = (self.plugin_root / "skills/context-atlas-add/SKILL.md").read_text(encoding="utf-8")
        revise = (self.plugin_root / "skills/context-atlas-revise/SKILL.md").read_text(encoding="utf-8")
        retire = (self.plugin_root / "skills/context-atlas-retire/SKILL.md").read_text(encoding="utf-8")
        upgrade = (self.plugin_root / "skills/context-atlas-upgrade/SKILL.md").read_text(encoding="utf-8")
        work = (self.plugin_root / "skills/context-atlas-work/SKILL.md").read_text(encoding="utf-8")

        for maintenance in (add, revise, retire):
            self.assertIn("$context-atlas-upgrade", maintenance)
            self.assertNotIn("upgrade-diagnose -> upgrade-propose", maintenance)
            self.assertIn("must not own a mixed Proposal", maintenance)
        self.assertIn("stable IDs", add)
        self.assertIn("`patch`", revise)
        self.assertIn("a successor will become current", revise)
        self.assertIn("archive-propose", retire)
        self.assertIn("does not establish supersession", retire)
        self.assertIn("only owner of a Proposal that mixes", work)
        self.assertIn("upgrade-diagnose -> upgrade-propose", upgrade)
        self.assertIn("never add, revise, retire, approve, or reinterpret project knowledge", upgrade)

    def test_skill_frontmatter_matches_official_constraints(self) -> None:
        """验证 skill_frontmatter_matches_official_constraints 场景。"""

        for skill_root in self.skill_roots:
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

    def test_installed_assets_exactly_match_manifest(self) -> None:
        """构建产物不得遗漏清单文件，也不得夹带未声明运行资产。"""

        manifest = json.loads(
            (self.assets_root / "manifest.json").read_text(encoding="utf-8")
        )
        actual = {
            path.relative_to(self.assets_root).as_posix()
            for path in self.assets_root.rglob("*")
            if path.is_file() and path.name != "manifest.json"
        }
        self.assertEqual(actual, set(manifest["files"]))

    def test_asset_materializer_rejects_escape_and_cleans_target(self) -> None:
        """资产清单不得越出源码根目录，失败后不保留半成品。"""

        from scripts.project_kb.plugin_assets import materialize_plugin_assets

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            target = root / "target"
            (source / "assets").mkdir(parents=True)
            (source / "assets/manifest.json").write_text(
                json.dumps({"files": ["../outside.txt"]}), encoding="utf-8"
            )
            with self.assertRaises(ValueError):
                materialize_plugin_assets(source, target)
            self.assertFalse(target.exists())

    def test_asset_materializer_copies_only_declared_files(self) -> None:
        """资产生成器只复制清单声明的唯一源码。"""

        from scripts.project_kb.plugin_assets import materialize_plugin_assets

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            target = root / "target"
            (source / "assets").mkdir(parents=True)
            (source / "assets/manifest.json").write_text(
                json.dumps({"files": ["declared.txt"]}), encoding="utf-8"
            )
            (source / "declared.txt").write_text("declared\n", encoding="utf-8")
            (source / "not-declared.txt").write_text("extra\n", encoding="utf-8")

            materialize_plugin_assets(source, target)

            self.assertTrue((target / "manifest.json").is_file())
            self.assertEqual((target / "declared.txt").read_text(), "declared\n")
            self.assertFalse((target / "not-declared.txt").exists())

    def test_asset_materializer_rejects_missing_source_and_cleans_target(self) -> None:
        """清单引用不存在的源码时构建必须失败且清理半成品。"""

        from scripts.project_kb.plugin_assets import materialize_plugin_assets

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            target = root / "target"
            (source / "assets").mkdir(parents=True)
            (source / "assets/manifest.json").write_text(
                json.dumps({"files": ["missing.txt"]}), encoding="utf-8"
            )
            with self.assertRaises(FileNotFoundError):
                materialize_plugin_assets(source, target)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
