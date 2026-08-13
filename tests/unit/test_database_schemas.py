"""验证数据库分层实体 Schema 和统一父级关系目录。"""

from __future__ import annotations

from pathlib import Path

from scripts.project_kb.relation_catalog import RelationCatalog
from scripts.project_kb.schema_catalog import SchemaCatalog
from tests.helpers import TempDirectoryTestCase


ROOT = Path(__file__).resolve().parents[2]


class DatabaseSchemaTests(TempDirectoryTestCase):
    """验证四类数据库实体具有确定的必填字段、枚举和编号。"""

    def setUp(self) -> None:
        """加载仓库权威 Schema 和关系目录。"""

        super().setUp()
        self.catalog = SchemaCatalog.load(ROOT / "schemas")

    def test_catalog_registers_four_database_entity_types(self) -> None:
        """Schema 目录必须显式登记数据源、数据库单元、命名空间和表。"""

        expected = {
            "data_source",
            "database_unit",
            "database_namespace",
            "database_table",
        }

        self.assertTrue(expected.issubset(self.catalog.schemas))

    def test_database_products_use_controlled_names(self) -> None:
        """数据源产品支持已批准的四种数据库和明确的其他类型。"""

        metadata: dict[str, object] = {
            "id": "DS-ORDER",
            "type": "data_source",
            "title": "订单数据源",
            "status": "approved",
            "product": "sqlite",
            "product_version": "unknown",
            "owner": "example-owner",
            "config_reference": "APP_DB_URL",
            "environments": ["development"],
            "sources": ["SRC-001"],
            "last_updated": "2026-08-13",
        }

        issues = self.catalog.validate(
            "data_source", metadata, self.root / "DS-ORDER.md"
        )

        self.assertIn("KB_SCHEMA_ENUM", {issue.code for issue in issues})

    def test_database_table_requires_parent_and_ddl_sources(self) -> None:
        """业务表必须声明所属层级和专业结构来源。"""

        metadata: dict[str, object] = {
            "id": "TABLE-ORDER",
            "type": "database_table",
            "title": "订单表",
            "status": "approved",
            "version": "1.0.0",
            "owner": "order-team",
            "physical_name": "orders",
            "sensitivity": "internal",
            "sources": ["SRC-001"],
            "last_updated": "2026-08-13",
        }

        issues = self.catalog.validate(
            "database_table", metadata, self.root / "TABLE-ORDER.md"
        )
        messages = {issue.message for issue in issues}

        self.assertIn("missing required field: rel_belongs_to", messages)
        self.assertIn("missing required field: ddl_sources", messages)

    def test_relation_catalog_registers_database_parent_relation(self) -> None:
        """数据库层级必须使用统一正向关系，而不是另设裸编号字段。"""

        catalog = RelationCatalog.load(ROOT / "schemas/relation-catalog.json")
        definition = catalog.get("rel_belongs_to")

        self.assertIsNotNone(definition)
        assert definition is not None
        self.assertEqual(frozenset({"DB", "NS", "TABLE"}), definition.source_prefixes)
        self.assertEqual(frozenset({"DS", "DB", "NS"}), definition.target_prefixes)
