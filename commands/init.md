---
description: 初始化当前项目的 Context Atlas 知识库
---

# Context Atlas Init

执行 Context Atlas 初始化流程。

要求：

1. 读取当前项目并生成 Proposal，明确目标目录、事实、假设、待确认项和验证命令。
2. 在用户确认同一 Proposal 后，调用插件内置的结构化 `init` 执行器；不要手工修改知识库文件。
3. 目标已存在时停止初始化；Claude Code 转入 `/context-atlas:update`，Codex 转入 `$context-atlas update`。
4. 报告结构化命令结果和校验结果。
