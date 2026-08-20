"""生成并执行旧知识来源关系到当前格式的轻量等价转换。"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Iterable

from .compatibility import CompatibilityPolicy
from .model import DocumentRecord


@dataclass(frozen=True)
class MigrationChange:
    """描述一个文件需要内嵌的来源对象及原内容摘要。"""

    path: Path
    links: tuple[str, ...]
    original_digest: str


@dataclass(frozen=True)
class MigrationMove:
    """描述知识治理文件的安全路径迁移。"""

    source: Path
    target: Path
    original_digest: str


@dataclass(frozen=True)
class MigrationRemoval:
    """描述可证明为旧模板占位内容的删除项。"""

    path: Path
    original_digest: str


@dataclass(frozen=True)
class MigrationRewrite:
    """描述旧治理路径引用的可审计文本替换。"""

    path: Path
    original_digest: str


@dataclass(frozen=True)
class MigrationUnresolved:
    """描述无法唯一定位、必须由用户确认的旧来源编号。"""

    path: Path
    source_id: str
    reason: str


@dataclass(frozen=True)
class MigrationProposal:
    """保存只读分析产生的不可变转换范围和确认修订号。"""

    proposal_revision: str
    source_version: int
    target_version: int
    changes: tuple[MigrationChange, ...]
    moves: tuple[MigrationMove, ...]
    removals: tuple[MigrationRemoval, ...]
    rewrites: tuple[MigrationRewrite, ...]
    unresolved: tuple[MigrationUnresolved, ...]


@dataclass(frozen=True)
class MigrationReport:
    """保存已确认迁移实际修改的文件和最终格式版本。"""

    status: str
    changed_files: tuple[str, ...]
    format_version: int


def _digest(data: bytes) -> str:
    """返回文件内容摘要，用于拒绝提案生成后的并发变化。"""

    return hashlib.sha256(data).hexdigest()


def _source_paths(records: Iterable[DocumentRecord]) -> dict[str, list[Path]]:
    """按来源稳定编号建立可能包含重复项的文件索引。"""

    index: dict[str, list[Path]] = {}
    for record in records:
        if record.metadata.get("type") != "source":
            continue
        identifier = record.metadata.get("id")
        if isinstance(identifier, str):
            index.setdefault(identifier, []).append(record.path.resolve())
    return index


def _revision(
    source_version: int,
    target_version: int,
    changes: Iterable[MigrationChange],
    moves: Iterable[MigrationMove],
    removals: Iterable[MigrationRemoval],
    rewrites: Iterable[MigrationRewrite],
    unresolved: Iterable[MigrationUnresolved],
) -> str:
    """根据完整提案内容生成稳定且不可猜测的短修订号。"""

    parts = [f"{source_version}->{target_version}"]
    parts.extend(
        f"change:{change.path}:{change.original_digest}:{','.join(change.links)}"
        for change in changes
    )
    parts.extend(
        f"move:{move.source}:{move.target}:{move.original_digest}" for move in moves
    )
    parts.extend(
        f"remove:{removal.path}:{removal.original_digest}" for removal in removals
    )
    parts.extend(f"rewrite:{rewrite.path}:{rewrite.original_digest}" for rewrite in rewrites)
    parts.extend(
        f"unresolved:{item.path}:{item.source_id}:{item.reason}"
        for item in unresolved
    )
    return "migration-" + hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:12]


LEGACY_PLACEHOLDERS = {
    "本地开发.md": """# 本地开发

| 目的 | 前置条件 | 命令 | 预期结果 | 来源 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 安装依赖 | 待确认 | 待确认 | 依赖可复现 | SRC-001 | missing |
| 启动项目 | 待确认 | 待确认 | 服务健康 | SRC-001 | missing |
| 构建产物 | 待确认 | 待确认 | 构建成功 | SRC-001 | missing |

Agent 从构建文件、脚本和 CI 验证命令，不凭语言猜测。环境差异、必要服务和非敏感配置应逐项说明。""",
    "测试规则.md": """# 测试规则

| 层级 | 工具/位置 | 命名 | 运行命令 | 覆盖要求 | 来源 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| 单元测试 | 待确认 | 待确认 | 待确认 | 关键分支 | SRC-001 | missing |

记录项目实际使用的测试框架、夹具、覆盖门槛和失败排查入口。功能完成前必须运行任务包指定验证并保存证据；未运行测试不得声称通过。""",
}


def _governance_layout(root: Path) -> tuple[tuple[MigrationMove, ...], tuple[MigrationRemoval, ...], tuple[MigrationRewrite, ...], tuple[MigrationUnresolved, ...]]:
    """计算格式 3 的目录迁移，不删除有实质内容的旧文件。"""

    legacy = root / "05-开发指南"
    target = root / "05-知识治理"
    moves: list[MigrationMove] = []
    removals: list[MigrationRemoval] = []
    rewrites: list[MigrationRewrite] = []
    unresolved: list[MigrationUnresolved] = []
    for name in ("README.md", "AI知识采集协议.md"):
        source = legacy / name
        destination = target / name
        if source.is_file():
            if destination.exists():
                unresolved.append(MigrationUnresolved(source, name, "新旧治理路径同时存在"))
            else:
                moves.append(MigrationMove(source, destination, _digest(source.read_bytes())))
    for name, placeholder in LEGACY_PLACEHOLDERS.items():
        path = legacy / name
        if not path.is_file():
            continue
        normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n").strip()
        if normalized == placeholder.strip():
            removals.append(MigrationRemoval(path, _digest(path.read_bytes())))
        else:
            unresolved.append(
                MigrationUnresolved(path, name, "包含项目内容，需确认迁入技术栈或技术契约")
            )
    readme = root / "README.md"
    if readme.is_file() and "05-开发指南" in readme.read_text(encoding="utf-8"):
        rewrites.append(MigrationRewrite(readme, _digest(readme.read_bytes())))
    return tuple(moves), tuple(removals), tuple(rewrites), tuple(unresolved)


def _rewrite_governance_paths(content: str, governance_readme: bool = False) -> str:
    """将旧开发指南语义收敛为知识治理，保留其他项目内容。"""

    result = (
        content.replace("05-开发指南", "05-知识治理")
        .replace("开发指南", "知识治理")
        .replace("00-项目总览/SRC-", "05-知识治理/公共来源/SRC-")
        .replace("rel_implements:", "rel_satisfies:")
    )
    if governance_readme:
        lines = [
            line for line in result.splitlines()
            if "./本地开发.md" not in line and "./测试规则.md" not in line
        ]
        result = "\n".join(lines).rstrip() + "\n"
    return result


def build_migration_proposal(
    root: Path,
    records: Iterable[DocumentRecord],
    policy: CompatibilityPolicy,
) -> MigrationProposal:
    """只读分析旧裸来源编号并生成可确认的一对一转换提案。

    先诊断格式兼容性并建立来源编号索引，再逐份扫描旧记录，把可唯一解析的来源构造成
    正式关系；歧义项保留为 unresolved，最后根据文件摘要构造稳定提案修订号。
    """

    resolved_root = root.resolve()
    result = policy.diagnose(resolved_root)
    if not result.conversion_available:
        raise ValueError("current format has no applicable conversion")
    record_list = list(records)
    sources = _source_paths(record_list)
    source_records = {
        str(record.metadata.get("id")): record
        for record in record_list
        if record.metadata.get("type") == "source" and isinstance(record.metadata.get("id"), str)
    }
    changes: list[MigrationChange] = []
    unresolved: list[MigrationUnresolved] = []
    referenced_source_ids: set[str] = set()
    for record in record_list if result.format_version <= 3 else ():
        if record.metadata.get("type") == "source":
            continue
        raw_sources = record.metadata.get("sources")
        if not isinstance(raw_sources, list) or not raw_sources or all(isinstance(item, dict) for item in raw_sources):
            continue
        links: list[str] = []
        record_unresolved: list[MigrationUnresolved] = []
        for raw_source in raw_sources:
            source_id = str(raw_source)
            referenced_source_ids.add(source_id)
            candidates = sources.get(source_id, [])
            if len(candidates) != 1:
                reason = "来源不存在" if not candidates else "来源编号不唯一"
                record_unresolved.append(
                    MigrationUnresolved(record.path.resolve(), source_id, reason)
                )
                continue
            source_record = source_records[source_id]
            confirmation_status = "confirmed" if record.metadata.get("status") == "approved" else "observed"
            embedded = {
                "type": source_record.metadata.get("source_type"),
                "reference": source_record.metadata.get("reference"),
                "observed_at": f"{source_record.metadata.get('last_updated')}T00:00:00Z",
                "confirmation_status": confirmation_status,
            }
            if confirmation_status == "confirmed":
                approved_at = record.metadata.get("approved_at")
                embedded["confirmed_at"] = f"{approved_at}T00:00:00Z" if approved_at else embedded["observed_at"]
            links.append(json.dumps(embedded, ensure_ascii=False, sort_keys=True))
        if record_unresolved:
            unresolved.extend(record_unresolved)
            continue
        if links:
            data = record.path.read_bytes()
            changes.append(
                MigrationChange(
                    record.path.resolve(), tuple(sorted(set(links))), _digest(data)
                )
            )
    ordered_changes = tuple(sorted(changes, key=lambda item: str(item.path)))
    moves, removals, rewrites, layout_unresolved = _governance_layout(resolved_root)
    rewrite_paths = {item.path.resolve() for item in rewrites}
    for path in resolved_root.rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        if ("00-项目总览/SRC-" in content or "rel_implements:" in content) and path.resolve() not in rewrite_paths:
            rewrites += (MigrationRewrite(path.resolve(), _digest(path.read_bytes())),)
            rewrite_paths.add(path.resolve())
    for source_id, record in source_records.items():
        if source_id not in referenced_source_ids:
            unresolved.append(MigrationUnresolved(record.path.resolve(), source_id, "来源未被任何知识项引用，不能安全删除"))
        try:
            relative = record.path.resolve().relative_to(resolved_root)
        except ValueError:
            unresolved.append(MigrationUnresolved(record.path.resolve(), source_id, "公共来源路径逃逸知识库"))
            continue
        if relative.parts and relative.parts[0] == "00-项目总览":
            destination = resolved_root / "05-知识治理" / "公共来源" / record.path.name
            if destination.exists():
                unresolved.append(MigrationUnresolved(record.path.resolve(), source_id, "公共来源新旧位置同时存在"))
            else:
                moves += (MigrationMove(record.path.resolve(), destination, _digest(record.path.read_bytes())),)
    unresolved.extend(layout_unresolved)
    ordered_unresolved = tuple(
        sorted(unresolved, key=lambda item: (str(item.path), item.source_id))
    )
    return MigrationProposal(
        proposal_revision=_revision(
            result.format_version,
            result.creates_format_version,
            ordered_changes,
            moves,
            removals,
            rewrites,
            ordered_unresolved,
        ),
        source_version=result.format_version,
        target_version=result.creates_format_version,
        changes=ordered_changes,
        moves=moves,
        removals=removals,
        rewrites=rewrites,
        unresolved=ordered_unresolved,
    )


def _add_supported_by(content: str, links: tuple[str, ...]) -> str:
    """把旧来源编号替换为 Front Matter 内嵌来源对象。"""

    lines = content.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        raise ValueError("migration target lacks front matter")
    closing: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.rstrip("\r\n") == "---":
            closing = index
            break
    if closing is None:
        raise ValueError("migration target has incomplete front matter")
    retained: list[str] = []
    skipping = False
    for line in lines[1:closing]:
        if line.startswith(("sources:", "rel_supported_by:")):
            skipping = True
            continue
        if skipping and line.startswith(("  ", "\t")):
            continue
        skipping = False
        retained.append(line)
    addition = ["sources:\n"]
    for encoded in links:
        source = json.loads(encoded)
        first = True
        for key in ("type", "reference", "observed_at", "confirmation_status", "confirmed_at"):
            if key not in source:
                continue
            prefix = "  - " if first else "    "
            addition.append(f'{prefix}{key}: {json.dumps(source[key], ensure_ascii=False)}\n')
            first = False
    return "".join([lines[0], *retained, *addition, lines[closing]]) + "".join(lines[closing + 1:])


def _set_format_version(content: str, target_version: int) -> str:
    """更新或补充内部格式版本，同时保持项目业务版本原值。"""

    lines = content.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if line.startswith("format_version:"):
            lines[index] = f"format_version: {target_version}\n"
            return "".join(lines)
    insertion = next(
        (index + 1 for index, line in enumerate(lines) if line.startswith("project_version:")),
        len(lines),
    )
    lines.insert(insertion, f"format_version: {target_version}\n")
    return "".join(lines)


def _atomic_write(path: Path, content: str) -> None:
    """在目标目录写入临时文件并原子替换单个知识文件。"""

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".migrating",
        delete=False,
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    temporary.replace(path)


def apply_migration(
    root: Path,
    proposal: MigrationProposal,
    confirmed_revision: str,
) -> MigrationReport:
    """在修订一致且无歧义时执行转换，并拒绝提案后的文件变化。

    先校验确认修订、未决项、目标边界和原文件摘要，再准备全部新内容；所有目标均未漂移后
    才逐项原子替换，并返回实际迁移文件及原格式版本。
    """

    if not confirmed_revision or confirmed_revision != proposal.proposal_revision:
        raise PermissionError("confirmed revision does not match migration proposal")
    if proposal.unresolved:
        raise ValueError("migration proposal contains unresolved source references")
    resolved_root = root.resolve()
    prepared: list[tuple[Path, str]] = []
    for change in proposal.changes:
        try:
            change.path.relative_to(resolved_root)
        except ValueError as error:
            raise ValueError("migration target escapes knowledge-base root") from error
        data = change.path.read_bytes()
        if _digest(data) != change.original_digest:
            raise ValueError(f"migration target changed after proposal: {change.path.name}")
        prepared.append(
            (change.path, _add_supported_by(data.decode("utf-8"), change.links))
        )
    for move in proposal.moves:
        if _digest(move.source.read_bytes()) != move.original_digest:
            raise ValueError(f"migration target changed after proposal: {move.source.name}")
        if move.target.exists():
            raise ValueError(f"migration target already exists: {move.target}")
    for removal in proposal.removals:
        if _digest(removal.path.read_bytes()) != removal.original_digest:
            raise ValueError(f"migration target changed after proposal: {removal.path.name}")
    for rewrite in proposal.rewrites:
        if _digest(rewrite.path.read_bytes()) != rewrite.original_digest:
            raise ValueError(f"migration target changed after proposal: {rewrite.path.name}")
    manifest = resolved_root / "knowledge-base.yaml"
    manifest_content = _set_format_version(
        manifest.read_text(encoding="utf-8"), proposal.target_version
    )
    manifest_content = _rewrite_governance_paths(manifest_content)
    affected = {path for path, _ in prepared} | {item.source for item in proposal.moves} | {item.target for item in proposal.moves} | {item.path for item in proposal.removals} | {item.path for item in proposal.rewrites} | {manifest}
    backups = {path: path.read_bytes() if path.is_file() else None for path in affected}
    try:
        for path, content in prepared:
            _atomic_write(path, content)
        for move in proposal.moves:
            move.target.parent.mkdir(parents=True, exist_ok=True)
            move.source.replace(move.target)
            if move.target.name == "README.md":
                _atomic_write(
                    move.target,
                    _rewrite_governance_paths(move.target.read_text(encoding="utf-8"), governance_readme=True),
                )
        for removal in proposal.removals:
            removal.path.unlink()
        for rewrite in proposal.rewrites:
            _atomic_write(
                rewrite.path,
                _rewrite_governance_paths(rewrite.path.read_text(encoding="utf-8")),
            )
        _atomic_write(manifest, manifest_content)
    except Exception:
        for path, content in backups.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
        raise
    changed = tuple(
        [path.relative_to(resolved_root).as_posix() for path, _ in prepared]
        + [move.target.relative_to(resolved_root).as_posix() for move in proposal.moves]
        + [removal.path.relative_to(resolved_root).as_posix() for removal in proposal.removals]
        + [rewrite.path.relative_to(resolved_root).as_posix() for rewrite in proposal.rewrites]
        + ["knowledge-base.yaml"]
    )
    return MigrationReport("migrated", changed, proposal.target_version)
