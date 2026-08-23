"""验证结构化初始化 Proposal 和确定性渲染。"""

from __future__ import annotations

from pathlib import Path
import json
import os
import subprocess
import sys

from scripts.project_kb.agent_operation import execute_initialization_proposal
from scripts.project_kb.initialization_contract import canonical_revision, validate_initialization_proposal
from tests.helpers import InstalledPluginTestCase


ROOT = Path(__file__).resolve().parents[2]


class InitializationContractTests(InstalledPluginTestCase):
    """确认修订门禁、来源规则和固定文件映射。"""

    def _proposal(self) -> dict[str, object]:
        """创建包含确认事实和未知项的合法 Proposal。"""

        proposal: dict[str, object] = {
            "operation": "initialize",
            "project": {
                "root": str(self.root),
                "id": "example",
                "name": "Example",
                "knowledge_base_name": "doc-example",
            },
            "facts": {
                "goals": [{
                    "id": "GOAL-001", "value": "提供可验证的知识库", "status": "confirmed",
                    "source": {"type": "user_statement", "reference": "当前用户确认"},
                }],
                "boundaries_in": [],
                "boundaries_out": [],
                "technology_stacks": [{
                    "id": "TECH-001", "value": "Python 3.14", "status": "confirmed",
                    "source": {"type": "repository_file", "reference": "pyproject.toml: requires-python"},
                    "name": "Python", "version": "3.14", "location": ".", "purpose": "项目实现",
                    "commands": ["py -m unittest"], "configuration": "pyproject.toml",
                }],
                "terms": [{"id": "TERM-001", "value": "Atlas：项目知识库", "status": "confirmed", "source": {"type": "repository_file", "reference": "README.md:1"}}],
                "capabilities": [{"id": "CAP-001", "value": "初始化知识库", "status": "confirmed", "source": {"type": "repository_file", "reference": "README.md:3"}}],
                "features": [{"id": "FEATURE-001", "value": "初始化命令", "status": "proposed", "source": {"type": "repository_file", "reference": "src/init.py:1"}}],
                "modules": [{"id": "MOD-001", "value": "src：应用模块", "status": "confirmed", "source": {"type": "repository_file", "reference": "src/"}}],
                "interfaces": [{"id": "API-001", "value": "POST /init", "status": "proposed", "source": {"type": "repository_file", "reference": "src/api.py:10"}}],
                "databases": [{"id": "DB-001", "value": "sqlite 数据库", "status": "proposed", "source": {"type": "repository_file", "reference": "migrations/"}}],
                "external_dependencies": [{"id": "EXT-001", "value": "GitHub API", "status": "proposed", "source": {"type": "repository_file", "reference": "pyproject.toml"}}],
                "tests": [{"id": "TEST-001", "value": "py -m unittest", "status": "confirmed", "source": {"type": "repository_file", "reference": "tests/"}}],
                "adrs": [{"id": "ADR-001", "value": "使用 Markdown", "status": "confirmed", "source": {"type": "existing_document", "reference": "docs/adr/001.md"}}],
            },
            "unknowns": [{"id": "UNKNOWN-001", "question": "部署环境是什么？", "owner_action": "项目负责人确认"}],
            "conflicts": [],
        }
        for group in proposal["facts"].values():  # type: ignore[union-attr]
            for item in group:
                item["source"]["observed_at"] = "2026-08-20T10:00:00+08:00"
                item["source"]["confirmation_status"] = "confirmed"
                item["source"]["confirmed_at"] = "2026-08-20T10:05:00+08:00"
        proposal["proposal_revision"] = canonical_revision(proposal)
        return proposal

    def test_confirmed_proposal_renders_only_fixed_documents(self) -> None:
        """确认后的 Proposal 只能渲染到预定义文档。"""

        proposal = self._proposal()
        report = execute_initialization_proposal(
            proposal, str(proposal["proposal_revision"]), self.assets_root
        )

        self.assertEqual("initialized", report.operation)
        self.assertEqual("passed", report.validation.result)
        self.assertEqual("python_executor", report.execution.mode)
        self.assertEqual("deterministic_executor", report.validation.authority)
        self.assertEqual("passed", report.validation.deterministic_validation)
        self.assertEqual(
            {
                "full_schema_and_reference_validation",
                "self_contained_children",
                "self_contained_neighbors",
                "self_contained_bounded_graph",
            },
            {check["name"] for check in report.validation.checks},
        )
        self.assertEqual(3, report.execution.runtime_detection.attempts[0].python_major)
        self.assertEqual(("UNKNOWN-001",), report.unknowns)
        target = self.root / "doc-example"
        self.assertIn("Python", (target / "02-架构与契约/系统架构.md").read_text(encoding="utf-8"))
        self.assertIn("提供可验证的知识库", (target / "00-项目总览/项目概述.md").read_text(encoding="utf-8"))
        self.assertIn("Atlas", (target / "00-项目总览/术语表.md").read_text(encoding="utf-8"))
        self.assertIn("初始化命令", (target / "01-功能基线/能力地图.md").read_text(encoding="utf-8"))
        self.assertIn("应用模块", (target / "02-架构与契约/模块/MOD-001.md").read_text(encoding="utf-8"))
        self.assertIn("POST /init", (target / "02-架构与契约/接口/API-001.md").read_text(encoding="utf-8"))
        self.assertIn("sqlite", (target / "02-架构与契约/数据库/README.md").read_text(encoding="utf-8"))
        self.assertIn("GitHub API", (target / "02-架构与契约/外部依赖/README.md").read_text(encoding="utf-8"))
        self.assertIn("py -m unittest", (target / "02-架构与契约/系统架构.md").read_text(encoding="utf-8"))
        self.assertIn("使用 Markdown", (target / "04-决策记录/README.md").read_text(encoding="utf-8"))

    def test_initialized_bundle_runs_navigation_without_plugin_assets(self) -> None:
        """生成知识库内置脚本必须能独立执行渐进导航。"""

        proposal = self._proposal()
        execute_initialization_proposal(
            proposal, str(proposal["proposal_revision"]), self.assets_root
        )
        target = self.root / "doc-example"
        command = [
            sys.executable,
            str(target / ".project-kb/scripts/agent_kb_operation.py"),
        ]
        cases = (
            ["children", str(target), "--path", "."],
            ["neighbors", str(target), "--id", "API-001"],
            ["graph", str(target), "--start", "API-001", "--depth", "1", "--max-nodes", "20"],
        )

        for arguments in cases:
            completed = subprocess.run(
                command + arguments,
                cwd=self.root,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr.decode("utf-8"))
            payload = json.loads(completed.stdout.decode("utf-8"))
            self.assertTrue(payload["ok"])

    def test_cli_uses_utf8_for_chinese_stdin_and_stdout(self) -> None:
        """Windows 非 UTF-8 默认环境也应稳定传递中文 Proposal 和 JSON。"""

        proposal = self._proposal()
        environment = os.environ.copy()
        environment["PYTHONIOENCODING"] = "cp1252"
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/agent_kb_operation.py"),
                "initialize",
                "--proposal",
                "-",
                "--confirmed-revision",
                str(proposal["proposal_revision"]),
            ],
            cwd=self.root,
            input=json.dumps(proposal, ensure_ascii=False).encode("utf-8"),
            capture_output=True,
            env=environment,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr.decode("utf-8"))
        payload = json.loads(completed.stdout.decode("utf-8"))
        self.assertEqual("initialized", payload["operation"])
        self.assertIn(
            "提供可验证的知识库",
            (self.root / "doc-example/00-项目总览/项目概述.md").read_text(encoding="utf-8"),
        )

    def test_revision_mismatch_has_zero_formal_writes(self) -> None:
        """确认修订不一致时不得创建正式目录。"""

        with self.assertRaises(PermissionError):
            execute_initialization_proposal(self._proposal(), "sha256:" + "0" * 64, self.assets_root)
        self.assertFalse((self.root / "doc-example").exists())

    def test_empty_project_keeps_routed_documents_empty(self) -> None:
        """空项目只初始化骨架，不把模板示例写成项目事实。"""

        proposal = self._proposal()
        for group in proposal["facts"]:  # type: ignore[union-attr]
            proposal["facts"][group] = []  # type: ignore[index]
        proposal["proposal_revision"] = canonical_revision(proposal)
        execute_initialization_proposal(
            proposal, str(proposal["proposal_revision"]), self.assets_root
        )

        target = self.root / "doc-example"
        combined = "\n".join(
            (target / relative).read_text(encoding="utf-8")
            for relative in (
                "01-功能基线/能力地图.md", "02-架构与契约/模块/README.md",
                "02-架构与契约/接口/README.md", "02-架构与契约/数据库/README.md",
                "02-架构与契约/外部依赖/README.md", "04-决策记录/README.md",
            )
        )
        for fictional in ("MOD-001", "API-001", "EXT-001", "示例组件", "示例服务"):
            self.assertNotIn(fictional, combined)

    def test_standard_profile_does_not_create_obsidian_settings(self) -> None:
        """默认初始化必须记录 standard 且不引入工具专属展示配置。"""

        proposal = self._proposal()
        execute_initialization_proposal(
            proposal, str(proposal["proposal_revision"]), self.assets_root
        )

        target = self.root / "doc-example"
        self.assertFalse((target / ".obsidian").exists())
        self.assertIn(
            "workspace_profile: standard",
            (target / "knowledge-base.yaml").read_text(encoding="utf-8"),
        )

    def test_obsidian_profile_creates_minimal_colored_graph(self) -> None:
        """显式 Obsidian 模式只生成最小配置和基于知识类型的颜色组。"""

        proposal = self._proposal()
        proposal["project"]["workspace_profile"] = "obsidian"  # type: ignore[index]
        proposal["proposal_revision"] = canonical_revision(proposal)
        report = execute_initialization_proposal(
            proposal, str(proposal["proposal_revision"]), self.assets_root
        )

        target = self.root / "doc-example"
        settings = target / ".obsidian"
        self.assertEqual(
            {"app.json", "graph.json"},
            {path.name for path in settings.iterdir()},
        )
        self.assertEqual({}, json.loads((settings / "app.json").read_text(encoding="utf-8")))
        graph = json.loads((settings / "graph.json").read_text(encoding="utf-8"))
        queries = {item["query"] for item in graph["colorGroups"]}
        self.assertIn("[type:feature]", queries)
        self.assertIn("[type:contract OR independent_contract]", queries)
        self.assertEqual('-path:"90-历史归档"', graph["search"])
        self.assertIn(".obsidian/app.json", report.written_files)
        self.assertIn("workspace_profile: obsidian", (target / "knowledge-base.yaml").read_text(encoding="utf-8"))

    def test_unknown_workspace_profile_is_rejected_before_writes(self) -> None:
        """未支持的工作区配置不得进入暂存初始化。"""

        proposal = self._proposal()
        proposal["project"]["workspace_profile"] = "unknown"  # type: ignore[index]
        proposal["proposal_revision"] = canonical_revision(proposal)
        with self.assertRaisesRegex(ValueError, "workspace_profile is unsupported"):
            execute_initialization_proposal(
                proposal, str(proposal["proposal_revision"]), self.assets_root
            )
        self.assertFalse((self.root / "doc-example").exists())

    def test_ai_inference_cannot_be_confirmed(self) -> None:
        """AI 推测不能冒充经过确认的项目事实。"""

        proposal = self._proposal()
        proposal["facts"]["goals"][0]["source"]["type"] = "ai_inference"  # type: ignore[index]
        proposal["proposal_revision"] = canonical_revision(proposal)
        with self.assertRaisesRegex(ValueError, "cannot confirm"):
            validate_initialization_proposal(proposal)


if __name__ == "__main__":
    import unittest

    unittest.main()
