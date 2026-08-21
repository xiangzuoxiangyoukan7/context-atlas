---
id: F01-AC-03
type: acceptance_contract
title: 可选 Obsidian 初始化
status: approved
approval_status: approved
lifecycle_status: active
spec_readiness: ready
subject_id: F01
behavior_id: BEH-F01-OBSIDIAN-001
verification_kind: automated
edge_case: false
sources:
  - user_statement:2026-08-22-obsidian-initialization-confirmation
  - existing_document:ADR-008
last_updated: 2026-08-22
---

# F01-AC-03：可选 Obsidian 初始化

## 前置条件

- 目标项目不存在同名正式知识库；初始化 Proposal 已按精确修订号确认。

## WHEN

- 用户使用默认标准模式，或明确选择 Obsidian 初始化模式。

## THEN

1. 标准模式不创建 `.obsidian/`，清单记录 `workspace_profile: standard`。
2. Obsidian 模式创建可解析的 `.obsidian/app.json` 和 `.obsidian/graph.json`，清单记录 `workspace_profile: obsidian`。
3. 默认图谱颜色组使用 Context Atlas `type` 属性查询，且全局搜索排除 `90-历史归档`。
4. `.obsidian/` 不参与正式知识校验、导航、摄取、影响分析或健康检查。
5. 已有目标或已有配置不被覆盖；临时剪藏不进入初始化产物与插件包。

## 验证方式

- 确定性测试覆盖两种模式、Proposal Schema、清单、配置 JSON、排除规则、构建资产和零覆盖。
- 真实 Codex 场景分别初始化标准与 Obsidian 模式，并检查实际文件摘要和目标内置校验结果。
