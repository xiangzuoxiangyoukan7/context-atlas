"""验证子表到主表字段的逻辑外键和已有物理约束记录。"""

from __future__ import annotations

from pathlib import Path

from scripts.project_kb.database import validate_database_relations
from scripts.project_kb.discovery import discover_records
from scripts.project_kb.relation_catalog import RelationCatalog
from scripts.project_kb.relations import RelationIndex
from tests.helpers import TempDirectoryTestCase


ROOT = Path(__file__).resolve().parents[2]
FIELD_HEADER = (
    "| 字段编号 | 字段名 | 数据类型 | 可空 | 默认值 | 中文含义 | 值域类型 | "
    "允许值或最小值 | 最大值或格式 | 允许其他值 | 约束执行位置 | 来源 | 锚点 |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
)
RELATION_HEADER = (
    "| 关系编号 | 子字段编号 | 主表与字段 | 物理约束 | 约束名称 |\n"
    "| --- | --- | --- | --- | --- |\n"
)


def _field_row(identifier: str, name: str) -> str:
    """生成具有块锚点的最小合法字段行。"""

    return (
        f"| {identifier} | {name} | bigint | 否 | — | 字段含义 | 任意 | — | 任意整数 | 否 | "
        f"数据库约束 | [[来源|SRC-001]] | ^{identifier} |\n"
    )


class DatabaseRelationTests(TempDirectoryTestCase):
    """验证逻辑外键始终从子表字段精确链接到主表字段。"""

    def _write(self, path: Path, identifier: str, relation: str, body: str) -> None:
        """写入测试使用的数据库表文档。"""

        path.write_text(
            f"---\nid: {identifier}\ntype: database_table\n{relation}---\n{body}",
            encoding="utf-8",
        )

    def _build(self) -> tuple[list[object], RelationIndex]:
        """发现临时文档并构造统一关系索引。"""

        records, discovery_issues = discover_records(self.root, frozenset())
        self.assertEqual([], discovery_issues)
        catalog = RelationCatalog.load(ROOT / "schemas/relation-catalog.json")
        index, relation_issues = RelationIndex.build(self.root, records, catalog)
        self.assertEqual([], relation_issues)
        return records, index

    def _write_parent_and_child(
        self,
        mapping_row: str,
        parent_relation: bool = True,
    ) -> tuple[list[object], RelationIndex]:
        """写入主表、子表字段及可选的父表关系。"""

        self._write(
            self.root / "主表.md",
            "TABLE-ORDER",
            "",
            "## 字段定义\n\n" + FIELD_HEADER + _field_row("FIELD-ORDER-001", "id"),
        )
        relation = (
            'rel_logical_parent:\n  - "[[主表|TABLE-ORDER]]"\n'
            if parent_relation
            else ""
        )
        self._write(
            self.root / "子表.md",
            "TABLE-ITEM",
            relation,
            "## 字段定义\n\n"
            + FIELD_HEADER
            + _field_row("FIELD-ITEM-001", "order_id")
            + "\n## 主子表关系\n\n"
            + RELATION_HEADER
            + mapping_row,
        )
        return self._build()

    def test_logical_foreign_key_links_exact_parent_field(self) -> None:
        """无物理约束时仍保留子字段、主表文件和主字段精确映射。"""

        row = (
            "| FK-ITEM-001 | FIELD-ITEM-001 | "
            "[[主表#^FIELD-ORDER-001|FIELD-ORDER-001]] | 否 | — |\n"
        )
        records, index = self._write_parent_and_child(row)

        issues = validate_database_relations(self.root, records, index)

        self.assertEqual([], issues)
        target = index.target("FIELD-ORDER-001")
        self.assertIsNotNone(target)
        assert target is not None
        self.assertEqual("^FIELD-ORDER-001", target.anchor)

    def test_existing_physical_foreign_key_requires_constraint_name(self) -> None:
        """如实填写存在物理外键时必须同时保存真实约束名称。"""

        row = (
            "| FK-ITEM-001 | FIELD-ITEM-001 | "
            "[[主表#^FIELD-ORDER-001|FIELD-ORDER-001]] | 是 | — |\n"
        )
        records, index = self._write_parent_and_child(row)

        issues = validate_database_relations(self.root, records, index)

        self.assertIn("KB_DB_PHYSICAL_FK", {issue.code for issue in issues})

    def test_mapping_requires_logical_parent_relation(self) -> None:
        """正文映射不能绕过统一关系字段形成第二套文档关系。"""

        row = (
            "| FK-ITEM-001 | FIELD-ITEM-001 | "
            "[[主表#^FIELD-ORDER-001|FIELD-ORDER-001]] | 否 | — |\n"
        )
        records, index = self._write_parent_and_child(row, parent_relation=False)

        issues = validate_database_relations(self.root, records, index)

        self.assertIn("KB_DB_PARENT_RELATION", {issue.code for issue in issues})

    def test_unknown_child_or_parent_field_is_rejected(self) -> None:
        """字段映射两端都必须指向实际登记的字段编号。"""

        row = (
            "| FK-ITEM-001 | FIELD-ITEM-999 | "
            "[[主表#^FIELD-ORDER-999|FIELD-ORDER-999]] | 否 | — |\n"
        )
        records, index = self._write_parent_and_child(row)

        issues = validate_database_relations(self.root, records, index)
        codes = {issue.code for issue in issues}

        self.assertIn("KB_DB_CHILD_FIELD", codes)
        self.assertIn("KB_DB_PARENT_FIELD", codes)
