"""验证 Obsidian 关系链接、端点类型和正反向索引。"""

from __future__ import annotations

from pathlib import Path

from scripts.project_kb.discovery import discover_records
from scripts.project_kb.relation_catalog import RelationCatalog
from tests.helpers import TempDirectoryTestCase


ROOT = Path(__file__).resolve().parents[2]


def _write_document(path: Path, frontmatter: str, body: str = "") -> Path:
    """写入保留块列表格式的最小关系测试文档。"""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}---\n{body}", encoding="utf-8")
    return path


class RelationIndexTests(TempDirectoryTestCase):
    """验证关系索引同时服务机器分析和 Obsidian 文件图谱。"""

    def _build(self) -> tuple[object, list[object]]:
        """发现当前临时知识库并构造关系索引。"""

        from scripts.project_kb.relations import RelationIndex

        records, discovery_issues = discover_records(self.root, frozenset())
        self.assertEqual([], discovery_issues)
        catalog = RelationCatalog.load(ROOT / "schemas" / "relation-catalog.json")
        return RelationIndex.build(self.root, records, catalog)

    def test_index_builds_forward_and_reverse_edges(self) -> None:
        """使用方只写正向关系，索引应自动得到基础文档的反向消费者。"""

        _write_document(
            self.root / "01-需求" / "订单需求.md",
            "id: REQ-001\ntype: knowledge_item\n",
        )
        _write_document(
            self.root / "01-功能" / "订单功能.md",
            "id: FEATURE-001\n"
            "type: feature\n"
            "rel_implements:\n"
            '  - "[[01-需求/订单需求|REQ-001]]"\n',
        )

        index, issues = self._build()

        self.assertEqual([], issues)
        self.assertEqual("REQ-001", index.outgoing("FEATURE-001")[0].target.identifier)
        self.assertEqual("FEATURE-001", index.incoming("REQ-001")[0].source.identifier)

    def test_aggregate_target_requires_exact_heading_anchor(self) -> None:
        """聚合文件中的知识项必须通过稳定编号加中文标题精确定位。"""

        _write_document(
            self.root / "01-需求" / "需求汇总.md",
            "type: knowledge_item\n",
            "## REQ-001 创建订单\n",
        )
        _write_document(
            self.root / "01-功能" / "订单功能.md",
            "id: FEATURE-001\n"
            "type: feature\n"
            "rel_implements:\n"
            '  - "[[01-需求/需求汇总#REQ-001 创建订单|REQ-001]]"\n',
        )

        index, issues = self._build()

        self.assertEqual([], issues)
        self.assertEqual(
            "REQ-001 创建订单",
            index.outgoing("FEATURE-001")[0].target.anchor,
        )

    def test_invalid_relations_report_exact_codes(self) -> None:
        """未知字段、断链、错 ID、错锚点、错方向和重复目标应分别定位。"""

        cases = {
            "unknown": (
                "rel_unknown:\n  - \"[[01-需求/需求|REQ-001]]\"\n",
                "KB_REL_FIELD_UNKNOWN",
            ),
            "format": ("rel_implements: [REQ-001]\n", "KB_REL_LINK_FORMAT"),
            "file": (
                "rel_implements:\n  - \"[[01-需求/缺失|REQ-001]]\"\n",
                "KB_REL_TARGET_FILE",
            ),
            "id": (
                "rel_implements:\n  - \"[[01-需求/需求|REQ-999]]\"\n",
                "KB_REL_TARGET_ID",
            ),
            "anchor": (
                "rel_implements:\n  - \"[[01-需求/需求#REQ-001 错误标题|REQ-001]]\"\n",
                "KB_REL_TARGET_ANCHOR",
            ),
            "direction": (
                "rel_reads:\n  - \"[[01-需求/需求|REQ-001]]\"\n",
                "KB_REL_DIRECTION",
            ),
            "duplicate": (
                "rel_implements:\n"
                "  - \"[[01-需求/需求|REQ-001]]\"\n"
                "  - \"[[01-需求/需求|REQ-001]]\"\n",
                "KB_REL_DUPLICATE",
            ),
        }
        for name, (relation_text, expected_code) in cases.items():
            with self.subTest(name=name):
                case_root = self.root / name
                _write_document(
                    case_root / "01-需求" / "需求.md",
                    "id: REQ-001\ntype: knowledge_item\n",
                    "## REQ-001 创建订单\n",
                )
                _write_document(
                    case_root / "01-功能" / "功能.md",
                    "id: FEATURE-001\ntype: feature\n" + relation_text,
                )
                from scripts.project_kb.relations import RelationIndex

                records, discovery_issues = discover_records(case_root, frozenset())
                self.assertEqual([], discovery_issues)
                catalog = RelationCatalog.load(
                    ROOT / "schemas" / "relation-catalog.json"
                )
                _, issues = RelationIndex.build(case_root, records, catalog)

                self.assertIn(expected_code, {issue.code for issue in issues})


if __name__ == "__main__":
    import unittest

    unittest.main()
