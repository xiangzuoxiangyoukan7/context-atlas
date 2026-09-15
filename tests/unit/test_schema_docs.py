"""验证 Schema 自动文档生成。"""

from pathlib import Path
import unittest

from scripts.generate_schema_docs import render

ROOT=Path(__file__).resolve().parents[2]

class SchemaDocsTests(unittest.TestCase):
    """确保生成结果稳定且仓库文档没有过期。"""

    def test_generated_schema_document_is_current(self) -> None:
        """验证提交的字段说明与当前 Schema 完全一致。"""
        expected=render(ROOT/"schemas")
        self.assertEqual(expected,(ROOT/"schemas"/"字段说明.md").read_text(encoding="utf-8"))

    def test_generated_document_contains_rules_and_enum_conditions(self) -> None:
        """验证生成文档包含规则和枚举使用条件。"""
        body=render(ROOT/"schemas")
        self.assertIn("RULE-SCHEMA-需求-就绪状态必须满足下阶段条件",body)
        self.assertIn("使用条件",body)
        self.assertIn("batch-ingest-report.schema.json",body)

if __name__ == "__main__": unittest.main()
