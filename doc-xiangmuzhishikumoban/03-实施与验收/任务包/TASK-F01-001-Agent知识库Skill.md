---
id: TASK-F01-001
type: task
title: 可安装的 Agent 项目知识库 Skill
feature: F01
status: acceptance
acceptance: [F01-AC-01, F01-AC-02, F02-AC-01, F02-AC-02]
last_updated: 2026-08-10
---

# TASK-F01-001：可安装的 Agent 项目知识库 Skill

## 计划

[Single Knowledge Base, Multi-Stack Implementation Plan](../../../docs/superpowers/plans/2026-08-10-single-knowledge-base-multi-stack.md) 的 Task 5。

## 关联依据

- 功能：[F01 Agent 驱动的知识库初始化](../../01-功能基线/F01-Agent驱动的知识库初始化.md)、[F02 AI 知识采集与确认](../../01-功能基线/F02-AI知识采集与确认.md)
- 契约：[初始化产物契约](../../02-架构与契约/初始化产物契约.md)、[知识项与 Proposal 契约](../../02-架构与契约/知识项与Proposal契约.md)
- 协议：[AI 知识采集协议](../../05-开发指南/AI知识采集协议.md)

## 范围

- 建立可安装、Agent 工具无关的 `project-knowledge-base` Skill。
- 将统一核心模板、Schema 和检查器同步为自包含资产。
- 明确初始化、采集确认、冲突归档、验证报告流程。
- 初始化不覆盖既有目标，也不创建 Agent 专属入口文件。

## 排除

- 不提供独立用户 CLI，不调用或托管模型，不实现黄金样例。

## 验收

以 F01/F02 验收项及实现计划 Task 5 的同步与包完整性测试为准。

阶段证据：[Agent Skill 阶段验证](../验收证据/F01-F02-Agent-Skill阶段验证.md)。Skill 结构、同步和行为契约已通过；真实初始化样例和第二 Agent 验收留待后续任务。
