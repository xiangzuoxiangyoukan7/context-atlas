"""验证三级关系影响分析的直接传播、间接传播和安全降级。"""

from __future__ import annotations

from pathlib import Path

from scripts.project_kb.discovery import discover_records
from scripts.project_kb.relation_catalog import RelationCatalog
from scripts.project_kb.relations import RelationIndex
from tests.helpers import TempDirectoryTestCase


ROOT = Path(__file__).resolve().parents[2]


def _write(path: Path, metadata: str) -> None:
    """写入影响分析测试使用的最小知识文档。"""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{metadata}---\n# 测试知识\n", encoding="utf-8")


class ImpactAnalysisTests(TempDirectoryTestCase):
    """验证变化从基础知识沿反向消费者关系传播。"""

    def _index(self) -> tuple[RelationIndex, RelationCatalog]:
        """建立 TABLE 到 MODULE 再到 FEATURE 的两层关系图。"""

        _write(self.root / "表.md", "id: TABLE-001\ntype: relation_fixture\n")
        _write(
            self.root / "模块.md",
            "id: MODULE-001\ntype: relation_fixture\n"
            "rel_reads:\n  - \"[[表|TABLE-001]]\"\n",
        )
        _write(
            self.root / "功能.md",
            "id: FEATURE-001\ntype: relation_fixture\n"
            "rel_depends_on:\n  - \"[[模块|MODULE-001]]\"\n",
        )
        records, discovery_issues = discover_records(self.root, frozenset())
        self.assertEqual([], discovery_issues)
        catalog = RelationCatalog.load(ROOT / "schemas" / "relation-catalog.json")
        index, relation_issues = RelationIndex.build(self.root, records, catalog)
        self.assertEqual([], relation_issues)
        return index, catalog

    def test_required_direct_impact_is_capped_for_indirect_consumer(self) -> None:
        """直接必改不能自动把第二层不确定消费者也判为必改。"""

        from scripts.project_kb.impact import analyze_impact

        index, catalog = self._index()
        impacts = analyze_impact(index, catalog, "TABLE-001", "enum_value_removed")

        self.assertEqual(
            [("MODULE-001", "required", 1), ("FEATURE-001", "review_required", 2)],
            [(item.affected_id, item.level, item.depth) for item in impacts],
        )

    def test_unknown_change_requires_review_and_formatting_is_informational(self) -> None:
        """未知变化不猜测为必改，纯格式变化也不制造业务阻断。"""

        from scripts.project_kb.impact import analyze_impact

        index, catalog = self._index()

        unknown = analyze_impact(index, catalog, "TABLE-001", "new_change")
        formatting = analyze_impact(index, catalog, "TABLE-001", "formatting_only")

        self.assertEqual("review_required", unknown[0].level)
        self.assertTrue(all(item.level == "informational" for item in formatting))

    def test_max_depth_limits_reverse_traversal(self) -> None:
        """调用方可以限制分析深度，避免在大型图谱中无限扩散。"""

        from scripts.project_kb.impact import analyze_impact

        index, catalog = self._index()
        impacts = analyze_impact(
            index, catalog, "TABLE-001", "enum_value_removed", max_depth=1
        )

        self.assertEqual(["MODULE-001"], [item.affected_id for item in impacts])
