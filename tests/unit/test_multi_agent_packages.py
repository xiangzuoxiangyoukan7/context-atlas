"""验证 Qoder 与 Trae 的共享 Skill 构建包。"""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest


class MultiAgentPackageTests(unittest.TestCase):
    """验证新增平台只改变适配边界，不复制核心实现。"""

    def test_qoder_package_has_manifest_and_root_relative_assets(self) -> None:
        """Qoder 包使用平台清单并保持运行资产相对路径有效。"""

        from scripts.build_plugin import build

        with tempfile.TemporaryDirectory() as directory:
            root = build(Path(directory) / "qoder", "qoder")
            self.assertTrue((root / ".qoder-plugin/plugin.json").is_file())
            self.assertTrue((root / "skills/context-atlas-work/SKILL.md").is_file())
            self.assertTrue((root / "skills/context-atlas-init/SKILL.md").is_file())
            self.assertTrue((root / "assets/manifest.json").is_file())
            self.assertTrue((root / "references/执行状态机.md").is_file())

    def test_trae_package_uses_agents_runtime_root(self) -> None:
        """Trae 包将 Skill 与运行资产放在 .agents 自包含目录。"""

        from scripts.build_plugin import build

        with tempfile.TemporaryDirectory() as directory:
            root = build(Path(directory) / "trae", "trae")
            self.assertTrue((root / ".agents/skills/context-atlas-work/SKILL.md").is_file())
            self.assertTrue((root / ".agents/skills/context-atlas-init/SKILL.md").is_file())
            self.assertTrue((root / ".agents/assets/manifest.json").is_file())
            self.assertTrue((root / ".agents/references/执行状态机.md").is_file())
            self.assertFalse((root / "skills").exists())
            self.assertTrue((root / "install.ps1").is_file())

    def test_qoder_package_contains_marketplace_metadata(self) -> None:
        """Qoder 包提供原生 Marketplace 所需的发布清单。"""

        from scripts.build_plugin import build
        import json

        with tempfile.TemporaryDirectory() as directory:
            root = build(Path(directory) / "qoder", "qoder")
            marketplace = json.loads((root / "marketplace.json").read_text(encoding="utf-8"))
            self.assertEqual("context-atlas", marketplace["plugins"][0]["name"])
            self.assertEqual("./", marketplace["plugins"][0]["source"])
