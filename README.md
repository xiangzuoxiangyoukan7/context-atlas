# Project Knowledge Base Template

这是一个可复用的项目知识库模板工程，目标是让不同 AI 工具在不同项目中获得一致、可追溯的上下文。

## 入口

- [本项目知识库](./knowledge-base/README.md)
- [通用模板](./template/README.md)
- [核心 Schema](./schemas/README.md)
- [Frontend 扩展](./profiles/frontend/README.md)
- [Java 扩展](./profiles/java/README.md)
- [Python 扩展](./profiles/python/README.md)
- [知识库检查器](./scripts/check_knowledge_base.py)
- [AI 上下文 Skill](./skills/project-knowledge-context/SKILL.md)

## 原则

知识库负责事实、设计、边界和验收标准；AI 只依据权威文档生成上下文和计划。自动检查只能证明结构和追溯关系正确，不能替代人工确认内容是否正确。

当前模板项目自身没有任何 frontend、Java 或 Python 产品功能完成声明。

## 当前状态

模板治理任务已完成；KB-AC-01–10 的最终命令、路径和版本记录在 `knowledge-base/03-实施与验收/验收证据/KB-AC-01-10-模板验收报告.md`。这不代表任何业务项目功能完成。
