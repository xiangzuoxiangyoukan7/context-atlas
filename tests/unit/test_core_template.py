"""test_core_template 自动化测试。"""

from pathlib import Path
import re
from urllib.parse import unquote

from scripts.project_kb.links import LINK_PATTERN
from scripts.project_kb.template_contract import TEMPLATE_MARKERS, required_template_paths
from scripts.project_kb.validator import ValidationConfig, validate
from tests.helpers import TempDirectoryTestCase, materialize_core_template


class CoreTemplateTests(TempDirectoryTestCase):
    """验证 CoreTemplateTests 相关行为。"""

    def test_current_change_is_optional_knowledge_not_an_execution_gate(self) -> None:
        """验证 current_change_is_optional_knowledge_not_an_execution_gate 场景。"""

        root = Path("templates/core/doc-project")
        current_change = root / "03-实施与验收/当前变更.md"
        manifest = (root / "knowledge-base.yaml").read_text(encoding="utf-8")
        collaboration = (
            root / "05-知识治理/AI知识采集协议.md"
        ).read_text(encoding="utf-8")

        self.assertTrue(current_change.is_file())
        self.assertFalse((root / "03-实施与验收/CURRENT.md").exists())
        self.assertNotIn("current:", manifest)
        self.assertIn("不构成任务执行许可", current_change.read_text(encoding="utf-8"))
        self.assertNotIn("无可执行开发任务", collaboration)

    def test_capture_guide_is_durable_fallback_not_runtime_specification(self) -> None:
        """生成的协作文档必须自包含，但不复制插件运行时细节。"""

        guide = Path(
            "templates/core/doc-project/05-知识治理/AI知识采集协议.md"
        ).read_text(encoding="utf-8")

        for phrase in (
            "持久化的治理说明",
            "不是插件完整运行时规范",
            "未安装 Skill 时",
            "当前修订标识",
            "沉默不是确认",
            "不表示内容已被正确批准",
        ):
            self.assertIn(phrase, guide)
        for runtime_detail in (
            "agent_kb_operation.py",
            "py -3",
            "python3",
            "Windows Store",
            "agent_host",
        ):
            self.assertNotIn(runtime_detail, guide)

        root = Path("templates/core/doc-project")
        self.assertFalse((root / "05-开发指南").exists())
        self.assertFalse((root / "05-知识治理/本地开发.md").exists())
        self.assertFalse((root / "05-知识治理/测试规则.md").exists())

    def test_data_asset_readme_has_inventory_columns_and_valid_card_template_link(
        self,
    ) -> None:
        """验证 data_asset_readme_has_inventory_columns_and_valid_card_template_link 场景。"""

        root = Path("templates/core/doc-project/02-架构与契约/数据资产")
        readme = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("## 资产总清单", readme)
        self.assertIn("| 资产编号 | 名称 | 负责人 | 状态 | 说明卡 |", readme)
        self.assertIn("./TEMPLATE.md", LINK_PATTERN.findall(readme))
        self.assertTrue((root / "TEMPLATE.md").is_file())

    def test_data_asset_template_has_complete_basis_fields(self) -> None:
        """验证 data_asset_template_has_complete_basis_fields 场景。"""

        template = Path(
            "templates/core/doc-project/02-架构与契约/数据资产/TEMPLATE.md"
        ).read_text(encoding="utf-8")

        for field in ("关联功能", "技术契约", "知识来源", "批准信息", "未决问题"):
            with self.subTest(field=field):
                self.assertRegex(template, rf"(?m)^\| {re.escape(field)} \|")

    def test_data_asset_template_explains_governance_boundaries(self) -> None:
        """验证 data_asset_template_explains_governance_boundaries 场景。"""

        root = Path("templates/core/doc-project/02-架构与契约/数据资产")
        readme = (root / "README.md").read_text(encoding="utf-8")
        template = (root / "TEMPLATE.md").read_text(encoding="utf-8")

        for phrase in ("业务含义", "数据来源", "质量要求", "安全要求", "保存规则"):
            self.assertIn(phrase, template)
        self.assertIn("知识来源", readme)
        self.assertIn("数据库", readme)
        self.assertIn("接口契约", readme)

    def test_core_template_contains_every_required_knowledge_type(self) -> None:
        """验证 core_template_contains_every_required_knowledge_type 场景。"""

        root = Path("templates/core/doc-project")
        missing = [path for path in required_template_paths() if not (root / path).exists()]
        markers = {
            marker
            for path in root.rglob("*")
            if path.is_file()
            for marker in re.findall(r"{{[A-Z][A-Z0-9_]*}}", path.read_text(encoding="utf-8"))
        }

        self.assertEqual(missing, [])
        self.assertEqual(markers, TEMPLATE_MARKERS)

    def test_materialized_template_is_self_contained_and_valid(self) -> None:
        """验证 materialized_template_is_self_contained_and_valid 场景。"""

        root = materialize_core_template(self.root, "example")
        unresolved: list[tuple[Path, str]] = []
        escaped: list[tuple[Path, str]] = []
        broken: list[tuple[Path, str]] = []

        for path in root.rglob("*"):
            if not path.is_file():
                continue
            content = path.read_text(encoding="utf-8")
            unresolved.extend((path, marker) for marker in re.findall(r"{{[A-Z][A-Z0-9_]*}}", content))
            if path.suffix != ".md":
                continue
            for target in LINK_PATTERN.findall(content):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                candidate = (path.parent / unquote(target.split("#", 1)[0])).resolve()
                if not candidate.is_relative_to(root.resolve()):
                    escaped.append((path, target))
                elif not candidate.exists():
                    broken.append((path, target))

        self.assertEqual(unresolved, [])
        self.assertEqual(escaped, [])
        self.assertEqual(broken, [])
        self.assertEqual(
            validate(root, ValidationConfig(schema_root=Path("schemas"))),
            [],
        )


if __name__ == "__main__":
    import unittest

    unittest.main()
