---
id: TASK-F06-001
type: task
title: Java 与 Python 可组合 Profile
feature: F06
status: ready
acceptance: [F06-AC-01, F06-AC-02]
last_updated: 2026-08-10
---

# TASK-F06-001：Java 与 Python 可组合 Profile

## 计划

[Agent-Native Project Knowledge Base MVP Implementation Plan](../../../docs/superpowers/plans/2026-08-10-agent-native-project-knowledge-base-mvp.md) 的 Task 4。

## 关联依据

- 功能：[F06 可选且可组合的技术栈 Profile](../../01-功能基线/F06-可选技术栈Profile.md)
- 契约：[Profile 扩展契约](../../02-架构与契约/Profile扩展契约.md)
- 决策：[ADR-003 Profile 可选且可组合](../../04-决策记录/ADR-003-Profile可选且可组合.md)

## 范围

- 实现 `java.v1`、`python.v1` 描述符、增量模板、知识请求和验收检查。
- 验证零个、单个及 Java+Python 组合均不覆盖核心规则。
- 将前端 Profile 明确移出 MVP 导航，但保留历史文件。

## 排除

- 不实现前端 Profile，不打包 Skill，不生成黄金样例。

## 验收

以 F06-AC-01、F06-AC-02 和实现计划 Task 4 的测试命令为准；四类黄金样例的最终证据在 Task 6 补齐。
