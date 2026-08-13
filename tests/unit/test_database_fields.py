"""验证数据表字段含义、值域、锚点和字段级来源。"""

from __future__ import annotations

from pathlib import Path

from scripts.project_kb.frontmatter import parse_document
from tests.helpers import TempDirectoryTestCase


HEADER = (
    "| 字段编号 | 字段名 | 数据类型 | 可空 | 默认值 | 中文含义 | 值域类型 | "
    "允许值或最小值 | 最大值或格式 | 允许其他值 | 约束执行位置 | 来源 | 锚点 |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
)


class DatabaseFieldTests(TempDirectoryTestCase):
    """验证一表一文件中的字段表可以被机器确定性检查。"""

    def _record(self, rows: str, include_section: bool = True) -> object:
        """写入最小数据库表文档并返回解析记录。"""

        body = f"## 字段定义\n\n{HEADER}{rows}" if include_section else "# 无字段定义\n"
        path = self.root / "TABLE-ORDER.md"
        path.write_text(
            "---\nid: TABLE-ORDER\ntype: database_table\n---\n" + body,
            encoding="utf-8",
        )
        return parse_document(path)

    def test_valid_enum_range_format_and_any_fields_pass(self) -> None:
        """枚举、范围、格式和任意值均有完整表达时应通过。"""

        from scripts.project_kb.database import validate_database_fields

        rows = (
            "| FIELD-ORDER-001 | status | smallint | 否 | 1 | 订单状态 | 枚举 | "
            "1=待处理;2=处理中;3=已完成 | — | 否 | 数据库约束 | "
            "[[00-项目总览/SRC-001|SRC-001]] | ^FIELD-ORDER-001 |\n"
            "| FIELD-ORDER-002 | amount | decimal(10,2) | 否 | 0 | 订单金额 | 范围 | "
            "0 | 99999999.99 | 否 | 应用规则 | [[00-项目总览/SRC-001|SRC-001]] | ^FIELD-ORDER-002 |\n"
            "| FIELD-ORDER-003 | order_no | varchar(32) | 否 | — | 订单编号 | 格式 | "
            "— | ORD-[0-9]{16} | 否 | 应用规则 | [[00-项目总览/SRC-001|SRC-001]] | ^FIELD-ORDER-003 |\n"
            "| FIELD-ORDER-004 | remark | text | 是 | — | 订单备注 | 任意 | "
            "— | 任意文本 | 是 | 仅文档 | [[00-项目总览/SRC-001|SRC-001]] | ^FIELD-ORDER-004 |\n"
        )

        issues = validate_database_fields([self._record(rows)])

        self.assertEqual([], issues)

    def test_missing_field_section_is_rejected(self) -> None:
        """数据表没有字段定义时不能成为可用的基础知识。"""

        from scripts.project_kb.database import validate_database_fields

        issues = validate_database_fields([self._record("", include_section=False)])

        self.assertEqual(["KB_DB_FIELDS_REQUIRED"], [issue.code for issue in issues])

    def test_invalid_field_rows_report_exact_codes(self) -> None:
        """重复编号、值域、锚点和来源问题必须可精确定位。"""

        from scripts.project_kb.database import validate_database_fields

        cases = {
            "duplicate": (
                "| FIELD-ORDER-001 | id | bigint | 否 | — | 主键 | 任意 | — | 任意整数 | 否 | 数据库约束 | [[来源|SRC-001]] | ^FIELD-ORDER-001 |\n"
                "| FIELD-ORDER-001 | other | bigint | 否 | — | 重复 | 任意 | — | 任意整数 | 否 | 数据库约束 | [[来源|SRC-001]] | ^FIELD-ORDER-001 |\n",
                "KB_DB_FIELD_DUPLICATE",
            ),
            "enum": (
                "| FIELD-ORDER-001 | status | int | 否 | 1 | 状态 | 枚举 | 1;2 | — | 否 | 数据库约束 | [[来源|SRC-001]] | ^FIELD-ORDER-001 |\n",
                "KB_DB_FIELD_DOMAIN",
            ),
            "range": (
                "| FIELD-ORDER-001 | amount | int | 否 | 0 | 金额 | 范围 | 10 | 1 | 否 | 应用规则 | [[来源|SRC-001]] | ^FIELD-ORDER-001 |\n",
                "KB_DB_FIELD_DOMAIN",
            ),
            "anchor": (
                "| FIELD-ORDER-001 | id | bigint | 否 | — | 主键 | 任意 | — | 任意整数 | 否 | 数据库约束 | [[来源|SRC-001]] | ^FIELD-WRONG-001 |\n",
                "KB_DB_FIELD_ANCHOR",
            ),
            "source": (
                "| FIELD-ORDER-001 | id | bigint | 否 | — | 主键 | 任意 | — | 任意整数 | 否 | 数据库约束 | SRC-001 | ^FIELD-ORDER-001 |\n",
                "KB_DB_FIELD_SOURCE",
            ),
        }
        for name, (rows, expected) in cases.items():
            with self.subTest(name=name):
                issues = validate_database_fields([self._record(rows)])
                self.assertIn(expected, {issue.code for issue in issues})
