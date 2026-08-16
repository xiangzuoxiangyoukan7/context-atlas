# Context Atlas 双平台 Marketplace 分发设计

## 状态

- 设计状态：已获用户批准
- 日期：2026-08-17
- 范围：Codex CLI 与 Claude Code 的标准 Marketplace 安装

## 目标

让其他项目的用户不再复制 `skills/context-atlas/`，而是通过各 Agent 的 Marketplace 入口发现并安装 `context-atlas`。安装后的插件仍使用同一份 Skill、模板、Schema 和确定性检查器。

## 方案

采用仓库内置 Marketplace。仓库同时维护：

- Codex 插件清单：`.codex-plugin/plugin.json`
- Claude Code 插件清单：`.claude-plugin/plugin.json`
- Codex Marketplace 索引：`.agents/plugins/marketplace.json`
- Claude Code Marketplace 索引：`.claude-plugin/marketplace.json`
- 唯一运行时 Skill：`skills/context-atlas/`

Marketplace 索引只负责发现和定位插件，不复制 Skill 内容。两个平台的索引必须指向相同的 `skills/context-atlas/`，并与两个插件清单保持名称、版本和仓库地址一致。

## 用户流程

### Codex

1. 在 Codex CLI 打开 `/plugins`。
2. 添加或选择 Context Atlas 的 Marketplace 来源。
3. 安装 `context-atlas`。
4. 新建会话，在目标项目中直接请求初始化或维护知识库。

### Claude Code

1. 添加仓库提供的 Claude Code Marketplace 来源。
2. 安装 `context-atlas`。
3. 新建会话，在目标项目中使用 `/context-atlas:context-atlas` 或自然语言触发 Skill。

README 必须给出复制可执行的命令和仓库来源，并说明安装后需要新建会话。

## 发布边界

正式插件发布物只包含：

- 对应平台的插件清单；
- 唯一的 `skills/context-atlas/`；
- Skill 所需的 `assets/`、`references/`、`agents/` 和内置脚本；
- 对应 Marketplace 索引和必要的发布说明。

不得把仓库根 `AGENTS.md`、`CLAUDE.md`、测试夹具、开发脚本或 `.worktrees/` 复制进插件运行时目录。不得创建第二份 Context Atlas Skill。

## 一致性规则

- 两个平台的插件名称必须为 `context-atlas`。
- 两个平台的版本必须相同并符合 SemVer。
- 两个平台必须引用同一仓库地址。
- 每个 Marketplace 条目必须包含插件名称、来源、安装策略、认证策略和分类。
- Marketplace 的插件来源路径必须是相对于索引文件的稳定路径。
- Marketplace 索引中的插件顺序保持稳定。

## 验证

新增或调整以下自动检查：

- 两个 Marketplace JSON 可解析且符合平台字段约束；
- Marketplace 条目指向存在的插件清单；
- 两个平台清单与 Marketplace 条目身份一致；
- 发布边界只包含一个 `context-atlas` Skill；
- Codex 与 Claude 的静态插件验证继续通过；
- 现有全量单元测试、Skill 资产同步和知识库检查继续通过。

## 非目标

- 不新增独立用户 CLI；
- 不改变知识库初始化确认流程；
- 不把项目知识库自动写入目标项目；
- 不承诺 Claude Code 当前真实模型行为已经达到 Codex 同等验收状态；
- 不在本次设计中接入公共插件目录的审核或自动发布服务。
