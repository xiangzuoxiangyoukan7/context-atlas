"""定义不同 Agent 运行器共用的场景结果模型。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScenarioResult:
    """保存一个验收场景可被机器复核的最小证据。"""

    workspace: Path
    before: set[str]
    after: set[str]
    messages: list[str]
    command_exit_codes: list[int]
