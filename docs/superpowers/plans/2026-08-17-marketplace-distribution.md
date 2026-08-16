# Marketplace Distribution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 Context Atlas 通过仓库内置 Marketplace 同时支持 Codex 和 Claude Code 的标准发现、安装和版本一致性校验。

**Architecture:** 保留现有双平台插件清单与唯一 `skills/context-atlas/`，新增 Codex 和 Claude Code 的仓库 Marketplace 索引。新增统一契约验证逻辑读取两个索引，检查索引、插件清单和 Skill 的身份、路径及发布边界；运行器和 README 使用 Marketplace 作为用户安装入口。

**Tech Stack:** JSON、Python 3 标准库、`unittest`、Codex CLI、Claude Code CLI、Markdown。

## Global Constraints

- 两个平台的插件名称必须为 `context-atlas`。
- 两个平台的版本必须相同并符合 SemVer。
- 两个平台必须引用同一仓库地址。
- 每个 Marketplace 条目必须包含插件名称、来源、安装策略、认证策略和分类。
- Marketplace 的插件来源路径必须是相对于索引文件的稳定路径。
- 正式插件发布物只包含平台清单、唯一 `skills/context-atlas/`、运行时资产和 Marketplace 索引。
- 不新增独立用户 CLI，不改变知识库初始化确认流程。

---

### Task 1: 扩展插件契约测试，先固定 Marketplace 行为

**Files:**
- Modify: `tests/unit/test_plugin_contract.py`
- Modify: `scripts/project_kb/plugin_contract.py`

**Interfaces:**
- Consumes: `.codex-plugin/plugin.json`、`.claude-plugin/plugin.json`、`.agents/plugins/marketplace.json`、`.claude-plugin/marketplace.json`。
- Produces: `load_marketplace_manifests(root: Path) -> tuple[dict[str, object], dict[str, object]]` 和 `validate_plugin_contract(root: Path) -> list[str]` 对 Marketplace 的确定性校验。

- [ ] **Step 1: 写失败测试**

在 `PluginContractTests` 中增加以下行为测试：

```python
def test_two_marketplaces_reference_the_same_plugin(self) -> None:
    codex_marketplace, claude_marketplace = load_marketplace_manifests(ROOT)
    self.assertEqual("context-atlas", codex_marketplace["plugins"][0]["name"])
    self.assertEqual("context-atlas", claude_marketplace["plugins"][0]["name"])
    self.assertEqual("./plugins/context-atlas", codex_marketplace["plugins"][0]["source"]["path"])
    self.assertEqual("./plugins/context-atlas", claude_marketplace["plugins"][0]["source"]["path"])

def test_repository_contract_requires_valid_marketplaces(self) -> None:
    self.assertEqual([], validate_plugin_contract(ROOT))
```

- [ ] **Step 2: 运行测试确认失败**

运行：

```powershell
py -m unittest tests.unit.test_plugin_contract
```

预期：由于两个 Marketplace 文件尚不存在，测试失败，失败原因必须指向 Marketplace 文件缺失或契约无法读取。

- [ ] **Step 3: 实现最小读取和校验接口**

在 `plugin_contract.py` 增加 JSON 对象读取函数和 `load_marketplace_manifests`，并在 `validate_plugin_contract` 中校验：

```python
required_marketplace_fields = {"name", "interface", "plugins"}
required_entry_fields = {"name", "source", "policy", "category"}
required_policy_fields = {"installation", "authentication"}
```

校验两个索引的第一条插件条目名称、来源路径、策略值、分类，并与两个插件清单的 `name`、`version`、`repository` 对齐；缺失、类型错误和 JSON 错误都返回可读的错误列表。

- [ ] **Step 4: 运行测试确认通过**

先只运行新增测试，确认在 Marketplace 文件尚未创建时仍按预期失败；该状态用于驱动下一任务创建发布物。完成 Task 2 后重新运行本任务测试确认全部通过。

- [ ] **Step 5: 提交测试与契约变更**

```powershell
git add tests/unit/test_plugin_contract.py scripts/project_kb/plugin_contract.py
git commit -m "test: 固定双平台 marketplace 契约"
```

### Task 2: 增加双平台 Marketplace 发布索引

**Files:**
- Create: `.agents/plugins/marketplace.json`
- Create: `.claude-plugin/marketplace.json`
- Modify: `tests/unit/test_plugin_contract.py`

**Interfaces:**
- Consumes: 现有 `.codex-plugin/plugin.json`、`.claude-plugin/plugin.json` 和 `skills/context-atlas/`。
- Produces: 两个可被平台 Marketplace 读取的索引，均将插件来源解析到 `./plugins/context-atlas`。

- [ ] **Step 1: 写发布物结构测试**

增加断言，验证每个索引包含非空 `name`、`interface.displayName`、`plugins`，且条目包含：

```python
{"name", "source", "policy", "category"}
```

策略必须是：

```python
{"installation": "AVAILABLE", "authentication": "ON_INSTALL"}
```

- [ ] **Step 2: 运行测试确认失败**

```powershell
py -m unittest tests.unit.test_plugin_contract.PluginContractTests.test_two_marketplaces_reference_the_same_plugin
```

预期：失败，因为索引文件尚不存在。

- [ ] **Step 3: 创建两个最小 Marketplace JSON**

两个文件都使用以下条目语义，并保持平台索引名称不同但插件条目一致：

```json
{
  "name": "context-atlas",
  "interface": {"displayName": "脉络地图"},
  "plugins": [
    {
      "name": "context-atlas",
      "source": {"source": "local", "path": "./plugins/context-atlas"},
      "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
      "category": "Productivity"
    }
  ]
}
```

索引相对于发布包根目录解析；发布包组装时把 `.codex-plugin` 或 `.claude-plugin` 和 `skills/` 放进 `plugins/context-atlas/`，不复制仓库开发入口和测试文件。

- [ ] **Step 4: 运行契约测试确认通过**

```powershell
py -m unittest tests.unit.test_plugin_contract
```

预期：插件契约测试全部通过。

- [ ] **Step 5: 提交 Marketplace 发布物**

```powershell
git add .agents/plugins/marketplace.json .claude-plugin/marketplace.json tests/unit/test_plugin_contract.py
git commit -m "feat: 增加双平台 marketplace 索引"
```

### Task 3: 增加发布包边界检查和平台验证

**Files:**
- Modify: `scripts/project_kb/plugin_contract.py`
- Modify: `tests/unit/test_plugin_contract.py`
- Modify: `scripts/agent_conformance/codex_runner.py`
- Modify: `scripts/agent_conformance/claude_runner.py`

**Interfaces:**
- Consumes: 两个平台 Marketplace 索引和插件目录。
- Produces: 发布包检查结果；Codex 运行器从仓库索引构造临时 Marketplace；Claude 运行器从仓库索引构造临时发布包并继续使用 `--plugin-dir` 做真实调用。

- [ ] **Step 1: 写失败测试**

增加一个临时目录测试：复制合法发布边界后校验通过，再加入 `AGENTS.md`、`.worktrees/old/skills/context-atlas/SKILL.md` 或第二份命名 Skill，确认 `validate_plugin_contract` 返回错误。

- [ ] **Step 2: 运行测试确认失败**

```powershell
py -m unittest tests.unit.test_plugin_contract.PluginContractTests.test_repository_contract_rejects_duplicate_or_development_files
```

预期：在边界检查尚未实现时失败。

- [ ] **Step 3: 实现边界和运行器接入**

让 Codex 运行器从 `.agents/plugins/marketplace.json` 读取条目并复制当前插件目录到临时 Marketplace 的 `plugins/context-atlas`；让 Claude 运行器创建只含 `.claude-plugin`、Marketplace 索引和唯一 `skills/` 的临时发布包。保留现有安全参数、临时主目录和不覆盖用户配置的行为。

- [ ] **Step 4: 运行静态和运行器测试**

```powershell
py -m unittest tests.unit.test_plugin_contract tests.unit.test_codex_runner tests.unit.test_claude_runner
```

预期：所有相关测试通过，且新增测试能识别开发文件和重复 Skill。

- [ ] **Step 5: 提交发布边界与运行器变更**

```powershell
git add scripts/project_kb/plugin_contract.py tests/unit/test_plugin_contract.py scripts/agent_conformance/codex_runner.py scripts/agent_conformance/claude_runner.py
git commit -m "test: 校验 marketplace 发布边界"
```

### Task 4: 编写用户安装与发布说明

**Files:**
- Modify: `README.md`
- Create: `docs/marketplace-installation.md`
- Modify: `doc-atlas/03-实施与验收/验收矩阵.md`

**Interfaces:**
- Consumes: 两个平台的 Marketplace 索引、插件清单和已验证命令。
- Produces: 用户可以按步骤添加仓库 Marketplace、安装插件、启动新会话并触发 Context Atlas；文档明确当前 Claude 真实行为验收边界。

- [ ] **Step 1: 写文档验收检查**

增加一个静态测试或脚本检查，确认 README 和安装文档包含：`/plugins`、`context-atlas`、Marketplace 来源、Claude 安装命令、新会话提示、确认后再初始化说明。

- [ ] **Step 2: 运行检查确认失败**

```powershell
py -m unittest tests.unit.test_plugin_contract
```

预期：文档检查在新安装章节尚不存在时失败；若现有测试框架不适合文档断言，则在本任务中增加一个小型 `scripts/check_plugin_docs.py` 并由单元测试调用。

- [ ] **Step 3: 编写安装说明**

README 只保留简短入口，详细文档说明：

```text
Codex: 添加仓库 Marketplace → /plugins → 安装 context-atlas → 新会话
Claude Code: 添加仓库 Marketplace → 安装 context-atlas → 新会话
```

同时说明仓库当前不是 Python 包、不需要 `pip install`，以及目标项目中自然语言初始化仍需用户确认 Proposal。

- [ ] **Step 4: 更新验收矩阵**

新增一个 Marketplace 验收项，证据指向安装文档、契约测试和双平台发布级运行报告；不把 Claude 尚未通过的确认后真实初始化误标为 passed。

- [ ] **Step 5: 运行文档和契约检查**

```powershell
py -m unittest tests.unit.test_plugin_contract
git diff --check
```

- [ ] **Step 6: 提交用户文档**

```powershell
git add README.md docs/marketplace-installation.md doc-atlas/03-实施与验收/验收矩阵.md
git commit -m "docs: 补充 marketplace 安装说明"
```

### Task 5: 全量验证和发布级报告

**Files:**
- Modify: `doc-atlas/03-实施与验收/验收证据/跨Agent执行一致性与Claude验收.md`
- Create: `scripts/marketplace/` only if a reusable packaging helper is required by Tasks 2–4

**Interfaces:**
- Consumes: 双平台索引、插件契约、运行器和安装文档。
- Produces: 可复现的全量验证结果和明确的 passed/partial 状态。

- [ ] **Step 1: 运行完整确定性验证**

```powershell
py -m unittest discover -s tests -p "test_*.py"
py scripts/sync_skill_assets.py --check
py scripts/check_rule_coverage.py --root .
py scripts/check_python_documentation.py --root .
py scripts/check_knowledge_base.py examples/single-stack --schema-root schemas
py scripts/check_knowledge_base.py examples/multi-stack --schema-root schemas
py scripts/check_knowledge_base.py doc-atlas --schema-root schemas
git diff --check
```

- [ ] **Step 2: 运行 Codex 和 Claude 发布级场景**

```powershell
py scripts/run_agent_conformance.py --agent codex --plugin-root . --output .agent-conformance-runs/codex-marketplace.json
py scripts/run_agent_conformance.py --agent claude --plugin-root . --output .agent-conformance-runs/claude-marketplace.json
py scripts/run_agent_conformance.py --compare .agent-conformance-runs/claude-marketplace.json .agent-conformance-runs/codex-marketplace.json
```

记录两个平台的安装发现、确认前零写入、已有目标防覆盖和确认后初始化结果；如果 Claude 确认后仍未落盘，验收项保持 `partial`。

- [ ] **Step 3: 更新验收证据并核对状态**

在证据文档中记录命令、版本、退出码和文件变化，区分 Marketplace 静态契约通过与真实 Agent 行为通过，不用静态结果替代真实行为证据。

- [ ] **Step 4: 提交最终验证证据**

```powershell
git add doc-atlas/03-实施与验收/验收证据/跨Agent执行一致性与Claude验收.md
git commit -m "test: 记录双平台 marketplace 验证"
```

## Self-review checklist

- 设计中的两个 Marketplace 索引由 Task 2 覆盖。
- 双平台身份、策略、路径和唯一 Skill 由 Task 1–3 覆盖。
- 用户安装说明由 Task 4 覆盖。
- 全量测试和 Claude 的已知 partial 边界由 Task 5 覆盖。
- 计划未引入独立 CLI、第三方 Python 依赖或第二份 Skill。
