from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Issue:
    code: str
    path: Path
    message: str
    location: str | None = None


@dataclass(frozen=True)
class DocumentRecord:
    path: Path
    metadata: dict[str, object]
    body: str
