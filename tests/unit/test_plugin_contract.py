"""test_plugin_contract 自动化测试。"""

from __future__ import annotations

import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.project_kb.plugin_contract import (
    load_qoder_manifest,
    load_marketplace_manifests,
    load_plugin_manifests,
    validate_plugin_contract,
)


ROOT = Path(__file__).resolve().parents[2]


class PluginContractTests(unittest.TestCase):
    """验证 PluginContractTests 相关行为。"""

    MARKETPLACE_FILES: tuple[str, str] = (
        ".agents/plugins/marketplace.json",
        ".claude-plugin/marketplace.json",
    )

    @staticmethod
    def _write_plugin_manifests(root: Path) -> None:
        """写入用于错误场景的最小双平台插件清单。"""

        for relative in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                '{"name":"context-atlas","version":"0.1.0","repository":"repo"}',
                encoding="utf-8",
            )

    @staticmethod
    def _write_release_plugin(root: Path) -> None:
        """写入一个满足发布契约的完整临时插件。"""

        codex_manifest = {
            "name": "context-atlas",
            "version": "0.1.0",
            "description": "通过统一协议初始化、维护和验证项目知识库",
            "author": {"name": "Context Atlas Maintainers"},
            "repository": "https://example.invalid/context-atlas",
            "skills": "./skills/",
            "interface": {
                "displayName": "context-atlas",
                "shortDescription": "初始化、维护和验证项目知识库",
                "longDescription": "通过统一 Skill、模板、Schema 和确定性检查器维护可追溯的项目知识库。",
                "developerName": "Context Atlas Maintainers",
                "category": "Productivity",
                "capabilities": ["Interactive", "Write"],
                "defaultPrompt": ["检查当前项目知识库并报告缺失内容。"],
            },
        }
        claude_manifest = {
            key: value
            for key, value in codex_manifest.items()
            if key != "interface"
        }
        (root / ".codex-plugin").mkdir(parents=True, exist_ok=True)
        (root / ".claude-plugin").mkdir(parents=True, exist_ok=True)
        (root / ".codex-plugin" / "plugin.json").write_text(
            json.dumps(codex_manifest, ensure_ascii=False),
            encoding="utf-8",
        )
        (root / ".claude-plugin" / "plugin.json").write_text(
            json.dumps(claude_manifest, ensure_ascii=False),
            encoding="utf-8",
        )
        PluginContractTests._write_valid_marketplaces(root)
        for name in ("context-atlas-work", "context-atlas-init", "context-atlas-navigate", "context-atlas-review", "context-atlas-ingest", "context-atlas-add", "context-atlas-revise", "context-atlas-retire", "context-atlas-upgrade"):
            skill = root / "skills" / name / "SKILL.md"
            skill.parent.mkdir(parents=True, exist_ok=True)
            skill.write_text(f"---\nname: {name}\n---\n", encoding="utf-8")

    @staticmethod
    def _write_marketplaces(root: Path, payload: object) -> None:
        """向两个平台位置写入同一测试载荷。"""

        for relative in PluginContractTests.MARKETPLACE_FILES:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload), encoding="utf-8")

    @staticmethod
    def _write_valid_marketplaces(root: Path) -> None:
        """写入分别符合 Codex 与 Claude 格式的 Marketplace。"""

        codex = {
            "name": "context-atlas",
            "interface": {"displayName": "Context Atlas"},
            "plugins": [{
                "name": "context-atlas",
                "source": {"source": "url", "url": "./"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Productivity",
            }],
        }
        claude = {
            "name": "context-atlas",
            "description": "Official marketplace for Context Atlas",
            "owner": {"name": "Context Atlas Maintainers"},
            "plugins": [{
                "name": "context-atlas",
                "description": "通过统一协议维护项目知识库",
                "version": "0.1.0",
                "source": "./",
                "author": {"name": "Context Atlas Maintainers"},
            }],
        }
        for relative, payload in zip(PluginContractTests.MARKETPLACE_FILES, (codex, claude)):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def test_two_platform_manifests_share_identity(self) -> None:
        """验证 two_platform_manifests_share_identity 场景。"""

        claude, codex = load_plugin_manifests(ROOT)

        for field in ("name", "version", "description"):
            self.assertEqual(claude[field], codex[field], field)
        self.assertEqual(claude["author"]["name"], codex["author"]["name"])
        self.assertEqual("context-atlas", claude["name"])
        self.assertRegex(claude["version"], re.compile(r"^\d+\.\d+\.\d+$"))
        self.assertEqual("./skills/", claude["skills"])
        self.assertEqual("./skills/", codex["skills"])

    def test_manifests_only_use_platform_supported_fields(self) -> None:
        """验证 manifests_only_use_platform_supported_fields 场景。"""

        claude, codex = load_plugin_manifests(ROOT)

        self.assertLessEqual(
            set(claude),
            {
                "name",
                "version",
                "description",
                "author",
                "homepage",
                "repository",
                "license",
                "keywords",
                "skills",
            },
        )
        self.assertNotIn("hooks", codex)
        self.assertIn("interface", codex)
        self.assertEqual(codex["name"], codex["interface"]["displayName"])
        self.assertTrue(codex["interface"]["defaultPrompt"])

    def test_qoder_manifest_shares_identity_without_copying_skills(self) -> None:
        """Qoder 清单共享插件身份，Skill 仍只保留源码根目录一份。"""

        qoder = load_qoder_manifest(ROOT)
        claude, _ = load_plugin_manifests(ROOT)
        for field in ("name", "version", "description"):
            self.assertEqual(claude[field], qoder[field], field)
        self.assertEqual("Context Atlas", qoder["displayName"])
        self.assertEqual("./skills/", qoder["skills"])
        self.assertFalse((ROOT / ".qoder-plugin" / "skills").exists())

    def test_plugin_exposes_nine_capability_skills(self) -> None:
        """插件公开统一工作编排入口与八个专用操作 Skill。"""

        skill_files = sorted(
            path
            for path in ROOT.rglob("SKILL.md")
            if not {".worktrees", ".codex", "build"}.intersection(path.relative_to(ROOT).parts)
        )
        named = [
            path
            for path in skill_files
            if "name: context-atlas-" in path.read_text(encoding="utf-8")
        ]

        self.assertEqual([
            ROOT / "skills" / "context-atlas-add" / "SKILL.md",
            ROOT / "skills" / "context-atlas-ingest" / "SKILL.md",
            ROOT / "skills" / "context-atlas-init" / "SKILL.md",
            ROOT / "skills" / "context-atlas-navigate" / "SKILL.md",
            ROOT / "skills" / "context-atlas-retire" / "SKILL.md",
            ROOT / "skills" / "context-atlas-review" / "SKILL.md",
            ROOT / "skills" / "context-atlas-revise" / "SKILL.md",
            ROOT / "skills" / "context-atlas-upgrade" / "SKILL.md",
            ROOT / "skills" / "context-atlas-work" / "SKILL.md",
        ], named)
        self.assertFalse(any((ROOT / "commands").glob("*.md")))
        self.assertFalse((ROOT / ".claude-plugin" / "skills").exists())
        self.assertFalse((ROOT / ".codex-plugin" / "skills").exists())

    def test_repository_contract_has_no_errors(self) -> None:
        """验证 repository_contract_has_no_errors 场景。"""

        self.assertEqual([], validate_plugin_contract(ROOT))

    def test_marketplace_installation_documentation_covers_user_flow(self) -> None:
        """Marketplace 文档必须覆盖两平台安装、确认门禁和路径替换说明。"""

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        guide_path = ROOT / "packaging/marketplace-installation.md"
        self.assertTrue(guide_path.is_file(), "缺少 Marketplace 安装文档")
        guide = guide_path.read_text(encoding="utf-8")
        evidence = (ROOT / "doc-atlas/03-变更与证据/README.md").read_text(encoding="utf-8")
        combined = "\n".join((readme, guide, evidence))

        for phrase in (
            "不是 Python 包",
            "不需要 `pip install`",
            ".agents/plugins/marketplace.json",
            "context-atlas",
            "新建 Agent 会话",
            "$context-atlas-work",
            "$context-atlas-init",
            "$context-atlas-navigate",
            "$context-atlas-review",
            "$context-atlas-ingest",
            "$context-atlas-add",
            "$context-atlas-revise",
            "$context-atlas-retire",
            "$context-atlas-upgrade",
            "/context-atlas:context-atlas-work",
            "/context-atlas:context-atlas-init",
            "/context-atlas:context-atlas-navigate",
            "/context-atlas:context-atlas-review",
            "/context-atlas:context-atlas-ingest",
            "/context-atlas:context-atlas-add",
            "/context-atlas:context-atlas-revise",
            "/context-atlas:context-atlas-retire",
            "/context-atlas:context-atlas-upgrade",
            "Proposal",
            "用户确认",
            "partial",
            "实际克隆路径",
            "发布仓库对应的 URL",
            "用户级共享安装、项目级启用",
            "不要将其指向目标项目的 `.codex/`",
            '[plugins."context-atlas@context-atlas"]',
            "项目不受信任时",
            "claude plugin marketplace add --scope project",
            "claude plugin install --scope project",
            "默认 scope 是 `user`",
            "context-atlas-qoder-plugin.git",
            "qoder plugins marketplace add",
            "qoder plugins install context-atlas@context-atlas",
            "Marketplace 选择 Project",
            "项目中只维护一套知识库",
            "codex plugin marketplace upgrade context-atlas",
            "codex plugin remove context-atlas@context-atlas",
            "codex plugin list",
            "marketplace add` 只用于首次登记",
            "qoder plugins marketplace update context-atlas",
            "qoder plugins update context-atlas@context-atlas",
            "源码清单版本、Marketplace 远端版本和本地安装版本",
            "九个 Skill 的用途如下",
            "当前用户支持范围是 Codex、Claude Code 和 Qoder",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, combined)

        self.assertIn("Codex", guide)
        self.assertIn("Claude Code", guide)
        self.assertIn("Qoder", guide)
        self.assertIn("Marketplace", guide)

    def test_scenario_guide_has_one_stable_template_source(self) -> None:
        """场景指南必须以模板为唯一规范源，并覆盖第一版用户流程。"""

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        guide_path = (
            ROOT
            / "templates/core/doc-project/05-知识治理/使用场景.md"
        )

        self.assertTrue(guide_path.is_file(), "缺少场景化使用指南")
        self.assertFalse((ROOT / "docs/context-atlas-usage-scenarios.md").exists())
        self.assertIn(
            "./templates/core/doc-project/05-知识治理/使用场景.md",
            readme,
        )

        guide = guide_path.read_text(encoding="utf-8")
        for phrase in (
            "需求来了怎么做",
            "只补充数据库信息",
            "摄取外部资料",
            "最多 20 个分别定位的来源",
            "新增、修订、退役、冲突或不沉淀",
            "自然语言“摄取”请求不触发该 Skill",
            "$context-atlas-add",
            "$context-atlas-revise",
            "$context-atlas-retire",
            "Proposal 确认边界",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, guide)

    def test_two_marketplaces_reference_the_same_plugin(self) -> None:
        """两个 Marketplace 应暴露同一个插件和稳定来源路径。"""

        codex_marketplace, claude_marketplace = load_marketplace_manifests(ROOT)
        self.assertEqual("context-atlas", codex_marketplace["plugins"][0]["name"])
        self.assertEqual("context-atlas", claude_marketplace["plugins"][0]["name"])
        self.assertEqual({"source": "url", "url": "./"}, codex_marketplace["plugins"][0]["source"])
        self.assertEqual("./", claude_marketplace["plugins"][0]["source"])
        self.assertEqual("Productivity", codex_marketplace["plugins"][0]["category"])

    def test_marketplace_type_errors_are_readable(self) -> None:
        """非法 Marketplace 根节点和字段类型应返回可读错误。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{"name": "context-atlas"}', encoding="utf-8")
            for relative in self.MARKETPLACE_FILES:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{"plugins": "not-a-list"}', encoding="utf-8")

            errors = validate_plugin_contract(root)

        self.assertTrue(errors)
        self.assertTrue(any("plugins" in error for error in errors))

    def test_marketplace_missing_file_is_readable(self) -> None:
        """Marketplace 文件缺失时应返回可读错误。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_plugin_manifests(root)
            errors = validate_plugin_contract(root)
        self.assertTrue(any("marketplace.json" in error for error in errors))

    def test_marketplace_invalid_json_is_readable(self) -> None:
        """Marketplace JSON 无效时应返回可读错误。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_plugin_manifests(root)
            self._write_marketplaces(root, {"name": "context-atlas"})
            (root / self.MARKETPLACE_FILES[0]).write_text("{", encoding="utf-8")
            errors = validate_plugin_contract(root)
        self.assertTrue(any("marketplace.json" in error for error in errors))

    def test_marketplace_root_type_is_readable(self) -> None:
        """Marketplace 根节点不是对象时应返回可读错误。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_plugin_manifests(root)
            self._write_marketplaces(root, [])
            errors = validate_plugin_contract(root)
        self.assertTrue(any("marketplace.json" in error and "对象" in error for error in errors))

    def test_marketplace_source_and_policy_types_are_readable(self) -> None:
        """source 与 policy 类型错误时应返回可读错误。"""

        payload = {
            "name": "context-atlas",
            "interface": {},
            "plugins": [{
                "name": "context-atlas",
                "source": "local",
                "policy": "available",
                "category": "Productivity",
            }],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_plugin_manifests(root)
            self._write_marketplaces(root, payload)
            errors = validate_plugin_contract(root)
        self.assertTrue(any("source" in error for error in errors))
        self.assertTrue(any("policy" in error for error in errors))

    def test_marketplace_policy_missing_fields_are_readable(self) -> None:
        """policy 缺少必填字段时应返回可读错误。"""

        payload = {
            "name": "context-atlas", "interface": {},
            "plugins": [{"name": "context-atlas", "source": {"source": "local", "path": "./plugins/context-atlas"},
                         "policy": {}, "category": "Productivity"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_plugin_manifests(root)
            self._write_marketplaces(root, payload)
            errors = validate_plugin_contract(root)
        self.assertTrue(any("installation" in error and "缺少" in error for error in errors))
        self.assertTrue(any("authentication" in error and "缺少" in error for error in errors))

    def test_marketplace_policy_enum_values_are_validated(self) -> None:
        """policy 枚举值必须限制在 Codex 支持范围内。"""

        payload = {
            "name": "context-atlas", "interface": {},
            "plugins": [{"name": "context-atlas", "source": {"source": "local", "path": "./plugins/context-atlas"},
                         "policy": {"installation": "INVALID", "authentication": "INVALID"},
                         "category": "Productivity"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_plugin_manifests(root)
            self._write_marketplaces(root, payload)
            errors = validate_plugin_contract(root)
        self.assertTrue(any("installation" in error and "无效" in error for error in errors))
        self.assertTrue(any("authentication" in error and "无效" in error for error in errors))

    def test_plugin_contract_rejects_worktrees_in_release_package(self) -> None:
        """发布包不得把开发用 `.worktrees` 一并发布。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / ".claude-plugin", root / ".claude-plugin")
            shutil.copytree(ROOT / ".codex-plugin", root / ".codex-plugin")
            self._write_valid_marketplaces(root)
            for name in ("context-atlas-work", "context-atlas-init", "context-atlas-navigate", "context-atlas-review", "context-atlas-ingest", "context-atlas-add", "context-atlas-revise", "context-atlas-retire", "context-atlas-upgrade"):
                canonical = root / "skills" / name / "SKILL.md"
                canonical.parent.mkdir(parents=True, exist_ok=True)
                canonical.write_text(f"---\nname: {name}\n---\n", encoding="utf-8")
            duplicate = root / ".worktrees/old/skills/context-atlas-init/SKILL.md"
            duplicate.parent.mkdir(parents=True)
            duplicate.write_text("---\nname: context-atlas-init\n---\n", encoding="utf-8")

            errors = validate_plugin_contract(root)

        self.assertTrue(any(".worktrees" in error for error in errors), errors)

    def test_repository_contract_rejects_duplicate_or_development_files(self) -> None:
        """运行时发布包不得携带开发入口、测试夹具、`.worktrees` 或第二份同名 Skill。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_release_plugin(root)

            self.assertEqual([], validate_plugin_contract(root))

        for relative, content, expected in (
            ("AGENTS.md", "# dev only\n", "AGENTS.md"),
            ("CLAUDE.md", "# dev only\n", "CLAUDE.md"),
            ("tests/fixtures/sample.txt", "fixture\n", "tests/fixtures"),
            (
                ".worktrees/old/skills/context-atlas-init/SKILL.md",
                "---\nname: context-atlas-init\n---\n",
                ".worktrees",
            ),
            (
                "skills/context-atlas-copy/SKILL.md",
                "---\nname: context-atlas-copy\n---\n",
                "必须且只能存在",
            ),
        ):
            with self.subTest(relative=relative):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    self._write_release_plugin(root)
                    path = root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content, encoding="utf-8")

                    errors = validate_plugin_contract(root)

                self.assertTrue(errors)
                self.assertTrue(any(expected in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
