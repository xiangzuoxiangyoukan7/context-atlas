"""以暂存目录和原子替换方式安全初始化知识库。"""

from __future__ import annotations

from datetime import date
from pathlib import Path
import re
import shutil
import uuid
from .validator import ValidationConfig, validate


MARKER_PATTERN = re.compile(r"{{[A-Z][A-Z0-9_]*}}")


def _cell(value: object) -> str:
    """将已校验文本安全放入 Markdown 表格单元格。"""

    return str(value).replace("\r", " ").replace("\n", " ").replace("|", "\\|")


def _source(fact: dict[str, object]) -> str:
    """把事实来源格式化为可回查的表格文本。"""

    source = fact["source"]
    assert isinstance(source, dict)
    return f"{_cell(source['type'])}: {_cell(source['reference'])}"


def _render_confirmed_content(root: Path, proposal: dict[str, object]) -> None:
    """把 Proposal 的受控字段渲染到预定义文档，禁止任意目标路径。"""

    facts = proposal["facts"]
    assert isinstance(facts, dict)

    overview = [f"# {_cell(proposal['project']['name'])} 项目概述", "", "## 项目定位", ""]
    goal_items = facts["goals"]
    assert isinstance(goal_items, list)
    if goal_items:
        overview.extend(f"- **{_cell(item['id'])}** {_cell(item['value'])}（{_cell(item['status'])}）" for item in goal_items)
    else:
        overview.append("待确认。")

    overview.extend(["", "## 长期职责", ""])
    inside = facts["boundaries_in"]
    outside = facts["boundaries_out"]
    assert isinstance(inside, list) and isinstance(outside, list)
    overview.extend(f"- **{_cell(item['id'])}** {_cell(item['value'])}（{_cell(item['status'])}）" for item in inside)
    if not inside:
        overview.append("待确认。")
    overview.extend(["", "## 明确不负责", ""])
    overview.extend(f"- **{_cell(item['id'])}** {_cell(item['value'])}（{_cell(item['status'])}）" for item in outside)
    if not outside:
        overview.append("待确认。")
    overview.extend(["", "## 来源", ""])
    source_items = [*goal_items, *inside, *outside]
    overview.extend(f"- **{_cell(item['id'])}** {_source(item)}" for item in source_items)
    if not source_items:
        overview.append("待确认。")
    overview.append("")
    (root / "00-项目总览" / "项目概述.md").write_text("\n".join(overview), encoding="utf-8", newline="\n")

    technologies = ["# 技术基线", "", "| 技术 | 版本 | 使用目录或模块 | 项目用途 | 构建、测试与运行命令 | 配置位置 | 来源 | 状态 |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    stacks = facts["technology_stacks"]
    assert isinstance(stacks, list)
    technologies.extend(
        f"| {_cell(item['name'])} | {_cell(item['version'])} | {_cell(item['location'])} | {_cell(item['purpose'])} | {_cell('; '.join(item['commands']))} | {_cell(item['configuration'])} | {_source(item)} | {_cell(item['status'])} |"
        for item in stacks
    )
    technologies.append("")
    (root / "02-架构与契约" / "技术基线.md").write_text("\n".join(technologies), encoding="utf-8", newline="\n")


def _safe_project_name(name: str) -> str:
    """验证项目名只能形成一个安全目录段。"""

    normalized = name.strip()
    if not normalized or normalized in {".", ".."} or "/" in normalized or "\\" in normalized:
        raise ValueError("project name must be one safe directory segment")
    return normalized


def _replace_markers(root: Path, values: dict[str, str]) -> None:
    """替换模板变量并拒绝任何未解析标记。"""

    unresolved: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for marker, value in values.items():
            content = content.replace(marker, value)
        unresolved.extend(f"{path}: {marker}" for marker in MARKER_PATTERN.findall(content))
        path.write_text(content, encoding="utf-8", newline="\n")
    if unresolved:
        raise ValueError("unresolved template markers: " + ", ".join(unresolved))


def initialize_from_assets(
    project_root: Path,
    project_name: str | None = None,
    assets_root: Path = Path("assets"),
    initialized_at: str | None = None,
    proposal: dict[str, object] | None = None,
    project_display_name: str | None = None,
) -> Path:
    """从 Skill 资产创建自包含且已验证的新知识库。"""

    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise ValueError("project root must be an existing directory")
    name = _safe_project_name(project_name or project_root.name)
    target = project_root / f"doc-{name}"
    if target.exists():
        raise FileExistsError(f"knowledge-base target already exists: {target}")

    assets_root = assets_root.resolve()
    template = assets_root / "templates" / "core" / "doc-project"
    schema_root = assets_root / "schemas"
    if not template.is_dir() or not schema_root.is_dir():
        raise ValueError("Skill assets are incomplete")

    # 先在同一文件系统完成复制和验证，最后原子改名，避免暴露半成品目标。
    staging = project_root / f".{target.name}.initializing-{uuid.uuid4().hex[:8]}"
    staging.mkdir()
    try:
        shutil.copytree(template, staging, dirs_exist_ok=True)
        _replace_markers(
            staging,
            {
                "{{PROJECT_ID}}": name,
                "{{PROJECT_NAME}}": project_display_name or name,
                "{{KNOWLEDGE_BASE_NAME}}": target.name,
                "{{INITIALIZED_AT}}": initialized_at or date.today().isoformat(),
            },
        )
        if proposal is not None:
            _render_confirmed_content(staging, proposal)
        shutil.copytree(assets_root / "scripts", staging / ".project-kb" / "scripts")
        shutil.copytree(schema_root, staging / ".project-kb" / "schemas")
        shutil.copy2(
            assets_root / "compatibility.json",
            staging / ".project-kb" / "compatibility.json",
        )
        issues = validate(staging, ValidationConfig(schema_root=staging / ".project-kb" / "schemas"))
        if issues:
            codes = ", ".join(issue.code for issue in issues)
            raise ValueError(f"materialized knowledge base is invalid: {codes}")
        if target.exists():
            raise FileExistsError(f"knowledge-base target appeared during initialization: {target}")
        staging.replace(target)
        return target
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise
