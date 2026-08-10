---
id: ADR-002
type: adr
title: Agent 原生且不提供独立用户 CLI
status: accepted
date: 2026-08-10
last_updated: 2026-08-10
---

# ADR-002：Agent 原生且不提供独立用户 CLI

## 背景

知识库的主要使用者是 Codex、ChatGPT、Claude Code 等 AI Agent。用户已经在 Agent 中通过自然语言完成调研和确认，额外的知识库交互式 CLI 会形成重复入口。

## 备选方案

1. 纯 Agent 直接写文件。
2. Agent + Skill、协议、模板、Schema 和确定性检查器。
3. 完整实现 `kb init/status/apply/approve` CLI。

## 决策

选择方案 2。用户只与 Agent 对话；Agent 通过可安装 Skill 初始化和维护知识库，并调用检查器验证结果。第一阶段不提供独立用户 CLI。

本项目不为目标项目生成或维护 `AGENTS.md`、`CLAUDE.md` 等工具专属入口，只提供工具无关协议。具体 Agent 可以按需自行创建薄适配器。

## 影响

必须提供完整模板、稳定 Schema、明确 Proposal 和确认协议、黄金样例及 Agent 一致性验收，以降低不同 Agent 输出差异。

## 回滚条件

只有在 CI、批量初始化或非 Agent 场景出现经验证的需求时，才从现有协议派生独立 CLI。
