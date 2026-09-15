"""验证自包含 JSON Schema 执行层。"""

from pathlib import Path
import json
import unittest

from scripts.project_kb.json_schema import LocalSchemaRegistry, SchemaValidationError, validate_instance

ROOT=Path(__file__).resolve().parents[2]

class JsonSchemaTests(unittest.TestCase):
    """覆盖本地引用、条件、枚举和网络拒绝。"""

    def setUp(self) -> None:
        """建立共享的本地 Schema 注册表。"""
        self.registry=LocalSchemaRegistry(ROOT/"schemas")

    def test_embedded_source_requires_confirmation_time(self) -> None:
        """验证来源确认必须同时提供确认时间。"""
        schema,path=self.registry.load("embedded-source.schema.json")
        value={"type":"user_statement","reference":"当前会话","observed_at":"2026-09-15T00:00:00+08:00","confirmation_status":"confirmed"}
        self.assertTrue(validate_instance(value,schema,self.registry,schema_path=path))
        value["confirmed_at"]="2026-09-15T00:01:00+08:00"
        self.assertFalse(validate_instance(value,schema,self.registry,schema_path=path))

    def test_batch_report_resolves_ingest_schema_locally(self) -> None:
        """验证批量报告能离线解析单项摄取 Schema。"""
        schema,path=self.registry.load("batch-ingest-report.schema.json")
        report={"operation":"batch_ingest","status":"blocked","source_count":21,"reports":[],"route_plan":[],"writes_performed":False,"confirmation_state":"not_applicable"}
        self.assertFalse(validate_instance(report,schema,self.registry,schema_path=path))

    def test_remote_resolution_is_forbidden(self) -> None:
        """验证远程 Schema 地址不会触发网络解析。"""
        with self.assertRaisesRegex(SchemaValidationError,"remote schema resolution is forbidden"):
            self.registry.load("https://example.com/unknown.schema.json")

    def test_schema_catalog_executes_nested_standard_constraints(self) -> None:
        """验证知识目录会执行标准层，而不只检查旧顶层键。"""

        from scripts.project_kb.schema_catalog import SchemaCatalog
        catalog=SchemaCatalog.load(ROOT/"schemas")
        metadata={"id":"MOD-QUERY","type":"module","title":"查询模块","status":"proposed","paths":[],"sources":[],"last_updated":"2026-09-15"}
        issues=catalog.validate("module",metadata,Path("MOD-QUERY-查询模块.md"))
        self.assertIn("KB_JSON_SCHEMA",{issue.code for issue in issues})

    def test_all_declared_valid_examples_pass_standard_execution(self) -> None:
        """验证所有当前 Schema 的合法示例都能被标准执行层接受。"""

        for path in (ROOT / "schemas").glob("*.schema.json"):
            if path.name == "schema-meta.schema.json":
                continue
            schema=json.loads(path.read_text(encoding="utf-8"))
            for index,example in enumerate(schema.get("examples",[])):
                with self.subTest(schema=path.name,example=index):
                    self.assertEqual([],validate_instance(example,schema,self.registry,schema_path=path))

    def test_deterministic_schema_rules_map_to_implemented_diagnostics(self) -> None:
        """验证确定性规则不引用检查器中不存在的诊断代码。"""

        implementation="\n".join(path.read_text(encoding="utf-8") for path in (ROOT/"scripts").rglob("*.py"))
        for path in (ROOT/"schemas").glob("*.json"):
            payload=json.loads(path.read_text(encoding="utf-8"))
            rules=payload.get("x-context-atlas",{}).get("rules",[])
            for schema_rule in rules:
                if schema_rule.get("enforcement") == "deterministic":
                    with self.subTest(schema=path.name,rule=schema_rule.get("id")):
                        self.assertIn(schema_rule["diagnostic_code"],implementation)

if __name__ == "__main__": unittest.main()
