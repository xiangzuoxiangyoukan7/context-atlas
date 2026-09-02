"""验证 Obsidian 类型颜色生成和保守合并。"""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.project_kb.obsidian import TYPE_COLORS, managed_color_groups, merge_graph_settings


class ObsidianColorTests(unittest.TestCase):
    """颜色映射是初始化、升级和质检的单一事实源。"""

    def test_every_type_has_one_stable_query(self) -> None:
        """每个正式类型只能生成一个稳定主查询。"""

        queries = [group["query"] for group in managed_color_groups()]
        self.assertEqual(len(TYPE_COLORS), len(queries))
        self.assertEqual(len(queries), len(set(queries)))

    def test_schema_catalog_types_are_all_colored(self) -> None:
        """Schema Catalog 新增正式类型时必须同步颜色映射。"""

        catalog = json.loads(Path("schemas/catalog.json").read_text(encoding="utf-8"))
        governed_types = set(catalog) - {"project_manifest"}
        self.assertEqual(set(), governed_types - set(TYPE_COLORS))

    def test_merge_updates_managed_groups_and_preserves_custom_settings(self) -> None:
        """升级替换受管颜色，但保留用户查询和其他设置。"""

        current = {
            "search": "custom",
            "colorGroups": [
                {"query": "[type:feature]", "color": {"rgb": 1}},
                {"query": "path:私有笔记", "color": {"rgb": 2}},
            ],
        }
        merged = merge_graph_settings(current)
        self.assertEqual("custom", merged["search"])
        queries = [group["query"] for group in merged["colorGroups"]]
        self.assertEqual(1, queries.count("[type:feature]"))
        self.assertIn("path:私有笔记", queries)


if __name__ == "__main__":
    unittest.main()
