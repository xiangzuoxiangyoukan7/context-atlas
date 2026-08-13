"""验证 Codex 与 Claude Code 插件清单的一致性。"""

from __future__ import annotations

import json
import re
from pathlib import Path


SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
CLAUDE_FIELDS = frozenset(
    {
        "name",
        "version",
        "description",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
        "skills",
    }
)
COMMON_FIELDS = ("name", "version", "description")


def _load_object(path: Path) -> dict[str, object]:
    """读取并确认插件清单根节点是 JSON 对象。"""

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"插件清单必须是 JSON 对象：{path}")
    return payload


def load_plugin_manifests(root: Path) -> tuple[dict[str, object], dict[str, object]]:
    """读取仓库中的 Claude 与 Codex 插件清单。"""

    root = root.resolve()
    claude = _load_object(root / ".claude-plugin" / "plugin.json")
    codex = _load_object(root / ".codex-plugin" / "plugin.json")
    return claude, codex


def _safe_skill_path(value: object) -> bool:
    """判断清单是否指向唯一共享 Skill 根目录。"""

    return value == "./skills/"


def _author_name(manifest: dict[str, object]) -> object:
    """安全提取清单中的作者名称。"""

    author = manifest.get("author")
    return author.get("name") if isinstance(author, dict) else None


def validate_plugin_contract(root: Path) -> list[str]:
    """返回双平台身份、字段和 Skill 唯一性错误。"""

    root = root.resolve()
    errors: list[str] = []
    try:
        claude, codex = load_plugin_manifests(root)
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
        return [str(error)]

    if claude.get("name") != "context-atlas":
        errors.append("Claude 插件名称必须是 context-atlas")
    for field in COMMON_FIELDS:
        if claude.get(field) != codex.get(field):
            errors.append(f"两个平台的 {field} 必须一致")
    if _author_name(claude) != _author_name(codex) or not _author_name(claude):
        errors.append("两个平台的 author.name 必须一致且非空")
    version = claude.get("version")
    if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
        errors.append("插件版本必须使用严格三段语义版本")
    if set(claude) - CLAUDE_FIELDS:
        errors.append(f"Claude 清单含不支持字段：{sorted(set(claude) - CLAUDE_FIELDS)}")
    for platform, manifest in (("Claude", claude), ("Codex", codex)):
        if not _safe_skill_path(manifest.get("skills")):
            errors.append(f"{platform} 的 skills 必须指向 ./skills/")
    if "hooks" in codex:
        errors.append("Codex 清单不得声明未提供的 hooks")
    interface = codex.get("interface")
    required_interface = {
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
        "capabilities",
        "defaultPrompt",
    }
    if not isinstance(interface, dict):
        errors.append("Codex 清单缺少 interface")
    else:
        missing = sorted(field for field in required_interface if not interface.get(field))
        if missing:
            errors.append(f"Codex interface 缺少字段：{missing}")

    canonical_skill = root / "skills" / "context-atlas" / "SKILL.md"
    named_skills: list[Path] = []
    for path in root.rglob("SKILL.md"):
        if ".worktrees" in path.relative_to(root).parts:
            continue
        try:
            if "name: context-atlas" in path.read_text(encoding="utf-8"):
                named_skills.append(path.resolve())
        except (OSError, UnicodeDecodeError):
            continue
    if named_skills != [canonical_skill.resolve()]:
        errors.append("仓库必须且只能存在一份 context-atlas Skill")
    for directory in (root / ".claude-plugin" / "skills", root / ".codex-plugin" / "skills"):
        if directory.exists():
            errors.append(f"平台目录不得复制 Skill：{directory.relative_to(root)}")
    return errors
