from __future__ import annotations

import re
import unittest
from pathlib import Path

from scripts.project_kb.plugin_contract import (
    load_plugin_manifests,
    validate_plugin_contract,
)


ROOT = Path(__file__).resolve().parents[2]


class PluginContractTests(unittest.TestCase):
    def test_two_platform_manifests_share_identity(self) -> None:
        claude, codex = load_plugin_manifests(ROOT)

        for field in ("name", "version", "description"):
            self.assertEqual(claude[field], codex[field], field)
        self.assertEqual(claude["author"]["name"], codex["author"]["name"])
        self.assertEqual("context-atlas", claude["name"])
        self.assertRegex(claude["version"], re.compile(r"^\d+\.\d+\.\d+$"))
        self.assertEqual("./skills/", claude["skills"])
        self.assertEqual("./skills/", codex["skills"])

    def test_manifests_only_use_platform_supported_fields(self) -> None:
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
        skill_files = sorted(ROOT.rglob("SKILL.md"))
        named = [
            path
            for path in skill_files
            if "name: context-atlas" in path.read_text(encoding="utf-8")
        ]

        self.assertEqual([ROOT / "skills" / "context-atlas" / "SKILL.md"], named)
        self.assertFalse((ROOT / ".claude-plugin" / "skills").exists())
        self.assertFalse((ROOT / ".codex-plugin" / "skills").exists())

    def test_repository_contract_has_no_errors(self) -> None:
        self.assertEqual([], validate_plugin_contract(ROOT))


if __name__ == "__main__":
    unittest.main()
