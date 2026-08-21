---
id: CONTRACT-KNOWLEDGE-001
type: contract
title: 知识项与 Proposal 契约
status: approved
last_updated: 2026-08-21
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

规格驱动知识进一步区分三个正交维度：

- `approval_status`：内容是否经过责任人确认，例如 `proposed`、`approved`、`rejected`。
- `lifecycle_status`：知识是否为当前权威，例如 `candidate`、`active`、`deprecated`、`retired`。
- `spec_readiness`：内容是否足以进入下一阶段，例如 `draft`、`clarifying`、`ready`、`blocked`。

现有单一 `status` 字段在格式迁移期间继续兼容；新 Schema 落地后由格式升级建立确定性映射。`approved` 或 `active` 均不得推导为 `ready`。阻塞问题必须具有稳定 ID、问题文本、影响范围和状态。

## Proposal

Proposal 必须记录目标知识项、候选内容、来源、假设、未决问题和所依据的知识库版本。Agent 在用户确认前不得把 Proposal 写成批准基线。

外部 OpenSpec、Spec Kit、Issue 或 Agent 任务可以成为 Proposal 来源或关系目标，但其批准、完成或归档状态不等于 Context Atlas 的正式确认。变更合并当前基线仍须通过对应知识维护 Skill 的精确 Proposal 确认门禁。

## 冲突

冲突必须保留各来源和值，标记需要项目责任人裁决。Agent 不得根据“更像正确答案”自行覆盖。
