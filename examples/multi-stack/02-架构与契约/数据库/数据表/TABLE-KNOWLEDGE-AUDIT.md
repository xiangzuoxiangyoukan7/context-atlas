---
id: TABLE-KNOWLEDGE-AUDIT
type: database_table
title: 知识审计表
status: approved
version: 1.0.0
physical_name: knowledge_audit
owner: example-owner
sensitivity: internal
sources: [SRC-002]
ddl_sources: [FILE-001]
approved_by: example-owner
approved_at: 2026-08-10
rel_belongs_to:
  - "[[02-架构与契约/数据库/数据命名空间/NS-KNOWLEDGE|NS-KNOWLEDGE]]"
rel_logical_parent:
  - "[[02-架构与契约/数据库/数据表/TABLE-KNOWLEDGE-001|TABLE-KNOWLEDGE-001]]"
last_updated: 2026-08-13
---
# TABLE-KNOWLEDGE-AUDIT 知识审计表

## 字段定义

| 字段编号 | 字段名 | 数据类型 | 可空 | 默认值 | 中文含义 | 值域类型 | 允许值或最小值 | 最大值或格式 | 允许其他值 | 约束执行位置 | 来源 | 锚点 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FIELD-AUDIT-001 | id | bigint | 否 | — | 审计主键 | 任意 | — | 正整数 | 否 | 数据库约束 | [[00-项目总览/SRC-002|SRC-002]] | ^FIELD-AUDIT-001 |
| FIELD-AUDIT-002 | knowledge_id | bigint | 否 | — | 对应知识项主键 | 任意 | — | 正整数 | 否 | 应用规则 | [[00-项目总览/SRC-002|SRC-002]] | ^FIELD-AUDIT-002 |

## 主子表关系

| 关系编号 | 子字段编号 | 主表与字段 | 物理约束 | 约束名称 |
| --- | --- | --- | --- | --- |
| FK-AUDIT-001 | FIELD-AUDIT-002 | [[02-架构与契约/数据库/数据表/TABLE-KNOWLEDGE-001#^FIELD-KNOWLEDGE-001|FIELD-KNOWLEDGE-001]] | 否 | — |
