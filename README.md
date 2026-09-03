# 脉络地图（Context Atlas）

Context Atlas 是面向长期项目协作的知识治理插件，支持 Codex、Claude Code 和 Qoder。它把需求、架构、接口、数据库、决策、变更和验收证据整理为项目内唯一的 `doc-<项目名>/` 知识库，让不同 Agent 读取同一套可确认、可追溯的事实。

当前源码清单版本为 `0.17.1`。源码版本不等于 Marketplace 实际安装版本；安装或升级后请以宿主显示的版本为准。

## 它解决什么问题

Context Atlas 用于解决以下问题：

- 项目事实散落在 README、源码、Issue、会议记录和对话中；
- 不同 Agent 对范围、约束和当前实现理解不一致；
- AI 推测、仓库观察和已批准事实混在一起；
- 知识变化没有来源、确认、版本、影响和验收证据；
- 更换 Agent 后需要重新解释项目背景。

它不负责开发任务调度，也不替代 Issue、OpenSpec、Superpowers、测试工具或人工验收。它只为这些工作提供经过治理的项目知识。

## 工作方式

Context Atlas 采用“一主多适配”架构：核心 Skill、协议、模板、Schema 和 Python 执行器只有一份，各宿主只维护安装入口和平台清单。

正式知识写入统一遵循：

```text
inspect → propose → await_confirmation → apply → validate → report
```

Agent 调研并展示 Proposal，用户确认精确的 `proposal_revision`，确定性执行器才会写入并验证。普通自然语言、外部任务完成状态、测试通过或检查器通过，都不能代替用户确认。

项目中只维护一套知识库：

```text
业务仓库/
├─ AGENTS.md 或 CLAUDE.md
└─ doc-<项目名>/
   ├─ README.md
   ├─ knowledge-base.yaml
   ├─ Clippings/
   ├─ .project-kb/
   ├─ 00-项目总览/
   ├─ 01-功能基线/
   ├─ 02-技术基线/
   ├─ 03-变更与证据/
   ├─ 05-知识治理/
   └─ 90-历史归档/
```

Codex 和 Qoder 使用 `AGENTS.md`，Claude Code 使用 `CLAUDE.md`；这些入口都指向同一个知识库。初始化只维护 Context Atlas 受管区块，不覆盖项目已有说明。

## 安装

Context Atlas 是 Agent 插件，不是 Python 包，不使用 `pip install`。完整的安装、升级、卸载、内外网源和版本核验步骤见 [Marketplace 安装与使用](./packaging/marketplace-installation.md)。

三个平台的安装范围不同：

| 平台 | 安装模型 | 项目隔离方式 |
| --- | --- | --- |
| Codex | 用户级共享安装 | 受信任项目的 `.codex/config.toml` 启用插件 |
| Claude Code | 原生 project scope | `.claude/settings.json` |
| Qoder | 原生 Project scope | 插件管理界面的 Project 范围 |

Codex 不要把 `CODEX_HOME` 指向项目 `.codex/`，否则沙箱、缓存、会话和数据库会在每个项目中重复生成。插件实体应保存在用户级 `CODEX_HOME`，项目只保存启用配置和自己的知识库。

安装或升级后请新建 Agent 会话，并确认九个 Skill 全部可见。

## Skill 职责

| Skill | 职责 | 调用与写入 |
| --- | --- | --- |
| `context-atlas-work` | 开发目标总入口；混合 add、revise、retire Proposal 的唯一编排者 | 可自动选择；精确确认后才写正式知识 |
| `context-atlas-init` | 创建项目的第一套知识库 | 必须显式调用；已有知识库时拒绝初始化 |
| `context-atlas-navigate` | 渐进查询目录、邻居和有边界的关系图 | 只读，可自动选择 |
| `context-atlas-review` | 审查规格质量、交付就绪度和知识健康 | 只读，可自动选择 |
| `context-atlas-ingest` | 摄取一个或有限批次来源并生成维护候选 | 必须显式调用；不写正式知识 |
| `context-atlas-add` | 新增此前不存在的稳定知识身份 | 必须显式调用；只处理 add-only Proposal |
| `context-atlas-revise` | 修订现有知识或建立明确后继项 | 必须显式调用；只处理 revise-only Proposal |
| `context-atlas-retire` | 无后继撤销当前权威，或归档已替代知识 | 必须显式调用；只处理 retire-only Proposal |
| `context-atlas-upgrade` | 升级知识库格式和物理结构 | 不得改变项目事实或批准状态 |

`context-atlas-work` 被自动选择后，只有用户明确选择“先建立知识基线”路径，它才可以组织维护 Proposal；初始开发请求仍不构成写入确认。用户确认当前 Proposal 后，不需要再次逐个调用底层维护 Skill。

## 常用场景

### 新项目初始化

1. 在目标业务仓库安装并启用插件。
2. 显式调用 `context-atlas-init`。
3. 选择 `standard` 或 `obsidian` 工作区模式。
4. 审阅目标、事实、来源、未知项、冲突、关系和验证计划。
5. 确认精确 Proposal 修订后初始化。
6. 检查结构验证及 `children`、`neighbors`、bounded `graph` 冒烟结果。

已有 `doc-*` 知识库时不得再次初始化，应使用新增、修订、退役或格式升级流程。存在多个候选知识库时必须先由用户指定当前权威。

### 开发新功能或修改现有功能

优先使用 `context-atlas-work`：

```text
定位相关知识 → 审查范围与验收 → 选择是否先建立知识基线
→ 开发与验证 → 核对实现差异 → 按需修订知识与验收证据
```

新稳定身份归入 `add`；修改现有身份或创建后继项归入 `revise`；无后继撤销或归档归入 `retire`。一个任务同时包含多类维护时，由 `work` 生成一个原子 Proposal。

### 排查问题

- 用 `navigate` 定位相关功能、模块、接口、数据库和验收项；
- 将日志、当前环境观察和假设与已批准知识分开；
- 一次性日志和未验证猜测留在任务上下文；
- 只有经过验证、可复用且具有长期价值的结论才进入维护 Proposal；
- 修复结果、知识结构验证和业务确认分别报告。

### 摄取外部资料

显式调用 `context-atlas-ingest` 处理网页、文档、Issue、会议纪要或 `Clippings/`。摄取只生成 `add | revise | retire | conflict | ignore` 候选，不批准事实，也不直接调用维护 Skill。

## 知识治理边界

### 可以进入正式知识库

- 项目目标、范围、术语、需求和功能；
- 架构、模块、接口、数据库、数据资产和外部依赖；
- 归属于需求、功能、技术或治理文档的决策依据、规格变化、内嵌验收场景、验收结果和实际证据；
- 来源、关系、未知项、冲突和替代关系。

### 不进入正式知识库

- 没有长期价值的日志和命令输出；
- 未验证的排查猜测；
- 普通对话查询结果；
- 外部任务的调度状态本身；
- 密码、Token、私钥和未脱敏个人数据；
- 未经确认的 Proposal；
- 只能从历史归档推导出的当前结论。

### 事实与来源

仓库观察、用户陈述、外部来源和 AI 推测必须分别标记。AI 推测只能作为待确认假设；发现冲突时保留竞争值、来源和待裁决问题，不能自行选择看起来更合理的内容。

正式知识使用 Markdown 和 YAML Front Matter。`knowledge-base.yaml` 是机器入口，`schemas/catalog.json` 与各类型 Schema 是格式权威，`.project-kb/scripts/check_knowledge_base.py` 负责确定性结构验证。当前初始化格式为 `format_version: 14`。决策依据保存在所属需求、功能、技术或治理文档中，不建立独立 ADR；需求以 Markdown 正文保存业务内容，Front Matter 只保留机器身份、状态、分类和更新时间。

知识关系使用登记过的正向 `rel_<type>` 字段和知识库内部链接，不维护人工反向列表。查询遵循 `children → neighbors → bounded graph`；返回 `truncated: true` 时不得把省略节点推断为不存在。

### 三层验证

| 层次 | 能证明什么 | 不能证明什么 |
| --- | --- | --- |
| 知识结构验证 | Schema、状态、来源、关系和引用合法 | 功能已经实现或业务已经接受 |
| 实现验证 | 测试、构建、接口调用或真实操作符合技术预期 | 项目责任人已经确认业务结果 |
| 业务确认 | 责任人接受范围、行为和结果 | 不能代替可定位的实现证据 |

检查器退出成功只表示知识结构合法。验收结果记录为 `passed` 时，必须关联对应版本和可定位证据。

## 仓库结构

| 目录 | 内容 |
| --- | --- |
| `skills/` | 九个用户入口 Skill |
| `references/` | 平台无关的治理和执行协议 |
| `templates/` | 初始化知识库模板 |
| `schemas/` | 知识类型和 Proposal 的机器契约 |
| `scripts/` | 初始化、更新、迁移、导航、验证和构建工具 |
| `operations/` | 确定性操作与规则映射 |
| `.codex-plugin/` | Codex 插件清单 |
| `.claude-plugin/` | Claude Code 插件与 Marketplace 清单 |
| `.qoder-plugin/` | Qoder 插件清单 |
| `packaging/` | 平台安装和发布说明 |
| `doc-atlas/` | 本项目自己的 Context Atlas 知识库 |

开发态只维护一份核心源码。平台发布包由构建脚本按 `assets/manifest.json` 生成，不直接修改独立发布仓库中的生成文件。

## 开发与验证

环境要求：Windows PowerShell、Python 3 和 Git。

```powershell
$env:PYTHONUTF8='1'
py -m unittest discover -s tests -p 'test_*.py'
py scripts/check_knowledge_base.py doc-atlas
py scripts/build_plugin.py claude --output build/claude/context-atlas
py scripts/build_plugin.py codex --output build/codex/context-atlas.zip --archive
py scripts/build_plugin.py qoder --output build/qoder/context-atlas
git diff --check
```

发布、同步独立仓库和打标签的完整流程见 [Marketplace 安装与使用](./packaging/marketplace-installation.md)。

## 文档导航

- [本项目知识库](./doc-atlas/README.md)
- [Marketplace 安装与使用](./packaging/marketplace-installation.md)
- [场景化使用指南](./templates/core/doc-project/05-知识治理/使用场景.md)
- [核心模板说明](./templates/core/README.md)
- [Schema 总览](./schemas/README.md)
- [Schema 字段说明](./schemas/字段说明.md)
- [AI 协作规则](./doc-atlas/05-知识治理/AI协作规则.md)

## 当前状态

核心 Schema、模板、检查器、九个 Skill 和三平台构建链路已实现。Codex 真实执行链路已经验证；Claude Code 和 Qoder 仍应在目标版本上继续完成真实 Agent 黑盒验收。命令成功或静态检查通过不能单独证明插件在目标宿主中可用。
