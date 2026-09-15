---
id: IDX-FEATURES
type: knowledge_index
rel_classified_under:
  - "[[01-功能基线/README|IDX-FUNCTIONAL-BASELINE]]"
title: 功能
---
# 功能

## 目录契约

本目录只保存功能规格。先用 `search` 定位功能；需要查看其需求、模块或验收关系时再使用 `children`、`neighbors` 和有边界的 `graph`。

每项功能使用 `.project-kb/templates/knowledge/feature.md` 创建独立文件，文件名为 `F-<领域>-<三位序号>-<名称>.md`。功能描述系统可观察行为，通过 `rel_satisfies` 关联需求，通过模块和接口关系关联实现结构。

现行功能必须使用本目录；升级器只在输入侧读取旧位置，并将其完整转换到当前布局。
