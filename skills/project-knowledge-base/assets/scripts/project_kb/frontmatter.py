from __future__ import annotations

from pathlib import Path

from .model import DocumentRecord


class FrontMatterError(ValueError):
    pass


def _parse_scalar(value: str) -> str | list[str]:
    if value.startswith("[") and value.endswith("]"):
        body = value[1:-1].strip()
        return [] if not body else [item.strip() for item in body.split(",")]
    return value


def parse_document(path: Path) -> DocumentRecord:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return DocumentRecord(path=path, metadata={}, body="".join(lines))

    metadata: dict[str, object] = {}
    closing_index: int | None = None
    for index, raw_line in enumerate(lines[1:], start=1):
        line = raw_line.rstrip("\r\n")
        if line == "---":
            closing_index = index
            break
        if line.startswith((" ", "\t", "- ")):
            raise FrontMatterError(f"{path}:{index + 1}: nested metadata is unsupported")
        if ":" not in line:
            raise FrontMatterError(f"{path}:{index + 1}: expected key: value")
        key, value = (part.strip() for part in line.split(":", maxsplit=1))
        if not key:
            raise FrontMatterError(f"{path}:{index + 1}: empty metadata key")
        if key in metadata:
            raise FrontMatterError(f"{path}:{index + 1}: duplicate metadata key: {key}")
        if not value:
            raise FrontMatterError(f"{path}:{index + 1}: nested metadata is unsupported")
        metadata[key] = _parse_scalar(value)

    if closing_index is None:
        raise FrontMatterError(f"{path}: missing closing front matter delimiter")

    return DocumentRecord(
        path=path,
        metadata=metadata,
        body="".join(lines[closing_index + 1 :]),
    )
