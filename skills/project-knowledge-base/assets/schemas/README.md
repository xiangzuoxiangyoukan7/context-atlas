# 核心 Schema

`catalog.json` 是检查器读取的唯一 Schema 目录。各 Schema 使用 JSON，确保 Python 标准库即可解析；知识库 Markdown 使用受控 YAML Front Matter，只支持字符串和一维字符串列表。

- [目录](./catalog.json)
- [项目清单](./project-manifest.schema.json)
- [通用知识项](./knowledge-item.schema.json)
- [功能](./feature.schema.json)
- [产品任务](./task.schema.json)
- [治理任务](./governance-task.schema.json)
- [验收](./acceptance.schema.json)
- [技术栈 Profile](./profile.schema.json)
- [知识来源](./source.schema.json)

Profile 只能增加约束，不能改变核心状态、权威来源、确认规则或验收结果。

