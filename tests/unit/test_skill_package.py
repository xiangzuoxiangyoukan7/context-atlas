"""test_skill_package 自动化测试。"""

import json
from pathlib import Path
import re
import tempfile
import unittest


SKILL_ROOT = Path("skills/context-atlas")
REFERENCES = (
    "初始化协议.md",
    "执行状态机.md",
    "知识采集与确认.md",
    "更新冲突与归档.md",
    "验证与结果报告.md",
    "关系与影响分析.md",
)


class SkillPackageTests(unittest.TestCase):
    """验证 SkillPackageTests 相关行为。"""

    def test_skill_has_required_progressive_disclosure_files(self) -> None:
        """验证 skill_has_required_progressive_disclosure_files 场景。"""

        self.assertTrue((SKILL_ROOT / "SKILL.md").is_file())
        self.assertTrue((SKILL_ROOT / "agents/openai.yaml").is_file())
        for name in REFERENCES:
            self.assertTrue((SKILL_ROOT / "references" / name).is_file(), name)
        self.assertFalse((SKILL_ROOT / "README.md").exists())

    def test_installed_skill_contains_all_runtime_assets(self) -> None:
        """验证 installed_skill_contains_all_runtime_assets 场景。"""

        assets = SKILL_ROOT / "assets"
        manifest = json.loads((assets / "manifest.json").read_text(encoding="utf-8"))
        missing = [path for path in manifest["files"] if not (assets / path).is_file()]

        self.assertEqual(missing, [])

    def test_skill_assets_match_canonical_sources(self) -> None:
        """验证 skill_assets_match_canonical_sources 场景。"""

        from scripts.sync_skill_assets import sync_assets

        mismatches = sync_assets(Path.cwd(), SKILL_ROOT, check=True)

        self.assertEqual(mismatches, [])

    def test_skill_declares_required_behavior_boundaries(self) -> None:
        """验证 skill_declares_required_behavior_boundaries 场景。"""

        content = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        required = (
            "doc-<项目目录名>",
            "显式确认",
            "目标已存在",
            "AGENTS.md",
            "CLAUDE.md",
            "references/初始化协议.md",
            "references/执行状态机.md",
            "references/知识采集与确认.md",
            "references/更新冲突与归档.md",
            "references/验证与结果报告.md",
            "references/关系与影响分析.md",
        )
        for phrase in required:
            self.assertIn(phrase, content)

    def test_relation_and_impact_reference_explains_human_decision_boundary(self) -> None:
        """Skill 必须解释统一链接、三级结果和人工确认边界。"""

        content = (SKILL_ROOT / "references" / "关系与影响分析.md").read_text(
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

        assets = SKILL_ROOT / "assets" / "templates" / "core" / "doc-project"

        self.assertTrue((assets / "02-架构与契约/关系目录.md").is_file())
        self.assertTrue((assets / "03-实施与验收/影响分析/TEMPLATE.md").is_file())

    def test_skill_state_machine_has_confirmation_and_revision_gates(self) -> None:
        """验证 skill_state_machine_has_confirmation_and_revision_gates 场景。"""

        content = (SKILL_ROOT / "references" / "执行状态机.md").read_text(
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

    def test_proposal_and_report_references_use_state_machine_contract(self) -> None:
        """验证 proposal_and_report_references_use_state_machine_contract 场景。"""

        proposal = (SKILL_ROOT / "references" / "知识采集与确认.md").read_text(
            encoding="utf-8"
        )
        report = (SKILL_ROOT / "references" / "验证与结果报告.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("proposal_revision", proposal)
        self.assertIn("confirmed_revision", proposal)
        self.assertIn("Confirmation state", report)
        self.assertIn("Validation result", report)
        self.assertIn("not_validated", report)

    def test_skill_ui_metadata_is_readable_and_legacy_assets_are_absent(self) -> None:
        """验证 skill_ui_metadata_is_readable_and_legacy_assets_are_absent 场景。"""

        metadata = (SKILL_ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
        manifest = json.loads(
            (SKILL_ROOT / "assets/manifest.json").read_text(encoding="utf-8")
        )

        self.assertIn('display_name: "脉络地图"', metadata)
        self.assertIn("$context-atlas", metadata)
        self.assertFalse(Path("skills/project-knowledge-context").exists())
        self.assertFalse(Path("profiles").exists())
        self.assertFalse(any(path.startswith("profiles/") for path in manifest["files"]))

    def test_skill_frontmatter_matches_official_constraints(self) -> None:
        """验证 skill_frontmatter_matches_official_constraints 场景。"""

        content = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)

        self.assertIsNotNone(match)
        assert match is not None
        fields = dict(
            line.split(":", 1)
            for line in match.group(1).splitlines()
            if ":" in line
        )
        self.assertEqual(set(fields), {"name", "description"})
        name = fields["name"].strip()
        description = fields["description"].strip()
        self.assertRegex(name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(name), 64)
        self.assertTrue(description.startswith("Use when"))
        self.assertNotRegex(description, r"[<>]")
        self.assertLessEqual(len(description), 1024)
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
