---
id: ADR-006
type: adr
title: 受治理的 LLM Wiki 摄取与场景化使用
status: accepted
date: 2026-08-21
last_updated: 2026-08-21
rel_classified_under:
  - "[[04-决策记录/README|IDX-DECISIONS]]"
---

# ADR-006：受治理的 LLM Wiki 摄取与场景化使用

## 背景

Context Atlas 已具备持久 Markdown、来源、关系、增量维护、冲突保留、渐进导航和结构检查等 LLM Wiki 核心能力，但现有说明主要围绕协议、Schema 和操作符，缺少面向实际使用者的场景化入口。LLM Wiki 强调来源摄取、持续综合和知识复利，其中部分方法可以提升 Context Atlas 的易用性；其“LLM 全权维护”和查询结果自动归档等做法则与正式知识的确认治理冲突。

## 备选方案

1. 只增加独立使用指南，不规划摄取 Skill。
2. 只增加 `context-atlas-ingest` Skill，由 Skill 同时承担使用说明和摄取编排。
3. 独立使用指南与 `context-atlas-ingest` Skill 并存，采用“受治理的 LLM Wiki”模式，并分阶段实施。

## 决策

选择方案 3：

- 独立场景化使用指南与 `context-atlas-ingest` Skill 可以同时存在，二者职责不同。
- 使用指南面向用户说明项目初始化、需求进入、单项数据库补充、资料摄取、查询、审查、修订和退役等实际场景。
- `context-atlas-ingest` 定位为只读摄取与路由入口：读取来源、分析与现有知识的关系、生成新增、修订、退役、冲突或不沉淀的候选映射，并路由到 `context-atlas-add`、`context-atlas-revise` 或 `context-atlas-retire`。
- `context-atlas-ingest` 不直接写入正式知识，不得绕过 Proposal、精确修订确认、来源、冲突、影响分析和确定性验证。
- 查询或分析产生的结论只有达到稳定知识标准时才形成去重候选；不得把每次查询结果自动归档为正式知识。
- 保持 Schema、共享协议、Skill、执行器、检查器和知识库入口之间的职责分层，不采用单一 Agent 配置文件控制全部行为。

## 分阶段实施

第一版实施范围：

1. 编写独立的场景化使用指南。
2. 在目标知识库模板 README 中增加指南入口。
3. 摄取流程一次处理一个来源，保持用户参与和可读的影响确认。

后续阶段另行设计、提案、确认和验收：

- `context-atlas-ingest` Skill 的协议、触发边界、候选映射和路由行为。
- 批量来源摄取及其确认粒度、失败回滚和去重策略。
- 查询结论转知识候选的稳定性判断。
- 孤立、陈旧、冲突、缺少来源和规格覆盖缺口等知识库健康检查增强。

## 影响

- 用户可以先按场景表达目标，不必先理解内部 Schema 和目录结构。
- 来源摄取成为独立的分析与路由语义，但正式写入仍由新增、修订和退役 Skill 承担。
- 第一版可以复用现有导航、审查和维护能力，不要求立即增加新的正式写入入口。
- `ingest` 可能同时发现新增、修订和退役候选；后续设计必须继续使用一个原子复合 Proposal，避免分步写入留下半完成状态。
- 本决策只批准方法论、职责和阶段边界，不代表第一版或后续能力已经实现、发布或通过验收。

## 与既有决策的关系

- 本决策遵守 ADR-003 的协议分层与权威边界。
- 本决策遵守 ADR-004 的知识维护 Skill 职责拆分；`ingest` 只分析和路由，不取代 `add`、`revise` 或 `retire`。
- 具体功能、模板、协议和验收变更在实施阶段另行形成 Proposal。

## 来源

- `user_statement`：2026-08-21 用户认可“受治理的 LLM Wiki”整体方案，确认独立使用指南与 `context-atlas-ingest` Skill 可以并存，同意第一版范围并要求正式记录。
- `existing_document`：`docs/llm-wiki-zh.md` 描述来源、Wiki、Schema、摄取、查询、检查、索引和日志方法。
- `existing_document`：`references/知识采集与确认.md` 规定正式知识的来源、Proposal、显式确认、冲突和主动采集语义。
- `existing_document`：ADR-003、ADR-004 和 CONTRACT-SPEC-001 规定协议分层、维护入口及规格事实基线边界。

## 回滚条件

如果场景化指南与摄取入口造成职责重复、用户无法区分分析与正式写入，或跨 Agent 验收证明 `ingest` 无法可靠路由到现有维护 Skill，应重新评估是否保留独立 `ingest` Skill；任何调整必须形成新的 Proposal，不静默改变本决策。
