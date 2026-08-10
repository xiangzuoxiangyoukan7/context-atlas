# Agent-Native Project Knowledge Base MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver an installable Agent Skill that initializes and maintains a complete `doc-<project-name>/` knowledge base, with optional Java/Python profiles and deterministic schema-driven validation.

**Architecture:** Canonical schemas, templates, profiles, and validator sources live at repository root. A packaging step synchronizes those assets into the installable Skill so the installed Skill is self-contained. Users interact only with an AI Agent; the Agent follows the Skill, presents proposals for confirmation, writes Markdown/YAML, and invokes the bundled Python validator.

**Tech Stack:** Markdown, controlled YAML front matter, JSON schema descriptors, Python 3.11+ standard library, `unittest`, Git.

## Global Constraints

- The user interacts through an AI Agent; do not add an independent user-facing knowledge-base CLI.
- Do not generate or maintain target-project `AGENTS.md`, `CLAUDE.md`, or other Agent-specific adapters.
- Initialize in the current project root as `doc-<current-directory-name>/`; an explicit user-approved name may override the default.
- Never overwrite an existing `doc-<project-name>/`; switch to the update workflow instead.
- The core knowledge base is language-independent and works with zero profiles.
- Profiles are optional and composable; MVP officially supports `java.v1` and `python.v1` only.
- Profiles may only add fields, templates, requests, and checks; they may not override core authority, states, approval, or evidence rules.
- AI inference remains a proposal until the project owner explicitly confirms it.
- Conflicting sources are preserved and surfaced; the Agent may not resolve them by preference.
- Initialized knowledge bases must be self-contained for reading, maintenance, and validation.
- The validator checks structure and traceability only; it never claims business content is correct.
- Runtime code uses Python 3.11+ standard library only; the Skill documents `py` on Windows and `python3` elsewhere.

---

### Task 1: Define the Canonical Schema Catalog and Front-Matter Parser

**Files:**
- Create: `schemas/catalog.json`
- Create: `schemas/project-manifest.schema.json`
- Create: `schemas/knowledge-item.schema.json`
- Replace: `schemas/feature.schema.yaml` with `schemas/feature.schema.json`
- Replace: `schemas/task.schema.yaml` with `schemas/task.schema.json`
- Replace: `schemas/acceptance.schema.yaml` with `schemas/acceptance.schema.json`
- Replace: `schemas/profile.schema.yaml` with `schemas/profile.schema.json`
- Create: `scripts/project_kb/__init__.py`
- Create: `scripts/project_kb/model.py`
- Create: `scripts/project_kb/frontmatter.py`
- Create: `scripts/project_kb/schema_catalog.py`
- Create: `tests/helpers.py`
- Create: `tests/unit/test_frontmatter.py`
- Create: `tests/unit/test_schema_catalog.py`
- Modify: `schemas/README.md`

**Interfaces:**
- Produces: `Issue(code: str, path: Path, message: str, location: str | None = None)`.
- Produces: `DocumentRecord(path: Path, metadata: dict[str, object], body: str)`.
- Produces: `parse_document(path: Path) -> DocumentRecord`.
- Produces: `SchemaCatalog.load(root: Path) -> SchemaCatalog`.
- Produces: `SchemaCatalog.validate(kind: str, metadata: Mapping[str, object], path: Path) -> list[Issue]`.
- Consumes: Flat controlled YAML front matter; scalar strings and one-dimensional scalar lists only.

- [ ] **Step 1: Write failing parser tests**

```python
from pathlib import Path
from tests.helpers import TempDirectoryTestCase
from scripts.project_kb.frontmatter import FrontMatterError, parse_document


class FrontMatterTests(TempDirectoryTestCase):
    def test_parse_document_returns_metadata_and_body(self) -> None:
        path = self.root / "F01.md"
        path.write_text("---\nid: F01\nsources: [SRC-001, SRC-002]\n---\n# Feature\n", encoding="utf-8")

        record = parse_document(path)

        self.assertEqual(record.metadata, {"id": "F01", "sources": ["SRC-001", "SRC-002"]})
        self.assertEqual(record.body, "# Feature\n")

    def test_parse_document_rejects_nested_yaml(self) -> None:
        path = self.root / "bad.md"
        path.write_text("---\nsource:\n  type: user\n---\n", encoding="utf-8")

        with self.assertRaisesRegex(FrontMatterError, "nested metadata is unsupported"):
            parse_document(path)
```

- [ ] **Step 2: Write failing schema-catalog tests**

```python
import json
from pathlib import Path
from tests.helpers import TempDirectoryTestCase
from scripts.project_kb.schema_catalog import SchemaCatalog


class SchemaCatalogTests(TempDirectoryTestCase):
    def test_catalog_reports_invalid_enum(self) -> None:
        (self.root / "catalog.json").write_text(json.dumps({"feature": "feature.schema.json"}), encoding="utf-8")
        (self.root / "feature.schema.json").write_text(json.dumps({
            "required": ["id", "status"],
            "enums": {"status": ["proposed", "approved"]}
        }), encoding="utf-8")

        issues = SchemaCatalog.load(self.root).validate(
            "feature", {"id": "F01", "status": "wrong"}, self.root / "F01.md"
        )

        self.assertEqual([issue.code for issue in issues], ["KB_SCHEMA_ENUM"])
```

- [ ] **Step 3: Run the new tests and verify they fail because the modules do not exist**

Run: `py -m unittest tests.unit.test_frontmatter tests.unit.test_schema_catalog -v`

Expected: import errors for `scripts.project_kb.frontmatter` and `scripts.project_kb.schema_catalog`.

- [ ] **Step 4: Implement the shared data types and controlled parser**

```python
# scripts/project_kb/model.py
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
```

```python
# tests/helpers.py
from pathlib import Path
import tempfile
import unittest


class TempDirectoryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()
```

Move the existing flat front-matter logic into `frontmatter.py`, preserve UTF-8, reject duplicate keys, orphan list items, nested mappings, and missing closing delimiters, and return `DocumentRecord`.

- [ ] **Step 5: Implement JSON schema-catalog loading and validation**

```python
# scripts/project_kb/schema_catalog.py
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Mapping

from .model import Issue


@dataclass(frozen=True)
class SchemaCatalog:
    root: Path
    schemas: dict[str, dict[str, object]]

    @classmethod
    def load(cls, root: Path) -> "SchemaCatalog":
        resolved_root = root.resolve()
        catalog = json.loads((resolved_root / "catalog.json").read_text(encoding="utf-8"))
        schemas: dict[str, dict[str, object]] = {}
        for kind, relative in catalog.items():
            candidate = (resolved_root / str(relative)).resolve()
            if candidate.parent != resolved_root:
                raise ValueError(f"schema escapes root: {relative}")
            schemas[str(kind)] = json.loads(candidate.read_text(encoding="utf-8"))
        return cls(root=resolved_root, schemas=schemas)

    def validate(self, kind: str, metadata: Mapping[str, object], path: Path) -> list[Issue]:
        schema = self.schemas[kind]
        issues: list[Issue] = []
        for field in schema.get("required", []):
            if field not in metadata:
                issues.append(Issue("KB_SCHEMA_REQUIRED", path, f"missing required field: {field}"))
        for field, allowed in schema.get("enums", {}).items():
            if field in metadata and metadata[field] not in allowed:
                issues.append(Issue("KB_SCHEMA_ENUM", path, f"invalid {field}: {metadata[field]!r}"))
        for field, pattern in schema.get("patterns", {}).items():
            value = metadata.get(field)
            if isinstance(value, str) and re.fullmatch(pattern, value) is None:
                issues.append(Issue("KB_SCHEMA_PATTERN", path, f"invalid {field}: {value!r}"))
        for field in schema.get("non_empty_lists", []):
            value = metadata.get(field)
            if not isinstance(value, list) or not value:
                issues.append(Issue("KB_SCHEMA_LIST", path, f"{field} must be a non-empty list"))
        for field in schema.get("unique_lists", []):
            value = metadata.get(field)
            if isinstance(value, list) and len(value) != len(set(value)):
                issues.append(Issue("KB_SCHEMA_LIST", path, f"{field} must contain unique values"))
        return issues
```

Support `required`, `enums`, `patterns`, `non_empty_lists`, and `unique_lists`. Reject catalog entries that point outside `schemas/`.

- [ ] **Step 6: Write the canonical JSON schemas and document the controlled subset**

`knowledge-item.schema.json` must require `id`, `type`, `title`, `status`, `version`, `sources`, and `last_updated`. Approval-specific requirements remain conditional validator rules in Task 2. Preserve the existing feature/task/acceptance controlled values unless the approved knowledge baseline explicitly supersedes them.

- [ ] **Step 7: Run focused and existing parser tests**

Run: `py -m unittest tests.unit.test_frontmatter tests.unit.test_schema_catalog tests.test_check_knowledge_base -v`

Expected: all tests pass; any existing tests importing `Issue` or `parse_front_matter` are updated to import the new canonical interfaces.

- [ ] **Step 8: Commit the schema foundation**

```powershell
git add -- schemas scripts/project_kb tests/unit tests/test_check_knowledge_base.py
git commit -m "feat: define schema-driven knowledge model"
```

---

### Task 2: Build the Schema-Driven Validator and Stable Reports

**Files:**
- Create: `scripts/project_kb/discovery.py`
- Create: `scripts/project_kb/links.py`
- Create: `scripts/project_kb/traceability.py`
- Create: `scripts/project_kb/security.py`
- Create: `scripts/project_kb/validator.py`
- Create: `scripts/project_kb/reporting.py`
- Modify: `scripts/check_knowledge_base.py`
- Split/Modify: `tests/test_check_knowledge_base.py`
- Create: `tests/unit/test_traceability.py`
- Create: `tests/unit/test_reporting.py`
- Create: `tests/unit/test_security.py`
- Modify: `tests/helpers.py`

**Interfaces:**
- Consumes: `SchemaCatalog`, `DocumentRecord`, and `Issue` from Task 1.
- Produces: `ValidationConfig(schema_root: Path, excluded_directories: frozenset[str])`.
- Produces: `validate(root: Path, config: ValidationConfig) -> list[Issue]`.
- Produces: `render_text(issues: Sequence[Issue]) -> str`.
- Produces: `render_json(issues: Sequence[Issue]) -> str`.
- Produces: `python scripts/check_knowledge_base.py <knowledge-base-root>` as the canonical validator entry point.
- Adds: `--schema-root <path>` and `--format text|json`; these are validator options used by Agents, not a knowledge-base product CLI.

- [ ] **Step 1: Write failing approval and conflict tests**

```python
from pathlib import Path
from tests.helpers import TempDirectoryTestCase, make_valid_knowledge_base, write_record
from scripts.project_kb.validator import ValidationConfig, validate


class LifecycleValidationTests(TempDirectoryTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.knowledge_base = make_valid_knowledge_base(self.root / "doc-example")
        self.config = ValidationConfig(schema_root=Path("schemas"))

    def test_approved_item_requires_approval_metadata(self) -> None:
        write_record(self.knowledge_base / "01-功能基线/F01.md", {
            "id": "F01", "type": "feature", "title": "Feature",
            "status": "approved", "version": "1.0.0", "sources": ["SRC-001"],
            "last_updated": "2026-08-10"
        })

        codes = {issue.code for issue in validate(self.knowledge_base, self.config)}

        self.assertIn("KB_APPROVAL_REQUIRED", codes)

    def test_conflicted_item_requires_two_distinct_sources(self) -> None:
        write_record(self.knowledge_base / "02-架构与契约/conflict.md", {
            "id": "CONFLICT-001", "type": "knowledge_item", "title": "Runtime",
            "status": "conflicted", "version": "1.0.0", "sources": ["SRC-001"],
            "last_updated": "2026-08-10"
        })

        codes = {issue.code for issue in validate(self.knowledge_base, self.config)}

        self.assertIn("KB_CONFLICT_SOURCES", codes)
```

Add concrete `write_record(path, metadata, body="# Document\n")` and `make_valid_knowledge_base(root)` helpers to `tests/helpers.py`. The valid fixture must create CURRENT, an empty acceptance matrix, and a registered `SRC-001` source so each negative test introduces exactly one defect.

- [ ] **Step 2: Write failing traceability, sensitive-value, and JSON-report tests**

Test missing feature-to-task links, acceptance rows without evidence/version, references to unknown database/prototype/external-dependency IDs, probable private keys or token assignments, and JSON output sorted by path/code with `ok`, `issue_count`, and `issues` fields.

- [ ] **Step 3: Run the focused validator tests and verify expected failures**

Run: `py -m unittest tests.unit.test_traceability tests.unit.test_security tests.unit.test_reporting -v`

Expected: failures identifying missing modules or missing rule codes, not fixture setup errors.

- [ ] **Step 4: Implement record discovery and schema validation orchestration**

```python
# scripts/project_kb/validator.py
@dataclass(frozen=True)
class ValidationConfig:
    schema_root: Path
    excluded_directories: frozenset[str] = frozenset({".obsidian", "Excalidraw", "90-历史归档"})


def validate(root: Path, config: ValidationConfig) -> list[Issue]:
    records, parse_issues = discover_records(root, config.excluded_directories)
    issues = list(parse_issues)
    issues.extend(validate_schemas(records, config.schema_root))
    issues.extend(validate_links(root, config.excluded_directories))
    issues.extend(validate_traceability(root, records))
    issues.extend(validate_security(records))
    return sorted(issues, key=lambda issue: (str(issue.path), issue.code, issue.message))
```

- [ ] **Step 5: Implement traceability and lifecycle rules**

Require unique IDs, valid source references, approval metadata for `approved`, at least two distinct sources plus a resolver for `conflicted`, exact acceptance-matrix reconciliation, one valid CURRENT state, non-destructive supersession links, additive profiles, and valid database/prototype/external-dependency references.

- [ ] **Step 6: Implement conservative sensitive-information warnings**

Detect PEM private-key headers and assignments whose key names end with `_TOKEN`, `_PASSWORD`, `_SECRET`, or `_PRIVATE_KEY`. Exclude documented placeholder values such as `example`, `redacted`, and `${ENV_VAR}`. Use warning/error codes defined in `schemas/catalog.json`; never print the secret value.

- [ ] **Step 7: Implement text/JSON reporting and the canonical entry point**

```python
payload = {
    "ok": not issues,
    "issue_count": len(issues),
    "issues": [
        {"code": i.code, "path": str(i.path), "message": i.message, "location": i.location}
        for i in issues
    ],
}
```

Return exit code `0` when clean, `1` for validation issues, and `2` for invalid invocation or unreadable schema configuration.

- [ ] **Step 8: Run all validator tests and validate the current project knowledge base**

Run: `py -m unittest discover -s tests -v`

Run: `py scripts/check_knowledge_base.py doc-xiangmuzhishikumoban --schema-root schemas`

Expected: zero test failures and `Knowledge base validation passed`.

- [ ] **Step 9: Commit the validator**

```powershell
git add -- scripts tests
git commit -m "feat: validate knowledge bases from canonical schemas"
```

---

### Task 3: Replace the Empty Skeleton with the Complete Core Template

**Files:**
- Rename: `template/` to `templates/core/`
- Create: `templates/core/doc-project/knowledge-base.yaml`
- Create/Replace: all files under `templates/core/doc-project/00-项目总览/`
- Create/Replace: all files under `templates/core/doc-project/01-功能基线/`
- Create/Replace: all files under `templates/core/doc-project/02-架构与契约/`
- Create/Replace: all files under `templates/core/doc-project/03-实施与验收/`
- Create/Replace: all files under `templates/core/doc-project/04-决策记录/`
- Create/Replace: all files under `templates/core/doc-project/05-开发指南/`
- Create: `templates/core/doc-project/90-历史归档/README.md`
- Create: `templates/core/doc-project/.project-kb/README.md`
- Create: `scripts/project_kb/template_contract.py`
- Create: `tests/unit/test_core_template.py`
- Modify: `tests/helpers.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: JSON schemas and validator from Tasks 1–2.
- Produces: `required_template_paths() -> Sequence[Path]`.
- Produces: template markers `{{PROJECT_ID}}`, `{{PROJECT_NAME}}`, `{{KNOWLEDGE_BASE_NAME}}`, `{{INITIALIZED_AT}}`.
- Produces: a template that becomes `doc-<project-name>/` after Agent substitution.

- [ ] **Step 1: Write a failing completeness test**

```python
from pathlib import Path
from tests.helpers import TempDirectoryTestCase
from scripts.project_kb.template_contract import required_template_paths


class CoreTemplateTests(TempDirectoryTestCase):
    def test_core_template_contains_every_required_knowledge_type(self) -> None:
        root = Path("templates/core/doc-project")
        missing = [path for path in required_template_paths() if not (root / path).exists()]
        self.assertEqual(missing, [])
```

The required paths include project goals, boundaries, capability map, glossary, technology/version, feature template, architecture, module boundary, interface contracts, database, prototypes, external dependencies, CURRENT, execution board, acceptance matrix, task packages, evidence, ADR, AI protocol, local development, testing, and archive guidance.

- [ ] **Step 2: Write a failing marker and self-containment test**

Add `materialize_core_template(target: Path, project_name: str, profiles: Sequence[str] = ()) -> Path` to `tests/helpers.py`. Copy the template to the temporary workspace, replace all four markers, assert no marker matching `{{MARKER_NAME}}` remains, assert every relative Markdown link resolves inside the copied knowledge base, and assert no link points back to this repository.

- [ ] **Step 3: Run the tests and verify they fail against the current README-only skeleton**

Run: `py -m unittest tests.unit.test_core_template -v`

Expected: missing-path and unresolved-marker failures.

- [ ] **Step 4: Create the complete core template**

Every formal template document must include concrete headings, field explanations, one valid example row, source/approval/version metadata where applicable, and explicit instructions for unknown information. Do not use completion claims or pre-populated business facts.

- [ ] **Step 5: Add the machine entry and internal validation bundle contract**

`knowledge-base.yaml` records protocol version, schema version, project identity, selected profiles, knowledge-base revision, and authority paths. `.project-kb/README.md` explains that the Agent copies the packaged validator and schemas there during initialization so the result remains self-contained.

- [ ] **Step 6: Validate a materialized generic template**

Run: `py -m unittest tests.unit.test_core_template -v`

Run the validator against the materialized fixture produced by the test helper.

Expected: all template tests pass and the generic fixture has zero validation issues.

- [ ] **Step 7: Commit the complete template**

```powershell
git add -- templates template README.md scripts/project_kb/template_contract.py tests/unit/test_core_template.py
git commit -m "feat: add complete language-neutral knowledge template"
```

---

### Task 4: Implement Optional Java and Python Profiles

**Files:**
- Replace: `profiles/java/README.md`
- Replace: `profiles/java/feature-card-template.md`
- Replace: `profiles/java/acceptance-checklist.md`
- Create: `profiles/java/profile.json`
- Create: `profiles/java/templates/技术栈-Java.md`
- Replace: `profiles/python/README.md`
- Replace: `profiles/python/feature-card-template.md`
- Replace: `profiles/python/acceptance-checklist.md`
- Create: `profiles/python/profile.json`
- Create: `profiles/python/templates/技术栈-Python.md`
- Delete obsolete: `profiles/frontend/`
- Create: `tests/unit/test_profiles.py`

**Interfaces:**
- Consumes: `profile.schema.json`, core template markers, and validator.
- Produces: `java.v1` and `python.v1` profile descriptors.
- Produces: additive `added_fields`, `added_templates`, `added_requests`, and `added_acceptance_checks` arrays.

- [ ] **Step 1: Write failing zero/one/multiple-profile tests**

```python
from pathlib import Path
from tests.helpers import TempDirectoryTestCase, materialize_core_template
from scripts.project_kb.validator import ValidationConfig, validate


class ProfileTests(TempDirectoryTestCase):
    def test_profiles_are_optional_and_composable(self) -> None:
        combinations = ((), ("java.v1",), ("python.v1",), ("java.v1", "python.v1"))
        for index, profiles in enumerate(combinations):
            root = materialize_core_template(self.root / str(index), "example", profiles)
            issues = validate(root, ValidationConfig(schema_root=Path("schemas")))
            self.assertEqual(issues, [], profiles)
```

- [ ] **Step 2: Write failing additive-boundary tests**

Load each `profile.json`, compare its declared fields and states with the core catalog, and assert that alternate core statuses, authority paths, approval rules, or acceptance result values produce `KB_PROFILE_OVERRIDE`.

- [ ] **Step 3: Run profile tests and verify missing descriptor failures**

Run: `py -m unittest tests.unit.test_profiles -v`

Expected: failures for missing `profile.json` and missing additive templates.

- [ ] **Step 4: Implement `java.v1`**

Require explicit JDK version, Maven/Gradle wrapper and build command, modules/packages, dependency sources, runtime/framework, unit/integration-test boundaries, public API/event/database contracts, and reproducible security-scan evidence. Do not assume Spring or a specific build tool without confirmation.

- [ ] **Step 5: Implement `python.v1`**

Require interpreter version, environment/package managers, dependency lock strategy, service/CLI entry points, configuration sources, pytest/type/lint commands, package/module boundaries, and secret-handling rules. Do not assume FastAPI, Django, Flask, Poetry, or uv without confirmation.

- [ ] **Step 6: Delete the obsolete frontend profile after retaining any needed rules**

Remove it from current README navigation and packaging manifests, add a short exclusion notice, and keep its files available only as historical input until a future approved feature restores it.

- [ ] **Step 7: Run profile and full validator tests**

Run: `py -m unittest tests.unit.test_profiles -v`

Run: `py -m unittest discover -s tests -v`

Expected: zero failures.

- [ ] **Step 8: Commit the profile work**

```powershell
git add -- profiles tests/unit/test_profiles.py README.md
git commit -m "feat: add optional java and python knowledge profiles"
```

---

### Task 5: Build the Installable Agent Skill and Asset Synchronization

**Files:**
- Create: `skills/project-knowledge-base/SKILL.md`
- Create: `skills/project-knowledge-base/references/初始化协议.md`
- Create: `skills/project-knowledge-base/references/知识采集与确认.md`
- Create: `skills/project-knowledge-base/references/更新冲突与归档.md`
- Create: `skills/project-knowledge-base/references/验证与结果报告.md`
- Create: `skills/project-knowledge-base/assets/manifest.json`
- Create: `scripts/sync_skill_assets.py`
- Create: `tests/unit/test_skill_package.py`
- Delete obsolete: `skills/project-knowledge-context/`

**Interfaces:**
- Consumes: canonical `templates/`, `profiles/`, `schemas/`, and validator runtime.
- Produces: a self-contained `skills/project-knowledge-base/` installation package.
- Produces: `sync_assets(source_root: Path, skill_root: Path, check: bool = False) -> list[str]`, returning changed or mismatched relative paths.
- Skill trigger: initialize, inspect, update, validate, or explain a project knowledge base.

- [ ] **Step 1: During implementation, invoke the required skill-authoring workflow**

Read and follow the available `skill-creator` and `superpowers:writing-skills` instructions before editing `SKILL.md`. Record any required validation command in the task notes.

- [ ] **Step 2: Write failing package-completeness and synchronization tests**

```python
import json
from pathlib import Path
import unittest

from scripts.sync_skill_assets import sync_assets


class SkillPackageTests(unittest.TestCase):
    def test_installed_skill_contains_all_runtime_assets(self) -> None:
        assets = Path("skills/project-knowledge-base/assets")
        manifest = json.loads((assets / "manifest.json").read_text(encoding="utf-8"))
        missing = [path for path in manifest["files"] if not (assets / path).exists()]
        self.assertEqual(missing, [])

    def test_skill_assets_match_canonical_sources(self) -> None:
        mismatches = sync_assets(Path.cwd(), Path("skills/project-knowledge-base"), check=True)
        self.assertEqual(mismatches, [])
```

- [ ] **Step 3: Run tests and verify missing Skill/package failures**

Run: `py -m unittest tests.unit.test_skill_package -v`

Expected: failures for missing Skill, manifest, references, and synchronized assets.

- [ ] **Step 4: Implement deterministic asset synchronization**

Copy only manifest-declared templates, profiles, schemas, and runtime files. Normalize text files to UTF-8/LF, compare SHA-256 hashes in check mode, reject paths escaping the repository or Skill directory, and never delete undeclared user files.

- [ ] **Step 5: Write the Skill initialization workflow**

The Skill requires the Agent to verify the project root, derive `doc-<directory-name>/`, stop on existing targets, inspect the repository, distinguish facts/inferences, present the directory and proposal, obtain explicit confirmation, materialize assets, run validation, and report unresolved items. It must not create Agent-specific adapter files.

- [ ] **Step 6: Write acquisition, update, conflict, and validation references**

Use the approved contracts verbatim for source types, Proposal content, approval metadata, conflict preservation, supersession, Profile addition/removal, sensitive data, and final Agent report fields.

- [ ] **Step 7: Synchronize and validate the Skill package**

Run: `py scripts/sync_skill_assets.py`

Run: `py scripts/sync_skill_assets.py --check`

Run: `py -m unittest tests.unit.test_skill_package -v`

Expected: check mode reports no mismatches and all package tests pass.

- [ ] **Step 8: Commit the Skill**

```powershell
git add -- skills scripts/sync_skill_assets.py tests/unit/test_skill_package.py
git commit -m "feat: package agent-native knowledge base skill"
```

---

### Task 6: Add Golden Examples and Agent Conformance Fixtures

**Files:**
- Create: `examples/generic/`
- Create: `examples/java/`
- Create: `examples/python/`
- Create: `examples/java-python/`
- Create: `tests/integration/test_golden_examples.py`
- Create: `tests/integration/test_initialization_safety.py`
- Create: `tests/fixtures/invalid/`
- Create: `tests/snapshots/expected-structures.json`

**Interfaces:**
- Consumes: packaged Skill assets, core template, profiles, and validator.
- Produces: four complete, approved-example knowledge bases with no business completion claims.
- Produces: invalid fixtures for overwrite, stale proposal, missing approval, unresolved conflict, broken traceability, Profile override, and sensitive material.

- [ ] **Step 1: Write failing golden-example validation tests**

```python
from pathlib import Path
import unittest

from scripts.project_kb.validator import ValidationConfig, validate


class GoldenExampleTests(unittest.TestCase):
    def test_all_golden_examples_validate(self) -> None:
        for name in ("generic", "java", "python", "java-python"):
            root = Path("examples") / name
            issues = validate(root, ValidationConfig(schema_root=Path("schemas")))
            self.assertEqual(issues, [], name)
```

- [ ] **Step 2: Write failing structure snapshot tests**

Record sorted relative paths for all four examples. Assert the generic example contains no language-specific required document, Java/Python examples contain only their selected Profile additions, and the mixed example contains both without duplicate core files.

- [ ] **Step 3: Write failing safety and negative-conformance tests**

Assert an initialization simulation refuses an existing target, invalid fixtures return their exact expected codes, archived content cannot satisfy current requirements, and no example contains `AGENTS.md`, `CLAUDE.md`, private keys, tokens, or repository-external relative links.

- [ ] **Step 4: Run tests and verify failures because examples are absent**

Run: `py -m unittest discover -s tests/integration -v`

Expected: missing example/snapshot failures.

- [ ] **Step 5: Create the generic and language-specific golden examples**

Use fictional, explicitly approved sample facts with source records. Include project goals, boundaries, capabilities, one feature, architecture, contract, database/prototype/external-dependency examples where applicable, one ADR, CURRENT, one task package, an acceptance matrix, and evidence. Keep all business implementation results `not_started` unless the example evidence genuinely demonstrates a governance-only condition.

- [ ] **Step 6: Create invalid fixtures with one isolated defect each**

Each fixture contains a `README.md` naming the single intended error code. Tests assert exact code sets so an unrelated parse failure cannot masquerade as successful negative coverage.

- [ ] **Step 7: Run integration and full tests**

Run: `py -m unittest discover -s tests/integration -v`

Run: `py -m unittest discover -s tests -v`

Expected: all tests pass with zero errors and zero failures.

- [ ] **Step 8: Commit examples and conformance fixtures**

```powershell
git add -- examples tests/integration tests/fixtures tests/snapshots
git commit -m "test: add knowledge base conformance examples"
```

---

### Task 7: Self-Host the New Standard and Complete MVP Acceptance

**Files:**
- Modify: `doc-xiangmuzhishikumoban/` to comply with the final schemas and template
- Create: `doc-xiangmuzhishikumoban/knowledge-base.yaml`
- Create: `doc-xiangmuzhishikumoban/.project-kb/` from the packaged runtime
- Modify: `doc-xiangmuzhishikumoban/03-实施与验收/CURRENT.md`
- Create: `doc-xiangmuzhishikumoban/03-实施与验收/任务包/TASK-Fxx-nnn-*.md` as approved by CURRENT
- Modify: `doc-xiangmuzhishikumoban/03-实施与验收/验收矩阵.md`
- Create: `doc-xiangmuzhishikumoban/03-实施与验收/验收证据/`
- Modify: `README.md`
- Create: `docs/agent-conformance/README.md`
- Create: `docs/agent-conformance/codex.md`
- Create: `docs/agent-conformance/second-agent.md`

**Interfaces:**
- Consumes: all prior tasks.
- Produces: a self-validating project knowledge base and evidence for F01-AC-01 through F06-AC-02.
- Produces: manual conformance evidence from Codex and one other available Agent; content may differ, but both structures must validate.

- [ ] **Step 1: Reconcile the implementation task sequence with the approved plan**

Confirm that CURRENT progressed through one task package per implementation slice, beginning with `TASK-F05-001` for Tasks 1–2. Link each completed slice to its features, architecture/contracts, ADRs, acceptance rows, commands, and evidence. Do not mark features completed before their evidence exists.

- [ ] **Step 2: Materialize the runtime and schemas into this project knowledge base**

Use the same Skill assets as a target project. Add `knowledge-base.yaml`, the internal runtime bundle, missing database/prototype/external-dependency indexes, and source/approval/version metadata required by the final schemas.

- [ ] **Step 3: Validate the self-hosted project and all examples**

Run: `py doc-xiangmuzhishikumoban/.project-kb/check.py doc-xiangmuzhishikumoban --format text`

Run: `py scripts/check_knowledge_base.py doc-xiangmuzhishikumoban --schema-root schemas --format json`

Run: `py -m unittest discover -s tests -v`

Expected: both validators report zero issues and all tests pass.

- [ ] **Step 4: Perform the Codex initialization conformance scenario**

In a disposable project, install/use the packaged Skill, ask Codex to initialize the knowledge base, answer with the fixed fixture responses documented in `docs/agent-conformance/README.md`, and save the transcript summary, generated tree, validator command, and result in `codex.md`.

- [ ] **Step 5: Perform a second-Agent conformance scenario**

Repeat the same fixture with another available Skill-capable Agent. If no second Agent is available, leave F01/F02 cross-Agent acceptance `partial` and report the external dependency; do not fabricate evidence or mark the MVP complete.

- [ ] **Step 6: Reconcile acceptance evidence without overstating completion**

For every F01–F06 acceptance row, record the exact command/path/version. Mark an item `passed` only when its evidence exists. Keep unavailable cross-Agent evidence `partial`; task/feature status must match the matrix.

- [ ] **Step 7: Run the final release gate**

Run: `py -m unittest discover -s tests -v`

Run: `py scripts/check_knowledge_base.py doc-xiangmuzhishikumoban --schema-root schemas`

Run: `py scripts/sync_skill_assets.py --check`

Run: `git diff --check`

Run: `git status --short`

Expected: tests and validators pass, Skill assets are synchronized, no whitespace errors exist, and Git status contains only the intended MVP changes before commit.

- [ ] **Step 8: Commit the self-hosted MVP evidence**

```powershell
git add -- README.md doc-xiangmuzhishikumoban docs/agent-conformance
git commit -m "docs: record agent-native knowledge base mvp evidence"
```

---

## Implementation Order and Review Gates

1. Task 1 freezes the machine model used everywhere else.
2. Task 2 provides deterministic validation before templates or Skill assets expand.
3. Task 3 makes the generic product usable without a Profile.
4. Task 4 adds optional Java/Python behavior without changing the core.
5. Task 5 packages the approved workflow for Agent use.
6. Task 6 proves generic and Profile combinations through golden examples.
7. Task 7 self-hosts the result and records real Agent evidence.

Each task requires a fresh diff review and its focused test command before proceeding. Tasks 3–6 must not weaken a Task 1 schema or Task 2 validator merely to make a fixture pass; schema changes require an explicit contract review and a new failing test.

## Specification Coverage

| Approved capability | Implemented by | Primary evidence |
| --- | --- | --- |
| F01 Agent-driven initialization | Tasks 3, 5, 6, 7 | Generic initialization fixture, overwrite refusal, Agent transcript |
| F02 Knowledge acquisition and confirmation | Tasks 1, 2, 5, 7 | Proposal/source/approval/conflict tests and Agent transcript |
| F03 Storage, versions, and traceability | Tasks 1, 2, 3, 7 | Lifecycle and traceability tests; self-hosted evidence |
| F04 Complete core template | Tasks 1, 3, 6 | Template completeness test and generic golden example |
| F05 Schema-driven validator | Tasks 1, 2, 6, 7 | Unit/negative tests and two clean validation runs |
| F06 Optional Java/Python profiles | Tasks 4, 6, 7 | Zero/Java/Python/mixed fixtures and additive-boundary tests |
| No independent user CLI | Tasks 2 and 5 | Validator-only entry point and Skill workflow review |
| No generated Agent adapters | Tasks 3, 5, and 6 | Template/package assertions and initialization safety test |
| Self-contained initialized output | Tasks 3, 5, 6, and 7 | Internal runtime bundle and external-link checks |
