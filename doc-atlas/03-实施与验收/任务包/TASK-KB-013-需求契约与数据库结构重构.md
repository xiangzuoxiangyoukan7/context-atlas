---
id: TASK-KB-013
type: governance_task
title: 需求、契约与数据库结构重构
plan: 已确认设计文档及十四项确认记录
status: completed
acceptance: [KB-AC-49, KB-AC-50, KB-AC-51]
last_updated: 2026-08-20
---

# TASK-KB-013：需求、契约与数据库结构重构

## 目标与依据

依据用户逐项确认的[知识库结构、关系与流转设计](../../../docs/superpowers/specs/2026-08-20-knowledge-structure-relations-discussion.md)，建立需求与功能追溯、契约分层、模块和接口独立知识、技术基线合并、数据库简化、关系扩展及格式 5 兼容迁移。

## 实施边界

- 新建格式采用已确认结构。
- 格式 4 保留一个版本的读取兼容。
- 只自动迁移可证明等价的表达；无法安全拆分的旧聚合知识不得猜测改写。
- 按功能拆分提交，提交信息使用中文。

## 验收

实际结果见[需求、契约与数据库结构重构验收](../验收证据/需求契约与数据库结构重构.md)。
