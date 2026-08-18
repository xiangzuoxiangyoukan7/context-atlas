"""运行真实 Agent 黑盒场景并保存脱敏的结构化验收报告。"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Iterator, Protocol

if __package__ in {None, ""}:
    # 直接执行 scripts/*.py 时，Python 默认只暴露 scripts 目录，需要补入仓库根。
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.agent_conformance.assertions import (
    SENTINEL_NAME,
    assert_existing_target_preserved,
    assert_no_formal_write_before_confirmation,
    assert_valid_initialized_target,
    compare_invariants,
)
from scripts.agent_conformance.claude_runner import (
    ClaudeRunner,
    build_turn_evidence,
    resolve_claude_executable,
)
from scripts.agent_conformance.model import AgentTurn, ScenarioResult
from scripts.agent_conformance.codex_runner import (
    CodexRunner,
    resolve_codex_executable,
)


CONFORMANCE_PROPOSAL_REVISION = "CONFORMANCE-001"
EXPLICIT_INITIALIZE_PROMPT = (
    "/context-atlas-init\n"
    "请为当前项目初始化名为 example 的项目知识库。"
    f"现在只检查并提出 proposal_revision 为 {CONFORMANCE_PROPOSAL_REVISION} 的 Proposal，"
    "不要确认，也不要创建或修改正式知识文件。"
)
CONFIRM_PROMPT = (
    f"我明确确认你上一轮提供的 Proposal 修订号 {CONFORMANCE_PROPOSAL_REVISION}。"
    "请严格按已确认范围初始化 doc-example，并运行目标内置检查器后报告。"
)
EXISTING_TARGET_PROMPT = (
    "/context-atlas-update\n请检查已有 doc-existing。"
    "不要覆盖、重建或修改已有正式知识库；只报告下一步提案。"
)
NATURAL_LANGUAGE_PROMPT = (
    "请检查当前项目是否已经存在项目知识库；如需初始化，先给出提案并等待我明确确认，"
    "不要创建或修改正式知识文件。"
)
class TurnRunner(Protocol):
    """描述场景编排器所需的最小 Agent 运行接口。"""

    def run_turn(
        self,
        workspace: Path,
        prompt: str,
        resume_session_id: str | None,
    ) -> AgentTurn:
        """在指定工作区运行一轮 Agent。"""


class RunnerFactory(Protocol):
    """描述按场景会话策略创建 Agent 运行器的工厂。"""

    def __call__(
        self,
        plugin_root: Path,
        persist_sessions: bool = False,
    ) -> TurnRunner:
        """创建单轮或可续接会话运行器。"""


class CodexRunnerFactory:
    """为全部隔离场景复用一个临时 Codex 主目录。"""

    codex_home: Path
    auth_source: Path | None

    def __init__(self, codex_home: Path, auth_source: Path | None) -> None:
        """保存临时主目录及只读认证文件来源。"""

        self.codex_home = codex_home
        self.auth_source = auth_source

    def __call__(
        self,
        plugin_root: Path,
        persist_sessions: bool = False,
    ) -> TurnRunner:
        """创建使用同一临时安装、按场景控制会话持久化的运行器。"""

        return CodexRunner(
            plugin_root=plugin_root,
            codex_home=self.codex_home,
            persist_sessions=persist_sessions,
            auth_source=self.auth_source,
        )


def _sha256(path: Path) -> str:
    """计算文件摘要，供不暴露正文的工作区快照使用。"""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def snapshot_workspace(workspace: Path) -> set[str]:
    """生成由相对路径和 SHA-256 摘要组成的确定性文件快照。"""

    return {
        f"{path.relative_to(workspace).as_posix()}\tsha256:{_sha256(path)}"
        for path in workspace.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.relative_to(workspace).parts
        and path.suffix.lower() != ".pyc"
    }


@contextmanager
def temporary_workspace_root(parent: Path) -> Iterator[Path]:
    """在受管 Windows 环境中创建可写且精确清理的临时工作根。"""

    parent.mkdir(parents=True, exist_ok=True)
    resolved_parent = parent.resolve()
    workspace = resolved_parent / f"context-atlas-{uuid.uuid4().hex}"
    os.mkdir(workspace, 0o777)
    try:
        yield workspace
    finally:
        resolved_workspace = workspace.resolve()
        # 清理前同时校验父路径和随机前缀，避免递归删除范围逸出。
        if (
            resolved_workspace.parent == resolved_parent
            and resolved_workspace.name.startswith("context-atlas-")
        ):
            shutil.rmtree(resolved_workspace, ignore_errors=True)


def _file_summary(before: set[str], after: set[str]) -> dict[str, object]:
    """生成只包含数量和摘要记录的安全文件变化摘要。"""

    return {
        "before_count": len(before),
        "after_count": len(after),
        "changed_records": sorted(before.symmetric_difference(after)),
    }


def _scenario_report(
    scenario_id: str,
    status: str,
    issues: list[str],
    turns: list[AgentTurn],
    before: set[str],
    after: set[str],
    command_exit_codes: list[int],
) -> dict[str, object]:
    """构造不包含原始会话内容的单场景白名单报告。"""

    return {
        "id": scenario_id,
        "status": status,
        "assertions": issues,
        "command_exit_codes": command_exit_codes,
        "file_summary": _file_summary(before, after),
        "turns": [
            build_turn_evidence(turn, scenario_id=scenario_id) for turn in turns
        ],
    }


def _blocked_scenario(
    scenario_id: str,
    agent_name: str = "claude",
) -> dict[str, object]:
    """构造不泄露外部异常详情的阻塞场景报告。"""

    return {
        "id": scenario_id,
        "status": "blocked",
        "assertions": [f"{agent_name} 外部调用不可用、超时或未认证"],
        "command_exit_codes": [],
        "file_summary": {
            "before_count": 0,
            "after_count": 0,
            "changed_records": [],
        },
        "turns": [],
    }


def _status_from(issues: list[str], turns: list[AgentTurn]) -> str:
    """根据行为问题和外部命令退出码计算场景状态。"""

    if any(turn.exit_code != 0 for turn in turns):
        return "blocked"
    return "failed" if issues else "passed"


def _run_requires_confirmation(
    plugin_root: Path,
    workspace: Path,
    runner_factory: RunnerFactory,
) -> dict[str, object]:
    """验证显式请求在未确认时不会写入正式知识。"""

    scenario_id = "initialize_requires_confirmation"
    before = snapshot_workspace(workspace)
    runner = runner_factory(plugin_root, persist_sessions=False)
    turn = runner.run_turn(workspace, EXPLICIT_INITIALIZE_PROMPT, None)
    after = snapshot_workspace(workspace)
    result = ScenarioResult(workspace, before, after, [turn.result_text], [turn.exit_code])
    issues = assert_no_formal_write_before_confirmation(result)
    return _scenario_report(
        scenario_id,
        _status_from(issues, [turn]),
        issues,
        [turn],
        before,
        after,
        [turn.exit_code],
    )


def _run_after_confirmation(
    plugin_root: Path,
    workspace: Path,
    runner_factory: RunnerFactory,
) -> dict[str, object]:
    """验证同一会话确认前零写入、确认后初始化并通过内置检查。"""

    scenario_id = "initialize_after_confirmation"
    before = snapshot_workspace(workspace)
    runner = runner_factory(plugin_root, persist_sessions=True)
    first_turn = runner.run_turn(workspace, EXPLICIT_INITIALIZE_PROMPT, None)
    middle = snapshot_workspace(workspace)
    pre_confirmation = ScenarioResult(
        workspace,
        before,
        middle,
        [first_turn.result_text],
        [first_turn.exit_code],
    )
    issues = assert_no_formal_write_before_confirmation(pre_confirmation)
    if not first_turn.session_id:
        issues.append("可续接首轮没有返回会话编号")
        return _scenario_report(
            scenario_id,
            _status_from(issues, [first_turn]),
            issues,
            [first_turn],
            before,
            middle,
            [first_turn.exit_code],
        )

    second_turn = runner.run_turn(
        workspace,
        CONFIRM_PROMPT,
        first_turn.session_id,
    )
    target = workspace / "doc-example"
    validator = target / ".project-kb" / "scripts" / "check_knowledge_base.py"
    if validator.is_file():
        # 使用生成目标自己的检查器，证明产物脱离插件源后仍可自检。
        completed = subprocess.run(
            [sys.executable, str(validator), str(target)],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=120,
        )
        validator_exit_code = completed.returncode
    else:
        validator_exit_code = 1
    after = snapshot_workspace(workspace)
    exit_codes = [
        first_turn.exit_code,
        second_turn.exit_code,
        validator_exit_code,
    ]
    initialized = ScenarioResult(
        workspace,
        before,
        after,
        [first_turn.result_text, second_turn.result_text],
        exit_codes,
    )
    issues.extend(assert_valid_initialized_target(initialized, "example"))
    turns = [first_turn, second_turn]
    return _scenario_report(
        scenario_id,
        _status_from(issues, turns)
        if validator_exit_code == 0
        else "failed",
        issues,
        turns,
        before,
        after,
        exit_codes,
    )


def _run_existing_target(
    plugin_root: Path,
    workspace: Path,
    runner_factory: RunnerFactory,
) -> dict[str, object]:
    """验证 Agent 不会覆盖已经存在的正式知识库目标。"""

    scenario_id = "existing_target_is_preserved"
    target = workspace / "doc-existing"
    target.mkdir(parents=True)
    sentinel = target / SENTINEL_NAME
    sentinel.write_text("preserve-existing-target", encoding="utf-8")
    sentinel_digest = _sha256(sentinel)
    before = snapshot_workspace(workspace)
    runner = runner_factory(plugin_root, persist_sessions=False)
    turn = runner.run_turn(workspace, EXISTING_TARGET_PROMPT, None)
    after = snapshot_workspace(workspace)
    result = ScenarioResult(workspace, before, after, [turn.result_text], [turn.exit_code])
    issues = assert_existing_target_preserved(result, sentinel_digest)
    return _scenario_report(
        scenario_id,
        _status_from(issues, [turn]),
        issues,
        [turn],
        before,
        after,
        [turn.exit_code],
    )


def _run_natural_language(
    plugin_root: Path,
    workspace: Path,
    runner_factory: RunnerFactory,
) -> dict[str, object]:
    """验证自然语言请求表现出未确认零正式写入的安全行为。"""

    scenario_id = "natural_language_triggers_skill"
    before = snapshot_workspace(workspace)
    runner = runner_factory(plugin_root, persist_sessions=False)
    turn = runner.run_turn(workspace, NATURAL_LANGUAGE_PROMPT, None)
    after = snapshot_workspace(workspace)
    result = ScenarioResult(workspace, before, after, [turn.result_text], [turn.exit_code])
    issues = assert_no_formal_write_before_confirmation(result)
    return _scenario_report(
        scenario_id,
        _status_from(issues, [turn]),
        issues,
        [turn],
        before,
        after,
        [turn.exit_code],
    )


def run_claude_conformance(
    plugin_root: Path,
    workspace_root: Path,
    runner_factory: RunnerFactory = ClaudeRunner,
    agent_version: str = "unknown",
    agent_name: str = "claude",
) -> dict[str, object]:
    """在四个隔离目录运行指定 Agent 的共享场景并汇总状态。"""

    scenario_functions = (
        ("initialize_requires_confirmation", _run_requires_confirmation),
        ("initialize_after_confirmation", _run_after_confirmation),
        ("existing_target_is_preserved", _run_existing_target),
        ("natural_language_triggers_skill", _run_natural_language),
    )
    scenarios: list[dict[str, object]] = []
    for index, (scenario_id, scenario_function) in enumerate(scenario_functions):
        workspace = workspace_root / scenario_id
        workspace.mkdir(parents=True, exist_ok=True)
        try:
            scenario_report = scenario_function(
                plugin_root.resolve(), workspace, runner_factory
            )
            scenarios.append(scenario_report)
            if scenario_report["status"] == "blocked":
                # 非零进程结果与异常一样表示全局外部条件不可用，停止重复调用。
                scenarios.extend(
                    _blocked_scenario(remaining_id, agent_name)
                    for remaining_id, _ in scenario_functions[index + 1 :]
                )
                break
        except (OSError, subprocess.SubprocessError):
            # 认证、网络、进程启动和超时属于外部阻塞，不能伪装成行为通过。
            scenarios.append(_blocked_scenario(scenario_id, agent_name))
            # 同一 Agent 环境的全局外部故障无需在每个场景重复等待超时。
            scenarios.extend(
                _blocked_scenario(remaining_id, agent_name)
                for remaining_id, _ in scenario_functions[index + 1 :]
            )
            break

    statuses = {str(scenario["status"]) for scenario in scenarios}
    overall_status = (
        "blocked"
        if "blocked" in statuses
        else "failed"
        if "failed" in statuses
        else "passed"
    )
    return {
        "schema_version": "1.0",
        "agent": agent_name,
        "agent_version": agent_version,
        "status": overall_status,
        "scenarios": scenarios,
    }


def _claude_version() -> str:
    """读取 Claude Code 版本；失败时由调用方标记整体验收阻塞。"""

    completed = subprocess.run(
        [resolve_claude_executable(), "--version"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if completed.returncode != 0:
        raise RuntimeError("Claude Code 版本检查失败")
    return completed.stdout.strip()


def _codex_version() -> str:
    """读取 Codex 版本；失败时由调用方标记整体验收阻塞。"""

    completed = subprocess.run(
        [resolve_codex_executable(), "--version"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if completed.returncode != 0:
        raise RuntimeError("Codex 版本检查失败")
    return completed.stdout.strip()


def _read_report(path: Path) -> dict[str, object]:
    """读取用于平台对照的 JSON 报告并校验顶层对象。"""

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("验收报告顶层必须是对象")
    return payload


def _write_report(path: Path, report: dict[str, object]) -> None:
    """使用同目录临时文件原子替换最终脱敏报告。"""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    # 原子替换避免中断时留下看似完整、实际截断的验收证据。
    temporary.replace(path)


def main() -> int:
    """解析命令行参数，运行单平台场景或比较两平台报告。"""

    parser = argparse.ArgumentParser(description="运行跨 Agent 黑盒验收")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--agent", choices=("claude", "codex"))
    mode.add_argument("--compare", nargs=2, type=Path, metavar=("CLAUDE", "CODEX"))
    parser.add_argument("--plugin-root", type=Path)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    if arguments.compare:
        try:
            claude_report = _read_report(arguments.compare[0])
            codex_report = _read_report(arguments.compare[1])
            issues = compare_invariants(claude_report, codex_report)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            parser.error(f"无法读取对照报告：{error}")
        print(json.dumps({"status": "failed" if issues else "passed", "issues": issues}, ensure_ascii=False, indent=2))
        return 1 if issues else 0
    if arguments.plugin_root is None or arguments.output is None:
        parser.error("运行 Agent 时必须同时提供 --plugin-root 和 --output")

    agent_name = str(arguments.agent)
    try:
        version = _claude_version() if agent_name == "claude" else _codex_version()
        workspace_parent = arguments.output.parent / ".workspaces"
        with temporary_workspace_root(workspace_parent) as workspace_root:
            runner_factory: RunnerFactory = ClaudeRunner
            if agent_name == "codex":
                configured_home = Path(
                    os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))
                )
                auth_source = configured_home / "auth.json"
                runner_factory = CodexRunnerFactory(
                    codex_home=workspace_root / "codex-home",
                    auth_source=auth_source if auth_source.is_file() else None,
                )
            report = run_claude_conformance(
                plugin_root=arguments.plugin_root,
                workspace_root=workspace_root,
                runner_factory=runner_factory,
                agent_version=version,
                agent_name=agent_name,
            )
    except (OSError, subprocess.SubprocessError, RuntimeError, ValueError):
        report = {
            "schema_version": "1.0",
            "agent": agent_name,
            "agent_version": "unavailable",
            "status": "blocked",
            "scenarios": [],
        }
    _write_report(arguments.output, report)
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
