import json

from tests.helpers import TempDirectoryTestCase
from scripts.project_kb.schema_catalog import SchemaCatalog


class SchemaCatalogTests(TempDirectoryTestCase):
    def write_catalog(self, schema: dict[str, object]) -> None:
        (self.root / "catalog.json").write_text(
            json.dumps({"feature": "feature.schema.json"}),
            encoding="utf-8",
        )
        (self.root / "feature.schema.json").write_text(
            json.dumps(schema),
            encoding="utf-8",
        )

    def test_catalog_reports_invalid_enum(self) -> None:
        self.write_catalog(
            {
                "required": ["id", "status"],
                "enums": {"status": ["proposed", "approved"]},
            }
        )

        issues = SchemaCatalog.load(self.root).validate(
            "feature",
            {"id": "F01", "status": "wrong"},
            self.root / "F01.md",
        )

        self.assertEqual([issue.code for issue in issues], ["KB_SCHEMA_ENUM"])

    def test_catalog_reports_all_supported_constraint_failures(self) -> None:
        self.write_catalog(
            {
                "required": ["id", "status", "sources"],
                "enums": {"status": ["proposed", "approved"]},
                "patterns": {"id": "F\\d{2}"},
                "non_empty_lists": ["sources"],
                "unique_lists": ["sources"],
            }
        )

        issues = SchemaCatalog.load(self.root).validate(
            "feature",
            {"id": "wrong", "status": "wrong", "sources": ["SRC-1", "SRC-1"]},
            self.root / "wrong.md",
        )

        self.assertEqual(
            [issue.code for issue in issues],
            [
                "KB_SCHEMA_ENUM",
                "KB_SCHEMA_PATTERN",
                "KB_SCHEMA_LIST",
            ],
        )

    def test_catalog_reports_missing_required_field(self) -> None:
        self.write_catalog({"required": ["id", "status"]})

        issues = SchemaCatalog.load(self.root).validate(
            "feature",
            {"id": "F01"},
            self.root / "F01.md",
        )

        self.assertEqual([issue.code for issue in issues], ["KB_SCHEMA_REQUIRED"])

    def test_catalog_rejects_schema_path_outside_root(self) -> None:
        outside = self.root.parent / "outside.json"
        outside.write_text("{}", encoding="utf-8")
        (self.root / "catalog.json").write_text(
            json.dumps({"feature": "../outside.json"}),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "schema escapes root"):
            SchemaCatalog.load(self.root)
