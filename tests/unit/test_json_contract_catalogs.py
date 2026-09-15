"""验证发布 JSON 目录与操作契约具有可执行的语义说明。"""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


def load(relative: str) -> dict[str, object]:
    """读取仓库内的 JSON 对象。"""

    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"JSON root must be an object: {relative}")
    return value


class JsonContractCatalogTests(unittest.TestCase):
    """保证非实体 Schema 的发布 JSON 同样见名知意。"""

    def test_schema_catalog_entries_explain_selection(self) -> None:
        """知识类型目录必须说明类型用途、正反使用条件和当前状态。"""

        catalog = load("schemas/catalog.json")
        self.assertEqual(2, catalog["catalog_version"])
        for kind, entry in catalog["entries"].items():
            with self.subTest(kind=kind):
                self.assertTrue(entry["purpose"])
                self.assertTrue(entry["use_when"])
                self.assertTrue(entry["do_not_use_when"])
                self.assertEqual("active", entry["status"])
                schema = load(f"schemas/{entry['schema']}")
                self.assertEqual(schema["$id"], entry["schema_id"])

    def test_rule_catalog_entries_explain_enforcement(self) -> None:
        """规则目录必须说明触发、执行、诊断和人工判断边界。"""

        catalog = load("rules/catalog.json")
        self.assertEqual(2, catalog["catalog_version"])
        for rule in catalog["rules"]:
            with self.subTest(rule=rule["id"]):
                for field in ("description", "use_when", "enforcement_layers", "diagnostic_codes", "human_review_boundary"):
                    self.assertIn(field, rule)
                self.assertTrue(rule["use_when"])
                self.assertTrue(rule["human_review_boundary"])

    def test_operations_explain_complete_execution_contract(self) -> None:
        """每个操作必须说明何时使用、输入输出、确认与失败行为。"""

        for path in sorted((ROOT / "operations").glob("*.json")):
            operation = load(path.relative_to(ROOT).as_posix())
            with self.subTest(operation=operation["id"]):
                self.assertEqual(2, operation["contract_version"])
                for field in ("description", "use_when", "do_not_use_when", "preconditions", "inputs", "outputs", "failure_modes", "rules"):
                    self.assertTrue(operation[field])
                self.assertIn(operation["execution_mode"], {"read_only", "proposal_gated"})
                self.assertEqual(operation["execution_mode"] == "proposal_gated", operation["confirmation"]["required"])

    def test_supporting_catalogs_explain_policies_and_values(self) -> None:
        """兼容、资产和关系目录必须解释读写、收录和枚举语义。"""

        compatibility = load("compatibility.json")
        for field in ("description", "read_policy", "write_policy", "unknown_version_policy"):
            self.assertTrue(compatibility[field])
        self.assertTrue(all(item["description"] and item["output_policy"] for item in compatibility["conversions"]))

        assets = load("assets/manifest.json")
        for field in ("description", "inclusion_rule", "exclusion_rule", "ordering_rule", "missing_file_policy"):
            self.assertTrue(assets[field])

        relations = load("schemas/relation-catalog.json")
        self.assertTrue(relations["value_semantics"])
        for relation in relations["relations"]:
            self.assertTrue(relation["description"])
            self.assertTrue(relation["use_when"])
            self.assertTrue(relation["do_not_use_when"])


if __name__ == "__main__":
    unittest.main()
