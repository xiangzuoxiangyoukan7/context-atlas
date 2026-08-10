from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .discovery import discover_records
from .links import validate_links
from .model import Issue
from .profiles import validate_embedded_profiles
from .schema_catalog import SchemaCatalog
from .security import validate_security
from .traceability import validate_traceability


@dataclass(frozen=True)
class ValidationConfig:
    schema_root: Path
    excluded_directories: frozenset[str] = frozenset(
        {".obsidian", "Excalidraw", "90-历史归档"}
    )


def validate(root: Path, config: ValidationConfig) -> list[Issue]:
    resolved_root = root.resolve()
    if not resolved_root.exists():
        return [Issue("KB_ROOT_MISSING", resolved_root, "knowledge-base root does not exist")]

    records, issues = discover_records(resolved_root, config.excluded_directories)
    catalog = SchemaCatalog.load(config.schema_root)
    for record in records:
        kind = record.metadata.get("type")
        if isinstance(kind, str) and kind in catalog.schemas:
            issues.extend(catalog.validate(kind, record.metadata, record.path))
    issues.extend(validate_links(resolved_root, config.excluded_directories))
    issues.extend(validate_traceability(resolved_root, records))
    issues.extend(validate_embedded_profiles(resolved_root, config.schema_root))
    issues.extend(validate_security(records))
    return sorted(issues, key=lambda issue: (str(issue.path), issue.code, issue.message))
