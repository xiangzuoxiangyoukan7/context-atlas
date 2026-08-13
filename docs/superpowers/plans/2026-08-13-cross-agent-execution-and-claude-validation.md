# 跨 Agent 执行一致性与 Claude Code 验收实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 Codex 与 Claude Code 加载同一份 `context-atlas` Skill，并用确定性检查和真实 Agent 黑盒场景证明 Claude Code 遵守提案、确认、防覆盖、初始化和结果报告契约。

**Architecture:** 平台清单只负责让 Agent 发现共享 Skill；Skill 只负责工作流和判断；模板物化及结构检查继续由仓库内 Python 标准库工具确定性执行。静态测试、确定性集成测试和真实 Claude Code 黑盒验收分别证明“包正确”“工具正确”“Agent 实际行为正确”，任何一层都不能代替另一层。

**Tech Stack:** Python 3 标准库、`unittest`、Markdown、JSON、Claude Code 2.1.226 或兼容版本、Codex CLI、PowerShell、Git。

## Global Constraints

- 设计依据为 `docs/superpowers/specs/2026-08-12-context-atlas-future-direction-design.md` 中 DIR-002、DIR-006、DIR-022～026、DIR-031、DIR-033、DIR-035、DIR-036、DIR-038、DIR-039。
- 第一版正式支持 Codex 与 Claude Code；两个平台共享唯一 `skills/context-atlas/`，不得复制或派生 Claude 专属 Skill 正文。
- 目标项目不得由本产品生成或维护 `AGENTS.md`、`CLAUDE.md`；平台入口由各 Agent 自己负责。
- 模型是否自动触发 Skill 不是正确性证明；发布验收必须包含显式调用和自然语言自动触发两类场景。
- 钩子只能作为提醒和可观测性增强，不能成为正确性的唯一门禁；平台禁用钩子时，核心初始化、更新和检查流程仍必须可用。
- 未获得用户明确确认前不得创建或修改正式知识基线；真实 Agent 黑盒测试必须证明这一点。
- 真实 Agent 测试只能在自动创建的临时项目中写文件，禁止对本仓库工作区执行生成式写入。
- 真实 Agent 输出具有非确定性；验收比较结构、状态、关系和行为不变量，不比较自然语言逐字一致。
- Context Atlas 不控制用户或其他插件能否执行代码任务；`CURRENT.md` 和 `TASK-*` 不得成为执行门禁，只有正式知识库写入仍受提案、确认和验证约束。
- 全量单元/集成测试不依赖模型账号和网络；真实 Claude/Codex 验收作为发布门禁单独执行并保存脱敏证据。
- 根目录 `schemas/`、`scripts/`、`templates/` 是规范源；Skill 内置副本只能由 `scripts/sync_skill_assets.py` 同步。
- 本计划只建立跨 Agent 执行与验收骨架，并验证当前已有的初始化、确认、防覆盖和检查能力；DIR-039 人员模型、完整关系目录、数据库新模型和主动知识捕获分别进入后续实施计划。

---

### Task 1: 建立跨 Agent 验收治理记录

**Files:**
- Create: `doc-atlas/03-实施与验收/任务包/TASK-KB-006-跨Agent执行一致性与Claude验收.md`
- Modify: `doc-atlas/01-功能基线/F01-Agent驱动的知识库初始化.md`
- Modify: `doc-atlas/01-功能基线/F02-AI知识采集与确认.md`
- Modify: `doc-atlas/03-实施与验收/验收矩阵.md`
- Create: `tests/unit/test_cross_agent_governance.py`

**Interfaces:**
- Consumes: 已确认的未来方向设计和本实施计划。
- Produces: 可追溯的实施记录 `TASK-KB-006`；验收项 `KB-AC-26`～`KB-AC-29`。该任务包不限制其他插件或用户任务的执行。

- [ ] **Step 1: 写入治理任务失败测试**

在 `tests/unit/test_cross_agent_governance.py` 中创建测试，读取任务包、F01、F02 和验收矩阵，并断言：任务包引用本计划且明确“不构成执行许可证”；矩阵存在 `KB-AC-26`～`KB-AC-29` 且初始状态均为 `not_started`。

- [ ] **Step 2: 运行测试并确认失败**

```powershell
py -m unittest tests.unit.test_cross_agent_governance -v
```

Expected: FAIL，原因是实施记录和四个验收项尚不存在。

- [ ] **Step 3: 写入任务包和验收边界**

四个验收项使用以下固定含义：

```markdown
| KB-AC-26 | 跨 Agent 插件 | Codex 与 Claude Code 平台清单有效并指向同一份 context-atlas Skill。 | not_started | — | — |
| KB-AC-27 | Claude 执行契约 | Claude Code 未确认时不写正式知识，确认后才执行初始化或更新。 | not_started | — | — |
| KB-AC-28 | 确定性结果 | Claude Code 产物通过内置检查器，防覆盖和错误定位场景符合契约。 | not_started | — | — |
| KB-AC-29 | 跨 Agent 一致性 | Codex 与 Claude Code 对同一场景满足相同的结构和行为不变量。 | not_started | — | — |
```

F01 增加“两个正式支持平台加载同一 Skill”的范围和验收引用；F02 增加“真实 Agent 两阶段确认”的范围和验收引用。不要把已有 `partial` 行提前改成 `passed`。

- [ ] **Step 4: 验证并提交治理变更**

```powershell
py -m unittest tests.unit.test_cross_agent_governance -v
py scripts/check_knowledge_base.py doc-atlas --schema-root schemas
git diff --check
git add -- doc-atlas tests/unit/test_cross_agent_governance.py
git commit -m "治理：启动跨 Agent 执行一致性验收"
```

---

### Task 2: 添加双平台薄清单和静态一致性检查

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.codex-plugin/plugin.json`
- Create: `scripts/project_kb/plugin_contract.py`
- Create: `tests/unit/test_plugin_contract.py`
- Modify: `tests/unit/test_skill_package.py`

**Interfaces:**
- Produces: `load_plugin_manifests(root: Path) -> tuple[dict[str, object], dict[str, object]]`；`validate_plugin_contract(root: Path) -> list[str]`。
- Invariants: 两个清单的 `name`、`version`、`description`、`author.name` 必须一致；名称固定为 `context-atlas`；Skill 路径只能指向 `./skills/`；不得存在第二份 Claude/Codex 专属 Skill。

- [ ] **Step 1: 写失败测试**

`tests/unit/test_plugin_contract.py` 至少覆盖：两个清单存在且为 JSON；共同字段一致；`skills/context-atlas/SKILL.md` 是唯一同名 Skill；Claude 清单只使用 Claude 支持字段；Codex 清单包含合法 `interface`；版本为严格三段语义版本。

- [ ] **Step 2: 运行测试并确认失败**

```powershell
py -m unittest tests.unit.test_plugin_contract tests.unit.test_skill_package -v
```

Expected: FAIL，原因是平台清单和检查模块不存在。

- [ ] **Step 3: 创建最小平台清单**

Claude 清单使用：

```json
{
  "name": "context-atlas",
  "version": "0.1.0",
  "description": "通过统一协议初始化、维护和验证项目知识库",
  "author": {"name": "Context Atlas Maintainers"},
  "skills": "./skills/"
}
```

Codex 清单使用相同共同字段，并增加：

```json
"interface": {
  "displayName": "脉络地图",
  "shortDescription": "初始化、维护和验证项目知识库",
  "longDescription": "通过统一 Skill、模板、Schema 和确定性检查器维护可追溯的项目知识库。",
  "developerName": "Context Atlas Maintainers",
  "category": "Productivity",
  "capabilities": ["Interactive", "Write"],
  "defaultPrompt": ["检查当前项目知识库并报告缺失内容。"]
}
```

不得在 Codex 清单中声明 `hooks`；不得在 `.claude-plugin/` 内复制 `skills/`。

- [ ] **Step 4: 实现仓库内共同字段检查器**

`validate_plugin_contract` 返回中文错误字符串，不直接退出进程。检查 JSON 对象类型、共同字段、语义版本、相对安全路径和唯一 Skill 路径，供单元测试和后续发布检查复用。

- [ ] **Step 5: 使用平台工具验证并提交**

```powershell
claude plugin validate . --strict
py -m unittest tests.unit.test_plugin_contract tests.unit.test_skill_package -v
git diff --check
git add -- .claude-plugin .codex-plugin scripts/project_kb/plugin_contract.py tests/unit/test_plugin_contract.py tests/unit/test_skill_package.py
git commit -m "插件：添加 Codex 与 Claude Code 共享 Skill 清单"
```

Expected: Claude 官方验证输出 `Validation passed`；仓库测试全部通过。

---

### Task 3: 把共享 Skill 收敛为可验证的执行状态机

**Files:**
- Modify: `skills/context-atlas/SKILL.md`
- Create: `skills/context-atlas/references/执行状态机.md`
- Modify: `skills/context-atlas/references/知识采集与确认.md`
- Modify: `skills/context-atlas/references/验证与结果报告.md`
- Modify: `tests/unit/test_skill_package.py`

**Interfaces:**
- Produces: 平台无关状态 `inspect -> propose -> await_confirmation -> apply -> validate -> report`。
- Gate: `await_confirmation` 没有当前 Proposal 的显式确认时，禁止进入 `apply`。
- Failure: 目标已存在时从 `inspect` 转入更新流程，不调用初始化器。

- [ ] **Step 1: 写失败测试**

在 `test_skill_package.py` 中断言共享 Skill 引用 `references/执行状态机.md`，状态机包含六个固定状态；确认门禁明确要求 `proposal_revision == confirmed_revision`；报告包含操作方、确认方、目标文件、检查命令、退出码和未决项。

- [ ] **Step 2: 运行测试并确认失败**

```powershell
py -m unittest tests.unit.test_skill_package -v
```

Expected: FAIL，原因是状态机引用及固定字段不存在。

- [ ] **Step 3: 编写平台无关状态机**

状态转换必须使用下表，不写 Claude 或 Codex 专属分支：

```markdown
| 当前状态 | 进入下一状态的条件 | 下一状态 |
| inspect | 已完成只读检查并区分事实、推测、未知和冲突 | propose |
| propose | 已展示目标路径、实质变化、来源、影响和提案修订号 | await_confirmation |
| await_confirmation | 用户明确确认当前提案修订号 | apply |
| apply | 仅完成已确认范围的文件操作 | validate |
| validate | 内置检查器退出码为 0 | report |
| validate | 检查失败 | propose，不得宣称完成 |
```

任何 Agent 都必须报告自己是 `operated_by`，不能把自己记录成 `confirmed_by`。

- [ ] **Step 4: 验证并提交**

```powershell
py -m unittest tests.unit.test_skill_package -v
claude plugin validate . --strict
git diff --check
git add -- skills/context-atlas tests/unit/test_skill_package.py
git commit -m "协议：统一跨 Agent 执行状态机"
```

---

### Task 4: 提供仅供 Agent 调用的确定性操作入口

**Files:**
- Create: `scripts/agent_kb_operation.py`
- Create: `scripts/project_kb/agent_operation.py`
- Create: `tests/unit/test_agent_operation.py`
- Modify: `skills/context-atlas/assets/manifest.json`
- Modify by synchronization: `skills/context-atlas/assets/scripts/agent_kb_operation.py`
- Modify by synchronization: `skills/context-atlas/assets/scripts/project_kb/agent_operation.py`

**Interfaces:**
- Produces: `execute_initialize(project_root: Path, project_name: str | None, proposal_revision: str, confirmed_revision: str, assets_root: Path) -> OperationReport`。
- `OperationReport`: `operation`、`target`、`changed_files`、`validator_exit_code`、`issues`。
- 该入口不是面向用户的交互式 CLI；不提问、不调用模型，只执行 Agent 已经确认的结构化操作。

- [ ] **Step 1: 写失败测试**

覆盖：修订号不一致拒绝且零写入；目标已存在拒绝且哨兵文件不变；相同修订号时调用现有 `initialize_from_assets`；初始化后自动使用目标内置检查器验证；报告不包含邮箱、令牌和完整会话文本。

- [ ] **Step 2: 运行测试并确认失败**

```powershell
py -m unittest tests.unit.test_agent_operation -v
```

Expected: FAIL，原因是 `agent_operation` 不存在。

- [ ] **Step 3: 实现最小确定性入口**

核心门禁必须先于任何目录创建：

```python
if not proposal_revision or proposal_revision != confirmed_revision:
    raise PermissionError("confirmed revision does not match current proposal")
```

随后调用现有 `initialize_from_assets`，再调用 `validate`。检查失败时返回问题并保留产物供诊断，但退出码非 0，Agent 不得报告成功。

- [ ] **Step 4: 同步 Skill 资产并验证**

```powershell
py scripts/sync_skill_assets.py
py -m unittest tests.unit.test_agent_operation tests.unit.test_skill_package tests.integration.test_initialization_safety -v
py scripts/sync_skill_assets.py --check
git diff --check
git add -- scripts tests/unit/test_agent_operation.py skills/context-atlas/assets
git commit -m "工具：增加 Agent 确认门禁操作入口"
```

---

### Task 5: 建立不依赖真实模型的跨 Agent 场景断言器

**Files:**
- Create: `scripts/agent_conformance/__init__.py`
- Create: `scripts/agent_conformance/model.py`
- Create: `scripts/agent_conformance/assertions.py`
- Create: `tests/unit/test_agent_conformance.py`
- Create: `tests/agent_conformance/scenarios.json`

**Interfaces:**
- `ScenarioResult(workspace: Path, before: set[str], after: set[str], messages: list[str], command_exit_codes: list[int])`。
- `assert_no_formal_write_before_confirmation(result) -> list[str]`。
- `assert_existing_target_preserved(result, sentinel_sha256: str) -> list[str]`。
- `assert_valid_initialized_target(result, expected_name: str) -> list[str]`。

- [ ] **Step 1: 写断言器失败测试**

使用手工构造的通过/失败结果覆盖三条核心不变量：未确认零正式写入；已有目标不覆盖；确认后产生自包含目标并通过内置检查器。测试不得调用 Claude 或 Codex。

- [ ] **Step 2: 运行测试并确认失败**

```powershell
py -m unittest tests.unit.test_agent_conformance -v
```

Expected: FAIL，原因是场景模型和断言器不存在。

- [ ] **Step 3: 实现确定性断言器和场景目录**

`scenarios.json` 至少声明：`initialize_requires_confirmation`、`initialize_after_confirmation`、`existing_target_is_preserved`、`natural_language_triggers_skill`。断言只读取临时目录差异、内置检查器退出码和结构化运行记录，不根据模型自述判断通过。

- [ ] **Step 4: 验证并提交**

```powershell
py -m unittest tests.unit.test_agent_conformance -v
git diff --check
git add -- scripts/agent_conformance tests/unit/test_agent_conformance.py tests/agent_conformance/scenarios.json
git commit -m "验收：建立跨 Agent 行为不变量断言"
```

---

### Task 6: 实现真实 Claude Code 黑盒运行器

**Files:**
- Create: `scripts/run_agent_conformance.py`
- Create: `scripts/agent_conformance/claude_runner.py`
- Create: `tests/unit/test_claude_runner.py`
- Create at runtime, ignored: `.agent-conformance-runs/`
- Modify: `.gitignore`

**Interfaces:**
- `ClaudeRunner.run_turn(workspace: Path, prompt: str, resume_session_id: str | None) -> AgentTurn`。
- 命令固定使用当前仓库绝对路径作为 `--plugin-dir`，目标工作目录使用临时目录。
- `AgentTurn`: `session_id`、`exit_code`、`result_text`、`structured_output`、`stderr`、`started_at`、`finished_at`。

- [ ] **Step 1: 用假进程写运行器失败测试**

测试命令参数必须包含：`--bare -p --plugin-dir <repo> --permission-mode acceptEdits --output-format json --no-session-persistence`；禁止 `bypassPermissions`；第二轮使用第一轮返回的 session ID。因为续接会话需要持久化，实际两阶段场景不得添加 `--no-session-persistence`，单轮场景才添加；测试必须分别覆盖两种命令。

- [ ] **Step 2: 运行测试并确认失败**

```powershell
py -m unittest tests.unit.test_claude_runner -v
```

Expected: FAIL，原因是运行器不存在。

- [ ] **Step 3: 实现 JSON 输出解析和脱敏证据**

运行器使用 `subprocess.run(..., cwd=workspace, capture_output=True, text=True, timeout=300)`；解析 Claude JSON 的 `session_id` 和 `result`。保存证据前删除完整用户目录、认证字段、环境变量、邮箱和未经脱敏的会话正文，只保留场景 ID、平台版本、命令参数白名单、退出码、结构断言和文件摘要。

- [ ] **Step 4: 实现两阶段真实场景**

第一轮显式调用 `/context-atlas:context-atlas`，要求初始化知识库但不确认任何 Proposal；断言目标目录不存在。第二轮续接同一 session，明确确认上一轮提案修订；断言目标目录存在且内置检查器退出码为 0。另起临时项目测试已有目标哨兵文件不变化。自然语言场景不显式写 Skill 名称，用于验证自动触发，但自动触发失败只阻止“正式支持”标记，不影响显式调用诊断结果。

- [ ] **Step 5: 在本机执行真实 Claude 验收**

```powershell
claude --version
claude plugin validate . --strict
py scripts/run_agent_conformance.py --agent claude --plugin-root . --output .agent-conformance-runs/claude.json
```

Expected: 四个场景全部通过；当前基线记录 Claude Code `2.1.226`。如果未认证、模型不可用或网络失败，结果必须是 `blocked`，不能记为通过。

- [ ] **Step 6: 提交运行器，不提交原始会话**

```powershell
py -m unittest tests.unit.test_claude_runner tests.unit.test_agent_conformance -v
git diff --check
git add -- scripts/run_agent_conformance.py scripts/agent_conformance tests/unit/test_claude_runner.py .gitignore
git commit -m "验收：增加 Claude Code 真实行为运行器"
```

---

### Task 7: 增加 Codex 对照运行并比较平台不变量

**Files:**
- Create: `scripts/agent_conformance/codex_runner.py`
- Create: `tests/unit/test_codex_runner.py`
- Modify: `scripts/run_agent_conformance.py`
- Modify: `scripts/agent_conformance/assertions.py`

**Interfaces:**
- `CodexRunner.run_turn(workspace: Path, prompt: str, resume_session_id: str | None) -> AgentTurn`。
- `compare_invariants(claude_report: dict, codex_report: dict) -> list[str]` 比较场景状态、结构摘要、检查器退出码和防覆盖结果，不比较自然语言。

- [ ] **Step 1: 写 Codex 命令和平台比较失败测试**

Codex 命令使用临时 `CODEX_HOME` 安装仓库插件后运行 `codex exec --ephemeral -s workspace-write --json -C <temp-project>`；禁止危险跳过审批参数。测试用伪报告证明任一平台未确认写入、覆盖已有目标或检查失败时，跨平台结果失败。

- [ ] **Step 2: 运行测试并确认失败**

```powershell
py -m unittest tests.unit.test_codex_runner tests.unit.test_agent_conformance -v
```

- [ ] **Step 3: 实现 Codex 运行器与归一化比较**

安装、执行和清理都限定在测试临时目录；不得改写用户真实 Codex 配置。Codex 和 Claude 使用同一个 `scenarios.json`、同一组断言函数和同一个仓库 Skill。

- [ ] **Step 4: 执行真实对照验收**

```powershell
py scripts/run_agent_conformance.py --agent claude --plugin-root . --output .agent-conformance-runs/claude.json
py scripts/run_agent_conformance.py --agent codex --plugin-root . --output .agent-conformance-runs/codex.json
py scripts/run_agent_conformance.py --compare .agent-conformance-runs/claude.json .agent-conformance-runs/codex.json
```

Expected: 两个平台四个场景满足相同不变量。模型措辞和调用次数可以不同。

- [ ] **Step 5: 验证并提交**

```powershell
py -m unittest tests.unit.test_codex_runner tests.unit.test_claude_runner tests.unit.test_agent_conformance -v
git diff --check
git add -- scripts/agent_conformance scripts/run_agent_conformance.py tests/unit/test_codex_runner.py
git commit -m "验收：增加 Codex 跨平台对照运行"
```

---

### Task 8: 全量验证、记录证据并关闭任务

**Files:**
- Create: `doc-atlas/03-实施与验收/验收证据/跨Agent执行一致性与Claude验收.md`
- Modify: `doc-atlas/03-实施与验收/验收矩阵.md`
- Modify: `doc-atlas/03-实施与验收/任务包/TASK-KB-006-跨Agent执行一致性与Claude验收.md`
- Inspect: Tasks 1～7 的全部变更和脱敏运行报告。

**Interfaces:**
- Consumes: 静态包验证、完整 Python 测试、真实 Claude/Codex 场景报告。
- Produces: `KB-AC-26`～`KB-AC-29` 可复现证据；只有四项均有证据时才关闭 `TASK-KB-006`。

- [ ] **Step 1: 运行全部确定性检查**

```powershell
py -m unittest discover -s tests -v
py scripts/sync_skill_assets.py --check
claude plugin validate . --strict
py scripts/check_knowledge_base.py examples/single-stack --schema-root schemas
py scripts/check_knowledge_base.py examples/multi-stack --schema-root schemas
py scripts/check_knowledge_base.py doc-atlas --schema-root schemas
git diff --check
```

- [ ] **Step 2: 重新运行发布级真实 Agent 验收**

```powershell
py scripts/run_agent_conformance.py --agent claude --plugin-root . --output .agent-conformance-runs/claude-release.json
py scripts/run_agent_conformance.py --agent codex --plugin-root . --output .agent-conformance-runs/codex-release.json
py scripts/run_agent_conformance.py --compare .agent-conformance-runs/claude-release.json .agent-conformance-runs/codex-release.json
```

Expected: 所有场景通过。只要某个平台因认证、版本、网络、权限或行为失败，就保持对应验收项 `partial` 或 `blocked`，不得用静态测试替代。

- [ ] **Step 3: 写入脱敏验收证据**

证据必须包含：插件版本、Claude/Codex 版本、场景 ID、每个不变量的实际结果、检查器退出码、产物结构摘要、执行日期和实现提交；明确声明“结构与行为契约通过不等于业务内容真实”。不得提交原始模型会话、认证信息或临时项目。

- [ ] **Step 4: 根据证据更新状态**

只有真实 Claude 两阶段确认通过后，才能将 `KB-AC-27` 标记 `passed`；只有目标内置检查器和防覆盖场景通过后，才能将 `KB-AC-28` 标记 `passed`；只有两个平台真实报告比较通过后，才能将 `KB-AC-29` 标记 `passed`。

- [ ] **Step 5: 最终验证并提交治理关闭记录**

```powershell
py scripts/check_knowledge_base.py doc-atlas --schema-root schemas
git diff --check
git status --short
git add -- doc-atlas/03-实施与验收
git commit -m "验收：完成跨 Agent 执行一致性验证"
```

关闭任务包只表示该实施记录完成，不声明其他插件或项目是否存在可执行任务，也不创建全局唯一下一动作。
