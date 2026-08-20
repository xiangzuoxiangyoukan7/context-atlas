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
        records, _ = discover_records(root, frozenset({"90-历史归档"}))
        self.assertEqual([], validate_structure(root, records))

    def test_missing_authority_and_wrong_type_directory_fail(self) -> None:
        """缺失权威目标和错放功能卡必须产生稳定错误。"""

        root = materialize_core_template(self.root, "example")
        (root / "01-功能基线/README.md").unlink()
        (root / "02-架构与契约/F01-wrong.md").write_text(
            "---\nid: F01\ntype: feature\n---\n# wrong\n", encoding="utf-8"
        )
        records, _ = discover_records(root, frozenset({"90-历史归档"}))
        codes = {issue.code for issue in validate_structure(root, records)}
        self.assertIn("KB_STRUCTURE_REQUIRED", codes)
        self.assertIn("KB_AUTHORITY_MISSING", codes)
        self.assertIn("KB_TYPE_DIRECTORY", codes)
