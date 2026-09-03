"""固定结构和内容归属校验。"""

from pathlib import Path
import shutil

from scripts.project_kb.discovery import discover_records
from scripts.project_kb.structure import validate_structure
from tests.helpers import TempDirectoryTestCase, materialize_core_template


class StructureTests(TempDirectoryTestCase):
    """验证固定入口、authority 与知识类型目录。"""

    def test_core_structure_and_authorities_exist(self) -> None:
        """完整核心模板的固定结构和权威目标均有效。"""

        root = materialize_core_template(self.root, "example")
        records, _ = discover_records(root, frozenset({".project-kb", "90-历史归档"}))
        self.assertEqual([], validate_structure(root, records))

    def test_missing_authority_and_wrong_type_directory_fail(self) -> None:
        """缺失权威目标和错放功能卡必须产生稳定错误。"""

        root = materialize_core_template(self.root, "example")
        (root / "01-功能基线/README.md").unlink()
        (root / "02-技术基线/F01-wrong.md").write_text(
            "---\nid: F01\ntype: feature\n---\n# wrong\n", encoding="utf-8"
        )
        records, _ = discover_records(root, frozenset({".project-kb", "90-历史归档"}))
        codes = {issue.code for issue in validate_structure(root, records)}
        self.assertIn("KB_STRUCTURE_REQUIRED", codes)
        self.assertIn("KB_AUTHORITY_MISSING", codes)
        self.assertIn("KB_TYPE_DIRECTORY", codes)

    def test_format_five_routes_requirements_and_features_to_distinct_directories(self) -> None:
        """格式五要求需求和功能分别进入其受控子目录。"""

        root = materialize_core_template(self.root, "example")
        (root / "01-功能基线/需求/REQ-ORDER-001.md").write_text(
            "---\nid: REQ-ORDER-001\ntype: requirement\n---\n# requirement\n", encoding="utf-8"
        )
        (root / "01-功能基线/F-ORDER-001.md").write_text(
            "---\nid: F-ORDER-001\ntype: feature\n---\n# legacy location\n", encoding="utf-8"
        )
        records, _ = discover_records(root, frozenset({".project-kb", "90-历史归档"}))
        issues = validate_structure(root, records)
        wrong_paths = {issue.path.name for issue in issues if issue.code == "KB_TYPE_DIRECTORY"}
        self.assertNotIn("REQ-ORDER-001.md", wrong_paths)
        self.assertIn("F-ORDER-001.md", wrong_paths)

    def test_classification_readme_must_point_to_direct_parent(self) -> None:
        """分类 README 跨级指向根节点时必须失败。"""

        root = materialize_core_template(self.root, "example")
        readme = root / "01-功能基线/需求/README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8").replace(
                "[[01-功能基线/README|IDX-FUNCTIONAL-BASELINE]]",
                "[[README|IDX-ROOT]]",
            ),
            encoding="utf-8",
        )
        records, _ = discover_records(root, frozenset({".project-kb", "90-历史归档"}))

        codes = {issue.code for issue in validate_structure(root, records)}

        self.assertIn("KB_CLASSIFICATION_PARENT", codes)

    def test_missing_registered_classification_readme_fails(self) -> None:
        """受管正式目录缺少 README 分类节点时必须失败。"""

        root = materialize_core_template(self.root, "example")
        (root / "02-技术基线/原型/README.md").unlink()
        records, _ = discover_records(root, frozenset({".project-kb", "90-历史归档"}))

        codes = {issue.code for issue in validate_structure(root, records)}

        self.assertIn("KB_CLASSIFICATION_README", codes)

    def test_data_source_readme_is_container_entity_for_tables(self) -> None:
        """数据源 README 同时承担目录入口，表只需归属该数据源。"""

        root = materialize_core_template(self.root, "example")
        directory = root / "02-技术基线/数据库/DS-ORDER"
        directory.mkdir()
        (directory / "README.md").write_text(
            """---
id: DS-ORDER
type: data_source
title: 订单数据源
status: proposed
product: postgresql
product_version: unknown
owner: missing
config_reference: APP_DATABASE_URL
database: missing
namespace: public
environments: [development]
sources: []
last_updated: 2026-08-10
rel_classified_under:
  - "[[02-技术基线/数据库/README|IDX-DATABASE]]"
---
# 订单数据源
""",
            encoding="utf-8",
        )
        (directory / "TABLE-ORDER.md").write_text(
            """---
id: TABLE-ORDER
type: database_table
title: 订单表
status: proposed
rel_belongs_to:
  - "[[02-技术基线/数据库/DS-ORDER/README|DS-ORDER]]"
---
# 订单表
""",
            encoding="utf-8",
        )
        records, _ = discover_records(root, frozenset({".project-kb", "90-历史归档"}))

        self.assertEqual([], validate_structure(root, records))

    def test_data_source_directory_rejects_separate_entity_and_wrong_table_parent(self) -> None:
        """数据源不得重复建卡，目录内表必须归属当前 README。"""

        root = materialize_core_template(self.root, "example")
        directory = root / "02-技术基线/数据库/DS-ORDER"
        directory.mkdir()
        (directory / "README.md").write_text(
            """---
id: DS-ORDER
type: data_source
title: 订单数据源
status: proposed
rel_classified_under:
  - "[[02-技术基线/数据库/README|IDX-DATABASE]]"
---
# 订单数据源
""",
            encoding="utf-8",
        )
        (directory / "DS-ORDER.md").write_text(
            """---
id: DS-ORDER-COPY
type: data_source
title: 重复数据源
status: proposed
rel_classified_under:
  - "[[02-技术基线/数据库/README|IDX-DATABASE]]"
---
# 重复数据源
""",
            encoding="utf-8",
        )
        (directory / "TABLE-ORDER.md").write_text(
            """---
id: TABLE-ORDER
type: database_table
title: 订单表
status: proposed
rel_belongs_to:
  - "[[02-技术基线/数据库/DS-OTHER/README|DS-OTHER]]"
---
# 订单表
""",
            encoding="utf-8",
        )
        records, _ = discover_records(root, frozenset({".project-kb", "90-历史归档"}))

        codes = {issue.code for issue in validate_structure(root, records)}

        self.assertIn("KB_DATABASE_DATASOURCE_README", codes)
        self.assertIn("KB_DATABASE_TABLE_DATASOURCE", codes)

    def test_data_source_table_rejects_direct_database_root_classification(self) -> None:
        """表只能归属数据源，不得同时直连数据库根索引。"""

        root = materialize_core_template(self.root, "example")
        directory = root / "02-技术基线/数据库/DS-ORDER"
        directory.mkdir()
        (directory / "README.md").write_text(
            "---\nid: DS-ORDER\ntype: data_source\ntitle: 订单数据源\nstatus: proposed\n"
            "rel_classified_under:\n  - \"[[02-技术基线/数据库/README|IDX-DATABASE]]\"\n"
            "---\n# 订单数据源\n",
            encoding="utf-8",
        )
        table = directory / "TABLE-ORDER.md"
        table.write_text(
            "---\nid: TABLE-ORDER\ntype: database_table\ntitle: 订单表\nstatus: proposed\n"
            "rel_classified_under:\n  - \"[[02-技术基线/数据库/README|IDX-DATABASE]]\"\n"
            "rel_belongs_to:\n  - \"[[02-技术基线/数据库/DS-ORDER/README|DS-ORDER]]\"\n"
            "---\n# 订单表\n",
            encoding="utf-8",
        )
        records, _ = discover_records(root, frozenset({".project-kb", "90-历史归档"}))

        codes = {issue.code for issue in validate_structure(root, records)}

        self.assertIn("KB_DATABASE_TABLE_DIRECT_CLASSIFICATION", codes)

    def test_database_namespace_is_retired(self) -> None:
        """独立命名空间必须迁入数据源 README，不能残留为当前实体。"""

        root = materialize_core_template(self.root, "example")
        directory = root / "02-技术基线/数据库/DS-ORDER"
        directory.mkdir()
        (directory / "README.md").write_text(
            "---\nid: DS-ORDER\ntype: data_source\ntitle: 订单数据源\nstatus: proposed\n"
            "rel_classified_under:\n  - \"[[02-技术基线/数据库/README|IDX-DATABASE]]\"\n"
            "---\n# 订单数据源\n",
            encoding="utf-8",
        )
        (directory / "NS-ORDER.md").write_text(
            "---\nid: NS-ORDER\ntype: database_namespace\ntitle: public\nstatus: proposed\n"
            "namespace_kind: schema\nphysical_name: public\nowner: missing\nsources: [missing]\n"
            "rel_belongs_to:\n  - \"[[02-技术基线/数据库/DS-ORDER/README|DS-ORDER]]\"\n"
            "last_updated: 2026-09-03\n"
            "rel_classified_under:\n  - \"[[02-技术基线/数据库/README|IDX-DATABASE]]\"\n"
            "---\n# public\n",
            encoding="utf-8",
        )
        records, _ = discover_records(root, frozenset({".project-kb", "90-历史归档"}))

        codes = {issue.code for issue in validate_structure(root, records)}

        self.assertIn("KB_DATABASE_LEVEL_RETIRED", codes)

    def test_data_source_directory_name_must_match_readme_identity(self) -> None:
        """数据源容器目录必须与 README 的稳定身份一致。"""

        root = materialize_core_template(self.root, "example")
        directory = root / "02-技术基线/数据库/DS-WRONG"
        directory.mkdir()
        (directory / "README.md").write_text(
            """---
id: DS-ORDER
type: data_source
title: 订单数据源
status: proposed
rel_classified_under:
  - "[[02-技术基线/数据库/README|IDX-DATABASE]]"
---
# 订单数据源
""",
            encoding="utf-8",
        )
        records, _ = discover_records(root, frozenset({".project-kb", "90-历史归档"}))

        codes = {issue.code for issue in validate_structure(root, records)}

        self.assertIn("KB_DATABASE_DATASOURCE_DIRECTORY", codes)

    def test_classification_cycle_fails(self) -> None:
        """分类关系即使同时跨级，也必须明确报告循环。"""

        root = materialize_core_template(self.root, "example")
        functional = root / "01-功能基线/README.md"
        requirements = root / "01-功能基线/需求/README.md"
        functional.write_text(
            functional.read_text(encoding="utf-8").replace(
                "[[README|IDX-ROOT]]",
                "[[01-功能基线/需求/README|IDX-REQUIREMENTS]]",
            ),
            encoding="utf-8",
        )
        records, _ = discover_records(root, frozenset({".project-kb", "90-历史归档"}))

        codes = {issue.code for issue in validate_structure(root, records)}

        self.assertIn("KB_CLASSIFICATION_CYCLE", codes)

    def test_classification_readmes_describe_directory_and_query_contract(self) -> None:
        """初始化模板的每个正式分类 README 都应说明保存边界和查询边界。"""

        root = materialize_core_template(self.root, "example")
        records, _ = discover_records(root, frozenset({".project-kb", "Clippings"}))
        indexes = [record for record in records if record.metadata.get("type") == "knowledge_index"]

        self.assertTrue(indexes)
        for record in indexes:
            with self.subTest(path=record.path):
                self.assertIn("只保存", record.body)
                self.assertIn("children", record.body)
                self.assertIn("neighbors", record.body)
                self.assertIn("graph", record.body)
