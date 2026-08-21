---
id: F02
type: feature
title: AI 知识采集与确认
status: baselined
phase: mvp
priority: P0
current_slice: included
depends_on: [F01]
acceptance: [F02-AC-01, F02-AC-02, F02-AC-03]
contracts: [CONTRACT-KNOWLEDGE-001]
adr: [ADR-002, ADR-004]
last_updated: 2026-08-21
---

# F02：AI 知识采集与确认

## 目标

知识库向 Agent 声明缺失信息，Agent 调研项目并询问用户，以 Proposal 形式提交候选知识；已有知识库通过按治理语义拆分的正式维护 Skill 进入新增、修订或退役流程。

## 规则

- 区分用户陈述、仓库事实、命令证据、外部资料和 AI 推测。
- 用户确认前，候选内容保持 `proposed`。
- AI 推测不得直接成为批准事实。
- 多个来源冲突时必须保留冲突并请求用户裁决。
- 正式知识维护入口分为 `context-atlas-add`、`context-atlas-revise` 和 `context-atlas-retire`；不保留通用 `context-atlas-update` 兼容入口，新入口就绪时直接替换旧入口。
- 三个 Skill 只定义触发边界、协议加载、流程编排和停止条件，共享 `references/` 中的执行协议及同一套确定性执行器。
- 同一请求同时包含新增、修订和退役时，必须形成一个原子复合 Proposal，避免分步写入留下半完成状态。

## 验收

- `F02-AC-01`：Agent 可以从协议获得缺失知识、目标位置、Schema 和确认要求。
- `F02-AC-02`：Proposal、用户确认和冲突处理均能保留来源，且 AI 不能自行批准或裁决。
- `F02-AC-03`：Agent 能将新增、修订或同步与替代、退役或归档与受控删除路由到对应 Skill，并继续遵守同一修订 Proposal 的显式确认门禁。
