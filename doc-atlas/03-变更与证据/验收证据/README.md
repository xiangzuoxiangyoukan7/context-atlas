---
id: IDX-EVIDENCE
type: knowledge_index
rel_classified_under:
  - "[[03-变更与证据/README|IDX-CHANGES-EVIDENCE]]"
title: 验收证据
---
# 验收证据

## 目录契约

本目录只保存可定位的实际验收证据。先用 `search` 定位证据；需要追踪功能、场景和版本关系时再使用 `children`、`neighbors` 和有边界的 `graph`。

从 `.project-kb/templates/knowledge/acceptance-evidence.md` 创建报告。证据应记录命令、环境、时间、输出摘要、失败项和对应版本；大文件可保存外部引用，但必须可追溯。

不得伪造第二个 Agent、人工确认或未运行的测试。无法取得的证据将结果保持为 `partial` 或 `not_started`。
