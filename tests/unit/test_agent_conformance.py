"""验证跨 Agent 场景结果模型与行为不变量断言。"""

from __future__ import annotations

import hashlib
import importlib
import json
import tempfile
import unittest
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = ROOT / "tests" / "agent_conformance" / "scenarios.json"


def _load_api() -> tuple[ModuleType, ModuleType]:
    """加载待实现接口，并将缺失模块转换为明确的测试失败。"""

    try:
        model = importlib.import_module("scripts.agent_conformance.model")
        assertions = importlib.import_module("scripts.agent_conformance.assertions")
    except ModuleNotFoundError as error:
        raise AssertionError(f"跨 Agent 断言接口尚未实现：{error.name}") from error
    return model, assertions


def _record(relative_path: str, digest: str) -> str:
    """构造独立于生产实现的手工文件快照记录。"""

    return f"{relative_path}\tsha256:{digest}"


class AgentConformanceTests(unittest.TestCase):
    """验证模型自述不能替代文件、摘要和退出码证据。"""

    def test_unconfirmed_scenario_rejects_new_formal_knowledge_files(self) -> None:
        """未确认时新增正式知识文件必须被识别为违规。"""

        model, assertions = _load_api()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            result = model.ScenarioResult(
                workspace=workspace,
                before={_record("notes.txt", "before")},
                after={
                    _record("notes.txt", "before"),
                    _record("doc-example/README.md", "written"),
                },
                messages=["我没有写入正式知识"],
                command_exit_codes=[0],
            )

            issues = assertions.assert_no_formal_write_before_confirmation(result)

        self.assertTrue(issues)
        self.assertIn("doc-example/README.md", "\n".join(issues))

    def test_unconfirmed_scenario_allows_non_formal_runtime_files(self) -> None:
        """未确认场景可以产生非正式运行记录而不误报知识写入。"""

        model, assertions = _load_api()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            result = model.ScenarioResult(
                workspace=workspace,
                before=set(),
                after={_record(".agent-runtime/turn.json", "runtime")},
                messages=[],
                command_exit_codes=[0],
            )

            issues = assertions.assert_no_formal_write_before_confirmation(result)

        self.assertEqual([], issues)

    def test_ingest_response_requires_core_read_only_fields(self) -> None:
        """摄取响应必须包含跨平台稳定字段、状态和候选动作。"""

        _, assertions = _load_api()
        valid = json.dumps(
            {
                "status": "analyzed",
                "source_identity": {"type": "repository_file", "reference": "source.md"},
                "observed_at": "2026-08-21",
                "source_digest_or_version": "sha256:test",
                "route_plan": ["context-atlas-add"],
                "candidate_action": "add",
                "writes_performed": False,
                "confirmation_state": "not_applicable",
                "next_action": "显式调用 context-atlas-add",
            },
            ensure_ascii=False,
        )

        self.assertEqual(
            [],
            assertions.assert_ingest_response(
                valid, expected_status="analyzed", expected_action="add"
            ),
        )
        issues = assertions.assert_ingest_response(
            "{}", expected_status="blocked", expected_action=None
        )
        self.assertTrue(issues)

    def test_existing_target_requires_unchanged_formal_files_and_sentinel_hash(self) -> None:
        """已有正式目标变化必须失败，但允许新增非正式运行记录。"""

        model, assertions = _load_api()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            target = workspace / "doc-example"
            target.mkdir()
            sentinel = target / ".context-atlas-sentinel"
            original = b"keep-existing-target"
            sentinel.write_bytes(original)
            digest = hashlib.sha256(original).hexdigest()
            before = {_record("doc-example/.context-atlas-sentinel", digest)}
            preserved = model.ScenarioResult(
                workspace=workspace,
                before=before,
                after={
                    *before,
                    _record(".agent-runtime/turn.json", "runtime"),
                },
                messages=["目标已保留"],
                command_exit_codes=[0],
            )

            self.assertEqual(
                [],
                assertions.assert_existing_target_preserved(preserved, digest),
            )

            sentinel.write_text("overwritten", encoding="utf-8")
            changed = model.ScenarioResult(
                workspace=workspace,
                before=before,
                after={_record("doc-example/.context-atlas-sentinel", "changed")},
                messages=["目标已保留"],
                command_exit_codes=[0],
            )
            issues = assertions.assert_existing_target_preserved(changed, digest)

        self.assertGreaterEqual(len(issues), 2)

    def test_confirmed_scenario_requires_self_contained_valid_target(self) -> None:
        """成功自述不能替代目标结构、项目名和检查器退出码。"""

        model, assertions = _load_api()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            target = workspace / "doc-example"
            (target / ".project-kb" / "scripts").mkdir(parents=True)
            (target / ".project-kb" / "schemas").mkdir(parents=True)
            (target / "knowledge-base.yaml").write_text(
                "knowledge_base_name: doc-example\n",
                encoding="utf-8",
            )
            (target / ".project-kb" / "scripts" / "check_knowledge_base.py").write_text(
                "# embedded checker\n",
                encoding="utf-8",
            )
            (target / ".project-kb" / "schemas" / "catalog.json").write_text(
                "{}\n",
                encoding="utf-8",
            )
            result = model.ScenarioResult(
                workspace=workspace,
                before=set(),
                after={
                    _record("doc-example/knowledge-base.yaml", "manifest"),
                    _record(
                        "doc-example/.project-kb/scripts/check_knowledge_base.py",
                        "checker",
                    ),
                    _record("doc-example/.project-kb/schemas/catalog.json", "schemas"),
                },
                messages=["初始化成功"],
                command_exit_codes=[0, 0],
            )

            self.assertEqual(
                [],
                assertions.assert_valid_initialized_target(result, "example"),
            )

            invalid = model.ScenarioResult(
                workspace=workspace,
                before=set(),
                after=set(result.after),
                messages=["初始化成功"],
                command_exit_codes=[0, 1],
            )
            issues = assertions.assert_valid_initialized_target(invalid, "example")

        self.assertTrue(issues)
        self.assertIn("退出码", "\n".join(issues))

    def test_scenario_catalog_declares_required_cross_agent_cases(self) -> None:
        """场景目录必须为后续两个真实运行器提供同一组场景。"""

        try:
            payload = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            self.fail(f"场景目录尚未创建：{error.filename}")
        scenario_ids = {item["id"] for item in payload["scenarios"]}
        self.assertEqual(
            {
                "initialize_requires_confirmation",
                "initialize_after_confirmation",
                "existing_target_is_preserved",
                "natural_language_triggers_skill",
                "review_is_read_only",
                "review_reports_blockers",
                "openspec_mapping_is_read_only",
                "spec_kit_mapping_is_read_only",
                "external_status_is_not_approval",
                "ingest_single_source_read_only",
                "ingest_multiple_sources_blocked",
                "ingest_conflict_read_only",
                "ingest_natural_language_not_triggered",
                "ingest_sensitive_source_blocked",
                "ingest_ai_inference_source_blocked",
                "ingest_missing_kb_routes_init",
                "ingest_unsupported_format_routes_upgrade",
                "ingest_revise_route",
                "ingest_retire_route",
                "ingest_ignore_route",
                "ingest_composite_add_revise_route",
            },
            scenario_ids,
        )


if __name__ == "__main__":
    unittest.main()
