---
id: TASK-KB-007
type: governance_task
title: 统一关系与影响分析
plan: docs/superpowers/plans/2026-08-13-typed-relations-and-impact-analysis.md
status: completed
acceptance: [KB-AC-30, KB-AC-31, KB-AC-32]
last_updated: 2026-08-13
---

# TASK-KB-007：统一关系与影响分析

## 范围

- 使用 `rel_<type>` 和 Obsidian 文件链接保存唯一权威正向关系。
- 校验关系字段、文件、稳定编号、锚点、方向和重复项，并计算反向使用方。
- 根据变化类型输出必须处理、需要复核和仅供参考三级影响。
- 为 Codex、Claude Code 等 Agent 提供相同的 Skill 说明、模板、内置检查器和示例。

## 边界

- 反向关系只在读取时计算，不作为第二套知识写回文件。
- 影响分析不自动修改关联文档，不替代责任人判断业务含义。
- 影响等级不构成开发任务执行门禁，也不控制 Superpowers、OpenSpec 或其他插件。

## 验收

- `KB-AC-30`：关系链接、目标和方向确定性验证。
- `KB-AC-31`：反向索引与三级影响分析。
- `KB-AC-32`：规则、模板、Skill、黄金样例和自包含资产一致。

证据见[统一关系与影响分析](../验收证据/统一关系与影响分析.md)。
