---
id: ADR-004
type: adr
title: 知识维护 Skill 按治理语义拆分
status: accepted
date: 2026-08-21
last_updated: 2026-08-21
---

# ADR-004：知识维护 Skill 按治理语义拆分

## 背景

现有 `context-atlas-update` 同时承载新增、修订、同步、替代、冲突处理、影响分析、归档和删除等职责。按文件 CRUD 将其机械拆为新增、更新和删除，无法表达批准知识的版本、替代、引用迁移与审计保留语义；继续保留通用入口又会使职责边界长期模糊。

## 备选方案

1. 保留 `context-atlas-update`，继续作为所有业务知识维护入口。
2. 新增三个核心 Skill，但保留 `context-atlas-update` 作为兼容路由入口。
3. 按治理语义建立三个直接入口，新入口就绪时删除 `context-atlas-update`。

## 决策

选择方案 3：

- `context-atlas-add` 负责向已有知识库新增知识，包括类型和目标目录判断、稳定 ID、重复与冲突检查、初始关系、影响分析及新增 Proposal。
- `context-atlas-revise` 负责修订、同步和替代已有知识；内部区分同一知识项的 `patch` 与建立新旧版本关系的 `supersede`。
- `context-atlas-retire` 负责知识退役；根据后继关系和审计价值选择替代、归档或经明确确认的物理删除，不把退役简化为删文件。
- 不保留 `context-atlas-update` 兼容路由。三个新 Skill 可用时直接删除旧入口，并同步所有安装、发布和使用说明。
- 三个 Skill 都保持为薄适配层，共享 `references/`、`rules/`、`operations/`、`schemas/` 和确定性执行器，不复制完整治理协议。
- 跨新增、修订和退役的单个用户请求形成一个原子复合 Proposal，确认后统一实施和验证。

## 影响

- 这是破坏性的用户入口变更；根 README、Marketplace 文档、插件清单、构建清单、操作映射、测试和跨 Agent 验收必须在实现时同步。
- 新增、修订和退役获得独立的触发边界与停止条件，降低单个 Skill 的职责复杂度。
- Proposal 修订、显式确认、来源、冲突、影响、原子写入、失败回滚和验证语义继续只有一套权威实现。
- 本决策只批准产品设计，不代表三个新 Skill 已实现或已通过发布验收。

## 与既有决策的关系

本决策细化 [ADR-003](./ADR-003-知识采集协议分层与权威边界.md) 的薄 Skill 分层，不替代 ADR-003；完整执行协议仍以 `references/` 为唯一规范源。

## 来源

- `user_statement`：2026-08-21 用户明确要求直接删除 `context-atlas-update`，并替换为新的维护 Skills。
- `repository_file`：`skills/context-atlas-update/SKILL.md` 当前记录了通用更新入口的过渡性质和职责范围。
- `existing_document`：ADR-003 已确立薄 Skill 与共享执行协议的权威边界。
- `repository_file`：`docs/marketplace-installation.md` 当前声明未来业务知识更新将拆分为更细的 Skills。

## 回滚条件

只有跨 Agent 验收证明三个直接入口无法被支持平台可靠发现或调用，且无法通过插件发布或命名修复解决时，才重新评估统一路由入口；任何恢复都必须形成新的 ADR，不能静默恢复 `context-atlas-update`。
