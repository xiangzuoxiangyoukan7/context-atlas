# 脉络地图（Context Atlas）

本项目提供一套供 Codex、Claude Code 和 Qoder 使用的项目知识库能力；核心协议、完整模板、Schema、多技术栈样例和确定性检查器与具体 Agent 解耦。

## 1. 概述

Context Atlas 是一个面向项目的知识治理插件。它把项目中的架构、约束、变更、验收证据、数据库信息和来源追溯整理成可持续维护的 `doc-<项目名>/` 知识库，让不同 Agent 在同一个项目中读取同一套事实。

它解决的不是“替 Agent 写代码”，而是解决以下问题：

- 项目知识散落在 README、源码、Issue、设计文档和会话中，难以持续读取。
- 不同 Agent 对项目结构和约束的理解不一致。
- AI 生成的推测被误当成正式事实。
- 知识写入缺少确认、来源、版本和校验边界。
- 项目更换 Codex、Claude Code 或 Qoder 后，知识库需要重新维护。

适合使用 Context Atlas 的项目通常需要多人或多个 Agent 长期协作，希望需求、设计、接口、数据库、决策和验收证据能够持续更新并追溯来源。它不替代需求管理、开发计划、编码工具和人工验收。

当前源码清单版本为 `0.12.0`。源码清单版本不等于各 Marketplace 已发布版本，安装或升级后必须以宿主实际显示的版本为准。

## 2. 总体设计

Context Atlas 采用“一主多适配”架构：核心 Skill、协议、模板、Schema 和 Python 执行器只有一份；Codex、Claude Code 和 Qoder 只提供平台清单、安装入口、路径布局和命令映射。

一次正式写入遵循固定状态机：

```text
inspect → propose → await_confirmation → apply → validate → report
```

Agent 负责调研、组织候选内容和展示 Proposal；用户负责确认；确定性执行器负责写入、版本、关系、来源和结构校验。没有用户明确确认，不会写入正式知识库。

系统采用“一主多适配”结构：`skills/` 提供用户入口，`references/` 保存平台无关协议，`templates/` 定义初始化知识库，`schemas/` 定义机器契约，`scripts/` 提供确定性执行和校验；Codex、Claude Code 和 Qoder 只维护各自的平台清单与安装适配，不复制核心协议。

目标业务仓库中只维护一套 `doc-<项目名>/`。Codex、Qoder 使用 `AGENTS.md`，Claude Code 使用 `CLAUDE.md` 进入同一知识库；已有入口文件只更新 Context Atlas 受管区块，不覆盖项目原有内容。

### 知识库目录结构

初始化后，业务仓库中的知识库默认采用以下结构：

```text
doc-<项目名>/
├─ README.md                 # 人工阅读入口
├─ knowledge-base.yaml       # 机器入口与格式版本
├─ Clippings/                # 待摄取外部资料暂存区
├─ .project-kb/              # Schema、检查器和运行资产
├─ 00-项目总览/              # 项目定位、边界和术语
├─ 01-功能基线/              # 需求、功能和能力地图
├─ 02-架构与契约/            # 当前实现结构与各类契约
├─ 03-变更与证据/            # 规格变化、验收及实际证据
├─ 04-决策记录/              # 当前有效的架构决策记录
├─ 05-知识治理/              # 协作、来源和维护规则
└─ 90-历史归档/              # 已退出当前权威的历史
```

| 位置 | 保存什么 | 不保存什么 |
| --- | --- | --- |
| `README.md` | 知识库入口、权威导航和常用场景 | 全部知识正文的重复副本 |
| `knowledge-base.yaml` | 协议、Schema、项目、格式、修订和权威入口 | 业务知识正文 |
| `00-项目总览` | 项目定位、职责边界和统一术语 | 模块实现和临时任务 |
| `01-功能基线` | 需求、功能、能力地图及验收引用 | 开发计划和代码修改记录 |
| `02-架构与契约` | 系统架构、模块、接口、数据库、数据资产、原型、外部依赖和独立契约 | 临时排查过程 |
| `03-变更与证据` | 当前变更、规格 Delta、验收契约、验收矩阵、实际证据、待确认知识和按需影响记录 | 长期产品定义和任务调度许可 |
| `04-决策记录` | 已确认 ADR、决策背景、选项和后果 | 尚未确认的讨论结论 |
| `05-知识治理` | AI 协作规则、使用场景、来源资料和维护说明 | 产品开发计划 |
| `90-历史归档` | 已被替代或退出当前权威但仍有审计价值的历史 | 当前需求、当前设计和当前完成状态 |
| `Clippings` | 尚待 `ingest` 分析的外部原文件 | 已批准正式知识 |
| `.project-kb` | 自包含的 Schema、模板、脚本和确定性检查器 | 项目业务事实 |

模块、接口和独立契约必须有明确目录并一项一文件。数据库默认按数据源隔离并一张表一个文件；只有实际存在复杂拓扑时，才增加 database、instance、service、schema 或 catalog 等层级。`90-历史归档` 默认不参与当前知识读取，不能用来覆盖现行基线。

## 3. 开发规范

### 知识读取规范

进入任务后先读取项目入口和知识库 README，再按请求定位需求、功能、架构、契约、ADR 和验收项。查询从最小范围开始：`children → neighbors → bounded graph`；结果出现 `truncated: true` 时不得把省略节点推断为不存在。

### 事实与来源规范

- 仓库观察、用户陈述、外部来源和 AI 推测必须分开标记。
- AI 推测只能作为待确认假设，不能直接成为批准事实。
- 发现冲突时保留竞争值、来源和待裁决问题，不自行选择看起来更合理的内容。
- 密码、Token、私钥和未脱敏个人数据不得进入知识库。

正式知识库可以保存项目目标、范围、术语、需求、功能、架构、模块、接口、数据源、数据表、数据资产、独立契约、外部依赖、ADR、规格变化、验收契约、验收结果、实际证据，以及支撑这些知识的来源、关系、冲突、未知项和替代关系。

以下内容不进入正式知识：没有长期价值的日志或命令输出、未验证的排查猜测、普通对话查询结果、外部任务的调度状态本身、没有来源和稳定身份的散文式结论，以及只能从历史归档推导出的当前结论。

### 文件格式规范

当前初始化知识库使用 `format_version: 8`。根目录的 `knowledge-base.yaml` 至少记录项目稳定编号与名称、知识库名称、工作区模式、可选业务项目版本、磁盘格式版本、知识库修订号、生成工具信息、初始化时间以及各类权威入口。只有 `format_version` 参与知识库兼容判断。

正式知识项使用 Markdown 正文和 YAML Front Matter。通用知识项至少包含稳定身份、知识类型、标题、状态、内容版本、内嵌来源和更新时间；批准知识还必须包含批准人和批准时间：

```yaml
---
id: MOD-ORDER-001
type: module
title: 订单模块
status: approved
version: 1.0.0
sources:
  - type: repository_file
    reference: src/order/README.md
    observed_at: 2026-08-24T10:00:00+08:00
    confirmation_status: confirmed
    confirmed_at: 2026-08-24T11:00:00+08:00
last_updated: 2026-08-24
approved_by: 项目责任人
approved_at: 2026-08-24T11:00:00+08:00
---
```

- `id` 是稳定知识身份，移动或改名文件时不能随意改变。
- `type` 决定使用哪个 Schema；需求、功能、模块、接口、数据库和验收等专用字段由对应 Schema 约束。
- `status` 表示知识生命周期，不能与开发任务状态或验收结果混用。
- `version` 使用三段式版本，`last_updated` 使用 `YYYY-MM-DD`。
- `sources` 使用内嵌来源对象，至少包含来源类型、精确定位、观察时间和确认状态；已确认来源还包含确认时间。
- `ai_inference` 必须单独标记并等待责任人确认，不能直接成为批准事实。

### 关系格式规范

知识关系使用登记过的正向 `rel_<type>` 字段和知识库内部链接：

```yaml
rel_satisfies:
  - "[[01-功能基线/需求/REQ-ORDER-001-创建订单|REQ-ORDER-001]]"
rel_reads:
  - "[[02-架构与契约/数据库/订单库/TABLE-ORDER-001-订单表|TABLE-ORDER-001]]"
```

关系不得只写裸 ID，不使用嵌套 `relations`，也不人工维护反向列表；反向使用方由检查器计算。聚合文件中的目标必须使用完整标题锚点或块锚点。允许的关系类型、源类型、目标类型和方向以 `relation-catalog.json` 为准。文件移动后先修正全部正向链接，再运行结构检查和影响分析。

### 格式权威

README 只解释使用方式，不复制所有机器规则。`knowledge-base.yaml` 是机器入口，`schemas/catalog.json` 是知识类型入口，各 `*.schema.json` 是必填字段、枚举、格式和列表约束的机器权威，`.project-kb/scripts/check_knowledge_base.py` 负责确定性验证。说明与当前 Schema 冲突时，以当前 Schema 和 `format_version` 为准。

`upgrade` 只迁移目录布局、内部元数据和格式版本，不能借格式升级新增、批准或改变业务事实。

### 正式写入规范

- 自然语言可以触发查询、讨论和补充信息，但不能单独触发正式写入。
- 新增知识使用 `add`，同一身份和含义发生变化使用 `revise`，当前权威退出使用时使用 `retire`，仅格式变化使用 `upgrade`。
- 正式写入必须展示目标、事实、来源、推断、未知项、冲突、关系、影响、验证方法和不可变的 `proposal_revision`。
- 只有用户明确确认当前修订后才能写入；内容或验证计划变化后必须生成新修订并重新确认。
- 多项相互依赖的新增、修订和退役应形成一个原子复合 Proposal，失败时整体回滚。

### 验证与报告规范

知识结构验证、实现验证和业务确认必须分开报告。检查器通过只能证明 Schema、状态、来源、关系和引用合法，不能证明功能实现或业务验收已经通过。`passed` 必须有可定位证据和对应版本。

## 4. 开发环境

Context Atlas 是 Agent Skill/插件，不是 Python 包，不使用 `pip install`。支持 Codex、Claude Code 和 Qoder，必须安装到目标业务仓库的项目范围，并在安装或升级后新建 Agent 会话。

开发和验证本插件需要：

- Windows PowerShell；
- Python 3，可通过 `py` 启动；
- Git；
- 至少一个待验证的宿主 Agent；
- 对应业务仓库中的项目级插件目录。

常用源码验证命令：

```powershell
py -m unittest discover -s tests -p 'test_*.py'
py scripts/check_knowledge_base.py doc-atlas
py scripts/build_plugin.py claude --output build/claude/context-atlas
py scripts/build_plugin.py codex --output build/codex/context-atlas.zip --archive
py scripts/build_plugin.py qoder --output build/qoder/context-atlas
git diff --check
```

如果旧环境在中文输出时使用 GBK，可在运行 Python 验证前设置 `$env:PYTHONUTF8='1'`。平台安装、升级、卸载和发布命令见第 7 章。

## 5. 场景实践

Context Atlas 不安排开发任务，也不规定怎样编码。它在开发过程中提供经过确认的需求、设计、约束和验收依据，并在实现完成后保存实际结果与证据。开发任务可以来自用户、Issue、OpenSpec 或其他工具。

一项工作的知识闭环是：

```text
需求进入 → 查询现有知识 → 审查范围与验收 → 确认开发前基线
        → 编码与排查 → 核对实现差异 → 执行验收 → 确认并沉淀结果
```

### 知识在什么阶段形成

知识不是只在编码前形成，也不是等代码完成后统一补写。不同阶段形成的知识用途不同：

| 阶段 | 形成的知识 | 作用 |
| --- | --- | --- |
| 编码前 | 需求目标、范围与非范围、业务规则、设计决策、接口与数据约束、验收标准 | 作为开发和验收依据 |
| 编码中 | 新发现的仓库事实、冲突、设计调整、故障原因和稳定约束 | 防止实现与已确认基线静默分叉 |
| 编码后 | 实际实现、最终接口或数据库结构、测试结果、验收证据和遗留问题 | 校准知识基线并证明实际结果 |

Agent 调研后可以随时形成候选知识，但候选不等于正式事实。正式写入仍须经过 `inspect → propose → await_confirmation → apply → validate → report`，并由用户明确确认当前 `proposal_revision`。

### 新建项目类场景

适用于一个业务仓库尚未存在 `doc-<项目名>/` 的情况：

1. 在业务仓库的项目范围安装 Context Atlas，并新建 Agent 会话。
2. 显式调用 `context-atlas-init`。
3. Agent 调查 README、现有文档、依赖和构建清单、源码模块、接口、数据库模型与迁移、测试、CI、发布配置和已有 ADR。
4. Agent 展示初始化 Proposal，明确准备创建的知识、来源、未知项、冲突、入口文件和验证方法。
5. 用户确认精确修订后，执行器才创建知识库、维护宿主入口并运行结构验证。
6. 初始化后实际执行 `children`、`neighbors` 和有限 `graph` 查询，确认安装后的 Agent 能够读取知识库，而不只检查文件是否存在。

已有知识库时不得重新初始化或覆盖，应根据实际变化进入 `add`、`revise`、`retire` 或 `upgrade`。

### 新建模块或功能场景

适用于已有项目中增加模块、功能、接口或数据库结构：

1. 使用 `navigate` 查询相关需求、已有模块、接口、数据库、契约和验收项。
2. 使用 `review` 检查新模块的职责、边界、依赖、失败行为、兼容要求和验收标准；本阶段只读。
3. 新模块和新功能使用 `add`；如果同时改变旧接口、旧模块或旧数据结构，将相关 `revise` 或 `retire` 合并为一个原子 Proposal。
4. 用户确认后形成开发前基线，再进入编码。
5. 编码完成后核对真实目录、公开入口、依赖关系、接口、数据读写和测试结果。
6. 实现与基线不一致时先修订知识，再关联实际验收证据，分别报告结构验证、实现验证和业务确认结果。

示例：

```text
先查询订单领域已有需求、模块、POST /orders 接口、订单表和验收项，
审查“新建订单导出模块”的职责边界、数据读取、失败行为和验收标准。
本轮只分析；确认影响后再生成包含新模块、新功能和关联关系的 add Proposal。
```

### 新需求来了怎么做

1. 用自然语言说明目标、使用者、背景和已知限制。
2. 使用 `navigate` 查询相关需求、功能、接口、数据库、契约和验收项；本步只读。
3. 使用 `review` 检查范围、异常行为、边界、影响和验收标准是否足以进入实现；本步只读。
4. 信息清楚后，新需求使用 `add`，修改已有行为使用 `revise`，取消已有行为使用 `retire`。
5. 用户确认精确 Proposal 后，写入开发前基线，再由原有开发工具安排和执行编码。
6. 编码完成后核对实际实现，执行验收；存在差异时再次通过 `revise` 提交确认，最后沉淀验收证据。

示例：

```text
先查询租户导入相关的需求、功能、接口、数据库和验收项，
再审查“增加租户批量导入”是否有明确范围、失败行为和可执行验收标准。
本轮只分析，不写入。
```

分析完成后，再显式调用对应维护 Skill。不能因为已经开始编码或任务已经完成，就跳过知识确认。

### 编写代码前怎么做

编码前至少确认以下内容：

- 为什么做、谁使用、范围和非范围是什么；
- 正常行为、失败行为和关键边界是什么；
- 会影响哪些模块、接口、表、外部依赖和兼容行为；
- 安全、性能、兼容性等约束如何验证；
- 验收场景、预期结果和证据形式是什么；
- 哪些内容未知、互相冲突或需要责任人裁决。

`review` 可以判断现有规格是否清晰、完整、可追溯，但不会批准规格。缺少关键范围或验收标准时，应先补充并确认，不应让 Agent 自行编造后进入开发。

### 编码过程中发现变化怎么做

源码、迁移、配置和运行结果可以证明仓库或环境事实，但不能自动证明业务含义和设计原因。开发中发现原设计不可行、接口行为改变、数据库结构调整或新增稳定约束时：

- 先记录实际观察、来源、影响、未知项和冲突；
- 不改变身份和含义的修正使用 `revise patch`；
- 权威或语义改变时使用 `revise supersede`；
- 需要新增或退役独立知识时，纳入同一个原子复合 Proposal；
- 用户确认新修订后再更新正式知识。

代码提交、Issue 完成或外部规格归档都不自动批准知识变化。

### 排查问题怎么做

1. 使用 `navigate` 读取故障相关功能、接口、数据库、模块、外部依赖、ADR 和验收项。
2. 通过日志、配置、源码、请求链路、数据库状态和运行环境收集实际证据。
3. 分开标记已批准知识、当前观察、用户陈述和未验证假设，不能把排查猜测写成事实。
4. 判断结论是否值得长期维护：一次性运行现象留在任务上下文；稳定约束用 `add`，错误或过期知识用 `revise`，退出使用的事实用 `retire`。
5. 修复后使用相同复现条件或明确回归场景验证原问题、正常路径和兼容行为。
6. 只有可复用结论和可定位证据进入正式 Proposal；原始秘密、未脱敏数据和无长期价值的日志不得进入知识库。

示例：

```text
查询订单提交失败涉及的功能、POST /orders 接口、订单表和超时契约。
结合本次日志与配置定位原因，分别列出事实和假设。本轮先排查，不写入。
修复验证完成后，再判断哪些稳定结论需要 revise。
```

### 功能完成后怎么验收

验收必须区分三层，不能互相替代：

| 层次 | 验证内容 | 能证明什么 |
| --- | --- | --- |
| 知识结构验证 | Schema、状态、来源、关系和引用 | 知识库结构合法 |
| 实现验证 | 测试、构建、接口调用、数据库检查或真实操作 | 实际实现满足技术预期 |
| 业务确认 | 项目责任人核对范围、行为和结果 | 业务上接受本次结果 |

验收前从知识库定位相关验收项，按对应版本执行真实验证。证据至少记录验收对象与版本、环境、操作或命令、预期结果、实际结果、证据位置、未通过项和剩余风险。只有结果有可定位证据并经责任人确认时，才能把对应验收结果记录为 `passed`。

检查器退出成功只表示结构和引用通过，不表示功能已经通过业务验收。未通过或未执行的场景必须如实保留，不得为了关闭任务改写为通过。

### 验收后怎么闭环

1. 对照编码前基线检查最终接口、数据库、模块行为和约束是否一致。
2. 用 `revise` 修订实现造成的知识变化，并保留未知项、冲突和遗留风险。
3. 将测试或实际操作结果关联到对应验收项和实现版本。
4. 用户确认 Proposal 后写入知识与证据，再运行知识结构验证。
5. 分别报告知识写入结果、结构验证结果、实现验证结果和业务确认状态。

如果实现与原设计不一致，不能仅补一份“已完成”证据；必须先修订当前权威知识或明确记录冲突。

### 只补充数据库、接口或外部资料

- 新数据源、新表、新接口或新的独立事实使用 `add`。
- 已有字段、索引、接口行为或说明发生变化使用 `revise`。
- 当前权威退出使用时使用 `retire`。
- 外部资料先使用 `ingest` 分析来源并生成候选路由；`ingest` 不直接写入正式知识。

数据库知识可以独立维护，不必虚构业务需求。DDL、迁移和 ORM 可以证明技术结构，但字段业务含义、业务值域和负责人仍需要相应来源或用户确认。

### 哪些情况不写入知识库

- 尚未验证的排查猜测；
- 一次性命令输出和没有长期价值的临时日志；
- 当前对话中的普通查询结果；
- 密码、Token、私钥和未脱敏个人数据；
- 外部任务的计划、调度和完成状态本身；
- 用户尚未确认的 Proposal；
- 只能从历史归档得出的当前结论。

### 场景与入口速查

| 当前目的 | 使用入口 | 是否写入 |
| --- | --- | --- |
| 初始化尚无知识库的项目 | `init` | 确认 Proposal 后初始化 |
| 开发前查询相关事实和影响 | `navigate` | 只读 |
| 判断需求、设计或验收是否就绪 | `review` | 只读 |
| 分析会议纪要、Issue、文档或网页来源 | `ingest` | 只读，只生成候选路由 |
| 增加此前不存在的知识 | `add` | 确认 Proposal 后新增 |
| 修正、同步或替代已有知识 | `revise` | 确认 Proposal 后修订 |
| 替代、归档或受控删除失效知识 | `retire` | 确认 Proposal 后退役 |
| 只改变知识库格式或结构 | `upgrade` | 确认 Proposal 后升级 |

完整的安装后操作符、数据库维护、来源摄取、渐进查询和 Proposal 要求见[场景化使用指南](./templates/core/doc-project/05-知识治理/使用场景.md)。

## 6. 常见问题

### 知识应该在编码前写，还是编码后写？

两个阶段都需要。编码前确认需求、设计、约束和验收标准；编码中记录新发现的事实与冲突；编码后用实际实现和验收证据校准知识。候选内容只有经过当前 Proposal 修订确认后才成为正式知识。

### 新需求来了，可以直接开始编码吗？

Context Atlas 不阻 止用户开始开发，但建议先用 `navigate` 查询影响，再用 `review` 检查范围、边界和验收标准。关键信息缺失时应先确认，避免 Agent 用推测补齐需求。

### 排查问题时，日志和猜测都要写入知识库吗？

不需要。一次性日志和未验证猜测留在任务上下文。只有已经验证、可复用且具有长期价值的故障边界、配置约束、恢复策略或接口行为，才进入维护 Proposal。

### 测试通过是否等于知识库验收通过？

不等于。测试证明实现行为，知识库检查证明结构合法，项目责任人确认业务结果；三者必须分别报告。验收结果为 `passed` 时必须关联实际证据和对应版本。

### 只想补一张数据库表，需要先创建需求吗？

不需要。数据库知识可以独立使用 `add` 或 `revise`。DDL、迁移和 ORM 可以作为技术结构来源；无法从这些来源确定的业务含义、值域和责任人应列为未知项或等待确认。

### 已有知识库还能再次初始化吗？

不能。已有知识库应进入新增、修订、退役或格式升级流程。初始化不得覆盖已有知识库、宿主入口文件或工具配置。

### 为什么命令执行成功仍不能宣布可用？

命令成功可能只证明程序没有报错。安装后还需要在实际目标项目中运行导航查询、执行真实场景和核对生成结果，才能证明 Agent 真正可读取和使用知识库。

### 可以让 Agent 自动保存所有对话结论吗？

不可以。普通查询结果默认只保留在当前对话；自动保存会把推测、临时信息和敏感内容混入正式知识。需要长期维护时，应显式进入 `ingest` 和对应维护流程。

## 7. 资源下载

### 当前版本

当前源码清单版本为 `0.12.0`，Codex、Claude Code 和 Qoder 共享产品名 `context-atlas`。源码清单版本不等于各 Marketplace 已发布版本；安装或升级后必须以宿主实际显示的版本为准。平台发布包由当前源码仓库构建，不维护平台专属源码分叉。

### 文档与源码入口

- [本项目知识库](doc-atlas/README.md)
- [通用核心模板](./templates/core/README.md)
- [核心 Schema](./schemas/README.md)
- [Schema 逐文件字段说明](./schemas/字段说明.md)
- [知识库检查器](./scripts/check_knowledge_base.py)
- [开发工作编排 Skill](./skills/context-atlas-work/SKILL.md)
- [初始化 Skill](./skills/context-atlas-init/SKILL.md)
- [渐进导航 Skill](./skills/context-atlas-navigate/SKILL.md)
- [规格审查 Skill](./skills/context-atlas-review/SKILL.md)
- [增强摄取 Skill](./skills/context-atlas-ingest/SKILL.md)
- [知识新增 Skill](./skills/context-atlas-add/SKILL.md)
- [知识修订 Skill](./skills/context-atlas-revise/SKILL.md)
- [知识退役 Skill](./skills/context-atlas-retire/SKILL.md)
- [知识库升级 Skill](./skills/context-atlas-upgrade/SKILL.md)
- [场景化使用指南](./templates/core/doc-project/05-知识治理/使用场景.md)
- [Marketplace 安装与使用](./packaging/marketplace-installation.md)

### Marketplace 下载与安装

Context Atlas 是 Agent Skill/插件，不是 Python 包，不需要 `pip install`。仓库根目录就是唯一插件源码，
Codex Marketplace 位于 `.agents/plugins/marketplace.json`，Claude Code Marketplace 位于
`.claude-plugin/marketplace.json`。安装 `context-atlas` 后请新建会话，让 Agent 载入最新 Skill。正式写入必须通过
`init` 或 `update` 命令完成；Skill 只能生成 Proposal 并调用命令，不能直接写入知识库。

插件只支持安装到目标项目：Claude Code 必须使用 `--scope project`；Codex 当前没有原生 scope 参数，
必须把 `CODEX_HOME` 指向目标项目的 `.codex/`，并在同一环境下安装和启动 Codex。不要省略项目隔离参数。
安装后，普通开发目标优先由 `$context-atlas-work` 自动编排；Codex 也可精确使用 `$context-atlas-init`、`$context-atlas-navigate`、`$context-atlas-review`、`$context-atlas-ingest`、`$context-atlas-add`、`$context-atlas-revise`、`$context-atlas-retire`、`$context-atlas-upgrade`。Claude Code 的原生命令使用插件命名空间，例如
`/context-atlas:context-atlas-init`、`/context-atlas:context-atlas-navigate`；命令面板可能把已唯一解析的命令显示或补全为 `/context-atlas-init`。以面板实际补全结果为准，不要把显示别名当成另一个 Skill。两个平台共用同一组 Skills，不发布 `commands/`；
`context-atlas-work` 可从自然语言目标自动选择读取和维护路由，但正式知识写入仍必须等待用户确认当前 Proposal 修订。

Qoder 适配包也从同一源码仓库构建，使用 `.qoder-plugin/plugin.json`。完整的三平台安装、使用、升级步骤和当前验收状态见[Marketplace 安装与使用](./packaging/marketplace-installation.md)。Trae 适配仍保留为内部候选，不属于当前用户支持范围。

#### 在团队业务仓库中安装

三位开发者可以分别使用 Claude Code、Codex 和 Qoder，但必须把 Context Atlas 安装到**同一个业务仓库的项目范围**。插件程序按平台分别安装；正式知识统一保存在业务仓库的 `doc-<项目目录名>/` 中并通过 Git 协作，不为每种 Agent 创建独立知识库。

以下命令都应在需要使用 Context Atlas 的业务仓库根目录执行，而不是在本源码仓库中执行。

安装时可以按所在网络选择一个发布源：

| 平台 | GitHub 公网源 | SuperMap 内网源 |
| --- | --- | --- |
| Claude Code | `https://github.com/xiangzuoxiangyoukan7/context-atlas-claude-plugin.git` | `http://sc.supermap.com/customDP/sh/public/framework/ai/plugins/context-atlas-claude-plugin.git` |
| Codex | `https://github.com/xiangzuoxiangyoukan7/context-atlas-codex-plugin.git` | `http://sc.supermap.com/customDP/sh/public/framework/ai/plugins/context-atlas-codex-plugin.git` |
| Qoder | `https://github.com/xiangzuoxiangyoukan7/context-atlas-qoder-plugin.git` | `http://sc.supermap.com/customDP/sh/public/framework/ai/plugins/context-atlas-qoder-plugin.git` |

下面示例默认使用 GitHub 公网源；在 SuperMap 内网使用时，只需把对应的 GitHub URL 替换为表中的 SuperMap URL，后续插件名和升级命令不变。同一项目、同一平台只选择一个源，不要同时添加两个同名的 `context-atlas` Marketplace。SuperMap 地址使用 HTTP，只应在可信内网中使用。

#### 开发者 1：Claude Code

```powershell
cd D:\你的业务仓库
claude plugin marketplace add --scope project `
  https://github.com/xiangzuoxiangyoukan7/context-atlas-claude-plugin.git
claude plugin install --scope project context-atlas@context-atlas
```

安装后新建 Claude Code 会话，在命令面板确认 `/context-atlas:context-atlas-work` 等九个命令可用。不得省略 `--scope project`，否则可能安装到用户范围。

升级已有 Claude Code 插件：

```powershell
cd D:\你的业务仓库
claude plugin marketplace remove --scope project context-atlas
claude plugin marketplace add --scope project `
  https://github.com/xiangzuoxiangyoukan7/context-atlas-claude-plugin.git
claude plugin install --scope project context-atlas@context-atlas
```

升级后新建会话，并在插件管理界面确认实际安装版本。

#### 开发者 2：Codex

Codex 当前没有原生项目 scope 参数，必须先把 `CODEX_HOME` 指向业务仓库内的 `.codex/`，安装和以后启动 Codex 时都使用相同设置：

```powershell
cd D:\你的业务仓库
$env:CODEX_HOME = (Join-Path $PWD ".codex")
codex plugin marketplace add `
  https://github.com/xiangzuoxiangyoukan7/context-atlas-codex-plugin.git
codex plugin add context-atlas@context-atlas
codex
```

新建 Codex 会话后确认 `$context-atlas-work` 等九个 Skill 可用。以后从新终端进入该业务仓库时，也必须先设置相同的 `CODEX_HOME` 再启动 Codex。

升级已有 Codex 插件不能再次使用 `marketplace add`；必须先刷新 Marketplace，再替换旧安装：

```powershell
cd D:\你的业务仓库
$env:CODEX_HOME = (Join-Path $PWD ".codex")
codex plugin marketplace upgrade context-atlas
codex plugin remove context-atlas@context-atlas
codex plugin add context-atlas@context-atlas
codex plugin list
```

`marketplace upgrade` 只刷新插件源，`remove` 加 `add` 才会替换已安装插件。最后以 `codex plugin list` 显示的版本为准，并新建 Codex 会话。

#### 开发者 3：Qoder

在 Qoder 中打开业务仓库，把 Marketplace 的安装范围选择为 **Project**，然后在该项目终端执行：

```powershell
qoder plugins marketplace add `
  https://github.com/xiangzuoxiangyoukan7/context-atlas-qoder-plugin.git
qoder plugins install context-atlas@context-atlas
```

重启 Qoder，在输入框中输入 `/`，确认 `/context-atlas-work` 等九个 Skill 已加载。不要安装到用户级 `~/.qoder/skills/`，也不要只复制源码仓库中的 `skills/`。

升级已有 Qoder 插件时，仍须确认当前 Marketplace 范围为 **Project**：

```powershell
qoder plugins marketplace update context-atlas
qoder plugins update context-atlas@context-atlas
```

升级后重启 Qoder，在插件管理界面确认实际版本，并再次检查九个 Skill。

#### 团队首次启用检查

每位开发者安装后都应在同一个业务仓库中完成以下检查：

1. 三个平台显示的 Context Atlas 版本与团队准备验证的目标版本一致；不能用源码清单版本代替实际安装版本。
2. 开发工作编排、初始化、导航、审查、摄取、新增、修订、退役和升级九个 Skill 全部可见。
3. 仓库中只存在一个 `doc-<项目目录名>/`，并将其纳入 Git；不得按 Agent 分成三套知识库。
4. Codex、Qoder 使用 `AGENTS.md`，Claude Code 使用 `CLAUDE.md`；两个入口都指向同一个知识库和协作规则。
5. 任一 Agent 正式写入前都必须展示 Proposal，并由用户明确确认；Git 分支、PR 和合并冲突仍按团队原有流程处理。

当前 Codex 真实执行链路已经验证；Claude Code 的确认后初始化验收仍为 `partial`，Qoder 已通过构建和静态契约检查但尚未完成真实 Agent 黑盒验收。三平台由用户继续验证；每个平台都应完成一次真实的“安装或升级 → 版本确认 → 初始化 Proposal → 确认 → 校验”和“读取既有知识库”试运行，不能只以命令退出成功作为可用性结论。

#### 项目级卸载

Codex 必须在当初安装插件的目标项目中执行，并保持相同的项目级 `CODEX_HOME`：

```powershell
$env:CODEX_HOME = (Join-Path $PWD ".codex")
codex plugin remove context-atlas@context-atlas
codex plugin marketplace remove context-atlas
```

Claude Code 从项目作用域卸载开发仓库中的插件和 Marketplace：

```powershell
claude plugin uninstall --scope project context-atlas@context-atlas-dev
claude plugin marketplace remove --scope project context-atlas-dev
```

不要直接删除目标项目的整个 `.codex/` 或 `.claude/` 目录，其中可能还有该项目的其他配置和插件。

Plugin 发布包由根目录唯一源码构建，不直接运行或发布开发仓库。`templates/`、`schemas/`、
`scripts/`、`rules/`、`operations/` 和 `compatibility.json` 只维护一份；开发态 `assets/` 只保存
`manifest.json`。构建程序按清单把这些源码物化为安装包中的完整 `assets/`，测试也以构建后的安装形态为准。
构建命令为：

```powershell
py scripts/build_plugin.py claude --output build/claude/context-atlas
py scripts/build_plugin.py codex --output build/codex/context-atlas.zip --archive
py scripts/build_plugin.py qoder --output build/qoder/context-atlas
```

将 Codex 发布内容同步到独立发布仓库：

```powershell
py scripts/sync_to_codex_plugin.py `
  --destination D:\loong-workspace-python\context-atlas-codex-plugin
```

校验后，在独立发布仓库中提交并推送：

```powershell
py C:\Users\Seven\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py `
  D:\loong-workspace-python\context-atlas-codex-plugin
git -C D:\loong-workspace-python\context-atlas-codex-plugin add --all
git -C D:\loong-workspace-python\context-atlas-codex-plugin commit -m "release: context-atlas <版本号>"
git -C D:\loong-workspace-python\context-atlas-codex-plugin push origin main
```

将 Claude Code 发布内容同步到独立发布仓库：

```powershell
py scripts/sync_to_claude_plugin.py `
  --destination D:\loong-workspace-python\context-atlas-claude-plugin
git -C D:\loong-workspace-python\context-atlas-claude-plugin add --all
git -C D:\loong-workspace-python\context-atlas-claude-plugin commit -m "release: context-atlas 0.12.0"
git -C D:\loong-workspace-python\context-atlas-claude-plugin push origin main
```

将 Qoder 发布内容同步到独立发布仓库：

```powershell
py scripts/sync_to_qoder_plugin.py `
  --destination D:\loong-workspace-python\context-atlas-qoder-plugin
git -C D:\loong-workspace-python\context-atlas-qoder-plugin add --all
git -C D:\loong-workspace-python\context-atlas-qoder-plugin commit -m "release: context-atlas 0.12.0"
git -C D:\loong-workspace-python\context-atlas-qoder-plugin push origin main
```

Claude Code 正式安装使用独立发布仓库：

```powershell
claude plugin marketplace add --scope project `
  https://github.com/xiangzuoxiangyoukan7/context-atlas-claude-plugin.git
claude plugin install --scope project context-atlas@context-atlas
```

发布新版本时，再为同一提交创建并推送 `v<版本号>` 标签。发布仓库内容由同步脚本生成，不得直接维护。

### 当前状态

产品方向、核心 Schema、检查器、统一核心模板、单/多技术栈样例和可安装 Skill 已进入实现；最终跨 Agent 验收仍待完成。
