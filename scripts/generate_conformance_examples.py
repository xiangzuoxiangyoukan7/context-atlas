from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.project_kb.initializer import initialize_from_assets


DATE = "2026-08-10"
EXAMPLE_NAMES = ("single-stack", "multi-stack")


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def _record(path: Path, metadata: dict[str, object], body: str) -> None:
    lines = ["---"]
    for key, value in metadata.items():
        if isinstance(value, list):
            lines.append(f"{key}: [{', '.join(str(item) for item in value)}]")
        else:
            lines.append(f"{key}: {value}")
    lines.extend(["---", body])
    _write(path, "\n".join(lines))


def _source(root: Path, identifier: str, source_type: str, reference: str) -> None:
    _record(
        root / "00-项目总览" / f"{identifier}.md",
        {
            "id": identifier,
            "type": "source",
            "title": f"示例来源 {identifier}",
            "source_type": source_type,
            "reference": reference,
            "last_updated": DATE,
        },
        f"# {identifier}\n\n这是黄金样例使用的虚构来源：`{reference}`。",
    )


def _approved_item(root: Path, relative: str, identifier: str, title: str, body: str) -> None:
    _record(
        root / relative,
        {
            "id": identifier,
            "type": "knowledge_item",
            "title": title,
            "status": "approved",
            "version": "1.0.0",
            "sources": ["SRC-001", "SRC-002"],
            "approved_by": "example-owner",
            "approved_at": DATE,
            "proposal_revision": "1",
            "confirmed_revision": "1",
            "last_updated": DATE,
        },
        body,
    )


def _approved_data_asset(root: Path, name: str) -> None:
    source_types = ["database"] if name == "single-stack" else ["database", "api", "file"]
    _record(
        root / "02-架构与契约/数据资产/DATA-001-知识项.md",
        {
            "id": "DATA-001",
            "type": "data_asset",
            "title": "知识项数据",
            "status": "approved",
            "version": "1.0.0",
            "sources": ["SRC-001", "SRC-002"],
            "owner": "example-owner",
            "source_types": source_types,
            "sensitivity": "internal",
            "retention": "project-lifetime",
            "approved_by": "example-owner",
            "approved_at": DATE,
            "proposal_revision": "1",
            "confirmed_revision": "1",
            "last_updated": DATE,
        },
        """# DATA-001：知识项数据

这是仅用于黄金样例的虚构业务数据资产，技术细节见[数据库契约](../数据库/DB-001.md)和[接口契约](../CONTRACT-001.md)。

## 数据流转

输入 → 存储 → 查询组件。

## 质量要求

写入前校验知识项标识和来源引用；缺失值必须显式标记。

## 访问规则

仅 `example-owner` 可访问此虚构内部示例数据。

## 保存规则

按 `project-lifetime` 保存，项目结束后按已确认的处置规则清理。
""",
    )


def _populate_example(root: Path, name: str) -> None:
    _source(root, "SRC-001", "user_statement", "fictional example-owner confirmation")
    _source(root, "SRC-002", "repository_file", "README.example")
    _write(
        root / "00-项目总览/项目目标与成功标准.md",
        """# 项目目标与成功标准

> 虚构黄金样例；事实由 `example-owner` 于 2026-08-10 确认，来源为 SRC-001、SRC-002。

| 编号 | 可观察结果 | 衡量方式 | 状态 | 来源 |
| --- | --- | --- | --- | --- |
| GOAL-01 | 团队能查询已批准的示例知识 | 返回带来源的结果 | approved | SRC-001 |
""",
    )
    _write(
        root / "00-项目总览/项目边界.md",
        """# 项目边界

| 类型 | 内容 | 状态 | 来源 |
| --- | --- | --- | --- |
| 范围内 | 存储并查询虚构项目知识 | approved | SRC-001 |
| 范围外 | 真实业务处理与用户凭据 | approved | SRC-001 |
""",
    )
    _write(
        root / "00-项目总览/产品能力地图.md",
        """# 产品能力地图

| 功能编号 | 名称 | 阶段 | 优先级 | 当前切片 | 状态 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| F01 | 查询已批准知识 | mvp | P0 | included | baselined | SRC-001 |
""",
    )
    _write(
        root / "00-项目总览/术语表.md",
        """# 术语表

| 术语 | 定义 | 来源 | 状态 |
| --- | --- | --- | --- |
| 知识项 | 带版本、状态和来源的项目事实 | SRC-001 | approved |
""",
    )
    _write(
        root / "00-项目总览/技术栈与版本.md",
        """# 技术栈与版本

| 技术 | 版本 | 使用目录或模块 | 项目用途 | 构建、测试与运行命令 | 配置位置 | 来源 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Java | 21 | backend | Spring Boot API | mvn test | application.yml | SRC-001 | approved |
""" if name == "single-stack" else """# 技术栈与版本

| 技术 | 版本 | 使用目录或模块 | 项目用途 | 构建、测试与运行命令 | 配置位置 | 来源 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Spring Boot | 3.x | backend | API 服务 | mvn test | application.yml | SRC-001 | approved |
| Python | 3.12 | tools | 数据处理任务 | pytest | pyproject.toml | SRC-002 | approved |
| Vue | 3.x | web | 浏览器界面 | npm test | package.json | SRC-001 | approved |
""",
    )

    for relative, identifier, title in (
        ("02-架构与契约/CONTRACT-001.md", "CONTRACT-001", "查询契约"),
        ("02-架构与契约/数据库/DB-001.md", "DB-001", "知识项存储"),
        ("02-架构与契约/原型/PROTO-001.md", "PROTO-001", "查询流程原型"),
        ("02-架构与契约/外部依赖/EXT-001.md", "EXT-001", "示例时钟依赖"),
        ("04-决策记录/ADR-001.md", "ADR-001", "采用版本化知识项"),
    ):
        _approved_item(
            root,
            relative,
            identifier,
            title,
            f"# {identifier}：{title}\n\n虚构设计事实；关联 F01，来源 SRC-001、SRC-002。",
        )
    _approved_data_asset(root, name)
    _write(
        root / "02-架构与契约/系统架构.md",
        """# 系统架构

查询组件读取 [DB-001](./数据库/DB-001.md)，遵循 [CONTRACT-001](./CONTRACT-001.md)，外部依赖见 [EXT-001](./外部依赖/EXT-001.md)。全部内容为已确认虚构样例。
""",
    )
    _record(
        root / "01-功能基线/F01-查询已批准知识.md",
        {
            "id": "F01",
            "type": "feature",
            "title": "查询已批准知识",
            "status": "baselined",
            "phase": "mvp",
            "priority": "P0",
            "current_slice": "included",
            "depends_on": [],
            "acceptance": ["F01-AC-01"],
            "contracts": ["CONTRACT-001"],
            "adr": ["ADR-001"],
            "database": ["DB-001"],
            "prototypes": ["PROTO-001"],
            "external_dependencies": ["EXT-001"],
            "last_updated": DATE,
        },
        "# F01：查询已批准知识\n\n返回知识值、版本和来源。业务实现尚未开始。",
    )
    _record(
        root / "03-实施与验收/任务包/TASK-F01-001.md",
        {
            "id": "TASK-F01-001",
            "type": "task",
            "title": "实现示例知识查询",
            "feature": "F01",
            "status": "ready",
            "acceptance": ["F01-AC-01"],
            "last_updated": DATE,
        },
        "# TASK-F01-001\n\n这是未执行的示例任务，不代表业务实现完成。",
    )
    _write(
        root / "03-实施与验收/CURRENT.md",
        """# 当前任务

- 任务编号：TASK-F01-001
- 任务包：[TASK-F01-001](./任务包/TASK-F01-001.md)
""",
    )
    _write(
        root / "03-实施与验收/验收矩阵.md",
        """# 验收矩阵

| 验收编号 | 对象 | 条件摘要 | 结果 | 证据位置 | 对应版本 |
| --- | --- | --- | --- | --- | --- |
| F01-AC-01 | F01 | 返回值、版本和来源 | not_started | — | — |
""",
    )
    _write(
        root / "03-实施与验收/验收证据/README.md",
        """# 验收证据

当前只有知识库结构校验证据；业务验收 `F01-AC-01` 尚未执行，不得标记为 passed。
""",
    )


def _minimal_fixture(root: Path, expected_code: str) -> None:
    root.mkdir(parents=True)
    _write(root / "README.md", f"# Invalid fixture\n\nexpected_code: {expected_code}")
    _write(root / "03-实施与验收/CURRENT.md", "# 当前状态\n\n- 当前任务：无可执行开发任务")
    _write(
        root / "03-实施与验收/验收矩阵.md",
        "# 验收矩阵\n\n| 验收编号 | 对象 | 条件摘要 | 结果 | 证据位置 | 对应版本 |\n| --- | --- | --- | --- | --- | --- |",
    )
    _source(root, "SRC-001", "user_statement", "fixture owner")
    _source(root, "SRC-002", "repository_file", "fixture.txt")


def _generate_invalid_fixtures(root: Path) -> None:
    if root.exists():
        raise FileExistsError(root)
    cases = {
        "stale-proposal": "KB_PROPOSAL_STALE",
        "missing-approval": "KB_APPROVAL_REQUIRED",
        "unresolved-conflict": "KB_CONFLICT_RESOLVER",
        "broken-traceability": "KB_TRACE_REFERENCE",
        "sensitive-material": "KB_SENSITIVE_VALUE",
        "archived-reference": "KB_TRACE_REFERENCE",
    }
    for name, code in cases.items():
        case = root / name
        _minimal_fixture(case, code)
        metadata = {
            "id": "KNOWLEDGE-001",
            "type": "knowledge_item",
            "title": "Fixture item",
            "status": "proposed",
            "version": "1.0.0",
            "sources": ["SRC-001"],
            "last_updated": DATE,
        }
        body = "# Fixture item"
        relative = "02-架构与契约/item.md"
        if name == "stale-proposal":
            metadata.update(
                status="approved",
                approved_by="owner",
                approved_at=DATE,
                proposal_revision="2",
                confirmed_revision="1",
            )
        elif name == "missing-approval":
            metadata["status"] = "approved"
        elif name == "unresolved-conflict":
            metadata["status"] = "conflicted"
            metadata["sources"] = ["SRC-001", "SRC-002"]
        elif name == "broken-traceability":
            metadata["contracts"] = ["CONTRACT-MISSING"]
        elif name == "sensitive-material":
            body += "\n\nSERVICE_TOKEN=real-sensitive-value"
        elif name == "archived-reference":
            metadata["depends_on"] = ["F01"]
            _record(
                case / "90-历史归档/F01.md",
                {
                    "id": "F01",
                    "type": "knowledge_item",
                    "title": "Archived feature",
                    "status": "archived",
                    "version": "1.0.0",
                    "sources": ["SRC-001"],
                    "last_updated": DATE,
                },
                "# Archived only",
            )
        _record(case / relative, metadata, body)


def generate() -> None:
    examples = Path("examples")
    fixtures = Path("tests/fixtures/invalid")
    snapshot = Path("tests/snapshots/expected-structures.json")
    if examples.exists() or fixtures.exists() or snapshot.exists():
        raise FileExistsError("example, fixture, or snapshot output already exists")
    examples.mkdir()
    try:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            for name in EXAMPLE_NAMES:
                materialized = initialize_from_assets(
                    temporary,
                    name,
                    initialized_at=DATE,
                )
                _populate_example(materialized, name)
                shutil.copytree(materialized, examples / name)
        _generate_invalid_fixtures(fixtures)
        structures = {
            name: sorted(
                path.relative_to(examples / name).as_posix()
                for path in (examples / name).rglob("*")
                if path.is_file()
            )
            for name in EXAMPLE_NAMES
        }
        _write(snapshot, json.dumps(structures, ensure_ascii=False, indent=2))
    except Exception:
        if examples.exists():
            shutil.rmtree(examples)
        if fixtures.exists():
            shutil.rmtree(fixtures)
        if snapshot.exists():
            snapshot.unlink()
        raise


if __name__ == "__main__":
    generate()
