---
id: TASK-KB-008
type: governance_task
title: 数据库知识治理
plan: docs/superpowers/plans/2026-08-13-database-knowledge-governance.md
status: completed
acceptance: [KB-AC-33, KB-AC-34, KB-AC-35]
last_updated: 2026-08-13
---

# TASK-KB-008：数据库知识治理

## 范围

- 数据源、数据库单元、可选数据命名空间和数据表四类实体。
- Oracle、PostgreSQL、KingbaseES、MySQL 真实层级映射。
- 一表一文件，字段中文含义、值域、来源和约束执行位置。
- 已有物理外键如实记录，所有业务主子表关系保留逻辑外键字段链接。
- 数据库作为基础知识被功能、接口和任务引用，不反向手填消费者。

## 验收

- `KB-AC-33`：数据库实体、层级关系与产品映射。
- `KB-AC-34`：字段含义、值域、来源、块锚点和逻辑外键检查。
- `KB-AC-35`：模板、Skill、自包含检查器和黄金样例一致。

证据见[数据库知识治理](../验收证据/数据库知识治理.md)。
