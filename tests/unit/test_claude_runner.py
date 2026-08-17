"""验证 Claude Code 黑盒运行器的命令、安全边界和输出解析。"""

from __future__ import annotations

import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Any

from scripts.agent_conformance.model import AgentTurn


ROOT = Path(__file__).resolve().parents[2]


def _load_runner_api() -> ModuleType:
    """加载待实现运行器，并把缺失模块转换为清晰的测试失败。"""

    try:
        return importlib.import_module("scripts.agent_conformance.claude_runner")
    except ModuleNotFoundError as error:
        raise AssertionError(f"Claude 运行器尚未实现：{error.name}") from error


class RecordingProcess:
    """记录命令边界并返回完整的 Claude JSON 进程结果。"""

    calls: list[tuple[list[str], dict[str, Any]]]

    def __init__(self, stdout: str, returncode: int = 0, stderr: str = "") -> None:
        """保存预设进程输出并初始化调用记录。"""

        self.stdout = stdout
        self.returncode = returncode
        self.stderr = stderr
        self.calls = []
        self.plugin_release_files: list[set[str]] = []

    def __call__(self, command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        """记录一次调用并返回预设完成结果。"""

        self.calls.append((command, kwargs))
        if "--plugin-dir" in command:
            plugin_directory = Path(command[command.index("--plugin-dir") + 1])
            self.plugin_release_files.append(
                {
                    path.relative_to(plugin_directory).as_posix()
                    for path in plugin_directory.rglob("*")
                    if path.is_file()
                }
            )
        return subprocess.CompletedProcess(
            args=command,
            returncode=self.returncode,
            stdout=self.stdout,
            stderr=self.stderr,
        )


class TimeoutThenSuccessProcess:
    """首轮抛出超时、第二轮返回成功，用于验证只读轮次安全重试。"""

    calls: int

    def __init__(self) -> None:
        """初始化调用次数。"""

        self.calls = 0

    def __call__(
        self,
        command: list[str],
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[str]:
        """第一次模拟外部停滞，后续返回完整 Claude 结果。"""

        self.calls += 1
        if self.calls == 1:
            raise subprocess.TimeoutExpired(command, timeout=600)
        return subprocess.CompletedProcess(
            command,
            0,
            '{"type":"result","session_id":"session-1","result":"完成"}',
            "",
        )


class ScriptedClaudeRunner:
    """在临时项目中模拟 Claude 场景的可观察文件副作用。"""

    persist_sessions: bool
    turns: int

    def __init__(self, plugin_root: Path, persist_sessions: bool = False) -> None:
        """保存会话策略；插件路径仅用于保持真实构造接口一致。"""

        self.persist_sessions = persist_sessions
        self.turns = 0

    def run_turn(
        self,
        workspace: Path,
        prompt: str,
        resume_session_id: str | None,
    ) -> AgentTurn:
        """在确认场景第二轮物化最小自包含知识库。"""

        self.turns += 1
        if workspace.name == "initialize_after_confirmation" and resume_session_id:
            target = workspace / "doc-example"
            scripts = target / ".project-kb" / "scripts"
            schemas = target / ".project-kb" / "schemas"
            scripts.mkdir(parents=True)
            schemas.mkdir(parents=True)
            (target / "knowledge-base.yaml").write_text(
                "knowledge_base_name: doc-example\n",
                encoding="utf-8",
            )
            (scripts / "check_knowledge_base.py").write_text(
                '"""测试内置检查器。"""\nraise SystemExit(0)\n',
                encoding="utf-8",
            )
            (schemas / "catalog.json").write_text("{}\n", encoding="utf-8")
        now = _fixed_now()
        return AgentTurn(
            session_id="session-1" if self.persist_sessions else None,
            exit_code=0,
            result_text="包含 user@example.com token=secret 的原始模型正文",
            structured_output=None,
            stderr="",
            started_at=now,
            finished_at=now,
        )


class FailingClaudeRunner:
    """模拟认证或网络故障，验证场景不能被误记为通过。"""

    constructions: int = 0

    def __init__(self, plugin_root: Path, persist_sessions: bool = False) -> None:
        """保持真实构造接口一致但不持有敏感状态。"""

        type(self).constructions += 1

    def run_turn(
        self,
        workspace: Path,
        prompt: str,
        resume_session_id: str | None,
    ) -> AgentTurn:
        """抛出超时以模拟外部 Agent 不可用。"""

        raise subprocess.TimeoutExpired(cmd="claude", timeout=300)


class NonzeroClaudeRunner:
    """模拟 Claude 返回结构化 JSON 但进程退出码非零。"""

    constructions: int = 0

    def __init__(self, plugin_root: Path, persist_sessions: bool = False) -> None:
        """记录运行器构造次数以验证全局阻塞后的快速停止。"""

        type(self).constructions += 1

    def run_turn(
        self,
        workspace: Path,
        prompt: str,
        resume_session_id: str | None,
    ) -> AgentTurn:
        """返回不含敏感正文的非零退出结果。"""

        now = _fixed_now()
        return AgentTurn(
            session_id=None,
            exit_code=1,
            result_text="",
            structured_output=None,
            stderr="Claude Code 产生标准错误输出",
            started_at=now,
            finished_at=now,
        )


def _fixed_now() -> datetime:
    """返回稳定时间，便于验证运行开始和结束字段。"""

    return datetime(2026, 8, 13, 12, 0, tzinfo=UTC)


class ClaudeRunnerTests(unittest.TestCase):
    """验证真实 subprocess 边界之外的全部确定性行为。"""

    def test_repository_root_is_accepted_as_plugin_root(self) -> None:
        """仓库根目录就是插件源码根。"""

        api = _load_runner_api()
        runner = api.ClaudeRunner(
            plugin_root=ROOT,
        )
        self.assertEqual(ROOT.resolve(), runner.plugin_root)

    def test_single_turn_uses_safe_non_persistent_command(self) -> None:
        """单轮命令必须加载当前插件并禁用会话持久化。"""

        api = _load_runner_api()
        process = RecordingProcess(
            '{"type":"result","session_id":"session-1","result":"完成",'
            '"structured_output":{"state":"report"}}'
        )
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            runner = api.ClaudeRunner(
                plugin_root=ROOT,
                persist_sessions=False,
                process_runner=process,
                now=_fixed_now,
            )

            turn = runner.run_turn(workspace, "检查知识库", None)

        command, kwargs = process.calls[0]
        self.assertTrue(Path(command[0]).name.lower().startswith("claude"))
        for required in (
            "--bare",
            "-p",
            "--plugin-dir",
            "--permission-mode",
            "acceptEdits",
            "--output-format",
            "json",
            "--no-session-persistence",
        ):
            self.assertIn(required, command)
        self.assertNotIn("bypassPermissions", command)
        self.assertNotIn("--dangerously-skip-permissions", command)
        plugin_directory = Path(command[command.index("--plugin-dir") + 1])
        self.assertNotEqual(ROOT.resolve(), plugin_directory)
        self.assertIn(".claude-plugin/plugin.json", process.plugin_release_files[0])
        self.assertIn(".claude-plugin/marketplace.json", process.plugin_release_files[0])
        self.assertIn("skills/context-atlas/SKILL.md", process.plugin_release_files[0])
        self.assertNotIn("AGENTS.md", process.plugin_release_files[0])
        self.assertNotIn("CLAUDE.md", process.plugin_release_files[0])
        self.assertFalse(any(path.startswith("tests/") for path in process.plugin_release_files[0]))
        self.assertEqual(workspace, kwargs["cwd"])
        self.assertTrue(kwargs["capture_output"])
        self.assertTrue(kwargs["text"])
        self.assertEqual("utf-8", kwargs["encoding"])
        self.assertEqual("replace", kwargs["errors"])
        self.assertEqual(600, kwargs["timeout"])
        self.assertEqual("session-1", turn.session_id)
        self.assertEqual("完成", turn.result_text)
        self.assertEqual({"state": "report"}, turn.structured_output)
        self.assertEqual(0, turn.exit_code)

    def test_default_runner_resolves_platform_launcher_before_subprocess(self) -> None:
        """Windows 脚本启动器必须解析成可直接交给 subprocess 的绝对路径。"""

        api = _load_runner_api()
        self.assertIsNotNone(shutil.which("claude"))
        process = RecordingProcess(
            '{"type":"result","session_id":"session-1","result":"完成"}'
        )
        with tempfile.TemporaryDirectory() as directory:
            runner = api.ClaudeRunner(
                plugin_root=ROOT,
                process_runner=process,
                now=_fixed_now,
            )

            runner.run_turn(Path(directory), "检查", None)

        resolved = Path(process.calls[0][0][0])
        self.assertTrue(resolved.is_file())
        if os.name == "nt":
            self.assertEqual(".exe", resolved.suffix.lower())

    def test_unconfirmed_read_only_turn_retries_one_transient_timeout(self) -> None:
        """没有续接编号的只读提案轮超时一次后应安全重试。"""

        api = _load_runner_api()
        process = TimeoutThenSuccessProcess()
        with tempfile.TemporaryDirectory() as directory:
            runner = api.ClaudeRunner(
                plugin_root=ROOT,
                process_runner=process,
                now=_fixed_now,
            )

            turn = runner.run_turn(Path(directory), "只检查并给出提案", None)

        self.assertEqual(2, process.calls)
        self.assertEqual(0, turn.exit_code)
        self.assertEqual("完成", turn.result_text)

    def test_confirmed_resumed_turn_does_not_retry_timeout(self) -> None:
        """可能产生正式写入的续接轮超时后不得自动重试。"""

        api = _load_runner_api()
        process = TimeoutThenSuccessProcess()
        with tempfile.TemporaryDirectory() as directory:
            runner = api.ClaudeRunner(
                plugin_root=ROOT,
                persist_sessions=True,
                process_runner=process,
                now=_fixed_now,
            )

            with self.assertRaises(subprocess.TimeoutExpired):
                runner.run_turn(Path(directory), "执行已确认提案", "session-1")

        self.assertEqual(1, process.calls)

    def test_resumable_turn_uses_session_without_disabling_persistence(self) -> None:
        """两阶段场景必须持久化首轮会话并用会话编号续接。"""

        api = _load_runner_api()
        process = RecordingProcess(
            '{"type":"result","session_id":"session-1","result":"继续"}'
        )
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            runner = api.ClaudeRunner(
                plugin_root=ROOT,
                persist_sessions=True,
                process_runner=process,
                now=_fixed_now,
            )

            runner.run_turn(workspace, "先生成提案", None)
            runner.run_turn(workspace, "确认上一轮提案", "session-1")

        first_command = process.calls[0][0]
        second_command = process.calls[1][0]
        self.assertNotIn("--no-session-persistence", first_command)
        self.assertNotIn("--no-session-persistence", second_command)
        resume_index = second_command.index("--resume")
        self.assertEqual("session-1", second_command[resume_index + 1])

    def test_malformed_json_is_a_failed_turn_without_raw_output_leak(self) -> None:
        """无法解析的输出必须失败，并且不复制到结构化结果。"""

        api = _load_runner_api()
        process = RecordingProcess(
            "not-json user@example.com token=secret",
            returncode=0,
            stderr="authorization bearer-secret",
        )
        with tempfile.TemporaryDirectory() as directory:
            runner = api.ClaudeRunner(
                plugin_root=ROOT,
                process_runner=process,
                now=_fixed_now,
            )

            turn = runner.run_turn(Path(directory), "检查", None)

        self.assertNotEqual(0, turn.exit_code)
        self.assertEqual("", turn.result_text)
        self.assertIsNone(turn.structured_output)
        self.assertNotIn("user@example.com", turn.stderr)
        self.assertNotIn("secret", turn.stderr)

    def test_evidence_omits_session_prompt_and_raw_conversation(self) -> None:
        """持久化证据只能保留白名单字段和脱敏结构摘要。"""

        api = _load_runner_api()
        process = RecordingProcess(
            '{"type":"result","session_id":"private-session","result":'
            '"C:\\\\Users\\\\Seven user@example.com token=secret",'
            '"structured_output":{"state":"report","token":"secret"}}'
        )
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            runner = api.ClaudeRunner(
                plugin_root=ROOT,
                process_runner=process,
                now=_fixed_now,
            )
            turn = runner.run_turn(workspace, "包含私密需求正文", None)

            evidence = api.build_turn_evidence(turn, scenario_id="safe-case")

        serialized = str(evidence)
        self.assertEqual("safe-case", evidence["scenario_id"])
        self.assertEqual(0, evidence["exit_code"])
        self.assertNotIn("private-session", serialized)
        self.assertNotIn("私密需求正文", serialized)
        self.assertNotIn("user@example.com", serialized)
        self.assertNotIn("secret", serialized)
        self.assertNotIn("C:\\Users\\Seven", serialized)

    def test_scenario_orchestrator_records_four_sanitized_behavior_results(self) -> None:
        """四个场景必须共享断言器并只输出脱敏结构证据。"""

        try:
            orchestration = importlib.import_module("scripts.run_agent_conformance")
        except ModuleNotFoundError as error:
            self.fail(f"Claude 场景编排器尚未实现：{error.name}")
        with tempfile.TemporaryDirectory() as directory:
            report = orchestration.run_claude_conformance(
                plugin_root=ROOT,
                workspace_root=Path(directory),
                runner_factory=ScriptedClaudeRunner,
                agent_version="2.1.226 (Claude Code)",
            )

        self.assertEqual("claude", report["agent"])
        self.assertEqual("passed", report["status"])
        scenarios = report["scenarios"]
        self.assertEqual(4, len(scenarios))
        self.assertEqual({"passed"}, {item["status"] for item in scenarios})
        serialized = json.dumps(report, ensure_ascii=False)
        for forbidden in (
            "session-1",
            "user@example.com",
            "token=secret",
            "原始模型正文",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_external_failure_marks_scenarios_blocked(self) -> None:
        """认证、网络或超时错误必须记为阻塞而不是通过。"""

        try:
            orchestration = importlib.import_module("scripts.run_agent_conformance")
        except ModuleNotFoundError as error:
            self.fail(f"Claude 场景编排器尚未实现：{error.name}")
        FailingClaudeRunner.constructions = 0
        with tempfile.TemporaryDirectory() as directory:
            report = orchestration.run_claude_conformance(
                plugin_root=ROOT,
                workspace_root=Path(directory),
                runner_factory=FailingClaudeRunner,
                agent_version="2.1.226 (Claude Code)",
            )

        self.assertEqual("blocked", report["status"])
        self.assertEqual({"blocked"}, {item["status"] for item in report["scenarios"]})
        self.assertEqual(1, FailingClaudeRunner.constructions)

    def test_script_entrypoint_can_load_repository_packages(self) -> None:
        """计划规定的直接脚本命令必须能加载顶层 scripts 包。"""

        completed = subprocess.run(
            [sys.executable, "scripts/run_agent_conformance.py", "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("--plugin-root", completed.stdout)

    def test_managed_workspace_root_is_writable_and_cleaned(self) -> None:
        """真实入口创建的工作根必须可写，并在退出上下文后精确清理。"""

        orchestration = importlib.import_module("scripts.run_agent_conformance")
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            with orchestration.temporary_workspace_root(parent) as workspace:
                probe = workspace / "probe.txt"
                probe.write_text("writable", encoding="utf-8")
                self.assertEqual("writable", probe.read_text(encoding="utf-8"))
                created_workspace = workspace

            self.assertFalse(created_workspace.exists())
            self.assertTrue(parent.exists())

    def test_main_lets_claude_resolve_auth_without_environment_preflight(self) -> None:
        """入口不得因进程环境缺少密钥而跳过 Claude 自己可解析的用户设置。"""

        orchestration = importlib.import_module("scripts.run_agent_conformance")
        passed_report = {
            "schema_version": "1.0",
            "agent": "claude",
            "agent_version": "2.1.226 (Claude Code)",
            "status": "passed",
            "scenarios": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "claude.json"
            arguments = [
                "run_agent_conformance.py",
                "--agent",
                "claude",
                "--plugin-root",
                str(ROOT),
                "--output",
                str(output),
            ]
            with (
                mock.patch.object(sys, "argv", arguments),
                mock.patch.dict(os.environ, {}, clear=True),
                mock.patch.object(
                    orchestration,
                    "_claude_version",
                    return_value="2.1.226 (Claude Code)",
                ),
                mock.patch.object(
                    orchestration,
                    "run_claude_conformance",
                    return_value=passed_report,
                ) as run_scenarios,
            ):
                exit_code = orchestration.main()

            report = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(0, exit_code)
        self.assertEqual("passed", report["status"])
        run_scenarios.assert_called_once()

    def test_explicit_scenario_prompt_starts_with_skill_command(self) -> None:
        """显式验收场景必须真正以 Skill 命令启动。"""

        orchestration = importlib.import_module("scripts.run_agent_conformance")

        self.assertTrue(
            orchestration.EXPLICIT_INITIALIZE_PROMPT.startswith(
                "/context-atlas:context-atlas"
            )
        )

    def test_nonzero_turn_stops_repeating_globally_blocked_scenarios(self) -> None:
        """结构化非零结果也必须快速阻塞剩余场景。"""

        orchestration = importlib.import_module("scripts.run_agent_conformance")
        NonzeroClaudeRunner.constructions = 0
        with tempfile.TemporaryDirectory() as directory:
            report = orchestration.run_claude_conformance(
                plugin_root=ROOT,
                workspace_root=Path(directory),
                runner_factory=NonzeroClaudeRunner,
                agent_version="2.1.226 (Claude Code)",
            )

        self.assertEqual("blocked", report["status"])
        self.assertEqual(1, NonzeroClaudeRunner.constructions)


if __name__ == "__main__":
    unittest.main()
