"""test_golden_examples 自动化测试。"""

import json
from pathlib import Path
import subprocess
import sys
import unittest

EXAMPLES = ("single-stack", "multi-stack")


def relative_files(root: Path) -> list[str]:
    """提供 relative_files 测试辅助行为。"""

    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file())


class GoldenExampleTests(unittest.TestCase):
    """验证 GoldenExampleTests 相关行为。"""

    def test_examples_include_governed_data_assets(self) -> None:
        """验证 examples_include_governed_data_assets 场景。"""

        expected_types = {
            "single-stack": "source_types: [database]",
            "multi-stack": "source_types: [database, api, file]",
        }
        for name, expected in expected_types.items():
            path = Path("examples") / name / "02-架构与契约/数据资产/DATA-001-知识项.md"
            self.assertTrue(path.is_file(), path)
            content = path.read_text(encoding="utf-8")
            self.assertIn(expected, content)
            self.assertIn("../数据库/DB-001.md", content)

    def test_examples_include_complete_data_source_mappings(self) -> None:
        """验证 examples_include_complete_data_source_mappings 场景。"""

        expected_rows = {
            "single-stack": (
                "| database | 知识项存储 | 流入 | 保存并提供虚构知识项数据 | "
                "[DB-001](../数据库/DB-001.md) |",
            ),
            "multi-stack": (
                "| database | 知识项存储 | 流入 | 保存并提供虚构知识项数据 | "
                "[DB-001](../数据库/DB-001.md) |",
                "| api | 知识查询接口 | 流出 | 向查询组件提供虚构知识项 | "
                "[CONTRACT-001](../CONTRACT-001.md) |",
                "| file | 知识项导入文件 | 流入 | 批量导入虚构知识项 | "
                "[FILE-001](../FILE-001.md) |",
            ),
        }
        link_targets = {
            "single-stack": ("../数据库/DB-001.md",),
            "multi-stack": (
                "../数据库/DB-001.md",
                "../CONTRACT-001.md",
                "../FILE-001.md",
            ),
        }

        for name, rows in expected_rows.items():
            with self.subTest(name=name):
                path = Path("examples") / name / "02-架构与契约/数据资产/DATA-001-知识项.md"
                content = path.read_text(encoding="utf-8")
                self.assertIn("| 来源类型 | 名称 | 流向 | 用途 | 技术契约 |", content)
                for row in rows:
                    self.assertIn(row, content)
                for target in link_targets[name]:
                    self.assertTrue((path.parent / target).resolve().is_file(), target)

    def test_all_golden_examples_validate_with_bundled_checkers(self) -> None:
        """验证 all_golden_examples_validate_with_bundled_checkers 场景。"""

        for name in EXAMPLES:
            with self.subTest(name=name):
                root = Path("examples") / name
                result = subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        str(root / ".project-kb/scripts/check_knowledge_base.py"),
                        str(root),
                        "--schema-root",
                        str(root / ".project-kb/schemas"),
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
                )

    def test_example_structures_match_snapshot(self) -> None:
        """验证 example_structures_match_snapshot 场景。"""

        expected = json.loads(
            Path("tests/snapshots/expected-structures.json").read_text(encoding="utf-8")
        )
        actual = {name: relative_files(Path("examples") / name) for name in EXAMPLES}

        self.assertEqual(actual, expected)

    def test_single_and_multi_stack_use_the_same_core_paths(self) -> None:
        """验证 single_and_multi_stack_use_the_same_core_paths 场景。"""

        single = relative_files(Path("examples") / "single-stack")
        multi = relative_files(Path("examples") / "multi-stack")
        self.assertEqual(single, multi)


if __name__ == "__main__":
    unittest.main()
