from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Iterable, Sequence
from urllib.parse import unquote


@dataclass(frozen=True)
class Issue:
    code: str
    path: Path
    message: str


class MetadataError(ValueError):
    pass


REQUIRED = {
    "feature": {"id", "type", "title", "status", "phase", "priority", "current_slice", "depends_on", "acceptance", "contracts", "adr", "last_updated"},
    "task": {"id", "type", "title", "feature", "status", "acceptance", "last_updated"},
    "governance_task": {"id", "type", "title", "plan", "status", "acceptance", "last_updated"},
}
STATUS = {
    "feature": {"candidate", "baselined", "scheduled", "in_progress", "acceptance", "completed", "deferred", "deprecated"},
    "task": {"draft", "ready", "in_progress", "blocked", "acceptance", "completed"},
    "governance_task": {"draft", "ready", "in_progress", "blocked", "acceptance", "completed"},
}
ACCEPTANCE_RESULTS = {"not_started", "partial", "passed", "not_applicable"}
EXCLUDED_DIRECTORIES = {".obsidian", "Excalidraw", "90-历史归档"}
LINK_PATTERN = re.compile(r"(?<!!)[^\]]*\]\(([^)]+)\)")
ACCEPTANCE_PATTERN = re.compile(r"(?:F\d{2}|KB)-AC-\d{2}\Z")


def parse_front_matter(path: Path) -> dict[str, str | list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return {}
    metadata: dict[str, str | list[str]] = {}
    active: str | None = None
    closed = False
    for number, line in enumerate(lines[1:], start=2):
        if line == "---":
            closed = True
            break
        if line.startswith("  - "):
            if active is None or not line[4:].strip():
                raise MetadataError(f"{path}:{number}: orphan or empty list item")
            value = metadata[active]
            assert isinstance(value, list)
            value.append(line[4:].strip())
            continue
        if line.startswith((" ", "\t", "- ")):
            raise MetadataError(f"{path}:{number}: nested metadata is unsupported")
        if ":" not in line:
            raise MetadataError(f"{path}:{number}: expected key: value")
        key, value = (part.strip() for part in line.split(":", maxsplit=1))
        if not key or key in metadata:
            raise MetadataError(f"{path}:{number}: invalid or duplicate metadata key")
        active = None
        if not value:
            metadata[key] = []
            active = key
        elif value.startswith("[") and value.endswith("]"):
            body = value[1:-1].strip()
            metadata[key] = [] if not body else [item.strip() for item in body.split(",")]
        else:
            metadata[key] = value
    if not closed:
        raise MetadataError(f"{path}: missing closing front matter delimiter")
    return metadata


def _excluded(path: Path, root: Path) -> bool:
    return any(part in EXCLUDED_DIRECTORIES for part in path.relative_to(root).parts)


def _as_list(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _issue(code: str, path: Path, message: str) -> Issue:
    return Issue(code, path, message)


def _records(root: Path, issues: list[Issue]) -> list[tuple[Path, dict[str, str | list[str]]]]:
    records: list[tuple[Path, dict[str, str | list[str]]]] = []
    for path in sorted(root.rglob("*.md")):
        if _excluded(path, root) or path.name.upper() == "TEMPLATE.MD":
            continue
        try:
            metadata = parse_front_matter(path)
        except MetadataError as error:
            issues.append(_issue("KB003", path, str(error)))
            continue
        if metadata:
            records.append((path, metadata))
    return records


def _validate_metadata(records: Iterable[tuple[Path, dict[str, str | list[str]]]], issues: list[Issue]) -> None:
    seen: dict[str, Path] = {}
    for path, metadata in records:
        identifier = metadata.get("id")
        if isinstance(identifier, str):
            if identifier in seen:
                issues.append(_issue("KB001", path, f"duplicate id {identifier}; first declared by {seen[identifier]}"))
            else:
                seen[identifier] = path
        kind = metadata.get("type")
        if kind not in REQUIRED:
            continue
        missing = REQUIRED[kind] - metadata.keys()
        if missing:
            issues.append(_issue("KB003", path, f"missing required metadata: {', '.join(sorted(missing))}"))
        status = metadata.get("status")
        if not isinstance(status, str) or status not in STATUS[kind]:
            issues.append(_issue("KB005", path, f"invalid {kind} status: {status!r}"))
        acceptance = _as_list(metadata.get("acceptance"))
        if not acceptance or len(acceptance) != len(set(acceptance)):
            issues.append(_issue("KB003", path, "acceptance declarations must be non-empty and unique"))
        if kind == "feature":
            if metadata.get("phase") not in {"mvp", "phase2", "phase3"} or metadata.get("priority") not in {"P0", "P1", "P2", "P3"}:
                issues.append(_issue("KB003", path, "invalid feature phase or priority"))
            if metadata.get("current_slice") not in {"included", "excluded"}:
                issues.append(_issue("KB003", path, "invalid feature current_slice"))


def _matrix_rows(path: Path, issues: list[Issue]) -> list[tuple[str, str, str, str]]:
    if not path.exists():
        return []
    rows: list[tuple[str, str, str, str]] = []
    header: list[str] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] == "验收编号":
            header = cells
            continue
        if not cells or not ACCEPTANCE_PATTERN.fullmatch(cells[0]) or header is None:
            continue
        required = {"结果", "证据位置", "对应版本"}
        if not required.issubset(header):
            issues.append(_issue("KB003", path, f"matrix header lacks {sorted(required - set(header))}"))
            continue
        indexes = {name: header.index(name) for name in required}
        if len(cells) <= max(indexes.values()):
            issues.append(_issue("KB003", path, f"matrix row is shorter than header: {cells[0]}"))
            continue
        rows.append((cells[0], cells[indexes["结果"]], cells[indexes["证据位置"]], cells[indexes["对应版本"]]))
    return rows


def _registered(value: str) -> bool:
    return bool(value.strip() and value.strip() not in {"—", "-"})


def _validate_matrix(root: Path, records: list[tuple[Path, dict[str, str | list[str]]]], issues: list[Issue]) -> None:
    declared: set[str] = set()
    completed: list[tuple[Path, list[str]]] = []
    for path, metadata in records:
        kind = metadata.get("type")
        if kind in {"feature", "task", "governance_task"}:
            acceptance = _as_list(metadata.get("acceptance"))
            declared.update(acceptance)
            if metadata.get("status") == "completed":
                completed.append((path, acceptance))
    matrix = root / "03-实施与验收" / "验收矩阵.md"
    if not matrix.exists():
        if declared:
            issues.append(_issue("KB004", matrix, "acceptance matrix is required when acceptance is declared"))
        return
    rows = _matrix_rows(matrix, issues)
    ids = [row[0] for row in rows]
    if set(ids) != declared:
        issues.append(_issue("KB004", matrix, f"matrix IDs do not exactly match declarations; missing={sorted(declared - set(ids))}, extra={sorted(set(ids) - declared)}"))
    for identifier in set(ids):
        if ids.count(identifier) != 1:
            issues.append(_issue("KB004", matrix, f"matrix acceptance must appear exactly once: {identifier}"))
    row_map = {row[0]: row for row in rows if ids.count(row[0]) == 1}
    for identifier, result, evidence, version in rows:
        if result not in ACCEPTANCE_RESULTS:
            issues.append(_issue("KB005", matrix, f"invalid acceptance result: {result!r}"))
        if result == "passed" and (not _registered(evidence) or not _registered(version)):
            issues.append(_issue("KB007", matrix, f"passed acceptance lacks evidence or version: {identifier}"))
    for path, acceptance in completed:
        for identifier in acceptance:
            row = row_map.get(identifier)
            if row is None or row[1] != "passed" or not _registered(row[2]) or not _registered(row[3]):
                issues.append(_issue("KB007", path, f"completed record lacks passed evidence: {identifier}"))


def _validate_current(root: Path, issues: list[Issue]) -> None:
    current = root / "03-实施与验收" / "CURRENT.md"
    if not current.exists():
        issues.append(_issue("KB006", current, "CURRENT.md is required"))
        return
    content = current.read_text(encoding="utf-8")
    no_task = re.findall(r"(?m)^-\s*当前任务：\s*无可执行开发任务\s*$", content)
    task_ids = re.findall(r"(?m)^-\s*任务编号：\s*(.*?)\s*$", content)
    package_links = re.findall(r"(?m)^-\s*任务包：\s*\[[^\]]+\]\(([^)]+)\)\s*$", content)
    if len(no_task) == 1 and not task_ids and not package_links:
        return
    if len(no_task) or len(task_ids) != 1 or len(package_links) != 1:
        issues.append(_issue("KB006", current, "CURRENT must declare one executable task with one package or one explicit no-task state"))


def _validate_links(root: Path, issues: list[Issue]) -> None:
    for path in root.rglob("*.md"):
        if _excluded(path, root):
            continue
        for target in LINK_PATTERN.findall(path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            candidate = (path.parent / unquote(target.split("#", 1)[0])).resolve()
            if not candidate.exists():
                issues.append(_issue("KB009", path, f"broken relative link: {target}"))


def _validate_profiles(root: Path, issues: list[Issue]) -> None:
    profiles = root.parent / "profiles"
    if not profiles.exists():
        return
    for path in profiles.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        if re.search(r"(允许|可以|must)\s*(修改|override)\s*(核心|core)", text, re.IGNORECASE):
            issues.append(_issue("KB008", path, "profile attempts to override core rules"))


def validate(root: Path) -> list[Issue]:
    root = root.resolve()
    issues: list[Issue] = []
    if not root.exists():
        return [_issue("KB010", root, "knowledge-base root does not exist")]
    records = _records(root, issues)
    _validate_metadata(records, issues)
    _validate_matrix(root, records, issues)
    _validate_current(root, issues)
    _validate_links(root, issues)
    _validate_profiles(root, issues)
    return issues


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if len(args) != 1:
        print("usage: python scripts/check_knowledge_base.py <knowledge-base>")
        return 2
    issues = validate(Path(args[0]))
    if issues:
        for issue in issues:
            print(f"{issue.code} {issue.path}: {issue.message}")
        return 1
    print("Knowledge base validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
