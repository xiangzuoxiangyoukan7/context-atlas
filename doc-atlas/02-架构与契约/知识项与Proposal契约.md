---
id: CONTRACT-KNOWLEDGE-001
type: contract
title: 知识项与 Proposal 契约
status: approved
last_updated: 2026-08-10
---

# 知识项与 Proposal 契约

## 知识项

正式知识项至少包含唯一 ID、类型、标题、状态、版本、来源和更新时间。批准内容还必须记录确认人、确认时间和被替代版本。

## 来源类型

- `user_statement`
- `repository_file`
- `command_output`
- `existing_document`
- `external_document`
- `ai_inference`

`ai_inference` 只能作为假设，不能直接成为批准事实。

## 状态

知识项使用 `missing`、`proposed`、`approved`、`conflicted`、`stale`、`superseded`、`archived`。实现任务状态和验收结果使用各自独立枚举，不得混用。

## Proposal

Proposal 必须记录目标知识项、候选内容、来源、假设、未决问题和所依据的知识库版本。Agent 在用户确认前不得把 Proposal 写成批准基线。

## 冲突

冲突必须保留各来源和值，标记需要项目责任人裁决。Agent 不得根据“更像正确答案”自行覆盖。
