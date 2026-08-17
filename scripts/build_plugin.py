"""Build platform-specific Context Atlas plugin payloads from the repository root."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

from project_kb.plugin_contract import validate_plugin_contract


ROOT = Path(__file__).resolve().parents[1]
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def _copy_tree(source: Path, target: Path) -> None:
    """复制目录树，并拒绝发布源根目录使用符号链接。"""

    if source.is_symlink():
        raise ValueError(f"发布源不得包含符号链接：{source}")
    shutil.copytree(source, target, dirs_exist_ok=True, symlinks=False)


def _copy_common(target: Path, platform: str) -> None:
    """复制指定平台共享的最小运行时文件。"""

    manifest_dir = ".codex-plugin" if platform == "codex" else ".claude-plugin"
    (target / manifest_dir).mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / manifest_dir / "plugin.json", target / manifest_dir / "plugin.json")
    if platform == "claude":
        shutil.copy2(
            ROOT / manifest_dir / "marketplace.json",
            target / manifest_dir / "marketplace.json",
        )
    _copy_tree(ROOT / "skills", target / "skills")
    if platform == "claude":
        _copy_tree(ROOT / "commands", target / "commands")
    for name in ("README.md", "LICENSE"):
        source = ROOT / name
        if source.is_file():
            shutil.copy2(source, target / name)


def build(output: Path, platform: str, archive: bool = False) -> Path:
    """Create a clean release tree or zip archive for one platform."""

    if platform not in {"codex", "claude"}:
        raise ValueError("platform must be codex or claude")
    contract_errors = validate_plugin_contract(ROOT)
    if contract_errors:
        raise ValueError("插件契约检查失败：\n- " + "\n- ".join(contract_errors))
    output = output.resolve()
    if output.exists():
        shutil.rmtree(output) if output.is_dir() else output.unlink()
    stage = output if not archive else output.with_suffix("")
    if stage.exists():
        shutil.rmtree(stage) if stage.is_dir() else stage.unlink()
    stage.mkdir(parents=True, exist_ok=True)
    _copy_common(stage, platform)
    if not archive:
        return output
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(stage.rglob("*")):
            if path.is_file():
                info = zipfile.ZipInfo(path.relative_to(stage).as_posix(), ZIP_TIMESTAMP)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                bundle.writestr(info, path.read_bytes())
    shutil.rmtree(stage, ignore_errors=True)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_name(output.name + ".sha256").write_text(
        f"{digest}  {output.name}\n",
        encoding="ascii",
        newline="\n",
    )
    return output


def main() -> int:
    """解析构建参数、生成产物并输出机器可读结果。"""

    parser = argparse.ArgumentParser(description="Build Context Atlas plugin payload")
    parser.add_argument("platform", choices=("codex", "claude"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--archive", action="store_true")
    args = parser.parse_args()
    result = build(args.output, args.platform, args.archive)
    print(json.dumps({"ok": True, "platform": args.platform, "output": str(result)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
