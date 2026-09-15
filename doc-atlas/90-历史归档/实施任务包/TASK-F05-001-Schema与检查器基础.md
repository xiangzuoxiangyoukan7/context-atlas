---
id: TASK-FEATURE-功能基线-功能-Schema-驱动的确定性检查器-001
type: task
title: Schema 与检查器基础
feature: FEATURE-功能基线-功能-Schema-驱动的确定性检查器
status: acceptance
acceptance: [FEATURE-功能基线-功能-Schema-驱动的确定性检查器-AC-01, FEATURE-功能基线-功能-Schema-驱动的确定性检查器-AC-02]
last_updated: 2026-08-10
---

# TASK-FEATURE-功能基线-功能-Schema-驱动的确定性检查器-001：Schema 与检查器基础

## 计划

[Single Knowledge Base, Multi-Stack Implementation Plan](../../../docs/superpowers/plans/2026-08-10-single-knowledge-base-multi-stack.md) 的基础检查任务。

## 关联依据

- 功能：[FEATURE-功能基线-功能-Schema-驱动的确定性检查器 Schema 驱动检查器](../../01-功能基线/FEATURE-功能基线-功能-Schema-驱动的确定性检查器.md)
- 依赖：[FEATURE-功能基线-功能-知识存储版本与追溯 知识存储版本与追溯](../../01-功能基线/FEATURE-功能基线-功能-知识存储版本与追溯.md)、[FEATURE-功能基线-功能-完整核心模板与知识模型 完整核心模板与知识模型](../../01-功能基线/FEATURE-功能基线-功能-完整核心模板与知识模型.md)
- 架构：[系统架构](../../02-技术基线/ARCH-技术基线-系统架构.md)
- 历史契约：[知识项与 Proposal 契约](../旧契约/知识项与Proposal契约.md)

## 范围

- 建立 JSON Schema 目录和受控 Front Matter 解析器。
- 将现有检查器重构为真正读取 Schema 的模块化实现。
- 增加批准、冲突、追溯、敏感信息和稳定报告测试。

## 排除

- 不实现核心模板、Skill 或黄金样例。
- 不完成 FEATURE-功能基线-功能-Agent-驱动的知识库初始化～FEATURE-功能基线-功能-完整核心模板与知识模型 的产品验收。

## 验收

以 FEATURE-功能基线-功能-Schema-驱动的确定性检查器-AC-01、FEATURE-功能基线-功能-Schema-驱动的确定性检查器-AC-02 及实现计划 Task 1～2 的测试和验证命令为准。

阶段实现已提交为 `5c6ebaf`、`e2e8864`。Schema、Front Matter、模块化检查、文本/JSON 报告和规定反例测试已通过；完整黄金样例留待实现计划 Task 6，因此 FEATURE-功能基线-功能-Schema-驱动的确定性检查器 整体验收尚未完成。
