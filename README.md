# 脉络地图（Context Atlas）

本项目规划一套供 AI Agent 使用的项目知识库能力。用户通过 Codex、ChatGPT、Claude Code 等 Agent 初始化和维护知识库；本项目提供工具无关的协议、完整模板、Schema、多技术栈样例和确定性检查器。

## 入口

- [本项目知识库](doc-atlas/README.md)
- [通用核心模板](./templates/core/README.md)
- [核心 Schema](./schemas/README.md)
- [知识库检查器](./scripts/check_knowledge_base.py)
- [脉络地图 Skill](./skills/context-atlas/SKILL.md)
- [Marketplace 安装与使用](./docs/marketplace-installation.md)

## Marketplace 安装

Context Atlas 是 Agent Skill/插件，不是 Python 包，不需要 `pip install`。仓库根目录就是唯一插件源码，
Codex Marketplace 位于 `.agents/plugins/marketplace.json`，Claude Code Marketplace 位于
`.claude-plugin/marketplace.json`。安装 `context-atlas` 后请新建会话，让 Agent 载入最新 Skill。正式写入必须通过
`init` 或 `update` 命令完成；Skill 只能生成 Proposal 并调用命令，不能直接写入知识库。

插件只支持安装到目标项目：Claude Code 必须使用 `--scope project`；Codex 当前没有原生 scope 参数，
必须把 `CODEX_HOME` 指向目标项目的 `.codex/`，并在同一环境下安装和启动 Codex。不要省略项目隔离参数。
安装后，Codex 使用 `$context-atlas init|update`，Claude Code 使用
`/context-atlas:init|update`；没有固定操作符的自然语言不得触发知识库写入。

完整的 Codex、Claude Code 操作步骤和当前验收状态见[Marketplace 安装与使用](./docs/marketplace-installation.md)。

### 项目级卸载

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

Plugin 发布包由根目录源码构建，不直接发布开发仓库。构建命令为：

```powershell
py scripts/build_plugin.py claude --output build/claude/context-atlas
py scripts/build_plugin.py codex --output build/codex/context-atlas.zip --archive
```

## 原则

AI 负责调研、提问和组织候选知识；项目责任人负责确认内容；知识库负责存储、版本、关联和结构校验。自动检查不能替代人工确认内容是否正确。

本项目不生成或维护目标项目的 `AGENTS.md`、`CLAUDE.md` 等工具专属文件，也不调用或托管大模型。

## 当前状态

产品方向、核心 Schema、检查器、统一核心模板、单/多技术栈样例和可安装 Skill 已进入实现；最终跨 Agent 验收仍待完成。
