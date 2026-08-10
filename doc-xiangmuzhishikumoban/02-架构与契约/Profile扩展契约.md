---
id: CONTRACT-PROFILE-001
type: contract
title: Profile 扩展契约
status: approved
last_updated: 2026-08-10
---

# Profile 扩展契约

- 核心知识库不得要求选择 Profile。
- 一个项目可以选择零个、一个或多个 Profile。
- Profile 只能增加字段、模板、知识请求和验收项。
- Profile 不得覆盖核心状态、权威来源、确认规则和验收结果。
- 增加 Profile 后，Agent 必须报告新增的知识缺口。
- 移除 Profile 时保留已经产生的知识和历史，只停止对应强制检查。
- 当前正式维护 `java.v1` 与 `python.v1`。
