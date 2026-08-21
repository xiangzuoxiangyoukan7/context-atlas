---
id: F02
type: feature
title: AI 知识采集与确认
status: baselined
phase: mvp
priority: P0
current_slice: included
depends_on: [F01]
acceptance: [F02-AC-01, F02-AC-02, F02-AC-03, F02-AC-04]
contracts: [CONTRACT-KNOWLEDGE-001, CONTRACT-INGEST-001]
adr: [ADR-002, ADR-004, ADR-006]
last_updated: 2026-08-21
---

# F02：AI 知识采集与确认

## 目标

知识库向 Agent 声明缺失信息，Agent 调研项目并询问用户，以 Proposal 形式提交候选知识；已有知识库通过按治理语义拆分的正式维护 Skill 进入新增、修订或退役流程。用户也可以显式调用只读 `context-atlas-ingest`，将一个可定位来源分析为候选映射和维护路由，再决定是否进入正式维护。

## 规则

- 区分用户陈述、仓库事实、命令证据、外部资料和 AI 推测。
- 用户确认前，候选内容保持 `proposed`。
- AI 推测不得直接成为批准事实，也不得作为 ingest 的主来源。
- 多个来源冲突时必须保留冲突并请求用户裁决。
- `context-atlas-ingest` 第一版一次只接受一个主来源，只输出会话内候选映射与 `route_plan`，保持 `writes_performed: false`。
- ingest 将候选分类为 `add`、`revise`、`retire`、`conflict` 或 `ignore`；它不写待确认队列、不生成正式 Proposal、不自动调用维护 Skill。
- 正式知识维护入口分为 `context-atlas-add`、`context-atlas-revise` 和 `context-atlas-retire`；不保留通用 `context-atlas-update` 兼容入口，新入口就绪时直接替换旧入口。
- 三个维护 Skill 只定义触发边界、协议加载、流程编排和停止条件，共享 `references/` 中的执行协议及同一套确定性执行器。
- 用户根据 ingest 报告显式调用一个或多个维护 Skill 后，必须重新检查当前知识库，并把同一请求中的新增、修订和退役形成一个原子复合 Proposal，避免分步写入留下半完成状态。

## 验收

- `F02-AC-01`：Agent 可以从协议获得缺失知识、目标位置、Schema 和确认要求。
- `F02-AC-02`：Proposal、用户确认和冲突处理均能保留来源，且 AI 不能自行批准或裁决。
- `F02-AC-03`：Agent 能将新增、修订或同步与替代、退役或归档与受控删除路由到对应 Skill，并继续遵守同一修订 Proposal 的显式确认门禁。
- `F02-AC-04`：显式 ingest 能对单个来源生成结构化候选与可解释路由，正确阻塞多来源、冲突和敏感输入，并在 Codex 与 Claude 安装形态中始终保持零写入。
