"""验证统一工作编排 Skill 的用户入口和治理边界。"""

from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class WorkSkillTests(unittest.TestCase):
    """保证自然语言开发任务可自动路由，且不绕过正式写入门禁。"""

    def test_work_skill_is_implicit_task_orchestrator(self) -> None:
        """统一入口必须可隐式触发并保留用户的开发目标。"""

        skill_root = ROOT / "skills/context-atlas-work"
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        metadata = (skill_root / "agents/openai.yaml").read_text(encoding="utf-8")

        self.assertIn("allow_implicit_invocation: true", metadata)
        self.assertIn("Preserve the user's concrete delivery goal", skill)
        self.assertIn("Do not turn the task into knowledge administration", skill)
        self.assertIn("Start read-only", skill)

    def test_work_skill_offers_development_paths_without_blocking(self) -> None:
        """持久知识需变化时应提供基线和只开发两条路径。"""

        skill = (ROOT / "skills/context-atlas-work/SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Establish the knowledge baseline, then develop", skill)
        self.assertIn("Proceed without formal knowledge updates", skill)
        self.assertIn("Do not block an explicitly authorized development task", skill)

    def test_work_skill_preserves_proposal_confirmation_gate(self) -> None:
        """自动路由不得把原始开发请求当作正式知识确认。"""

        skill = (ROOT / "skills/context-atlas-work/SKILL.md").read_text(encoding="utf-8")

        self.assertIn("The initial task request is not confirmation", skill)
        self.assertIn("confirms the exact current revision", skill)
        self.assertIn("reject stale confirmation", skill)
        self.assertIn("knowledge validation separately", skill)

    def test_work_skill_is_the_only_mixed_maintenance_owner(self) -> None:
        """混合维护由 work 主持，且显式调用后无需重复调用底层 Skill。"""

        skill = (ROOT / "skills/context-atlas-work/SKILL.md").read_text(encoding="utf-8")

        self.assertIn("only owner of a Proposal that mixes", skill)
        self.assertIn("does not need to invoke each maintenance Skill again", skill)
        self.assertIn("explicit selection of the baseline path", skill)
        self.assertIn("replacement by a successor to revise", skill)
        self.assertIn("withdrawal without creating a successor to retire", skill)

    def test_work_skill_synthesizes_candidate_solution_from_usage(self) -> None:
        """使用场景足够时必须先给推荐候选，不能只把缺失项退回用户。"""

        skill = (ROOT / "skills/context-atlas-work/SKILL.md").read_text(encoding="utf-8")
        review = (ROOT / "references/规格审查与SDD适配.md").read_text(encoding="utf-8")
        database = (ROOT / "references/数据库知识.md").read_text(encoding="utf-8")

        self.assertIn("synthesize the smallest usable recommended solution", skill)
        self.assertIn("two or three concrete choices", skill)
        self.assertIn("proposed columns, SQL data types", skill)
        self.assertIn("最小可用的推荐方案", review)
        self.assertIn("二至三个具体选项", review)
        self.assertIn("主动形成字段、SQL 数据类型", database)
        self.assertIn("不得只列出“类型缺失”", database)


if __name__ == "__main__":
    unittest.main()
