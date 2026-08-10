# Single Knowledge Base, Multi-Stack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace language-specific Profile variants with one language-agnostic project knowledge base that records any discovered technology stack in one document set.

**Architecture:** Keep one core template, one initializer contract, and one validator. Technology entries are ordinary approved knowledge in `技术栈与版本.md`; no profile selection, profile schema, or profile-specific materialization remains. Golden examples cover one single-stack and one multi-stack project using the same structure.

**Tech Stack:** Python 3 standard library, Markdown, YAML-compatible front matter, JSON Schema catalog, `unittest`, PowerShell verification commands.

## Global Constraints

- Every user-facing response and every commit message is Chinese.
- Initialization creates exactly `doc-<project-name>/` and never creates or maintains `AGENTS.md` or `CLAUDE.md`.
- No backward-compatibility layer is required; obsolete Profile assets and language-split examples are deleted.
- Java, Python, frontend, and future technologies are recorded as project facts, not knowledge-base variants.
- Unknown facts remain `missing` or Proposal; the Agent must not invent versions, commands, or ownership.

---

### Task 1: Make the core knowledge model stack-neutral

**Files:**
- Modify: `templates/core/doc-project/knowledge-base.yaml`
- Modify: `templates/core/doc-project/00-项目总览/技术栈与版本.md`
- Modify: `templates/core/doc-project/05-开发指南/AI知识采集协议.md`
- Modify: `templates/core/doc-project/00-项目总览/README.md`
- Modify: corresponding synchronized files under `skills/context-atlas/assets/templates/core/doc-project/`
- Test: `tests/unit/test_core_template.py`, `tests/unit/test_skill_package.py`

**Interfaces:** Remove `profiles` metadata and profile wording. Preserve the existing core knowledge IDs and add explicit multi-stack recording guidance.

- [ ] **Step 1: Add failing assertions** that the core manifest has no profile field, the technology document accepts multiple named entries, and the protocol asks the Agent to discover stacks without a selection prompt.
- [ ] **Step 2: Run the focused tests** and confirm they fail against current profile-bearing templates.
- [ ] **Step 3: Edit the core template and synchronized Skill assets** to remove profile references and document name, version, modules, purpose, commands, configuration, evidence, and unknown fields for each technology.
- [ ] **Step 4: Run focused tests and `py scripts/sync_skill_assets.py --check`**; expect PASS.
- [ ] **Step 5: Commit** with `模型：统一核心模板的多技术栈记录`.

### Task 2: Remove Profile implementation and contracts

**Files:**
- Delete: `profiles/`
- Delete: `doc-xiangmuzhishikumoban/02-架构与契约/Profile扩展契约.md`
- Modify: `doc-xiangmuzhishikumoban/00-项目总览/项目边界.md`, `项目目标与成功标准.md`, `产品能力地图.md`, `术语表.md`
- Modify: `doc-xiangmuzhishikumoban/02-架构与契约/README.md`, `初始化产物契约.md`, `系统架构.md`
- Modify: `README.md` and `skills/context-atlas/SKILL.md`
- Test: `tests/unit/test_profiles.py`, `tests/unit/test_skill_package.py`

**Interfaces:** The initializer and validator accept only project root/name and core assets; no profile argument or profile descriptor is exposed.

- [ ] **Step 1: Add failing tests** asserting the profile directories, descriptors, profile schema, and profile-selection API are absent.
- [ ] **Step 2: Run focused tests** and confirm the old implementation is detected.
- [ ] **Step 3: Delete obsolete Profile source, contracts, descriptors, and references; merge useful collection guidance into the core protocol.** Do not retain a compatibility shim.
- [ ] **Step 4: Run the full unit suite and repository-wide `rg` checks** for `Profile`, `profiles/java`, `profiles/python`, and `profile` parameters; remove every obsolete product reference except historical lifecycle terminology explicitly needed by schemas.
- [ ] **Step 5: Commit** with `清理：删除语言 Profile 模型与旧契约`.

### Task 3: Simplify initialization and synchronization

**Files:**
- Modify: `scripts/project_kb/initializer.py`
- Modify: `skills/context-atlas/assets/scripts/project_kb/initializer.py`
- Modify: `scripts/sync_skill_assets.py` and `skills/context-atlas/assets/manifest.json`
- Test: `tests/integration/test_initialization_safety.py`, `tests/unit/test_skill_package.py`

**Interfaces:** `initialize_from_assets(project_root: Path, project_name: str, assets_root: Path) -> Path`; no profile parameter. Existing-target refusal remains atomic and self-contained.

- [ ] **Step 1: Add a regression test** that passes no technology/profile selection and verifies a single `doc-<name>` target is produced.
- [ ] **Step 2: Run the test** and expose any current profile-driven branches.
- [ ] **Step 3: Remove profile selection and profile materialization from the initializer; copy only core assets and preserve the existing staging/validation/rename safety behavior.
- [ ] **Step 4: Synchronize packaged runtime assets and run initializer safety tests.**
- [ ] **Step 5: Commit** with `初始化：固定生成单一项目知识库`.

### Task 4: Replace language-split examples with shared-structure examples

**Files:**
- Modify: `scripts/generate_conformance_examples.py`
- Delete and recreate: `examples/`
- Modify: `tests/integration/test_golden_examples.py`, `tests/integration/test_initialization_safety.py`
- Modify: `tests/snapshots/expected-structures.json`

**Interfaces:** Generator creates `examples/single-stack/` and `examples/multi-stack/`; both call the same initializer and validator. Multi-stack records Spring Boot, Python, and frontend facts in one technology document.

- [ ] **Step 1: Change tests** to expect exactly the two example roots and identical core paths.
- [ ] **Step 2: Run integration tests** and confirm they fail while four language-split examples remain.
- [ ] **Step 3: Update the generator** to materialize only the two examples, remove profile overlays, and write stack facts as ordinary approved knowledge.
- [ ] **Step 4: Regenerate examples and snapshots; run all integration tests and verify no example contains adapter files or secrets.
- [ ] **Step 5: Commit** with `测试：改为单一模型的多技术栈黄金样例`.

### Task 5: Rebaseline project knowledge and acceptance evidence

**Files:**
- Modify: `doc-xiangmuzhishikumoban/03-实施与验收/CURRENT.md`
- Modify: `doc-xiangmuzhishikumoban/03-实施与验收/验收矩阵.md`
- Delete: `doc-xiangmuzhishikumoban/01-功能基线/F06-可选技术栈Profile.md`
- Modify: relevant F05/F01/F02 feature cards and evidence reports
- Modify: `TASK-KB-004-黄金样例与一致性测试.md`
- Modify: `docs/superpowers/plans/2026-08-10-agent-native-project-knowledge-base-mvp.md`

**Interfaces:** Current knowledge base must describe one canonical implementation path and no obsolete Profile acceptance rows.

- [ ] **Step 1: Add evidence references** for the two examples, exact commands, and deletion checks.
- [ ] **Step 2: Run the knowledge-base checker** and confirm all current links and acceptance rows resolve.
- [ ] **Step 3: Rewrite feature and architecture references** so technology stacks are facts, delete F06 acceptance rows and evidence, and remove F06 from feature indexes and dependency lists.
- [ ] **Step 4: Set CURRENT to the next executable self-host/MVP task and update acceptance status only from recorded evidence.
- [ ] **Step 5: Commit** with `基线：更新单知识库多技术栈验收`.

### Task 6: Full verification and final cleanup

**Files:**
- Test: `tests/`
- Inspect: all tracked Markdown, schemas, Skill assets, examples, and manifests.

- [ ] **Step 1: Run `py -m unittest discover -s tests -v`.**
- [ ] **Step 2: Run the asset sync check, project knowledge-base checker, and `git diff --check`.**
- [ ] **Step 3: Run `rg` to prove no obsolete Profile directories, language-split examples, or profile-selection instructions remain.
- [ ] **Step 4: Review `git status --short` and ensure generated outputs are intentional and no temporary files are tracked.
- [ ] **Step 5: Commit** with `验收：完成单知识库多技术栈清理`.
