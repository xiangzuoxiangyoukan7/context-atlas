---
id: ADR-003
type: adr
title: Profile 可选且可组合
status: accepted
date: 2026-08-10
last_updated: 2026-08-10
---

# ADR-003：Profile 可选且可组合

## 背景

项目可能使用未知语言，也可能同时包含 Java 和 Python。强制单一 Profile 会错误限制核心知识库能力。

## 决策

核心知识库不依赖 Profile。项目可以选择零个、一个或多个 Profile。第一阶段正式维护 Java 和 Python，前端暂不进入实现和验收范围。

Profile 只能增加字段、模板、知识请求和检查规则。移除 Profile 不删除既有知识或历史记录。

## 影响

通用模板必须独立完整；Profile 组合需要黄金样例和冲突测试；检查器不得根据源文件自动批准 Profile 选择。
