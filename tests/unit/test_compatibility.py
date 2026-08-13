"""验证知识库格式版本的轻量兼容诊断。"""

from __future__ import annotations

import json
from pathlib import Path

from tests.helpers import TempDirectoryTestCase


ROOT = Path(__file__).resolve().parents[2]


class CompatibilityTests(TempDirectoryTestCase):
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

        self._manifest("format_version: 2\n")
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
                    "version": 1,
                    "plugin_version": "0.1.0",
                    "reads_format_versions": [2],
                    "creates_format_version": 2,
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
            assets_root=ROOT / "skills/context-atlas/assets",
            initialized_at="2026-08-13",
        )

        self.assertTrue((target / ".project-kb/compatibility.json").is_file())
        manifest = (target / "knowledge-base.yaml").read_text(encoding="utf-8")
        self.assertIn("project_version: 0.1.0", manifest)
        self.assertIn("format_version: 2", manifest)
