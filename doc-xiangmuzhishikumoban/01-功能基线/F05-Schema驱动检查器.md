---
id: F05
type: feature
title: Schema 驱动的确定性检查器
status: baselined
phase: mvp
priority: P0
current_slice: included
depends_on: [F03, F04]
acceptance: [F05-AC-01, F05-AC-02]
contracts: [CONTRACT-KNOWLEDGE-001]
adr: []
last_updated: 2026-08-10
---

# F05：Schema 驱动的确定性检查器

## 目标

检查器实际读取 Schema，对知识库结构、状态、版本、链接和追溯关系进行确定性校验。

## 包含

- 元数据、枚举、ID 和状态流转。
- 文档链接和跨知识类型引用。
- Profile 增量约束。
- 功能、设计、任务、验收和证据闭环。
- 数据库、原型、外部依赖引用。
- 批准来源、版本、冲突和敏感信息风险。

## 验收

- `F05-AC-01`：检查器以 Schema 为唯一结构规则来源，不维护不一致的硬编码副本。
- `F05-AC-02`：有效样例通过，规定的结构、追溯、冲突和安全反例失败并提供定位信息。
