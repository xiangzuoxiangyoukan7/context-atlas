"""验证单来源摄取 Skill、共享协议和会话报告 Schema。"""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class IngestContractTests(unittest.TestCase):
    """确保 ingest 保持显式、单来源、结构化和零写入。"""

    def test_skill_is_explicit_read_only_and_thin(self) -> None:
        """Skill 只编排共享协议，不复制写入状态机。"""

        skill = (ROOT / "skills/context-atlas-ingest/SKILL.md").read_text(
            encoding="utf-8"
        )
        metadata = (ROOT / "skills/context-atlas-ingest/agents/openai.yaml").read_text(
            encoding="utf-8"
        )

        for phrase in (
            "Use only when explicitly invoked",
            "../../references/单来源摄取与路由.md",
            "../../assets/schemas/ingest-report.schema.json",
            "all early-return and `blocked` outcomes",
            "complete JSON report itself",
            "writes_performed: false",
            "confirmation_state: not_applicable",
            "Do not create a file",
        ):
            self.assertIn(phrase, skill)
        self.assertIn("allow_implicit_invocation: false", metadata)
        self.assertNotIn("await_confirmation -> apply", skill)

    def test_reference_defines_all_candidate_actions_and_blocks_batching(self) -> None:
        """共享协议必须覆盖五类候选、单来源和敏感信息边界。"""

        reference = (ROOT / "references/单来源摄取与路由.md").read_text(
            encoding="utf-8"
        )

        for phrase in (
            "增强模式允许一次处理 1～20 个",
            "超过 20 个来源或重复来源身份返回 `blocked`",
            "`add`",
            "`revise`",
            "`retire`",
            "`conflict`",
            "`ignore`",
            "不得在报告中回显值",
            "不调用其他 Skill",
        ):
            self.assertIn(phrase, reference)

    def test_report_schema_fixes_read_only_fields_and_actions(self) -> None:
        """会话报告 Schema 固定零写入并限制候选与路由枚举。"""

        path = ROOT / "schemas/ingest-report.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))

        self.assertNotIn("ingest_report", json.loads(
            (ROOT / "schemas/catalog.json").read_text(encoding="utf-8")
        ))
        self.assertEqual(False, schema["properties"]["writes_performed"]["const"])
        self.assertEqual(
            "not_applicable",
            schema["properties"]["confirmation_state"]["const"],
        )
        actions = schema["$defs"]["candidate"]["properties"]["candidate_action"]["enum"]
        self.assertEqual(["add", "revise", "retire", "conflict", "ignore"], actions)
        source_types = schema["properties"]["source_identity"]["properties"]["type"]["enum"]
        self.assertNotIn("ai_inference", source_types)


if __name__ == "__main__":
    unittest.main()
