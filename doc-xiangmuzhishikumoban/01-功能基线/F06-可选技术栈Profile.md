---
id: F06
type: feature
title: 可选且可组合的技术栈 Profile
status: baselined
phase: mvp
priority: P1
current_slice: included
depends_on: [F04, F05]
acceptance: [F06-AC-01, F06-AC-02]
contracts: [CONTRACT-PROFILE-001]
adr: [ADR-003]
last_updated: 2026-08-10
---

# F06：可选且可组合的技术栈 Profile

## 目标

核心知识库不限制语言；Profile 只按需增加技术栈知识、模板和校验规则。

## 当前范围

- 支持零个、一个或多个 Profile。
- 第一阶段维护 Java 和 Python。
- 支持 Java+Python 混合项目。

## 验收

- `F06-AC-01`：无 Profile、Java、Python 和 Java+Python 四种初始化结果均符合核心协议。
- `F06-AC-02`：Profile 只能增加约束，移除 Profile 不删除历史知识或改变核心规则。
