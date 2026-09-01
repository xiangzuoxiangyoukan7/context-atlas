"""验证知识库格式版本的轻量兼容诊断。"""

from __future__ import annotations

import json
from pathlib import Path

from tests.helpers import InstalledPluginTestCase


ROOT = Path(__file__).resolve().parents[2]


class CompatibilityTests(InstalledPluginTestCase):
    """验证插件升级和目标知识库迁移保持相互独立。"""

    def _manifest(self, extra: str = "") -> None:
        """写入测试使用的最小知识库清单。"""

        (self.root / "knowledge-base.yaml").write_text(
            "project_id: example\nproject_version: 3.4.0\n" + extra,
            encoding="utf-8",
        )

    def test_current_format_is_directly_compatible(self) -> None:
        """新建格式与当前格式一致时不应提示迁移。"""

        from scripts.project_kb.compatibility import CompatibilityPolicy

        self._manifest("format_version: 13\n")
        policy = CompatibilityPolicy.load(ROOT / "compatibility.json")

        result = policy.diagnose(self.root)

        self.assertEqual("compatible", result.status)
        self.assertFalse(result.write_blocked)
        self.assertFalse(result.conversion_available)

    def test_missing_format_is_legacy_one_and_readable(self) -> None:
        """旧知识库缺少内部字段时只按格式一识别，不修改文件。"""

        from scripts.project_kb.compatibility import CompatibilityPolicy

        self._manifest()
        before = (self.root / "knowledge-base.yaml").read_bytes()
        policy = CompatibilityPolicy.load(ROOT / "compatibility.json")

        result = policy.diagnose(self.root)

        self.assertEqual(1, result.format_version)
        self.assertEqual("conversion_available", result.status)
        self.assertFalse(result.write_blocked)
        self.assertTrue(result.conversion_available)
        self.assertEqual(before, (self.root / "knowledge-base.yaml").read_bytes())

    def test_unreadable_format_blocks_formal_writes(self) -> None:
        """未知格式只允许诊断和迁移提案，不能继续正式写入。"""

        from scripts.project_kb.compatibility import CompatibilityPolicy

        self._manifest("format_version: 99\n")
        policy = CompatibilityPolicy.load(ROOT / "compatibility.json")

        result = policy.diagnose(self.root)

        self.assertEqual("unsupported", result.status)
        self.assertTrue(result.write_blocked)
        self.assertFalse(result.conversion_available)

    def test_policy_rejects_inconsistent_conversion_versions(self) -> None:
        """转换器起始版本必须包含在可读版本中并低于新建格式。"""

        from scripts.project_kb.compatibility import CompatibilityPolicy

        path = self.root / "compatibility.json"
        path.write_text(
            json.dumps(
                {
                    "manifest_version": 1,
                    "supported_format_versions": [2],
                    "created_format_version": 2,
                    "conversions": [{"from": 1, "to": 2, "id": "legacy"}],
                }
            ),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            CompatibilityPolicy.load(path)

    def test_initialized_knowledge_base_contains_compatibility_policy(self) -> None:
        """自包含知识库必须携带与检查器配套的兼容声明。"""

        from scripts.project_kb.initializer import initialize_from_assets

        target = initialize_from_assets(
            self.root,
            project_name="example",
            assets_root=self.assets_root,
            initialized_at="2026-08-13",
        )

        self.assertTrue((target / ".project-kb/compatibility.json").is_file())
        manifest = (target / "knowledge-base.yaml").read_text(encoding="utf-8")
        self.assertIn("project_version: 0.1.0", manifest)
        self.assertIn("format_version: 13", manifest)
        self.assertIn("knowledge_revision: 1", manifest)
        self.assertNotIn("protocol_version:", manifest)
        self.assertNotIn("schema_version:", manifest)

    def test_format_seven_has_unified_version_model_conversion(self) -> None:
        """格式七可读取，并提供到统一版本模型的确定性转换。"""

        from scripts.project_kb.compatibility import CompatibilityPolicy

        self._manifest("format_version: 7\n")
        result = CompatibilityPolicy.load(ROOT / "compatibility.json").diagnose(self.root)

        self.assertEqual("conversion_available", result.status)
        self.assertEqual(13, result.created_format_version)

    def test_format_five_is_readable_with_conversion(self) -> None:
        """旧格式仍可读取，并提供到当前格式的受控转换。"""

        from scripts.project_kb.compatibility import CompatibilityPolicy

        self._manifest("format_version: 5\n")
        result = CompatibilityPolicy.load(ROOT / "compatibility.json").diagnose(self.root)

        self.assertEqual("conversion_available", result.status)
        self.assertFalse(result.write_blocked)
        self.assertTrue(result.conversion_available)

    def test_format_two_is_readable_and_has_governance_conversion(self) -> None:
        """格式二可读，但应提示转换到知识治理目录。"""

        from scripts.project_kb.compatibility import CompatibilityPolicy

        self._manifest("format_version: 2\n")
        result = CompatibilityPolicy.load(ROOT / "compatibility.json").diagnose(self.root)

        self.assertEqual("conversion_available", result.status)
        self.assertFalse(result.write_blocked)
        self.assertTrue(result.conversion_available)
