# AI 项目知识库

本项目规划一套供 AI Agent 使用的项目知识库能力。用户通过 Codex、ChatGPT、Claude Code 等 Agent 初始化和维护知识库；本项目提供工具无关的协议、完整模板、Schema、可选 Profile、示例和确定性检查器。

## 入口

- [本项目知识库](doc-xiangmuzhishikumoban/README.md)
- [通用模板](./template/README.md)
- [核心 Schema](./schemas/README.md)
- [Java 扩展](./profiles/java/README.md)
- [Python 扩展](./profiles/python/README.md)
- [知识库检查器](./scripts/check_knowledge_base.py)
- [AI 上下文 Skill](./skills/project-knowledge-context/SKILL.md)

## 原则

AI 负责调研、提问和组织候选知识；项目责任人负责确认内容；知识库负责存储、版本、关联和结构校验。自动检查不能替代人工确认内容是否正确。

本项目不生成或维护目标项目的 `AGENTS.md`、`CLAUDE.md` 等工具专属文件，也不调用或托管大模型。

## 当前状态

项目正在重新建立产品基线。当前已批准产品方向，但 Skill、完整模板、Java/Python Profile、示例和新版检查器尚未按新基线实现。旧版 KB-AC-01–10 只代表概念骨架曾通过结构验收。
