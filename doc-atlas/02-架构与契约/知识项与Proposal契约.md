---
id: CONTRACT-KNOWLEDGE-001
type: contract
title: 知识项与 Proposal 契约
status: approved
last_updated: 2026-08-25
---

# 知识项与 Proposal 契约

## 版本与修订模型

| 概念 | 字段 | 唯一权威 | 约束 |
| --- | --- | --- | --- |
| Context Atlas 产品版本 | `product_version` | 当前宿主插件清单 | SemVer；模板、兼容清单和执行器不得复制维护 |
| 业务项目版本 | `project_version` | `knowledge-base.yaml` | 可选；格式升级必须保持原值 |
| 知识格式版本 | `format_version` | `knowledge-base.yaml` | 正整数；唯一参与可读、可写和转换判断的版本 |
| 知识库修订 | `knowledge_revision` | `knowledge-base.yaml` | 正整数；每次正式知识事务成功后单调递增 |
| 知识项修订 | `content_revision` | 知识项元数据 | 正整数；只描述同一稳定 ID 的内容修订 |
| 领域对象版本 | 类型专用字段或 `subject_version` | 对应知识项 | 只描述 API、协议、文件格式等被记录对象的真实版本 |

`created_by.product_version` 只记录知识库由哪一版工具生成，不参与兼容判断。兼容清单使用 `manifest_version`、`supported_format_versions`、`created_format_version` 和 `conversions`；不得保存或比较 `plugin_version`。

新知识项使用 `content_revision`。格式 7 的通用 `version` 在一个兼容周期内继续读取；能够确定性映射时转换，无法确定性映射时保存为 `legacy_version` 并要求人工复核，不得猜测为某个修订号或领域版本。

## 知识项

正式知识项至少包含唯一 ID、类型、标题、状态、内容修订、来源和更新时间。批准内容还必须记录确认人、确认时间和被替代修订或身份。

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

Proposal 必须记录目标知识项、候选内容、来源、假设、未决问题和所依据的知识格式版本与知识库修订。Agent 在用户确认前不得把 Proposal 写成批准基线。

外部 OpenSpec、Spec Kit、Issue 或 Agent 任务可以成为 Proposal 来源或关系目标，但其批准、完成或归档状态不等于 Context Atlas 的正式确认。变更合并当前基线仍须通过对应知识维护 Skill 的精确 Proposal 确认门禁。

## 冲突

冲突必须保留各来源和值，标记需要项目责任人裁决。Agent 不得根据“更像正确答案”自行覆盖。
