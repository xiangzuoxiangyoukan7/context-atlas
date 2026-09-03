"""验证知识节点的一跳正向与反向渐进导航。"""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.project_kb.navigation import query_children, query_graph, query_neighbors
from scripts.agent_kb_operation import main


ROOT = Path(__file__).resolve().parents[2]


class NavigationTests(unittest.TestCase):
    """验证按编号或文件路径查询轻量邻接摘要。"""

    def setUp(self) -> None:
        """建立具有需求、功能、接口和数据表关系的最小知识库。"""

        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "doc-example"
        schema_root = self.root / ".project-kb/schemas"
        schema_root.mkdir(parents=True)
        shutil.copy2(ROOT / "schemas/relation-catalog.json", schema_root / "relation-catalog.json")
        self._write(
            "01-功能基线/需求/REQ-ORDER-001.md",
            """---
id: REQ-ORDER-001
type: requirement
title: 创建订单需求
status: approved
---
# 创建订单需求
""",
        )
        self._write(
            "01-功能基线/功能/F-ORDER-001.md",
            """---
id: F-ORDER-001
type: feature
title: 创建订单
status: baselined
rel_satisfies:
  - "[[01-功能基线/需求/REQ-ORDER-001|REQ-ORDER-001]]"
rel_calls:
  - "[[02-技术基线/接口/API-ORDER-001|API-ORDER-001]]"
---
# 创建订单
""",
        )
        self._write(
            "02-技术基线/接口/API-ORDER-001.md",
            """---
id: API-ORDER-001
type: interface
title: 创建订单接口
status: approved
rel_writes:
  - "[[02-技术基线/数据库/DS-ORDER/TABLE-ORDER-001|TABLE-ORDER-001]]"
---
# 创建订单接口
""",
        )
        self.table_path = "02-技术基线/数据库/DS-ORDER/TABLE-ORDER-001.md"
        self._write(
            self.table_path,
            """---
id: TABLE-ORDER-001
type: database_table
title: 订单表
status: approved
---
# 订单表
""",
        )

    def tearDown(self) -> None:
        """清理临时知识库。"""

        self.temporary.cleanup()

    def _write(self, relative: str, content: str) -> None:
        """写入测试知识文件。"""

        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def test_table_path_returns_incoming_interface_without_loading_body(self) -> None:
        """从数据表路径应反查直接写入它的接口。"""

        report = query_neighbors(self.root, path=self.table_path)

        self.assertEqual("TABLE-ORDER-001", report.node.id)
        self.assertEqual((), report.outgoing)
        self.assertEqual(["API-ORDER-001"], [edge.node.id for edge in report.incoming])
        self.assertEqual("rel_writes", report.incoming[0].relation)
        self.assertEqual("02-技术基线/接口/API-ORDER-001.md", report.incoming[0].node.path)

    def test_interface_returns_table_and_calling_feature(self) -> None:
        """接口节点应同时返回正向数据表和反向功能。"""

        report = query_neighbors(self.root, identifier="API-ORDER-001")

        self.assertEqual(["TABLE-ORDER-001"], [edge.node.id for edge in report.outgoing])
        self.assertEqual(["F-ORDER-001"], [edge.node.id for edge in report.incoming])

    def test_relation_and_direction_filters_remain_one_hop(self) -> None:
        """过滤条件不应隐式递归到需求。"""

        report = query_neighbors(
            self.root,
            identifier="API-ORDER-001",
            direction="incoming",
            relation="rel_calls",
        )

        self.assertEqual((), report.outgoing)
        self.assertEqual(["F-ORDER-001"], [edge.node.id for edge in report.incoming])
        self.assertNotIn("REQ-ORDER-001", [edge.node.id for edge in report.incoming])

    def test_path_without_stable_id_is_rejected(self) -> None:
        """聚合文件没有稳定编号时必须要求精确节点编号。"""

        self._write("01-功能基线/README.md", "# 功能基线\n")
        with self.assertRaisesRegex(ValueError, "stable id"):
            query_neighbors(self.root, path="01-功能基线/README.md")

    def test_children_returns_only_direct_tree_summaries(self) -> None:
        """目录查询应返回直接子节点，并使用 README 描述当前目录。"""

        self._write(
            "02-技术基线/README.md",
            "# 架构与契约\n\n这里保存接口、数据库等技术知识。\n",
        )
        self._write("02-技术基线/TEMPLATE.md", "# 模板\n")

        report = query_children(self.root, path="02-技术基线")

        self.assertEqual("这里保存接口、数据库等技术知识。", report.node.description)
        self.assertEqual(
            ["02-技术基线/接口", "02-技术基线/数据库"],
            [node.path for node in report.children],
        )
        self.assertTrue(all(node.kind == "directory" for node in report.children))

    def test_data_source_readme_identity_is_exposed_on_directory_node(self) -> None:
        """数据源 README 的实体身份应由 children 暴露在目录节点上。"""

        self._write(
            "02-技术基线/数据库/DS-ORDER/README.md",
            """---
id: DS-ORDER
type: data_source
title: 订单数据源
status: proposed
---
# 订单数据源

保存订单表。
""",
        )

        report = query_children(self.root, path="02-技术基线/数据库")
        node = next(item for item in report.children if item.path.endswith("DS-ORDER"))

        self.assertEqual("DS-ORDER", node.id)
        self.assertEqual("data_source", node.type)
        self.assertEqual("proposed", node.status)

    def test_root_children_include_archive_but_exclude_system_directories(self) -> None:
        """历史归档属于知识树，暂存箱和内部运行目录不属于。"""

        self._write("90-历史归档/README.md", "# 历史归档\n")
        self._write("Clippings/README.md", "# 暂存\n")
        self._write(".obsidian/README.md", "# 配置\n")

        report = query_children(self.root)
        paths = [node.path for node in report.children]

        self.assertIn("90-历史归档", paths)
        self.assertNotIn("Clippings", paths)
        self.assertNotIn(".obsidian", paths)

    def test_children_file_summary_exposes_identity_without_body_loading(self) -> None:
        """文件树节点应暴露身份、类型和状态摘要。"""

        report = query_children(self.root, path="02-技术基线/接口")

        self.assertEqual(1, len(report.children))
        node = report.children[0]
        self.assertEqual("API-ORDER-001", node.id)
        self.assertEqual("interface", node.type)
        self.assertEqual("approved", node.status)

    def test_graph_expands_both_directions_to_requested_depth(self) -> None:
        """多跳子图应从起点沿正反向关系展开，但不超过指定深度。"""

        report = query_graph(self.root, start="API-ORDER-001", depth=1)

        self.assertEqual("subgraph", report.mode)
        self.assertEqual(
            ["API-ORDER-001", "F-ORDER-001", "TABLE-ORDER-001"],
            [node.id for node in report.nodes],
        )
        self.assertNotIn("REQ-ORDER-001", [node.id for node in report.nodes])
        self.assertEqual(2, len(report.edges))

    def test_full_graph_is_explicit_and_bounded(self) -> None:
        """完整图必须显式请求，并通过节点上限报告截断。"""

        report = query_graph(self.root, all_nodes=True, max_nodes=2)

        self.assertEqual("all", report.mode)
        self.assertTrue(report.truncated)
        self.assertEqual(2, len(report.nodes))
        self.assertIsNone(report.depth)

    def test_graph_supports_relation_filter(self) -> None:
        """关系过滤应同时约束遍历和输出边。"""

        report = query_graph(
            self.root,
            start="F-ORDER-001",
            depth=2,
            relation="rel_satisfies",
        )

        self.assertEqual(
            ["F-ORDER-001", "REQ-ORDER-001"],
            [node.id for node in report.nodes],
        )
        self.assertEqual(["rel_satisfies"], [edge.relation for edge in report.edges])

    def test_graph_stops_at_classification_index_by_default(self) -> None:
        """普通图到达 README 分类节点后不得反向扩展同类成员。"""

        self._write(
            "01-功能基线/功能/README.md",
            """---
id: IDX-FEATURES
type: knowledge_index
title: 功能
rel_classified_under: []
---
# 功能
""",
        )
        for name in ("F-ORDER-001.md",):
            path = self.root / "01-功能基线/功能" / name
            content = path.read_text(encoding="utf-8").replace(
                "status: baselined\n",
                'status: baselined\nrel_classified_under:\n  - "[[01-功能基线/功能/README|IDX-FEATURES]]"\n',
            )
            path.write_text(content, encoding="utf-8")
        self._write(
            "01-功能基线/功能/F-ORDER-002.md",
            """---
id: F-ORDER-002
type: feature
title: 查询订单
status: baselined
rel_classified_under:
  - "[[01-功能基线/功能/README|IDX-FEATURES]]"
---
# 查询订单
""",
        )

        report = query_graph(self.root, start="F-ORDER-001", depth=2)

        self.assertIn("IDX-FEATURES", [node.id for node in report.nodes])
        self.assertNotIn("F-ORDER-002", [node.id for node in report.nodes])

    def test_graph_expands_classification_members_only_when_explicit(self) -> None:
        """显式分类成员查询仍受深度和节点上限控制。"""

        self._write(
            "01-功能基线/功能/README.md",
            """---
id: IDX-FEATURES
type: knowledge_index
title: 功能
rel_classified_under: []
---
# 功能
""",
        )
        for identifier in ("F-ORDER-001", "F-ORDER-002"):
            path = self.root / "01-功能基线/功能" / f"{identifier}.md"
            if identifier == "F-ORDER-001":
                content = path.read_text(encoding="utf-8").replace(
                    "status: baselined\n",
                    'status: baselined\nrel_classified_under:\n  - "[[01-功能基线/功能/README|IDX-FEATURES]]"\n',
                )
                path.write_text(content, encoding="utf-8")
            else:
                self._write(
                    f"01-功能基线/功能/{identifier}.md",
                    f'''---\nid: {identifier}\ntype: feature\ntitle: 查询订单\nstatus: baselined\nrel_classified_under:\n  - "[[01-功能基线/功能/README|IDX-FEATURES]]"\n---\n# 查询订单\n''',
                )

        report = query_graph(
            self.root,
            start="IDX-FEATURES",
            depth=1,
            max_nodes=2,
            expand_classification_members=True,
        )

        self.assertTrue(report.truncated)
        self.assertEqual(2, len(report.nodes))

    def test_cli_exposes_children_and_graph_as_json(self) -> None:
        """统一 Agent 命令应公开树导航和关系图查询。"""

        children_output = StringIO()
        with redirect_stdout(children_output):
            children_code = main(["children", str(self.root), "--path", "."])
        graph_output = StringIO()
        with redirect_stdout(graph_output):
            graph_code = main(
                ["graph", str(self.root), "--start", "F-ORDER-001", "--depth", "1"]
            )

        children_payload = json.loads(children_output.getvalue())
        graph_payload = json.loads(graph_output.getvalue())
        self.assertEqual(0, children_code)
        self.assertEqual("children", children_payload["operation"])
        self.assertTrue(children_payload["ok"])
        self.assertEqual(0, graph_code)
        self.assertEqual("graph", graph_payload["operation"])
        self.assertEqual("subgraph", graph_payload["mode"])
        self.assertTrue(graph_payload["ok"])


if __name__ == "__main__":
    unittest.main()
