"""test_schema_catalog 自动化测试。"""

import json
from pathlib import Path

from tests.helpers import TempDirectoryTestCase
from scripts.project_kb.schema_catalog import SchemaCatalog


class SchemaCatalogTests(TempDirectoryTestCase):
    """验证 SchemaCatalogTests 相关行为。"""

    def write_catalog(self, schema: dict[str, object]) -> None:
        """提供 write_catalog 测试辅助行为。"""

        (self.root / "catalog.json").write_text(
            json.dumps({
                "catalog_version": 2,
                "entries": {
                    "feature": {
                        "schema": "feature.schema.json",
                        "schema_id": schema.get("$id"),
                    }
                },
            }),
            encoding="utf-8",
        )
        (self.root / "feature.schema.json").write_text(
            json.dumps(schema),
            encoding="utf-8",
        )

    def test_catalog_reports_invalid_enum(self) -> None:
        """验证 catalog_reports_invalid_enum 场景。"""

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
        """验证 catalog_reports_all_supported_constraint_failures 场景。"""

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
        """验证 catalog_reports_missing_required_field 场景。"""

        self.write_catalog({"required": ["id", "status"]})

        issues = SchemaCatalog.load(self.root).validate(
            "feature",
            {"id": "F01"},
            self.root / "F01.md",
        )

        self.assertEqual([issue.code for issue in issues], ["KB_SCHEMA_REQUIRED"])

    def test_catalog_reports_invalid_list_enum_member(self) -> None:
        """验证 catalog_reports_invalid_list_enum_member 场景。"""

        self.write_catalog(
            {
                "required": ["source_types"],
                "list_enums": {"source_types": ["database", "api"]},
            }
        )

        issues = SchemaCatalog.load(self.root).validate(
            "feature",
            {"source_types": ["database", "spreadsheet"]},
            self.root / "DATA-001.md",
        )

        self.assertEqual([issue.code for issue in issues], ["KB_SCHEMA_ENUM"])

    def test_catalog_reports_list_enum_field_with_non_list_value(self) -> None:
        """验证 catalog_reports_list_enum_field_with_non_list_value 场景。"""

        self.write_catalog(
            {
                "required": ["source_types"],
                "list_enums": {"source_types": ["database", "api"]},
            }
        )

        issues = SchemaCatalog.load(self.root).validate(
            "feature",
            {"source_types": "database"},
            self.root / "DATA-001.md",
        )

        self.assertEqual([issue.code for issue in issues], ["KB_SCHEMA_LIST"])

    def test_catalog_rejects_schema_path_outside_root(self) -> None:
        """验证 catalog_rejects_schema_path_outside_root 场景。"""

        outside = self.root.parent / "outside.json"
        outside.write_text("{}", encoding="utf-8")
        (self.root / "catalog.json").write_text(
            json.dumps({
                "catalog_version": 2,
                "entries": {
                    "feature": {"schema": "../outside.json", "schema_id": None}
                },
            }),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "schema escapes root"):
            SchemaCatalog.load(self.root)

    def test_catalog_loads_repository_self_describing_requirement(self) -> None:
        """验证仓库中的需求样板通过自描述完整性门禁。"""

        repository_root = Path(__file__).resolve().parents[2]
        catalog = SchemaCatalog.load(repository_root / "schemas")

        self.assertEqual(
            catalog.schemas["requirement"]["x-context-atlas"]["profile"],
            "self_describing/v1",
        )

    def test_catalog_loads_first_self_describing_schema_batch(self) -> None:
        """验证功能、模块和接口均已进入自描述门禁。"""

        repository_root = Path(__file__).resolve().parents[2]
        catalog = SchemaCatalog.load(repository_root / "schemas")

        for kind in ("feature", "module", "interface"):
            with self.subTest(kind=kind):
                extension = catalog.schemas[kind]["x-context-atlas"]
                self.assertEqual(extension["profile"], "self_describing/v1")
                self.assertTrue(extension["rules"])
                self.assertTrue(extension["invalid_examples"])

    def test_catalog_loads_second_self_describing_schema_batch(self) -> None:
        """验证数据源、数据表、数据资产和验收均已进入自描述门禁。"""

        repository_root = Path(__file__).resolve().parents[2]
        catalog = SchemaCatalog.load(repository_root / "schemas")

        for kind in ("data_source", "database_table", "data_asset", "acceptance"):
            with self.subTest(kind=kind):
                extension = catalog.schemas[kind]["x-context-atlas"]
                self.assertEqual(extension["profile"], "self_describing/v1")
                self.assertTrue(extension["rules"])
                self.assertTrue(extension["invalid_examples"])

    def test_catalog_loads_third_self_describing_schema_batch(self) -> None:
        """验证通用知识、索引、托管来源和内嵌来源均已自描述化。"""

        repository_root = Path(__file__).resolve().parents[2]
        catalog = SchemaCatalog.load(repository_root / "schemas")

        for kind in ("knowledge_item", "knowledge_index", "managed_source"):
            with self.subTest(kind=kind):
                extension = catalog.schemas[kind]["x-context-atlas"]
                self.assertEqual(extension["profile"], "self_describing/v1")
                self.assertTrue(extension["rules"])
                self.assertTrue(extension["invalid_examples"])

        embedded = json.loads(
            (repository_root / "schemas/embedded-source.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            embedded["x-context-atlas"]["profile"],
            "self_describing/v1",
        )
        self.assertEqual(
            embedded["x-context-atlas"]["knowledge_type"],
            "embedded_source",
        )

    def test_catalog_loads_fourth_self_describing_schema_batch(self) -> None:
        """验证规格变更、Delta 和知识候选均已进入自描述门禁。"""

        repository_root = Path(__file__).resolve().parents[2]
        catalog = SchemaCatalog.load(repository_root / "schemas")

        for kind in ("specification_change", "specification_delta", "knowledge_proposal"):
            with self.subTest(kind=kind):
                extension = catalog.schemas[kind]["x-context-atlas"]
                self.assertEqual(extension["profile"], "self_describing/v1")
                self.assertTrue(extension["rules"])
                self.assertTrue(extension["invalid_examples"])

    def test_all_current_schema_assets_are_self_describing(self) -> None:
        """验证所有当前 Schema 和关系目录都声明统一自描述 Profile。"""

        repository_root = Path(__file__).resolve().parents[2]
        schema_root = repository_root / "schemas"
        excluded = {"schema-meta.schema.json"}
        current_assets = [
            path for path in schema_root.glob("*.json")
            if path.name not in excluded and path.name != "catalog.json"
        ]

        self.assertGreater(len(current_assets), 0)
        for path in current_assets:
            with self.subTest(schema=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(
                    payload["x-context-atlas"]["profile"],
                    "self_describing/v1",
                )

    def test_current_schema_assets_exclude_legacy_entity_formats(self) -> None:
        """验证旧来源和数据库层级只能作为升级输入，不能作为当前 Schema 发布。"""

        repository_root = Path(__file__).resolve().parents[2]
        schema_root = repository_root / "schemas"

        for filename in (
            "source.schema.json",
            "database-unit.schema.json",
            "database-namespace.schema.json",
        ):
            with self.subTest(schema=filename):
                self.assertFalse((schema_root / filename).exists())

    def test_all_schema_ids_use_one_offline_registry_namespace(self) -> None:
        """验证 Schema 身份统一且可按文件名映射到本地注册表。"""

        repository_root = Path(__file__).resolve().parents[2]
        schema_root = repository_root / "schemas"

        for path in schema_root.glob("*.schema.json"):
            with self.subTest(schema=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(
                    f"https://context-atlas.dev/schemas/{path.name}",
                    payload["$id"],
                )

    def test_catalog_rejects_incomplete_opt_in_schema(self) -> None:
        """验证声明自描述 Profile 后不能遗漏枚举语义。"""

        self.write_catalog(
            {
                "title": "功能",
                "description": "功能 Schema。",
                "x-context-atlas": {
                    "profile": "self_describing/v1",
                    "schema_version": "1.0.0",
                    "knowledge_type": "feature",
                    "purpose": "保存功能。",
                    "use_when": ["存在稳定功能时"],
                    "do_not_use_when": ["仅有任务时"],
                    "canonical_location": "01-功能基线/功能/",
                    "identity_contract": {},
                    "body_contract": {},
                    "lifecycle": {},
                    "compatibility": {},
                    "rules": [],
                },
                "properties": {
                    "status": {
                        "title": "状态",
                        "description": "功能状态。",
                        "oneOf": [
                            {
                                "const": "proposed",
                                "title": "待确认",
                                "description": "功能等待确认。",
                            }
                        ],
                        "examples": ["proposed"],
                    }
                },
                "required": ["status"],
                "enums": {"status": ["proposed"]},
                "examples": [{"status": "proposed"}, {"status": "proposed"}],
            }
        )

        with self.assertRaisesRegex(ValueError, "must explain.*use_when"):
            SchemaCatalog.load(self.root)

    def test_catalog_rejects_invalid_example_with_unknown_rule(self) -> None:
        """验证反例必须引用同一 Schema 中已声明的稳定规则。"""

        repository_root = Path(__file__).resolve().parents[2]
        schema = json.loads(
            (repository_root / "schemas/requirement.schema.json").read_text(encoding="utf-8")
        )
        schema["x-context-atlas"]["invalid_examples"][0]["expected_rule"] = "REQ-UNKNOWN"
        self.write_catalog(schema)

        with self.assertRaisesRegex(ValueError, "references unknown rule"):
            SchemaCatalog.load(self.root)

    def test_catalog_rejects_lifecycle_state_outside_enum(self) -> None:
        """验证生命周期只能引用状态字段登记的枚举值。"""

        repository_root = Path(__file__).resolve().parents[2]
        schema = json.loads(
            (repository_root / "schemas/requirement.schema.json").read_text(encoding="utf-8")
        )
        schema["x-context-atlas"]["knowledge_type"] = "feature"
        schema["x-context-atlas"]["lifecycle"]["terminal_states"] = ["unknown"]
        self.write_catalog(schema)

        with self.assertRaisesRegex(ValueError, "terminal_states must use values"):
            SchemaCatalog.load(self.root)

    def test_requirement_identity_rejects_invalid_date_filename_and_title(self) -> None:
        """验证需求身份同时约束真实日期、文件名和语义名称。"""

        repository_root = Path(__file__).resolve().parents[2]
        catalog = SchemaCatalog.load(repository_root / "schemas")
        metadata = {
            "id": "REQ-ATLAS-20260230-错误名称",
            "type": "requirement",
            "title": "正确名称",
            "status": "proposed",
            "readiness": "draft",
            "priority": "P1",
            "last_updated": "2026-09-15",
        }

        issues = catalog.validate("requirement", metadata, self.root / "其他文件名.md")

        self.assertEqual(
            {"KB_SCHEMA_ID_DATE", "KB_SCHEMA_ID_FILENAME", "KB_SCHEMA_ID_SEMANTIC"},
            {issue.code for issue in issues},
        )
