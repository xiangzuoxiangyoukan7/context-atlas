"""验证 Python 注释与类型标注规范。"""

from __future__ import annotations

# context-atlas-rules: [[rules/知识治理规则#RULE-CODE-001|RULE-CODE-001]]

import tempfile
import unittest
from pathlib import Path

from scripts.check_python_documentation import validate_python_documentation


class PythonDocumentationTests(unittest.TestCase):
    """检查所有 Python 权威源和生成副本的说明完整性。"""

    def test_missing_documentation_and_annotations_are_reported(self) -> None:
        """缺少模块、类、方法说明或类型标注时必须报告。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "undocumented.py"
            source.write_text(
                "class Example:\n"
                "    value = None\n"
                "    def run(self, argument):\n"
                "        return argument\n",
                encoding="utf-8",
            )

            issues = validate_python_documentation(root, [source])

        codes = {issue.code for issue in issues}
        self.assertIn("PY_DOC_MODULE", codes)
        self.assertIn("PY_DOC_CLASS", codes)
        self.assertIn("PY_DOC_FUNCTION", codes)
        self.assertIn("PY_TYPE_ARGUMENT", codes)
        self.assertIn("PY_TYPE_RETURN", codes)
        self.assertIn("PY_TYPE_CLASS_ATTRIBUTE", codes)

    def test_every_tracked_python_file_conforms(self) -> None:
        """仓库中的全部已跟踪 Python 文件必须通过规范检查。"""

        self.assertEqual([], validate_python_documentation(Path.cwd()))

    def test_repository_owned_worktrees_are_not_scanned(self) -> None:
        """主工作区检查不得把其他 Git worktree 的旧代码计入结果。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            current = root / "current.py"
            current.write_text('"""当前代码。"""\n', encoding="utf-8")
            old = root / ".worktrees" / "old" / "undocumented.py"
            old.parent.mkdir(parents=True)
            old.write_text("def old(value):\n    return value\n", encoding="utf-8")

            issues = validate_python_documentation(root)

        self.assertEqual([], issues)


if __name__ == "__main__":
    unittest.main()
