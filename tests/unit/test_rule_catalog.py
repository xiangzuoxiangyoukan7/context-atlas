from __future__ import annotations

# context-atlas-rules: [[rules/知识治理规则#RULE-AGENT-001|RULE-AGENT-001]] [[rules/知识治理规则#RULE-DB-001|RULE-DB-001]] [[rules/知识治理规则#RULE-GOV-001|RULE-GOV-001]] [[rules/知识治理规则#RULE-GOV-002|RULE-GOV-002]] [[rules/知识治理规则#RULE-GOV-003|RULE-GOV-003]] [[rules/知识治理规则#RULE-IMPACT-001|RULE-IMPACT-001]] [[rules/知识治理规则#RULE-REL-001|RULE-REL-001]] [[rules/知识治理规则#RULE-SRC-001|RULE-SRC-001]]

import unittest
import shutil
import tempfile
from pathlib import Path

from scripts.project_kb.rule_catalog import (
    EXPECTED_OPERATION_IDS,
    build_reverse_index,
    build_rule_change_impact,
    load_operations,
    load_rule_catalog,
    validate_rule_coverage,
)


ROOT = Path(__file__).resolve().parents[2]


class RuleCatalogTests(unittest.TestCase):
    def test_authorities_resolve_to_existing_markdown_anchors(self) -> None:
        catalog = load_rule_catalog(ROOT)

        self.assertGreaterEqual(len(catalog), 8)
        for rule in catalog.values():
            self.assertTrue(rule.authority_path.is_file(), rule.id)
            body = rule.authority_path.read_text(encoding="utf-8")
            self.assertIn(f'<a id="{rule.id}"></a>', body, rule.id)

    def test_standard_operations_exist_and_only_reference_known_rules(self) -> None:
        catalog = load_rule_catalog(ROOT)
        operations = load_operations(ROOT)

        self.assertEqual(EXPECTED_OPERATION_IDS, frozenset(operations))
        for operation in operations.values():
            self.assertTrue(operation.name_zh)
            self.assertTrue(operation.rules)
            self.assertLessEqual(operation.rules, frozenset(catalog), operation.id)

    def test_consumers_form_a_complete_reverse_index(self) -> None:
        catalog = load_rule_catalog(ROOT)
        reverse_index = build_reverse_index(ROOT)

        self.assertEqual(set(catalog), set(reverse_index))
        self.assertFalse(validate_rule_coverage(ROOT))
        self.assertTrue(
            any(consumer.kind == "skill" for consumer in reverse_index["RULE-AGENT-001"])
        )
        self.assertTrue(
            any(consumer.kind == "validator" for consumer in reverse_index["RULE-GOV-002"])
        )

    def test_unknown_consumer_rule_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "rules", root / "rules")
            shutil.copytree(ROOT / "operations", root / "operations")
            (root / "scripts").mkdir()
            rogue_rule = "RULE-" + "NOT-FOUND"
            (root / "scripts" / "rogue.py").write_text(
                f"# [[rules/知识治理规则#{rogue_rule}|{rogue_rule}]]\n",
                encoding="utf-8",
            )

            issues = validate_rule_coverage(root)

        self.assertTrue(any(issue.code == "RULE_REFERENCE_UNKNOWN" for issue in issues))

    def test_rule_change_impact_classifies_consumers(self) -> None:
        impacts = build_rule_change_impact(ROOT, {"RULE-GOV-002"})

        self.assertTrue(any(item.action == "must_handle" for item in impacts))
        self.assertTrue(any(item.consumer.kind == "validator" for item in impacts))


if __name__ == "__main__":
    unittest.main()
