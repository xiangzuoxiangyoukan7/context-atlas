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
- 只支持项目级安装：Codex 使用目标项目的 `.codex/` 作为 `CODEX_HOME`，Claude Code 安装命令使用 `--scope project`。
- 保持两个平台使用同一份 Context Atlas Skill 和一致的安装确认门禁。
- Codex 使用 `$context-atlas init`、`$context-atlas update`，Claude Code 使用 `/context-atlas:init`、`/context-atlas:update`。
- 固定操作符触发正式写入；自然语言用于调研、补充需求和确认，不单独触发正式写入。
- 安装后要求新建 Agent 会话，初始化知识库前先展示 Proposal。

## 当前验证状态

仓库已有项目级安装说明、固定操作符适配和相应测试变更。当前相关单元测试运行 53 项，其中 2 项失败：项目内 `.codex/plugins/cache/` 的已安装 Skill 被仓库唯一 Skill 契约扫描为第二份副本。该冲突解决并重新验证前，不宣称本任务完成。

## 验收

- `KB-AC-42`：两个平台能在项目隔离范围内发现并安装同一个 Skill，使用各自固定操作符；Claude 的真实确认后初始化行为仍单独记录。
- `KB-AC-43`：安装不依赖 `pip install`，不会写入用户级插件配置，正式知识写入遵守固定操作符、Proposal 和明确确认门禁。

证据见 [Marketplace 安装与使用](../../../docs/marketplace-installation.md)。
