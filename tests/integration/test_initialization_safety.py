from pathlib import Path
import re
import tempfile
import unittest
from urllib.parse import unquote

from scripts.project_kb.links import LINK_PATTERN


class InitializationSafetyTests(unittest.TestCase):
    def test_initialization_refuses_existing_target_without_changes(self) -> None:
        from scripts.project_kb.initializer import initialize_from_assets

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "doc-example"
            target.mkdir()
            sentinel = target / "keep.txt"
            sentinel.write_text("unchanged", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                initialize_from_assets(root, "example")

            self.assertEqual(sentinel.read_text(encoding="utf-8"), "unchanged")

    def test_examples_have_no_adapters_secrets_or_external_relative_links(self) -> None:
        for root in (Path("examples") / name for name in ("single-stack", "multi-stack")):
            self.assertFalse((root / "AGENTS.md").exists(), root)
            self.assertFalse((root / "CLAUDE.md").exists(), root)
            for path in root.rglob("*.md"):
                content = path.read_text(encoding="utf-8")
                self.assertNotIn("-----BEGIN PRIVATE KEY-----", content, path)
                self.assertIsNone(
                    re.search(r"(?im)\b[A-Z0-9_]*(?:TOKEN|PASSWORD|SECRET)\s*[:=]\s*(?!\$\{)", content),
                    path,
                )
                for target in LINK_PATTERN.findall(content):
                    if target.startswith(("http://", "https://", "#", "mailto:")):
                        continue
                    candidate = (path.parent / unquote(target.split("#", 1)[0])).resolve()
                    self.assertTrue(candidate.is_relative_to(root.resolve()), (path, target))
                    self.assertTrue(candidate.exists(), (path, target))


if __name__ == "__main__":
    unittest.main()
