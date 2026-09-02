"""test_data_assets 自动化测试。"""

from pathlib import Path
import unittest

from scripts.project_kb.schema_catalog import SchemaCatalog


class DataAssetSchemaTests(unittest.TestCase):
    """验证 DataAssetSchemaTests 相关行为。"""

    def setUp(self) -> None:
        """初始化当前测试所需的隔离环境。"""

        self.catalog = SchemaCatalog.load(Path("schemas"))
        self.path = Path("DATA-001.md")
        self.metadata = {
            "id": "DATA-001",
            "type": "data_asset",
            "title": "客户信息",
            "status": "proposed",
            "version": "0.1.0",
            "sources": ["SRC-001"],
            "owner": "missing",
            "source_types": ["database", "api"],
            "independence_basis": ["cross_feature"],
            "sensitivity": "missing",
            "retention": "missing",
            "last_updated": "2026-08-10",
        }

    def test_valid_data_asset_metadata_passes_schema(self) -> None:
        """验证 valid_data_asset_metadata_passes_schema 场景。"""

        self.assertEqual(
            self.catalog.validate("data_asset", self.metadata, self.path),
            [],
        )

    def test_data_asset_rejects_unknown_source_type(self) -> None:
        """验证 data_asset_rejects_unknown_source_type 场景。"""

        self.metadata["source_types"] = ["database", "spreadsheet"]
        codes = {
            issue.code
            for issue in self.catalog.validate("data_asset", self.metadata, self.path)
        }
        self.assertIn("KB_SCHEMA_ENUM", codes)

    def test_data_asset_requires_governance_fields(self) -> None:
        """验证 data_asset_requires_governance_fields 场景。"""

        for field in ("owner", "source_types", "independence_basis", "sensitivity", "retention"):
            with self.subTest(field=field):
                metadata = dict(self.metadata)
                metadata.pop(field)
                codes = {
                    issue.code
                    for issue in self.catalog.validate(
                        "data_asset", metadata, self.path
                    )
                }
                self.assertIn("KB_SCHEMA_REQUIRED", codes)


if __name__ == "__main__":
    unittest.main()
