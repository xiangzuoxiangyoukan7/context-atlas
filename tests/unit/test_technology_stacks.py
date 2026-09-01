"""test_technology_stacks 自动化测试。"""

from pathlib import Path

from scripts.project_kb.validator import ValidationConfig, validate
from tests.helpers import TempDirectoryTestCase, materialize_core_template


class TechnologyStackTests(TempDirectoryTestCase):
    """验证 TechnologyStackTests 相关行为。"""

    def test_single_and_multi_stack_projects_share_one_core_structure(self) -> None:
        """验证 single_and_multi_stack_projects_share_one_core_structure 场景。"""

        cases = {
            "single": "| Java | 21 | app | Spring Boot service | mvn test | application.yml | SRC-001 | approved |",
            "multi": "| Spring Boot | 3.x | backend | API | mvn test | application.yml | SRC-001 | approved |\n| Python | 3.12 | tools | data job | pytest | pyproject.toml | SRC-002 | approved |\n| Vue | 3.x | web | frontend | npm test | package.json | SRC-001 | approved |",
        }
        for name, rows in cases.items():
            with self.subTest(name=name):
                root = materialize_core_template(self.root / name, name)
                technology = root / "02-技术基线" / "系统架构.md"
                content = technology.read_text(encoding="utf-8").replace(
                    "| 待确认 | 待确认 | 待确认 | 待确认 | 待确认 | 待确认 | SRC-001 | missing |",
                    rows,
                )
                technology.write_text(content, encoding="utf-8")
                self.assertEqual(validate(root, ValidationConfig(schema_root=Path("schemas"))), [])
                self.assertFalse((root / ".project-kb" / "profiles").exists())


if __name__ == "__main__":
    import unittest

    unittest.main()
