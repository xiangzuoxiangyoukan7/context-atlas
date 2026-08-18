"""把仓库权威源按清单同步到 Context Atlas Skill 资产。"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence


TEXT_SUFFIXES = frozenset({".json", ".md", ".py", ".yaml", ".yml"})


def _safe_child(root: Path, relative_text: str) -> Path:
    """解析并拒绝绝对路径、父级跳转和根目录逃逸。"""

    relative = Path(relative_text)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"unsafe manifest path: {relative_text}")
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root.resolve()):
        raise ValueError(f"manifest path escapes root: {relative_text}")
    return candidate


def _normalized(path: Path) -> bytes:
    """读取文件并统一文本换行以便跨平台比较。"""

    data = path.read_bytes()
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return data
    text = data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return text.encode("utf-8")


def _digest(data: bytes) -> str:
    """返回资产内容的 SHA-256 摘要。"""

    return hashlib.sha256(data).hexdigest()


def _manifest_files(skill_root: Path) -> list[str]:
    """读取并验证有序且唯一的 Skill 资产清单。"""

    path = skill_root / "assets" / "manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    files = payload.get("files") if isinstance(payload, dict) else None
    if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
        raise ValueError("manifest files must be a list of paths")
    if files != sorted(set(files)):
        raise ValueError("manifest files must be sorted and unique")
    return files


def sync_assets(source_root: Path, skill_root: Path, check: bool = False) -> list[str]:
    """同步清单文件并返回不一致的相对路径。"""

    source_root = source_root.resolve()
    skill_root = skill_root.resolve()
    assets_root = skill_root / "assets"
    mismatches: list[str] = []
    for relative_text in _manifest_files(skill_root):
        source = _safe_child(source_root, relative_text)
        target = _safe_child(assets_root, relative_text)
        if not source.is_file():
            mismatches.append(relative_text)
            continue
        expected = _normalized(source)
        if target.is_file():
            try:
                actual = _normalized(target)
            except UnicodeDecodeError:
                actual = target.read_bytes()
        else:
            actual = None
        if actual is not None and _digest(actual) == _digest(expected):
            continue
        mismatches.append(relative_text)
        if not check:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(expected)
    return mismatches


def _parser() -> argparse.ArgumentParser:
    """创建资产同步命令的参数解析器。"""

    parser = argparse.ArgumentParser(description="Synchronize canonical project knowledge assets")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--source-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--skill-root",
        type=Path,
        default=Path("."),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行同步或只读一致性检查并返回退出码。"""

    args = _parser().parse_args(list(argv) if argv is not None else None)
    mismatches = sync_assets(args.source_root, args.skill_root, check=args.check)
    if mismatches:
        action = "mismatched" if args.check else "synchronized"
        for path in mismatches:
            print(f"{action}: {path}")
        return 1 if args.check else 0
    print("Skill assets are synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
