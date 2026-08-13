"""test_plugin_contract 自动化测试。"""

from __future__ import annotations

import re
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.project_kb.plugin_contract import (
    load_plugin_manifests,
    validate_plugin_contract,
)


ROOT = Path(__file__).resolve().parents[2]


class PluginContractTests(unittest.TestCase):
    """验证 PluginContractTests 相关行为。"""

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
        self.assertTrue(codex["interface"]["displayName"])
        self.assertTrue(codex["interface"]["defaultPrompt"])

    def test_shared_skill_is_the_only_context_atlas_skill(self) -> None:
        """验证 shared_skill_is_the_only_context_atlas_skill 场景。"""

        skill_files = sorted(
            path
            for path in ROOT.rglob("SKILL.md")
            if ".worktrees" not in path.relative_to(ROOT).parts
        )
        named = [
            path
            for path in skill_files
            if "name: context-atlas" in path.read_text(encoding="utf-8")
        ]

        self.assertEqual([ROOT / "skills" / "context-atlas" / "SKILL.md"], named)
        self.assertFalse((ROOT / ".claude-plugin" / "skills").exists())
        self.assertFalse((ROOT / ".codex-plugin" / "skills").exists())

    def test_repository_contract_has_no_errors(self) -> None:
        """验证 repository_contract_has_no_errors 场景。"""

        self.assertEqual([], validate_plugin_contract(ROOT))

    def test_plugin_contract_ignores_other_git_worktrees(self) -> None:
        """插件唯一性只统计当前工作区，不统计 `.worktrees` 下的分支副本。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / ".claude-plugin", root / ".claude-plugin")
            shutil.copytree(ROOT / ".codex-plugin", root / ".codex-plugin")
            canonical = root / "skills/context-atlas/SKILL.md"
            canonical.parent.mkdir(parents=True)
            canonical.write_text("---\nname: context-atlas\n---\n", encoding="utf-8")
            duplicate = root / ".worktrees/old/skills/context-atlas/SKILL.md"
            duplicate.parent.mkdir(parents=True)
            duplicate.write_text("---\nname: context-atlas\n---\n", encoding="utf-8")

            errors = validate_plugin_contract(root)

        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
