from __future__ import annotations

import json
from pathlib import Path
import shutil
from typing import Iterable

from .model import Issue
from .schema_catalog import SchemaCatalog


OVERRIDE_KEYS = frozenset(
    {"core_statuses", "authority_paths", "approval_rules", "acceptance_results"}
)


def _load_json(path: Path) -> tuple[dict[str, object] | None, list[Issue]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return None, [Issue("KB_PROFILE_DESCRIPTOR", path, f"invalid profile JSON: {error}")]
    if not isinstance(payload, dict):
        return None, [Issue("KB_PROFILE_DESCRIPTOR", path, "profile JSON must be an object")]
    return payload, []


def _as_strings(value: object) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _core_fields(catalog: SchemaCatalog) -> set[str]:
    fields: set[str] = set()
    for kind, schema in catalog.schemas.items():
        if kind == "profile":
            continue
        fields.update(str(field) for field in schema.get("required", []))
        for group in ("enums", "patterns"):
            values = schema.get(group, {})
            if isinstance(values, dict):
                fields.update(str(field) for field in values)
        for group in ("non_empty_lists", "unique_lists"):
            fields.update(str(field) for field in schema.get(group, []))
    return fields


def validate_profile_descriptor(
    path: Path,
    schema_root: Path,
    knowledge_base: Path | None = None,
) -> list[Issue]:
    descriptor, issues = _load_json(path)
    if descriptor is None:
        return issues
    catalog = SchemaCatalog.load(schema_root)
    issues.extend(catalog.validate("profile", descriptor, path))
    for key in sorted(OVERRIDE_KEYS):
        if descriptor.get(key):
            issues.append(
                Issue("KB_PROFILE_OVERRIDE", path, f"profile declares forbidden override: {key}")
            )
    collisions = sorted(set(_as_strings(descriptor.get("added_fields"))) & _core_fields(catalog))
    if collisions:
        issues.append(
            Issue(
                "KB_PROFILE_OVERRIDE",
                path,
                f"added_fields collide with core fields: {', '.join(collisions)}",
            )
        )
    for target in _as_strings(descriptor.get("added_templates")):
        relative = Path(target)
        source = (
            knowledge_base / relative
            if knowledge_base is not None
            else path.parent / "templates" / relative.name
        )
        if relative.is_absolute() or ".." in relative.parts:
            issues.append(Issue("KB_PROFILE_PATH", path, f"unsafe template path: {target}"))
        elif not source.is_file():
            issues.append(Issue("KB_PROFILE_TEMPLATE", path, f"missing additive template: {target}"))
    return sorted(issues, key=lambda issue: (str(issue.path), issue.code, issue.message))


def find_profile(profile_id: str, profile_root: Path = Path("profiles")) -> Path:
    for path in sorted(profile_root.glob("*/profile.json")):
        descriptor, _ = _load_json(path)
        if descriptor and descriptor.get("profile_id") == profile_id:
            return path
    raise ValueError(f"unknown profile: {profile_id}")


def apply_profiles(
    knowledge_base: Path,
    profile_ids: Iterable[str],
    schema_root: Path = Path("schemas"),
    profile_root: Path = Path("profiles"),
) -> None:
    selected = list(profile_ids)
    if len(selected) != len(set(selected)):
        raise ValueError("profile IDs must be unique")
    embedded = knowledge_base / ".project-kb" / "profiles"
    for profile_id in selected:
        descriptor_path = find_profile(profile_id, profile_root)
        issues = validate_profile_descriptor(descriptor_path, schema_root)
        if issues:
            raise ValueError(", ".join(issue.code for issue in issues))
        descriptor, _ = _load_json(descriptor_path)
        assert descriptor is not None
        embedded.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(descriptor_path, embedded / f"{profile_id}.json")
        for target_text in _as_strings(descriptor.get("added_templates")):
            target = knowledge_base / target_text
            if target.exists():
                raise ValueError(f"profile template would overwrite: {target_text}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(descriptor_path.parent / "templates" / target.name, target)


def validate_embedded_profiles(root: Path, schema_root: Path) -> list[Issue]:
    directory = root / ".project-kb" / "profiles"
    if not directory.exists():
        return []
    issues: list[Issue] = []
    for path in sorted(directory.glob("*.json")):
        issues.extend(validate_profile_descriptor(path, schema_root, knowledge_base=root))
    return issues
