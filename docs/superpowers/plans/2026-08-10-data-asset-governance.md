# Data Asset Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a business-oriented data asset knowledge type that links database, API, message, file, object-storage, manual-input, and other data sources without replacing existing technical contracts.

**Architecture:** Introduce `data_asset` as an independently validated lifecycle type with one canonical JSON Schema. Add a `数据资产/` directory and reusable card template to the core knowledge-base template, then synchronize canonical sources into the installable Skill. Golden examples prove that one logical data asset can reference one or many technical sources while existing database, interface, and external-dependency documents keep their current responsibilities.

**Tech Stack:** Python 3 standard library, Markdown, controlled YAML Front Matter, JSON Schema catalog, `unittest`, PowerShell, Git.

## Global Constraints

- 所有用户回复和提交信息使用中文。
- 设计依据为 `docs/superpowers/specs/2026-08-10-data-asset-governance-design.md`，并关联现有 F04、F05、CONTRACT-INIT-001；本任务使用新增验收项 KB-AC-23、KB-AC-24、KB-AC-25，不复用旧验收结果证明新增能力。
- 执行 Task 1 前必须展示实施 Proposal 的精确目标、来源、未知项、冲突和验证命令，并获得用户显式确认。
- 当前 `doc-atlas/` 迁移属于用户已有改动；不得把旧目录删除或其他迁移文件混入本计划的提交。先运行 `git ls-files --error-unmatch doc-atlas/README.md`，失败时暂停并请用户先确认迁移基线。
- 数据资产描述业务数据；数据库、接口契约和外部依赖继续描述技术细节，不能被删除或改成数据资产的重复副本。
- 未知内容使用 `missing`，冲突内容使用 `conflicted`；AI 不得把推测标记为 `approved`。
- 不建设独立数据目录服务，不自动扫描血缘，不运行质量监控，不执行真实权限控制。
- 不写入真实密码、Token、私钥或未脱敏个人数据；黄金样例只能使用虚构数据。
- 根目录的 `schemas/`、`scripts/`、`templates/` 是唯一规范源；Skill 内置副本只能通过 `py scripts/sync_skill_assets.py` 同步。

---

### Task 1: 建立可执行的项目治理任务

**Files:**
- Create: `doc-atlas/03-实施与验收/任务包/TASK-KB-005-数据资产治理.md`
- Modify: `doc-atlas/03-实施与验收/CURRENT.md`
- Modify: `doc-atlas/01-功能基线/F04-完整核心模板与知识模型.md`
- Modify: `doc-atlas/01-功能基线/F05-Schema驱动检查器.md`
- Modify: `doc-atlas/02-架构与契约/初始化产物契约.md`
- Modify: `doc-atlas/02-架构与契约/系统架构.md`
- Modify: `doc-atlas/03-实施与验收/验收矩阵.md`

**Interfaces:**
- Consumes: approved design `docs/superpowers/specs/2026-08-10-data-asset-governance-design.md` and the implementation Proposal confirmed immediately before execution.
- Produces: active governance task `TASK-KB-005` referencing F04/F05, CONTRACT-INIT-001, and new acceptance rows KB-AC-23～25; later tasks may execute only while CURRENT points to this task.

- [ ] **Step 1: Verify the knowledge-base rename is already tracked**

Run:

```powershell
git ls-files --error-unmatch doc-atlas/README.md
git status --short
```

Expected: the first command prints `doc-atlas/README.md`; existing unrelated changes are recorded and excluded from later `git add -- <paths>` commands. If the first command fails, stop without editing and ask the user to resolve or explicitly authorize adoption of the rename.

- [ ] **Step 2: Write the task package and activate CURRENT**

Create the task package with this metadata and scope:

```markdown
---
id: TASK-KB-005
type: governance_task
title: 数据资产治理
plan: docs/superpowers/plans/2026-08-10-data-asset-governance.md
status: ready
acceptance: [KB-AC-23, KB-AC-24, KB-AC-25]
last_updated: 2026-08-10
---

# TASK-KB-005：数据资产治理

## 范围

- 新增数据资产 Schema、核心模板、生命周期检查、黄金样例和 Skill 同步资产。
- 保留数据库、接口契约和外部依赖的技术职责。

## 排除

- 独立数据目录服务、自动血缘、质量监控和真实权限执行。

## 依据

- 设计：`docs/superpowers/specs/2026-08-10-data-asset-governance-design.md`
- 功能：F04、F05
- 契约：CONTRACT-INIT-001
- 验收：KB-AC-23（模板与 Schema）、KB-AC-24（生命周期与来源类型）、KB-AC-25（Skill 与黄金样例一致性）
```

Set CURRENT to exactly one active task:

```markdown
# 当前状态

- 任务编号：TASK-KB-005
- 任务包：[TASK-KB-005 数据资产治理](./任务包/TASK-KB-005-数据资产治理.md)
- 当前阶段：ready
- 唯一下一动作：执行数据资产 Schema 的测试驱动实现
- 当前阻塞：无
```

- [ ] **Step 3: Update approved product knowledge**

Add “数据资产” to F04's required knowledge types, add `data_asset` Schema and source-type list validation to F05's included checks, add `02-架构与契约/数据资产/` to CONTRACT-INIT-001, and add the data-asset component and its relationship to technical contracts to the system architecture. Add KB-AC-23、KB-AC-24、KB-AC-25 to the matrix with `not_started`; do not rewrite the historical results of F04-AC-01～02 or F05-AC-01～02.

- [ ] **Step 4: Validate the active baseline**

Run:

```powershell
py scripts/check_knowledge_base.py doc-atlas --schema-root schemas
git diff --check
```

Expected: checker exit code 0 and no whitespace errors.

- [ ] **Step 5: Commit only the governance files**

```powershell
git add -- doc-atlas/01-功能基线/F04-完整核心模板与知识模型.md doc-atlas/01-功能基线/F05-Schema驱动检查器.md doc-atlas/02-架构与契约/初始化产物契约.md doc-atlas/02-架构与契约/系统架构.md doc-atlas/03-实施与验收/CURRENT.md doc-atlas/03-实施与验收/验收矩阵.md doc-atlas/03-实施与验收/任务包/TASK-KB-005-数据资产治理.md
git commit -m "治理：启动数据资产知识模型任务"
```

---

### Task 2: 添加数据资产 Schema 和来源类型列表校验

**Files:**
- Create: `schemas/data-asset.schema.json`
- Create: `tests/unit/test_data_assets.py`
- Modify: `schemas/catalog.json`
- Modify: `schemas/README.md`
- Modify: `scripts/project_kb/schema_catalog.py`
- Modify: `tests/unit/test_schema_catalog.py`
- Modify: `skills/context-atlas/assets/manifest.json`
- Modify by synchronization: `skills/context-atlas/assets/schemas/`, `skills/context-atlas/assets/scripts/project_kb/schema_catalog.py`

**Interfaces:**
- Consumes: existing `SchemaCatalog.validate(kind, metadata, path) -> list[Issue]`.
- Produces: schema keyword `list_enums: dict[str, list[str]]` and catalog kind `data_asset`; invalid list members return `KB_SCHEMA_ENUM`.

- [ ] **Step 1: Write failing list-enum and data-asset schema tests**

Append this test to `tests/unit/test_schema_catalog.py`:

```python
def test_catalog_reports_invalid_list_enum_member(self) -> None:
    self.write_catalog(
        {
            "required": ["source_types"],
            "list_enums": {"source_types": ["database", "api"]},
        }
    )

    issues = SchemaCatalog.load(self.root).validate(
        "feature",
        {"source_types": ["database", "spreadsheet"]},
        self.root / "DATA-001.md",
    )

    self.assertEqual([issue.code for issue in issues], ["KB_SCHEMA_ENUM"])
```

Create `tests/unit/test_data_assets.py` with a valid metadata helper and these assertions:

```python
from pathlib import Path
import unittest

from scripts.project_kb.schema_catalog import SchemaCatalog


class DataAssetSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = SchemaCatalog.load(Path("schemas"))
        self.path = Path("DATA-001.md")
        self.metadata = {
            "id": "DATA-001",
            "type": "data_asset",
            "title": "客户信息",
            "status": "proposed",
            "version": "0.1.0",
            "sources": ["SRC-001"],
            "owner": "missing",
            "source_types": ["database", "api"],
            "sensitivity": "missing",
            "retention": "missing",
            "last_updated": "2026-08-10",
        }

    def test_valid_data_asset_metadata_passes_schema(self) -> None:
        self.assertEqual(
            self.catalog.validate("data_asset", self.metadata, self.path),
            [],
        )

    def test_data_asset_rejects_unknown_source_type(self) -> None:
        self.metadata["source_types"] = ["database", "spreadsheet"]
        codes = {
            issue.code
            for issue in self.catalog.validate("data_asset", self.metadata, self.path)
        }
        self.assertIn("KB_SCHEMA_ENUM", codes)

    def test_data_asset_requires_governance_fields(self) -> None:
        for field in ("owner", "source_types", "sensitivity", "retention"):
            with self.subTest(field=field):
                metadata = dict(self.metadata)
                metadata.pop(field)
                codes = {
                    issue.code
                    for issue in self.catalog.validate("data_asset", metadata, self.path)
                }
                self.assertIn("KB_SCHEMA_REQUIRED", codes)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify the expected failures**

Run:

```powershell
py -m unittest tests.unit.test_schema_catalog tests.unit.test_data_assets -v
```

Expected: the list-enum test fails because `list_enums` is unsupported, and the data-asset tests error because `data_asset` is absent from `schemas/catalog.json`.

- [ ] **Step 3: Implement list-enum validation**

Add this block after scalar enum validation in `SchemaCatalog.validate`:

```python
for field, allowed in schema.get("list_enums", {}).items():
    value = metadata.get(field)
    if isinstance(value, list):
        invalid = [item for item in value if item not in allowed]
        if invalid:
            issues.append(
                Issue("KB_SCHEMA_ENUM", path, f"invalid {field} values: {invalid!r}")
            )
```

- [ ] **Step 4: Add the exact data-asset schema and register it**

Create `schemas/data-asset.schema.json`:

```json
{
  "required": ["id", "type", "title", "status", "version", "sources", "owner", "source_types", "sensitivity", "retention", "last_updated"],
  "enums": {
    "type": ["data_asset"],
    "status": ["missing", "proposed", "approved", "conflicted", "stale", "superseded", "archived"],
    "sensitivity": ["public", "internal", "sensitive", "restricted", "missing"]
  },
  "list_enums": {
    "source_types": ["database", "api", "message", "file", "object_storage", "manual_input", "other"]
  },
  "patterns": {
    "id": "DATA-\\d{3}",
    "version": "\\d+\\.\\d+\\.\\d+",
    "last_updated": "\\d{4}-\\d{2}-\\d{2}"
  },
  "non_empty_lists": ["sources", "source_types"],
  "unique_lists": ["sources", "source_types"]
}
```

Register `"data_asset": "data-asset.schema.json"` in `schemas/catalog.json`, document `data_asset` and `list_enums` in `schemas/README.md`, add `schemas/data-asset.schema.json` to the sorted Skill asset manifest, then synchronize:

```powershell
py scripts/sync_skill_assets.py
```

- [ ] **Step 5: Verify and commit**

Run:

```powershell
py -m unittest tests.unit.test_schema_catalog tests.unit.test_data_assets tests.unit.test_skill_package -v
py scripts/sync_skill_assets.py --check
git diff --check
```

Expected: all focused tests pass, asset sync reports synchronized, and the diff check is empty.

```powershell
git add -- schemas scripts/project_kb/schema_catalog.py tests/unit/test_schema_catalog.py tests/unit/test_data_assets.py skills/context-atlas/assets
git commit -m "模型：新增数据资产结构规则"
```

---

### Task 3: 让数据资产复用知识生命周期

**Files:**
- Modify: `scripts/project_kb/traceability.py`
- Modify: `tests/unit/test_lifecycle.py`
- Modify by synchronization: `skills/context-atlas/assets/scripts/project_kb/traceability.py`

**Interfaces:**
- Consumes: metadata type `data_asset` registered by Task 2.
- Produces: `LIFECYCLE_TYPES = frozenset({"knowledge_item", "data_asset"})`; both types share source, approval, conflict, stale, supersession, and archive rules.

- [ ] **Step 1: Write failing lifecycle tests**

Add this helper and test cases to `tests/unit/test_lifecycle.py`:

```python
def write_data_asset(self, **overrides: object) -> None:
    metadata: dict[str, object] = {
        "id": "DATA-001",
        "type": "data_asset",
        "title": "客户信息",
        "status": "approved",
        "version": "1.0.0",
        "sources": ["SRC-001"],
        "owner": "project-owner",
        "source_types": ["database"],
        "sensitivity": "internal",
        "retention": "project-lifetime",
        "last_updated": "2026-08-10",
    }
    metadata.update(overrides)
    write_record(
        self.knowledge_base / "02-架构与契约/数据资产/DATA-001.md",
        metadata,
    )

def test_approved_data_asset_requires_approval_metadata(self) -> None:
    self.write_data_asset()

    codes = {issue.code for issue in validate(self.knowledge_base, self.config)}

    self.assertIn("KB_APPROVAL_REQUIRED", codes)

def test_data_asset_rejects_unknown_knowledge_source(self) -> None:
    self.write_data_asset(status="proposed", sources=["SRC-999"])

    codes = {issue.code for issue in validate(self.knowledge_base, self.config)}

    self.assertIn("KB_SOURCE_UNKNOWN", codes)

def test_conflicted_data_asset_requires_two_sources(self) -> None:
    self.write_data_asset(
        status="conflicted",
        resolution_required_from="project-owner",
    )

    codes = {issue.code for issue in validate(self.knowledge_base, self.config)}

    self.assertIn("KB_CONFLICT_SOURCES", codes)

def test_data_asset_rejects_broken_local_contract_link(self) -> None:
    self.write_data_asset(status="proposed")
    path = self.knowledge_base / "02-架构与契约/数据资产/DATA-001.md"
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\n[缺失数据库契约](../数据库/DB-999.md)\n",
        encoding="utf-8",
    )

    codes = {issue.code for issue in validate(self.knowledge_base, self.config)}

    self.assertIn("KB_LINK_BROKEN", codes)
```

- [ ] **Step 2: Run the lifecycle tests and verify failure**

Run:

```powershell
py -m unittest tests.unit.test_lifecycle -v
```

Expected: approval、unknown-source、conflict tests fail because `_validate_lifecycle` currently skips every type except `knowledge_item`; the broken-link test already passes through the existing generic link validator.

- [ ] **Step 3: Generalize the lifecycle gate**

Add near the traceability constants:

```python
LIFECYCLE_TYPES = frozenset({"knowledge_item", "data_asset"})
```

Replace:

```python
if metadata.get("type") != "knowledge_item":
    continue
```

with:

```python
if metadata.get("type") not in LIFECYCLE_TYPES:
    continue
```

- [ ] **Step 4: Synchronize, verify, and commit**

```powershell
py scripts/sync_skill_assets.py
py -m unittest tests.unit.test_lifecycle tests.unit.test_data_assets tests.unit.test_skill_package -v
py scripts/sync_skill_assets.py --check
git diff --check
git add -- scripts/project_kb/traceability.py tests/unit/test_lifecycle.py skills/context-atlas/assets/scripts/project_kb/traceability.py
git commit -m "治理：统一数据资产生命周期检查"
```

Expected: all focused tests pass and Skill assets match canonical sources.

---

### Task 4: 添加数据资产核心模板

**Files:**
- Create: `templates/core/doc-project/02-架构与契约/数据资产/README.md`
- Create: `templates/core/doc-project/02-架构与契约/数据资产/TEMPLATE.md`
- Modify: `templates/core/doc-project/02-架构与契约/README.md`
- Modify: `templates/core/doc-project/02-架构与契约/数据库/README.md`
- Modify: `templates/core/doc-project/02-架构与契约/接口契约.md`
- Modify: `scripts/project_kb/template_contract.py`
- Modify: `tests/unit/test_core_template.py`
- Modify: `skills/context-atlas/assets/manifest.json`
- Modify by synchronization: corresponding files under `skills/context-atlas/assets/templates/` and `skills/context-atlas/assets/scripts/project_kb/template_contract.py`

**Interfaces:**
- Consumes: `data_asset` metadata contract and lifecycle behavior from Tasks 2–3.
- Produces: required template paths `数据资产/README.md` and `数据资产/TEMPLATE.md`; cards use `DATA-<three digits>` IDs and link to, rather than copy, technical contracts.

- [ ] **Step 1: Write failing core-template assertions**

Add to `tests/unit/test_core_template.py`:

```python
def test_data_asset_template_explains_governance_boundaries(self) -> None:
    root = Path("templates/core/doc-project/02-架构与契约/数据资产")
    readme = (root / "README.md").read_text(encoding="utf-8")
    template = (root / "TEMPLATE.md").read_text(encoding="utf-8")

    for phrase in ("业务含义", "数据来源", "质量要求", "安全要求", "保存规则"):
        self.assertIn(phrase, template)
    self.assertIn("知识来源", readme)
    self.assertIn("数据库", readme)
    self.assertIn("接口契约", readme)
```

Also add these paths to `required_template_paths()`:

```python
"02-架构与契约/数据资产/README.md",
"02-架构与契约/数据资产/TEMPLATE.md",
```

- [ ] **Step 2: Run the test and verify failure**

```powershell
py -m unittest tests.unit.test_core_template -v
```

Expected: failure because the data-asset directory and files do not exist.

- [ ] **Step 3: Create the README and card template**

Use this exact Front Matter in `TEMPLATE.md`, followed by sections for 基本信息、数据来源、主要内容、数据流转、质量要求、安全要求、保存规则、依据与未决问题:

```yaml
---
id: DATA-001
type: data_asset
title: 数据资产名称
status: proposed
version: 0.1.0
sources: [SRC-001]
owner: missing
source_types: [database]
sensitivity: missing
retention: missing
last_updated: {{INITIALIZED_AT}}
---
```

The README must distinguish actual data sources from evidence sources and include this source mapping table:

```markdown
| 来源类型 | 名称 | 流向 | 用途 | 技术契约 | 状态 |
| --- | --- | --- | --- | --- | --- |
| database | 示例数据库 | 流入 | 提供示例数据 | DB-001（确认后链接） | proposed |
```

Update the architecture index to link the new directory. Update database and interface guidance to state that they keep technical details while data-asset cards carry business meaning, quality, security, and retention.

- [ ] **Step 4: Register new Skill files and synchronize**

Add the two new template paths to the sorted manifest and run:

```powershell
py scripts/sync_skill_assets.py
```

- [ ] **Step 5: Verify and commit**

```powershell
py -m unittest tests.unit.test_core_template tests.unit.test_skill_package -v
py scripts/sync_skill_assets.py --check
git diff --check
git add -- templates/core/doc-project/02-架构与契约 scripts/project_kb/template_contract.py tests/unit/test_core_template.py skills/context-atlas/assets
git commit -m "模板：新增数据资产说明卡"
```

Expected: the materialized core template remains self-contained and valid, and Skill synchronization passes.

---

### Task 5: 在黄金样例中证明多来源治理

**Files:**
- Modify: `scripts/generate_conformance_examples.py`
- Modify: `tests/integration/test_golden_examples.py`
- Regenerate: `examples/single-stack/`
- Regenerate: `examples/multi-stack/`
- Regenerate: `tests/fixtures/invalid/`
- Regenerate: `tests/snapshots/expected-structures.json`

**Interfaces:**
- Consumes: Skill-packaged template, scripts, and schemas synchronized by Tasks 2–4.
- Produces: `DATA-001-知识项.md` in both golden examples; single-stack uses `database`, multi-stack uses `database`, `api`, and `file`; both validate through the same checker.

- [ ] **Step 1: Write failing golden-example assertions**

Add to `tests/integration/test_golden_examples.py`:

```python
def test_examples_include_governed_data_assets(self) -> None:
    expected_types = {
        "single-stack": "source_types: [database]",
        "multi-stack": "source_types: [database, api, file]",
    }
    for name, expected in expected_types.items():
        path = Path("examples") / name / "02-架构与契约/数据资产/DATA-001-知识项.md"
        self.assertTrue(path.is_file(), path)
        content = path.read_text(encoding="utf-8")
        self.assertIn(expected, content)
        self.assertIn("../数据库/DB-001.md", content)
```

- [ ] **Step 2: Run the test and verify failure**

```powershell
py -m unittest tests.integration.test_golden_examples -v
```

Expected: failure because neither example contains `DATA-001-知识项.md`.

- [ ] **Step 3: Add a dedicated generator helper**

Add `_approved_data_asset(root: Path, name: str) -> None` to the generator. It must call `_record` with this metadata:

```python
source_types = ["database"] if name == "single-stack" else ["database", "api", "file"]
metadata = {
    "id": "DATA-001",
    "type": "data_asset",
    "title": "知识项数据",
    "status": "approved",
    "version": "1.0.0",
    "sources": ["SRC-001", "SRC-002"],
    "owner": "example-owner",
    "source_types": source_types,
    "sensitivity": "internal",
    "retention": "project-lifetime",
    "approved_by": "example-owner",
    "approved_at": DATE,
    "proposal_revision": "1",
    "confirmed_revision": "1",
    "last_updated": DATE,
}
```

The body must use fictional content, link `../数据库/DB-001.md` and `../CONTRACT-001.md`, describe the flow “输入 → 存储 → 查询组件”, and include quality, access, and retention rules. Call this helper from `_populate_example` after DB-001 and CONTRACT-001 exist.

- [ ] **Step 4: Regenerate only the declared tracked outputs**

```powershell
git rm -r -- examples tests/fixtures/invalid tests/snapshots/expected-structures.json
py scripts/generate_conformance_examples.py
```

Expected: the generator recreates exactly `examples/single-stack`, `examples/multi-stack`, the invalid fixtures, and the snapshot. Both snapshot structures include `.project-kb/schemas/data-asset.schema.json`, `数据资产/README.md`, `数据资产/TEMPLATE.md`, and `DATA-001-知识项.md`.

- [ ] **Step 5: Verify and commit**

```powershell
py -m unittest tests.integration.test_golden_examples tests.integration.test_initialization_safety -v
py scripts/check_knowledge_base.py examples/single-stack --schema-root schemas
py scripts/check_knowledge_base.py examples/multi-stack --schema-root schemas
git diff --check
git add -- scripts/generate_conformance_examples.py tests/integration/test_golden_examples.py examples tests/fixtures/invalid tests/snapshots/expected-structures.json
git commit -m "示例：覆盖数据资产多来源治理"
```

Expected: focused integration tests and both explicit checker runs pass.

---

### Task 6: 全量验证并关闭治理任务

**Files:**
- Create: `doc-atlas/03-实施与验收/验收证据/数据资产治理阶段验证.md`
- Modify: `doc-atlas/03-实施与验收/任务包/TASK-KB-005-数据资产治理.md`
- Modify: `doc-atlas/03-实施与验收/CURRENT.md`
- Modify: `doc-atlas/03-实施与验收/验收矩阵.md`
- Inspect: all files changed by Tasks 1–5

**Interfaces:**
- Consumes: passing schema, lifecycle, template, synchronization, initialization, and golden-example tests.
- Produces: reproducible evidence for KB-AC-23～25; TASK-KB-005 becomes `completed` only when all three new acceptance rows have passing evidence.

- [ ] **Step 1: Run the complete automated suite**

```powershell
py -m unittest discover -s tests -v
```

Expected: exit code 0 and zero failures/errors.

- [ ] **Step 2: Run all repository-level checks**

```powershell
py scripts/sync_skill_assets.py --check
py scripts/check_knowledge_base.py examples/single-stack --schema-root schemas
py scripts/check_knowledge_base.py examples/multi-stack --schema-root schemas
py scripts/check_knowledge_base.py doc-atlas --schema-root schemas
git diff --check
```

Expected: all commands exit 0; Skill assets are synchronized; each knowledge base reports no issues; diff check prints nothing.

- [ ] **Step 3: Record exact evidence**

Create the evidence document with the command list, execution date, exit codes, unittest test count, example paths, and commit hashes from Tasks 2–5. State explicitly that validation proves structure and traceability only, not business correctness.

- [ ] **Step 4: Close the task only from evidence**

Set TASK-KB-005 to `completed`. Update KB-AC-23、KB-AC-24、KB-AC-25 to `passed` only when the evidence document contains the corresponding successful checks and version/commit. Do not change the historical results of F04/F05 acceptance rows merely because this task passes. Set CURRENT to the project's single next action; if no next task is approved, use exactly:

```markdown
# 当前状态

- 当前任务：无可执行开发任务
- 最近完成：TASK-KB-005（数据资产治理）
- 唯一下一动作：由项目责任人确认下一项治理任务
- 当前阻塞：无
```

- [ ] **Step 5: Verify the closure and commit**

```powershell
py scripts/check_knowledge_base.py doc-atlas --schema-root schemas
git diff --check
git status --short
git add -- doc-atlas/03-实施与验收/CURRENT.md doc-atlas/03-实施与验收/验收矩阵.md doc-atlas/03-实施与验收/任务包/TASK-KB-005-数据资产治理.md doc-atlas/03-实施与验收/验收证据/数据资产治理阶段验证.md
git commit -m "验收：完成数据资产治理阶段验证"
```

Expected: the knowledge-base checker passes before the commit, and the staged set contains only the four governance files listed above.
