---
id: TASK-KB-004
type: governance_task
title: 黄金样例与 Agent 一致性测试
plan: docs/superpowers/plans/2026-08-10-single-knowledge-base-multi-stack.md
status: acceptance
acceptance: [F01-AC-01, F01-AC-02, F02-AC-01, F02-AC-02, F03-AC-01, F03-AC-02, F05-AC-02]
last_updated: 2026-08-19
---

# TASK-KB-004：单知识库多技术栈黄金样例与一致性测试

## 计划

[Single Knowledge Base, Multi-Stack Implementation Plan](../../../docs/superpowers/plans/2026-08-10-single-knowledge-base-multi-stack.md) 的 Task 4。

## 关联依据

- 功能：F01、F02、F03、F05 的产品验收项。
- 历史契约：[初始化产物契约](../旧契约/初始化产物契约.md)、[知识项与 Proposal 契约](../旧契约/知识项与Proposal契约.md)
- Skill：[初始化 Skill](../../../skills/context-atlas-init/SKILL.md)、[更新 Skill](../../../skills/context-atlas-update/SKILL.md)

## 范围

- 建立单技术栈和多技术栈两套黄金知识库，使用同一目录和 Schema。
- 固定期望目录快照，验证包内资产能够独立物化和校验。
- 建立覆盖保护、过期 Proposal、缺少确认、冲突、追踪和敏感值的负例。
- 验证初始化不会写 `AGENTS.md`、`CLAUDE.md` 或覆盖既有目标。

## 排除

- 不伪造不可用的第二 Agent 验收；不可取得时保持 `partial`。

## 验收

以实现计划 Task 6 的集成测试、快照和负例精确错误码为准。
