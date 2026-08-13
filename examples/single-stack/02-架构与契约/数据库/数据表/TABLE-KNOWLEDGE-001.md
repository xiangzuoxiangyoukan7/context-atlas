---
id: TABLE-KNOWLEDGE-001
type: database_table
title: 知识项表
status: approved
version: 1.0.0
physical_name: knowledge_item
owner: example-owner
sensitivity: internal
sources: [SRC-002]
ddl_sources: [FILE-001]
approved_by: example-owner
approved_at: 2026-08-10
rel_belongs_to:
  - "[[02-架构与契约/数据库/数据命名空间/NS-KNOWLEDGE|NS-KNOWLEDGE]]"
last_updated: 2026-08-13
---
# TABLE-KNOWLEDGE-001 知识项表

## 字段定义

| 字段编号 | 字段名 | 数据类型 | 可空 | 默认值 | 中文含义 | 值域类型 | 允许值或最小值 | 最大值或格式 | 允许其他值 | 约束执行位置 | 来源 | 锚点 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FIELD-KNOWLEDGE-001 | id | bigint | 否 | — | 知识项主键 | 任意 | — | 正整数 | 否 | 数据库约束 | [[00-项目总览/SRC-002|SRC-002]] | ^FIELD-KNOWLEDGE-001 |
| FIELD-KNOWLEDGE-002 | status | smallint | 否 | 1 | 知识状态 | 枚举 | 1=待确认;2=已批准;3=已归档 | — | 否 | 数据库约束 | [[00-项目总览/SRC-002|SRC-002]] | ^FIELD-KNOWLEDGE-002 |
| FIELD-KNOWLEDGE-003 | title | varchar(200) | 否 | — | 知识标题 | 格式 | — | 长度1到200 | 否 | 应用规则 | [[00-项目总览/SRC-002|SRC-002]] | ^FIELD-KNOWLEDGE-003 |
