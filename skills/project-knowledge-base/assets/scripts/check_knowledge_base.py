from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.project_kb.frontmatter import FrontMatterError as MetadataError
from scripts.project_kb.frontmatter import parse_document
from scripts.project_kb.model import Issue
from scripts.project_kb.reporting import render_json, render_text
from scripts.project_kb.validator import ValidationConfig
from scripts.project_kb.validator import validate as validate_with_config


def parse_front_matter(path: Path) -> dict[str, object]:
    return parse_document(path).metadata


def default_schema_root() -> Path:
    return Path(__file__).resolve().parents[1] / "schemas"


def validate(root: Path) -> list[Issue]:
    return validate_with_config(root, ValidationConfig(schema_root=default_schema_root()))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a project knowledge base")
    parser.add_argument("root", type=Path)
    parser.add_argument("--schema-root", type=Path, default=default_schema_root())
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
        issues = validate_with_config(
            args.root,
            ValidationConfig(schema_root=args.schema_root),
        )
    except (OSError, ValueError) as error:
        parser.exit(2, f"configuration error: {error}\n")
    print(render_json(issues) if args.format == "json" else render_text(issues))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
