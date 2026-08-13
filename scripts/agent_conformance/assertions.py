"""根据文件和命令证据断言跨 Agent 行为不变量。"""

from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath

from .model import ScenarioResult


SNAPSHOT_SEPARATOR = "\tsha256:"
SENTINEL_NAME = ".context-atlas-sentinel"


def _record_path(record: str) -> str:
    """从带摘要的快照记录中提取 POSIX 相对路径。"""

    return record.split(SNAPSHOT_SEPARATOR, maxsplit=1)[0]


def _is_formal_knowledge_path(relative_path: str) -> bool:
    """判断路径是否位于 Context Atlas 正式知识库目录。"""

    parts = PurePosixPath(relative_path).parts
    return bool(parts) and parts[0].startswith("doc-")


def _sha256(path: Path) -> str:
    """计算哨兵文件摘要，避免依赖 Agent 的文字声明。"""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _snapshot_paths(records: set[str]) -> set[str]:
    """将快照记录集合转换为相对路径集合。"""

    return {_record_path(record) for record in records}


def assert_no_formal_write_before_confirmation(result: ScenarioResult) -> list[str]:
    """报告未确认阶段新增、删除或修改的正式知识文件。"""

    # 使用对称差集同时捕获新增、删除和同路径内容摘要变化。
    changed_records = result.before.symmetric_difference(result.after)
    changed_paths = sorted(
        {
            _record_path(record)
            for record in changed_records
            if _is_formal_knowledge_path(_record_path(record))
        }
    )
    return [f"未确认阶段修改了正式知识文件：{path}" for path in changed_paths]


def assert_existing_target_preserved(
    result: ScenarioResult,
    sentinel_sha256: str,
) -> list[str]:
    """报告已有目标快照或固定哨兵内容发生的任何变化。"""

    issues: list[str] = []
    changed_records = result.before.symmetric_difference(result.after)
    changed_formal_paths = sorted(
        {
            _record_path(record)
            for record in changed_records
            if _is_formal_knowledge_path(_record_path(record))
        }
    )
    if changed_formal_paths:
        issues.append(
            "已有正式目标发生变化：" + "、".join(changed_formal_paths)
        )

    sentinels = sorted(result.workspace.rglob(SENTINEL_NAME))
    if len(sentinels) != 1:
        issues.append(f"应存在且仅存在一个哨兵文件，实际为 {len(sentinels)} 个")
        return issues
    if _sha256(sentinels[0]) != sentinel_sha256:
        issues.append("已有目标的哨兵文件摘要发生变化")
    return issues


def assert_valid_initialized_target(
    result: ScenarioResult,
    expected_name: str,
) -> list[str]:
    """报告确认后目标在结构、自包含性、名称或检查结果上的问题。"""

    issues: list[str] = []
    target_name = expected_name if expected_name.startswith("doc-") else f"doc-{expected_name}"
    target = result.workspace / target_name
    required_files = (
        target / "knowledge-base.yaml",
        target / ".project-kb" / "scripts" / "check_knowledge_base.py",
        target / ".project-kb" / "schemas" / "catalog.json",
    )
    after_paths = _snapshot_paths(result.after)
    before_paths = _snapshot_paths(result.before)

    for path in required_files:
        relative_path = path.relative_to(result.workspace).as_posix()
        if not path.is_file():
            issues.append(f"初始化目标缺少自包含文件：{relative_path}")
        if relative_path not in after_paths or relative_path in before_paths:
            issues.append(f"初始化场景未产生预期文件：{relative_path}")

    manifest = target / "knowledge-base.yaml"
    if manifest.is_file():
        expected_line = f"knowledge_base_name: {target_name}"
        if expected_line not in manifest.read_text(encoding="utf-8").splitlines():
            issues.append(f"知识库名称不是预期值：{target_name}")

    # 退出码是实际检查器结果；自然语言中的“成功”不能替代它。
    if not result.command_exit_codes or any(
        exit_code != 0 for exit_code in result.command_exit_codes
    ):
        issues.append(f"场景命令存在非零退出码：{result.command_exit_codes}")
    return issues
