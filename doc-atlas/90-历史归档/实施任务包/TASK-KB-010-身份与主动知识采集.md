---
id: TASK-KB-010
type: governance_task
title: 身份与主动知识采集
plan: docs/superpowers/plans/2026-08-13-remaining-knowledge-operations.md
status: completed
acceptance: [KB-AC-39, KB-AC-40, KB-AC-41]
last_updated: 2026-08-13
---

# TASK-KB-010：身份与主动知识采集

## 范围

- 用稳定 `PERSON-*` 编号登记人员，以 Git 名称和邮箱 SHA-256 摘要匹配候选。
- 新身份或歧义身份保持 `PERSON-UNKNOWN`，首次映射必须人工确认。
- 区分内容提出者、Agent 操作方、内容确认者和 Git 提交者。
- 在八类自然检查点捕获新项目知识，并按目标编号和内容摘要去重。
- 自动捕获只创建 `proposed` 知识提案，不复制其他插件过程全文，不控制任务执行。

## 验收

- `KB-AC-39`：Git 候选匹配不泄露明文邮箱且不自动批准身份。
- `KB-AC-40`：八类检查点只创建去重后的待确认知识提案。
- `KB-AC-41`：模板、Skill、自包含命令和黄金样例保持一致。

证据见[格式兼容、身份与主动采集](../../03-变更与证据/验收证据/格式兼容身份与主动采集.md)。

