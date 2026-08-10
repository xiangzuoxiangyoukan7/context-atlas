from pathlib import Path
import unittest

from scripts.project_kb.schema_catalog import SchemaCatalog


class DataAssetSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
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
            "sensitivity": "missing",
            "retention": "missing",
            "last_updated": "2026-08-10",
        }

    def test_valid_data_asset_metadata_passes_schema(self) -> None:
        self.assertEqual(
            self.catalog.validate("data_asset", self.metadata, self.path),
            [],
        )

    def test_data_asset_rejects_unknown_source_type(self) -> None:
        self.metadata["source_types"] = ["database", "spreadsheet"]
        codes = {
            issue.code
            for issue in self.catalog.validate("data_asset", self.metadata, self.path)
        }
        self.assertIn("KB_SCHEMA_ENUM", codes)

    def test_data_asset_requires_governance_fields(self) -> None:
        for field in ("owner", "source_types", "sensitivity", "retention"):
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
