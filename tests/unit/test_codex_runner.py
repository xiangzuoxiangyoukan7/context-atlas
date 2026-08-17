"""验证 Codex 黑盒运行器和跨平台不变量比较。"""

from __future__ import annotations

import importlib
import json
import subprocess
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


class RecordingProcess:
    """按顺序返回完整进程结果并记录真实命令边界。"""

    calls: list[tuple[list[str], dict[str, Any]]]

    def __init__(self) -> None:
        """初始化调用记录。"""

        self.calls = []

    def __call__(self, command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        """根据命令类型返回 marketplace、安装或执行结果。"""

        self.calls.append((command, kwargs))
        if "marketplace" in command:
            output = '{"name":"context-atlas-test"}'
        elif "plugin" in command and "add" in command:
            output = '{"installed":true}'
        else:
            output = (
                '{"type":"thread.started","thread_id":"thread-1"}\n'
                '{"type":"item.completed","item":{"type":"agent_message",'
                '"text":"完成"}}\n'
                '{"type":"turn.completed"}\n'
            )
        return subprocess.CompletedProcess(command, 0, output, "")


def _now() -> datetime:
    """返回稳定 UTC 时间。"""

    return datetime(2026, 8, 13, 14, 0, tzinfo=UTC)


class CodexRunnerTests(unittest.TestCase):
    """验证临时安装、命令安全和结构化输出解析。"""

    def test_repository_root_is_accepted_as_plugin_root(self) -> None:
        """仓库根目录就是插件源码根。"""

        api = importlib.import_module("scripts.agent_conformance.codex_runner")
        with tempfile.TemporaryDirectory() as directory:
            runner = api.CodexRunner(
                plugin_root=ROOT,
                codex_home=Path(directory),
            )
            self.assertEqual(ROOT.resolve(), runner.plugin_root)

    def test_runner_installs_into_temporary_home_and_executes_safely(self) -> None:
        """运行器不得修改用户配置，且执行命令不得包含危险绕过参数。"""

        try:
            api = importlib.import_module("scripts.agent_conformance.codex_runner")
        except ModuleNotFoundError as error:
            self.fail(f"Codex 运行器尚未实现：{error.name}")
        process = RecordingProcess()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "codex-home"
            workspace = root / "project"
            workspace.mkdir()
            runner = api.CodexRunner(
                plugin_root=ROOT,
                codex_home=home,
                process_runner=process,
                now=_now,
                executable="codex",
                auth_source=None,
            )

            turn = runner.run_turn(workspace, "$context-atlas 检查知识库", None)
            temporary_config = (home / "config.toml").read_text(encoding="utf-8")
            marketplace = home / "context-atlas-marketplace"
            installed_manifest = json.loads(
                (marketplace / ".agents/plugins/marketplace.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertTrue(
                (marketplace / ".codex-plugin/plugin.json").is_file()
            )
            self.assertTrue(
                (marketplace / "skills/context-atlas/SKILL.md").is_file()
            )
            self.assertFalse((marketplace / "AGENTS.md").exists())
            self.assertFalse((marketplace / "tests").exists())

        commands = [call[0] for call in process.calls]
        self.assertIn("marketplace", commands[0])
        self.assertIn("plugin", commands[1])
        execute = commands[2]
        for required in (
            "exec",
            "--ephemeral",
            "-s",
            "workspace-write",
            "--json",
            "-C",
            str(workspace),
        ):
            self.assertIn(required, execute)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", execute)
        self.assertEqual(str(home), process.calls[2][1]["env"]["CODEX_HOME"])
        self.assertEqual(600, process.calls[2][1]["timeout"])
        self.assertEqual('[windows]\nsandbox = "unelevated"\n', temporary_config)
        self.assertEqual(
            json.loads(
                (ROOT / ".agents/plugins/marketplace.json").read_text(
                    encoding="utf-8"
                )
            ),
            installed_manifest,
        )
        self.assertTrue(
            all(call[1].get("encoding") == "utf-8" for call in process.calls)
        )
        self.assertTrue(
            all(call[1].get("errors") == "replace" for call in process.calls)
        )
        self.assertEqual("thread-1", turn.session_id)
        self.assertEqual("完成", turn.result_text)

    def test_continuation_replays_context_in_fresh_writable_turn(self) -> None:
        """两阶段场景应以内存上下文重放规避原生 resume 恢复只读权限。"""

        api = importlib.import_module("scripts.agent_conformance.codex_runner")
        process = RecordingProcess()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "project"
            workspace.mkdir()
            runner = api.CodexRunner(
                plugin_root=ROOT,
                codex_home=root / "home",
                persist_sessions=True,
                process_runner=process,
                now=_now,
                executable="codex",
                auth_source=None,
            )

            runner.run_turn(workspace, "第一轮", None)
            runner.run_turn(workspace, "第二轮", "thread-1")

        first = process.calls[2][0]
        second = process.calls[3][0]
        self.assertIn("--ephemeral", first)
        self.assertIn("--ephemeral", second)
        self.assertNotIn("resume", second)
        self.assertTrue(second[-1].startswith("$context-atlas\n"))
        self.assertIn("第一轮", second[-1])
        self.assertIn("第二轮", second[-1])
        self.assertEqual(1, second[-1].count("完成"))

    def test_compare_invariants_reports_platform_behavior_difference(self) -> None:
        """任一平台场景失败或退出码不同都必须导致对照失败。"""

        assertions = importlib.import_module("scripts.agent_conformance.assertions")
        claude = {
            "status": "passed",
            "scenarios": [
                {
                    "id": "initialize_requires_confirmation",
                    "status": "passed",
                    "command_exit_codes": [0],
                    "file_summary": {"changed_records": []},
                }
            ],
        }
        codex = {
            "status": "failed",
            "scenarios": [
                {
                    "id": "initialize_requires_confirmation",
                    "status": "failed",
                    "command_exit_codes": [1],
                    "file_summary": {
                        "changed_records": ["doc-example/README.md\tsha256:changed"]
                    },
                }
            ],
        }

        issues = assertions.compare_invariants(claude, codex)

        self.assertTrue(issues)
        self.assertIn("initialize_requires_confirmation", "\n".join(issues))

    def test_compare_invariants_ignores_natural_language_wording(self) -> None:
        """平台正文不同但结构、状态与退出码一致时应通过。"""

        assertions = importlib.import_module("scripts.agent_conformance.assertions")
        scenario = {
            "id": "existing_target_is_preserved",
            "status": "passed",
            "command_exit_codes": [0],
            "file_summary": {
                "changed_records": [
                    "doc-existing/.context-atlas-sentinel\tsha256:same"
                ]
            },
        }
        claude = {"status": "passed", "scenarios": [{**scenario, "message": "甲"}]}
        codex_scenario = {
            **scenario,
            "message": "乙",
            "file_summary": {
                "changed_records": [
                    "doc-existing/.context-atlas-sentinel\tsha256:another-valid-hash"
                ]
            },
        }
        codex = {"status": "passed", "scenarios": [codex_scenario]}

        self.assertEqual([], assertions.compare_invariants(claude, codex))

    def test_workspace_snapshot_ignores_python_runtime_cache(self) -> None:
        """行为报告不得把检查器运行生成的 Python 缓存当作知识文件。"""

        orchestration = importlib.import_module("scripts.run_agent_conformance")
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            source = workspace / "doc-example" / "script.py"
            cache = workspace / "doc-example" / "__pycache__" / "script.pyc"
            source.parent.mkdir()
            cache.parent.mkdir()
            source.write_text("pass\n", encoding="utf-8")
            cache.write_bytes(b"runtime")

            snapshot = orchestration.snapshot_workspace(workspace)

        self.assertTrue(any("script.py\tsha256:" in record for record in snapshot))
        self.assertFalse(any("__pycache__" in record for record in snapshot))

    def test_shared_orchestrator_can_label_codex_report(self) -> None:
        """共享场景编排器不得把 Codex 报告错误标记为 Claude。"""

        orchestration = importlib.import_module("scripts.run_agent_conformance")
        claude_tests = importlib.import_module("tests.unit.test_claude_runner")
        with tempfile.TemporaryDirectory() as directory:
            report = orchestration.run_claude_conformance(
                plugin_root=ROOT,
                workspace_root=Path(directory),
                runner_factory=claude_tests.ScriptedClaudeRunner,
                agent_version="0.147.0",
                agent_name="codex",
            )

        self.assertEqual("codex", report["agent"])
        self.assertEqual("passed", report["status"])

    def test_confirmation_prompt_names_the_exact_proposal_revision(self) -> None:
        """两轮提示必须携带同一固定修订号，不能让 Agent 猜测用户确认对象。"""

        orchestration = importlib.import_module("scripts.run_agent_conformance")

        self.assertIn(
            orchestration.CONFORMANCE_PROPOSAL_REVISION,
            orchestration.EXPLICIT_INITIALIZE_PROMPT,
        )
        self.assertIn(
            orchestration.CONFORMANCE_PROPOSAL_REVISION,
            orchestration.CONFIRM_PROMPT,
        )


if __name__ == "__main__":
    unittest.main()
