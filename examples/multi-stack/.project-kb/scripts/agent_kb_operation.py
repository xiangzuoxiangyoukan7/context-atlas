"""为 Agent 提供非交互式知识库结构化操作命令。"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
from typing import Sequence

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.project_kb.agent_operation import execute_initialize


def _default_assets_root() -> Path:
    """根据脚本位于源码仓库还是发布资产中推导默认资源根目录。"""

    scripts_parent = Path(__file__).resolve().parents[1]
    if (scripts_parent / "templates" / "core" / "doc-project").is_dir():
        return scripts_parent
    return scripts_parent / "skills" / "context-atlas" / "assets"


def _parser() -> argparse.ArgumentParser:
    """创建只接受已确认结构化参数的命令行解析器。"""

    parser = argparse.ArgumentParser(description="执行已确认的 Context Atlas 结构化操作")
    subparsers = parser.add_subparsers(dest="operation", required=True)
    initialize = subparsers.add_parser("initialize")
    initialize.add_argument("project_root", type=Path)
    initialize.add_argument("--project-name")
    initialize.add_argument("--proposal-revision", required=True)
    initialize.add_argument("--confirmed-revision", required=True)
    initialize.add_argument("--assets-root", type=Path, default=_default_assets_root())
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行初始化操作并输出不含会话内容的 JSON 报告。"""

    parser = _parser()
    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
        report = execute_initialize(
            project_root=args.project_root,
            project_name=args.project_name,
            proposal_revision=args.proposal_revision,
            confirmed_revision=args.confirmed_revision,
            assets_root=args.assets_root,
        )
    except (OSError, ValueError, PermissionError) as error:
        print(
            json.dumps(
                {"ok": False, "error_type": type(error).__name__, "message": str(error)},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2
    payload = asdict(report)
    payload["target"] = str(report.target)
    payload["ok"] = report.validator_exit_code == 0
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return report.validator_exit_code


if __name__ == "__main__":
    raise SystemExit(main())
