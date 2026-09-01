"""验证受控关系目录的完整性与失败边界。"""

from __future__ import annotations

import json
from pathlib import Path

from tests.helpers import TempDirectoryTestCase


ROOT = Path(__file__).resolve().parents[2]
CORE_RELATIONS = {
    "rel_classified_under",
    "rel_supported_by",
    "rel_conforms_to",
    "rel_implements",
    "rel_satisfies",
    "rel_primary_module",
    "rel_participating_modules",
    "rel_provides",
    "rel_calls",
    "rel_exposes",
    "rel_reads",
    "rel_writes",
    "rel_depends_on",
    "rel_verified_by",
    "rel_changes",
    "rel_supersedes",
    "rel_logical_parent",
    "rel_evidenced_by",
    "rel_executes",
    "rel_belongs_to",
    "rel_scenario_for",
    "rel_changed_by",
}


class RelationCatalogTests(TempDirectoryTestCase):
    """验证关系名称、方向、端点与影响等级由单一目录控制。"""

    def test_catalog_declares_every_approved_core_relation(self) -> None:
        """正式目录不得遗漏已经批准的核心关系。"""

        from scripts.project_kb.relation_catalog import RelationCatalog

        catalog = RelationCatalog.load(ROOT / "schemas" / "relation-catalog.json")

        self.assertEqual(CORE_RELATIONS, set(catalog.relations))
        self.assertEqual("实现该需求", catalog.get("rel_implements").name_zh)
        self.assertEqual("deprecated", catalog.get("rel_implements").status)
        self.assertEqual("满足该需求", catalog.get("rel_satisfies").name_zh)

    def test_catalog_returns_specific_and_default_impact_levels(self) -> None:
        """明确变化使用确定等级，未登记变化安全降级为人工复核。"""

        from scripts.project_kb.relation_catalog import RelationCatalog

        catalog = RelationCatalog.load(ROOT / "schemas" / "relation-catalog.json")

        self.assertEqual("required", catalog.impact_level("rel_reads", "field_removed"))
        self.assertEqual(
            "informational",
            catalog.impact_level("rel_reads", "formatting_only"),
        )
        self.assertEqual(
            "review_required",
            catalog.impact_level("rel_reads", "unknown_business_change"),
        )

    def test_catalog_rejects_invalid_relation_definition(self) -> None:
        """缺中文名和非法影响等级的目录不得被加载。"""

        from scripts.project_kb.relation_catalog import RelationCatalog

        path = self.root / "relation-catalog.json"
        path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "relations": [
                        {
                            "field": "rel_invalid",
                            "name_zh": "",
                            "source_prefixes": [],
                            "target_prefixes": ["REQ"],
                            "direction": "forward_only",
                            "status": "active",
                            "default_impact": "guessed",
                            "impact_rules": {},
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            RelationCatalog.load(path)


if __name__ == "__main__":
    import unittest

    unittest.main()
