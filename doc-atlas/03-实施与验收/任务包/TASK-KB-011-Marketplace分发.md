---
id: TASK-KB-011
type: governance_task
title: 双平台 Marketplace 分发
plan: docs/superpowers/plans/2026-08-17-marketplace-distribution.md
status: in_progress
acceptance: [KB-AC-42, KB-AC-43]
last_updated: 2026-08-17
---

# TASK-KB-011：双平台 Marketplace 分发

## 范围

- 为 Codex 和 Claude Code 提供统一的 `context-atlas` Marketplace 入口。
- 保持两个平台使用同一份 Context Atlas Skill 和一致的安装确认门禁。
- 安装后要求新建 Agent 会话，初始化知识库前先展示 Proposal。

## 验收

- `KB-AC-42`：两个平台可以从 `marketplaces/context-atlas` 发现并安装同一个 Skill；Claude 的真实确认后初始化行为仍单独记录。
- `KB-AC-43`：安装不依赖 `pip install`，初始化写入遵守 Proposal 和明确确认门禁。

证据见 [Marketplace 安装与使用](../../../docs/marketplace-installation.md)。
