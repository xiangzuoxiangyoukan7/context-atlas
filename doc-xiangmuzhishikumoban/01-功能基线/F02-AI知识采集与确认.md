---
id: F02
type: feature
title: AI 知识采集与确认
status: baselined
phase: mvp
priority: P0
current_slice: included
depends_on: [F01]
acceptance: [F02-AC-01, F02-AC-02]
contracts: [CONTRACT-KNOWLEDGE-001]
adr: [ADR-002]
last_updated: 2026-08-10
---

# F02：AI 知识采集与确认

## 目标

知识库向 Agent 声明缺失信息，Agent 调研项目并询问用户，以 Proposal 形式提交候选知识。

## 规则

- 区分用户陈述、仓库事实、命令证据、外部资料和 AI 推测。
- 用户确认前，候选内容保持 `proposed`。
- AI 推测不得直接成为批准事实。
- 多个来源冲突时必须保留冲突并请求用户裁决。

## 验收

- `F02-AC-01`：Agent 可以从协议获得缺失知识、目标位置、Schema 和确认要求。
- `F02-AC-02`：Proposal、用户确认和冲突处理均能保留来源，且 AI 不能自行批准或裁决。
