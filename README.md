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

Context Atlas 是 Agent Skill/插件，不是 Python 包，不需要 `pip install`。将仓库中的
`marketplaces/context-atlas` 作为 Marketplace 添加到 Codex 或 Claude Code，再安装
`context-atlas`；安装完成后请新建会话，让 Agent 载入最新 Skill。目标项目中可使用自然语言
或 `/context-atlas:context-atlas` 调用。初始化会先展示 Proposal，只有用户确认后才写入正式知识。

完整的 Codex、Claude Code 操作步骤和当前验收状态见[Marketplace 安装与使用](./docs/marketplace-installation.md)。

## 原则

AI 负责调研、提问和组织候选知识；项目责任人负责确认内容；知识库负责存储、版本、关联和结构校验。自动检查不能替代人工确认内容是否正确。

本项目不生成或维护目标项目的 `AGENTS.md`、`CLAUDE.md` 等工具专属文件，也不调用或托管大模型。

## 当前状态

产品方向、核心 Schema、检查器、统一核心模板、单/多技术栈样例和可安装 Skill 已进入实现；最终跨 Agent 验收仍待完成。
