# Project Knowledge Base Template Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** 创建一个可服务 frontend、Java、Python 等项目的通用知识库模板工程，并让该工程通过自己的知识库描述自身结构、规则和验收标准。

**Architecture:** `knowledge-base/` 是本项目自身的权威知识库；`template/` 是新项目复制骨架；`profiles/` 是技术栈扩展；`schemas/` 和 `scripts/` 负责结构检查；`skills/` 负责 AI 上下文读取规则。核心规则不可被 profile 放宽，只能增加约束。

**Tech Stack:** Markdown、受控 YAML Front Matter、Python 3 标准库检查器、unittest；不引入第三方运行时依赖。

## Global Constraints

- 所有项目必须保留项目目标、范围、边界、功能、架构、契约、ADR、任务、验收和证据追溯。
- 技术栈 profile 只能增加字段和验收项，不能修改核心状态流转、权威来源和验收证据规则。
- AI skill 只负责读取和上下文治理，不负责执行代码、不替代人工内容正确性评审。
- 检查器必须把结构完整性与内容正确性区分开；自动检查通过不等于业务内容已批准。
- `knowledge-base/` 必须是本模板项目的真实知识库，不得只放空目录或占位说明。

---

### Task 1: 创建项目骨架与自身知识库

**Files:**
- Create: `README.md`
- Create: `knowledge-base/README.md`
- Create: `knowledge-base/00-项目总览/项目目标与成功标准.md`
- Create: `knowledge-base/00-项目总览/产品能力地图.md`
- Create: `knowledge-base/00-项目总览/项目边界.md`
- Create: `knowledge-base/03-实施与验收/CURRENT.md`
- Create: `knowledge-base/03-实施与验收/验收矩阵.md`

**Interfaces:**
- Produces the authoritative project navigation and the initial no-executable-task state consumed by all later tasks.

- [ ] **Step 1: 写自身知识库的失败验收夹具**

Create a matrix row requiring the project README to reach the core model and profiles within three links, and a CURRENT row declaring no executable development task.

- [ ] **Step 2: 验证夹具当前不能通过**

Run `python scripts/check_knowledge_base.py knowledge-base` after Task 4 exists; before the checker exists, inspect the required paths manually and record the missing paths in the task report.

- [ ] **Step 3: 创建项目入口和自身知识文档**

The project README must link to `knowledge-base/README.md`, the template contract, all three profiles, schemas, checker and skill. `knowledge-base/README.md` must identify itself as the authority for this template project and state that no product implementation is claimed complete.

- [ ] **Step 4: 创建可恢复的 CURRENT 和验收矩阵**

CURRENT must say `当前任务：无可执行开发任务` and only list the next action as reviewing the template M0 decisions. The matrix must distinguish template-governance acceptance from future project-product acceptance.

- [ ] **Step 5: 验证文档导航**

Run a relative-link scan over `README.md` and `knowledge-base/`; every link must stay inside the project directory and point to an existing file.

- [ ] **Step 6: Commit**

Commit message: `docs: add template project knowledge base`

### Task 2: 定义核心 Schema、模板与状态规范

**Files:**
- Create: `schemas/feature.schema.yaml`
- Create: `schemas/task.schema.yaml`
- Create: `schemas/acceptance.schema.yaml`
- Create: `schemas/profile.schema.yaml`
- Create: `template/knowledge-base/README.md`
- Create: `template/knowledge-base/00-项目总览/README.md`
- Create: `template/knowledge-base/01-功能基线/README.md`
- Create: `template/knowledge-base/03-实施与验收/CURRENT.md`
- Create: `template/knowledge-base/03-实施与验收/验收矩阵.md`
- Create: `template/README.md`

**Interfaces:**
- `feature.schema.yaml` defines required fields `id,type,title,status,phase,priority,current_slice,depends_on,acceptance,contracts,adr,last_updated`.
- `task.schema.yaml` defines product and governance task identity, status, plan and non-empty unique acceptance declarations.
- `acceptance.schema.yaml` defines `not_started,partial,passed,not_applicable`; `passed` requires evidence and version.
- `profile.schema.yaml` defines additive profile fields and forbidden core-field overrides.

- [ ] **Step 1: 写 Schema 反例清单**

List invalid cases in `knowledge-base/05-开发指南/文档元数据规范.md`: missing acceptance, duplicate acceptance, illegal transition, unknown result state, passed without evidence/version and profile overriding core status.

- [ ] **Step 2: 固化核心 schema 和模板**

Use the same field names and controlled values in `schemas/` and `template/`; do not add language-specific fields to the core schemas.

- [ ] **Step 3: 写模板使用规则**

Document copy boundaries, required first edits, authority order, and how a project selects one or more profiles.

- [ ] **Step 4: 验证 Schema 与模板一致**

Run a script-level comparison that every required schema field appears in the corresponding template example and no template field contradicts the controlled enums.

- [ ] **Step 5: Commit**

Commit message: `docs: define core knowledge base schemas`

### Task 3: 创建 frontend、Java、Python 扩展包

**Files:**
- Create: `profiles/frontend/README.md`
- Create: `profiles/frontend/feature-card-template.md`
- Create: `profiles/frontend/acceptance-checklist.md`
- Create: `profiles/java/README.md`
- Create: `profiles/java/feature-card-template.md`
- Create: `profiles/java/acceptance-checklist.md`
- Create: `profiles/python/README.md`
- Create: `profiles/python/feature-card-template.md`
- Create: `profiles/python/acceptance-checklist.md`
- Modify: `knowledge-base/00-项目总览/产品能力地图.md`

**Interfaces:**
- Each profile declares `profile_id`, supported project types, additive required sections, default acceptance checks and excluded assumptions.
- Each profile links back to core schemas and explicitly states it cannot override core status, evidence or authority rules.

- [ ] **Step 1: 写 profile 合同反例**

Document examples of invalid profiles: changing `completed` semantics, removing core acceptance, or making a language tool mandatory without an explicit project decision.

- [ ] **Step 2: 写三套扩展内容**

Frontend covers Node/package manager/build/browser/E2E; Java covers JDK/build system/framework/dependency/CodeQL; Python covers interpreter/environment/package manager/framework/pytest/type checking.

- [ ] **Step 3: 写 profile 选择规则**

Allow one primary profile and optional secondary profiles; profile selection must be recorded in the project overview and cannot be inferred from a source file alone.

- [ ] **Step 4: 验证扩展只增加约束**

Check every profile contains links to core rules and has no alternate status or acceptance vocabulary.

- [ ] **Step 5: Commit**

Commit message: `docs: add frontend java python knowledge profiles`

### Task 4: 实现知识库检查器与测试

**Files:**
- Create: `scripts/check_knowledge_base.py`
- Create: `tests/test_check_knowledge_base.py`

**Interfaces:**
- `parse_front_matter(path: Path) -> dict[str, str | list[str]]`
- `validate(root: Path) -> list[Issue]`
- `main(argv: Sequence[str] | None = None) -> int`
- `Issue` contains `code`, `path` and `message`.

- [ ] **Step 1: 写失败测试**

Cover malformed metadata, duplicate IDs, invalid status transitions, missing/duplicate acceptance, broken links, profile core-field override, missing matrix rows, passed without evidence/version, missing CURRENT and Excalidraw/Obsidian workspace documents.

- [ ] **Step 2: 运行测试确认失败**

Run `python -m unittest tests.test_check_knowledge_base -v`; new behavior tests must fail for the expected missing validation, not because of test setup errors.

- [ ] **Step 3: 实现最小检查器**

Implement only standard-library parsing, metadata validation, relative-link validation, exact acceptance-matrix reconciliation, CURRENT state validation and profile additive-constraint validation.

- [ ] **Step 4: 运行全量测试**

Run `python -m unittest tests.test_check_knowledge_base -v` and require zero failures.

- [ ] **Step 5: 对真实自身知识库运行检查器**

Run `python scripts/check_knowledge_base.py knowledge-base`; expected output is `Knowledge base validation passed`.

- [ ] **Step 6: Commit**

Commit message: `test: enforce knowledge base governance rules`

### Task 5: 创建 AI 上下文 Skill 与多工具入口

**Files:**
- Create: `skills/project-knowledge-context/SKILL.md`
- Create: `AGENTS.md`
- Create: `CLAUDE.md`
- Create: `.github/copilot-instructions.md`
- Modify: `knowledge-base/05-开发指南/AI协作规则.md`

**Interfaces:**
- All adapters point to the same `knowledge-base/05-开发指南/AI协作规则.md`.
- The skill consumes `CURRENT`, project overview, selected profile, task package and linked acceptance items; it produces a context summary and unresolved-question list, not an execution plan implementation.

- [ ] **Step 1: 写 AI 入口失败场景**

Define expected behavior for no current task, current task with missing package, conflicting authority documents and missing acceptance evidence.

- [ ] **Step 2: 写正式 AI 协作规则和 skill**

Require AGENTS → README → AI rules → CURRENT → task package → linked feature/contract/acceptance order; prohibit deriving current requirements from archive or inventing missing decisions.

- [ ] **Step 3: 验证三个适配器一致**

Run `rg -n "knowledge-base/05-开发指南/AI协作规则.md" AGENTS.md CLAUDE.md .github/copilot-instructions.md skills/project-knowledge-context/SKILL.md` and require all adapters to point to one rule file.

- [ ] **Step 4: Commit**

Commit message: `docs: add AI knowledge context protocol`

### Task 6: 建立模板项目验收与发布说明

**Files:**
- Create: `knowledge-base/03-实施与验收/任务包/TASK-KB-001-模板知识库建设.md`
- Create: `knowledge-base/03-实施与验收/验收证据/KB-AC-01-10-模板验收报告.md`
- Create: `knowledge-base/04-决策记录/ADR-001-核心模型与技术栈扩展.md`
- Create: `knowledge-base/04-决策记录/README.md`
- Modify: `README.md`
- Modify: `knowledge-base/README.md`

**Interfaces:**
- `TASK-KB-001` closes only after the checker, links, adapters, schemas, profiles and context protocol pass; it does not claim any frontend/Java/Python product is complete.

- [ ] **Step 1: 写验收矩阵反例**

List missing core field, missing profile reference, broken adapter link, stale CURRENT and product-completion fabrication cases.

- [ ] **Step 2: 写任务包、ADR 和证据报告**

Record actual commands, paths, result counts and commit SHA; keep business/product acceptance at `not_started`.

- [ ] **Step 3: 运行最终验证**

Run `python -m unittest tests.test_check_knowledge_base -q`, `python scripts/check_knowledge_base.py knowledge-base`, `git diff --check`, and verify `git status --short` is clean within the new project.

- [ ] **Step 4: Commit**

Commit message: `docs: accept reusable knowledge base template`

