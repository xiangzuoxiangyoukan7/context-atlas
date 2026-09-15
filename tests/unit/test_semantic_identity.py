"""语义知识身份测试。"""

from pathlib import Path
import unittest

from scripts.project_kb.semantic_identity import build_semantic_id, normalize_semantic_name
from scripts.project_kb.migration import _replace_moved_link_targets, _replace_semantic_references


class SemanticIdentityTests(unittest.TestCase):
    """验证文件用途与 README 作用域均能直接反映在 ID 中。"""

    def test_document_identity_uses_type_and_title(self) -> None:
        """普通文件使用知识类型和文件用途。"""

        root = Path("C:/project/doc-demo")
        path = root / "01-功能基线/功能/旧文件.md"
        self.assertEqual(
            "FEAT-20260916-Agent-驱动的知识库初始化",
            build_semantic_id(
                "feature", "Agent 驱动的知识库初始化", path, root,
                identity_created_at="2026-09-16",
            ),
        )

    def test_readme_identity_uses_directory_scope(self) -> None:
        """README 使用目录作用域。"""

        root = Path("C:/project/doc-demo")
        path = root / "03-变更与证据/验收证据/README.md"
        self.assertEqual(
            "IDX-变更与证据-验收证据",
            build_semantic_id("knowledge_index", "验收证据", path, root),
        )

    def test_readme_does_not_repeat_title_when_spacing_differs(self) -> None:
        """目录名与标题仅分词空格不同时不得重复拼接作用域。"""

        root = Path("C:/project/doc-demo")
        path = root / "03-变更与证据/变更/CHG-20260915-001-Schema自描述/README.md"
        self.assertEqual(
            "IDX-变更与证据-变更-CHG-20260915-001-Schema自描述",
            build_semantic_id("knowledge_index", "Schema 自描述", path, root),
        )

    def test_root_architecture_keeps_fixed_authority_identity(self) -> None:
        """固定权威入口在清单驱动改造前保持兼容身份。"""

        root = Path("C:/project/doc-demo")
        path = root / "02-技术基线/系统架构.md"
        self.assertEqual(
            "ARCH-技术基线-系统架构",
            build_semantic_id(
                "architecture", "Agent 原生项目知识库系统架构", path, root,
                identity_created_at="2026-09-16",
            ),
        )

    def test_content_update_date_does_not_change_identity(self) -> None:
        """last_updated 变化不得改变已经建立的身份日期。"""

        root = Path("C:/project/doc-demo")
        path = root / "02-技术基线/接口/IFACE-20260916-刷新统计.md"
        self.assertEqual(
            "IFACE-20260916-刷新统计",
            build_semantic_id(
                "interface", "刷新统计", path, root,
                current_id=path.stem,
                identity_created_at="2026-09-16",
                last_updated="2026-09-18",
            ),
        )

    def test_normalization_keeps_chinese_and_technical_words(self) -> None:
        """中文与英文技术词可读，标点和连续空白不进入身份。"""

        self.assertEqual("Schema-驱动-检查器", normalize_semantic_name("Schema 驱动：检查器"))

    def test_moved_filename_replacement_is_limited_to_links(self) -> None:
        """通用文件名不能污染正文、标题或目录名称。"""

        content = (
            "# Schema 自描述与需求身份改造\n\n"
            "当前变更保存在变更目录。参见[变更](./变更.md)与"
            "[[03-变更与证据/变更/变更|CHG-001]]。\n"
        )
        updated = _replace_moved_link_targets(
            content,
            {"变更.md": "CHG-Schema-自描述.md", "变更": "CHG-Schema-自描述"},
        )
        self.assertIn("当前变更保存在变更目录", updated)
        self.assertIn("[变更](./CHG-Schema-自描述.md)", updated)
        self.assertIn("[[03-变更与证据/变更/CHG-Schema-自描述|CHG-001]]", updated)

    def test_identifier_inside_new_link_filename_is_not_expanded_twice(self) -> None:
        """新文件名保留其完整语义 ID，不递归替换其中的旧 ID 片段。"""

        updated = _replace_semantic_references(
            "关联 [[01-功能基线/需求/REQ-ATLAS-001-旧名称|REQ-ATLAS-001]]。",
            {"REQ-ATLAS-001": "REQ-ATLAS-20260914-新名称"},
            {
                "REQ-ATLAS-001-旧名称": "REQ-ATLAS-20260914-新名称",
            },
        )
        self.assertEqual(
            "关联 [[01-功能基线/需求/REQ-ATLAS-20260914-新名称|REQ-ATLAS-20260914-新名称]]。",
            updated,
        )


if __name__ == "__main__":
    unittest.main()
