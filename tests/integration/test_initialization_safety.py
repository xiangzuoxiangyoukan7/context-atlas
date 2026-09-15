"""test_initialization_safety 自动化测试。"""

from pathlib import Path
import tempfile
import unittest


class InitializationSafetyTests(unittest.TestCase):
    """验证 InitializationSafetyTests 相关行为。"""

    def test_initialization_refuses_existing_target_without_changes(self) -> None:
        """验证 initialization_refuses_existing_target_without_changes 场景。"""

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

if __name__ == "__main__":
    unittest.main()
