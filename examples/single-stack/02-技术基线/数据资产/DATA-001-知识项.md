---
id: DATA-001
type: data_asset
rel_classified_under:
  - "[[02-技术基线/数据资产/README|IDX-DATA-ASSETS]]"
title: 知识项数据
status: approved
version: 1.0.0
owner: example-owner
source_types: [database]
sensitivity: internal
retention: project-lifetime
approved_by: example-owner
approved_at: 2026-08-10
proposal_revision: 1
confirmed_revision: 1
last_updated: 2026-08-10
sources:
  - type: "repository_file"
    reference: "README.example"
    observed_at: "2026-08-10T00:00:00Z"
    confirmation_status: "confirmed"
    confirmed_at: "2026-08-10T00:00:00Z"
  - type: "user_statement"
    reference: "fictional example-owner confirmation"
    observed_at: "2026-08-10T00:00:00Z"
    confirmation_status: "confirmed"
    confirmed_at: "2026-08-10T00:00:00Z"
---
# DATA-001：知识项数据

这是仅用于黄金样例的虚构业务数据资产，技术细节见[数据库对象](../数据库/DB-001.md)和[知识查询接口](../接口/API-QUERY-001.md)。

## 数据来源映射

| 来源类型 | 名称 | 流向 | 用途 | 技术契约 |
| --- | --- | --- | --- | --- |
| database | 知识项存储 | 流入 | 保存并提供虚构知识项数据 | [DB-001](../数据库/DB-001.md) |

## 数据流转

输入 → 存储 → 查询组件。

## 质量要求

写入前校验知识项标识和来源引用；缺失值必须显式标记。

## 访问规则

仅 `example-owner` 可访问此虚构内部示例数据。

## 保存规则

按 `project-lifetime` 保存，项目结束后按已确认的处置规则清理。
