import json
from pathlib import Path
import re
import tempfile
import unittest


SKILL_ROOT = Path("skills/project-knowledge-base")
REFERENCES = (
    "初始化协议.md",
    "知识采集与确认.md",
    "更新冲突与归档.md",
    "验证与结果报告.md",
)


class SkillPackageTests(unittest.TestCase):
    def test_skill_has_required_progressive_disclosure_files(self) -> None:
        self.assertTrue((SKILL_ROOT / "SKILL.md").is_file())
        self.assertTrue((SKILL_ROOT / "agents/openai.yaml").is_file())
        for name in REFERENCES:
            self.assertTrue((SKILL_ROOT / "references" / name).is_file(), name)
        self.assertFalse((SKILL_ROOT / "README.md").exists())

    def test_installed_skill_contains_all_runtime_assets(self) -> None:
        assets = SKILL_ROOT / "assets"
        manifest = json.loads((assets / "manifest.json").read_text(encoding="utf-8"))
        missing = [path for path in manifest["files"] if not (assets / path).is_file()]

        self.assertEqual(missing, [])

    def test_skill_assets_match_canonical_sources(self) -> None:
        from scripts.sync_skill_assets import sync_assets

        mismatches = sync_assets(Path.cwd(), SKILL_ROOT, check=True)

        self.assertEqual(mismatches, [])

    def test_skill_declares_required_behavior_boundaries(self) -> None:
        content = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        required = (
            "doc-<项目目录名>",
            "显式确认",
            "目标已存在",
            "AGENTS.md",
            "CLAUDE.md",
            "references/初始化协议.md",
            "references/知识采集与确认.md",
            "references/更新冲突与归档.md",
            "references/验证与结果报告.md",
        )
        for phrase in required:
            self.assertIn(phrase, content)

    def test_skill_ui_metadata_is_readable_and_legacy_assets_are_absent(self) -> None:
        metadata = (SKILL_ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
        manifest = json.loads(
            (SKILL_ROOT / "assets/manifest.json").read_text(encoding="utf-8")
        )

        self.assertIn('display_name: "项目知识库"', metadata)
        self.assertIn("$project-knowledge-base", metadata)
        self.assertFalse(Path("skills/project-knowledge-context").exists())
        self.assertFalse(Path("profiles").exists())
        self.assertFalse(any(path.startswith("profiles/") for path in manifest["files"]))

    def test_skill_frontmatter_matches_official_constraints(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
