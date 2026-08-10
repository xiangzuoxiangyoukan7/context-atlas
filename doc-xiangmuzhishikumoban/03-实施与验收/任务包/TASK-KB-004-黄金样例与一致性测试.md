---
id: TASK-KB-004
type: governance_task
title: 黄金样例与 Agent 一致性测试
plan: docs/superpowers/plans/2026-08-10-agent-native-project-knowledge-base-mvp.md
status: ready
acceptance: [F01-AC-01, F01-AC-02, F02-AC-01, F02-AC-02, F03-AC-01, F03-AC-02, F05-AC-02, F06-AC-01, F06-AC-02]
last_updated: 2026-08-10
---

# TASK-KB-004：黄金样例与 Agent 一致性测试

## 计划

[Agent-Native Project Knowledge Base MVP Implementation Plan](../../../docs/superpowers/plans/2026-08-10-agent-native-project-knowledge-base-mvp.md) 的 Task 6。

## 关联依据

- 功能：F01、F02、F03、F05、F06 的产品验收项。
- 契约：[初始化产物契约](../../02-架构与契约/初始化产物契约.md)、[知识项与 Proposal 契约](../../02-架构与契约/知识项与Proposal契约.md)、[Profile 扩展契约](../../02-架构与契约/Profile扩展契约.md)
- Skill：[项目知识库 Skill](../../../skills/project-knowledge-base/SKILL.md)

## 范围

- 建立 generic、Java、Python、Java+Python 四套黄金知识库。
- 固定期望目录快照，验证包内资产能够独立物化和校验。
- 建立覆盖覆盖保护、过期 Proposal、缺少确认、冲突、追踪、Profile 越界和敏感值的负例。
- 验证初始化不会写 `AGENTS.md`、`CLAUDE.md` 或覆盖既有目标。

## 排除

- 不伪造不可用的第二 Agent 验收；不可取得时保持 `partial`。

## 验收

以实现计划 Task 6 的集成测试、快照和负例精确错误码为准。
