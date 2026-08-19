"""验证结构化初始化 Proposal 和确定性渲染。"""

from __future__ import annotations

from pathlib import Path

from scripts.project_kb.agent_operation import execute_initialization_proposal
from scripts.project_kb.initialization_contract import canonical_revision, validate_initialization_proposal
from tests.helpers import TempDirectoryTestCase


ROOT = Path(__file__).resolve().parents[2]


class InitializationContractTests(TempDirectoryTestCase):
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
            },
            "unknowns": [{"id": "UNKNOWN-001", "question": "部署环境是什么？", "owner_action": "项目负责人确认"}],
            "conflicts": [],
        }
        proposal["proposal_revision"] = canonical_revision(proposal)
        return proposal

    def test_confirmed_proposal_renders_only_fixed_documents(self) -> None:
        """确认后的 Proposal 只能渲染到预定义文档。"""

        proposal = self._proposal()
        report = execute_initialization_proposal(
            proposal, str(proposal["proposal_revision"]), ROOT / "assets"
        )

        self.assertEqual("initialized", report.operation)
        self.assertEqual("passed", report.validation.result)
        self.assertEqual("python_executor", report.execution.mode)
        self.assertEqual("deterministic_executor", report.validation.authority)
        self.assertEqual("passed", report.validation.deterministic_validation)
        self.assertEqual(3, report.execution.runtime_detection.attempts[0].python_major)
        self.assertEqual(("UNKNOWN-001",), report.unknowns)
        target = self.root / "doc-example"
        self.assertIn("Python", (target / "02-架构与契约/技术基线.md").read_text(encoding="utf-8"))
        self.assertIn("提供可验证的知识库", (target / "00-项目总览/项目概述.md").read_text(encoding="utf-8"))

    def test_revision_mismatch_has_zero_formal_writes(self) -> None:
        """确认修订不一致时不得创建正式目录。"""

        with self.assertRaises(PermissionError):
            execute_initialization_proposal(self._proposal(), "sha256:" + "0" * 64, ROOT / "assets")
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
