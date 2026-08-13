---
id: TASK-KB-009
type: governance_task
title: 格式兼容与轻量迁移
plan: docs/superpowers/plans/2026-08-13-remaining-knowledge-operations.md
status: completed
acceptance: [KB-AC-36, KB-AC-37, KB-AC-38]
last_updated: 2026-08-13
---

# TASK-KB-009：格式兼容与轻量迁移

## 范围

- 区分项目业务版本 `project_version` 与知识库结构版本 `format_version`。
- 使用兼容声明只读诊断当前格式；未知格式禁止正式写入。
- 只在知识表达逻辑变化时提供等价转换，不强制升级可读旧格式。
- 迁移先生成带修订号的提案，存在歧义或确认修订号不一致时零写入。
- 旧 `sources` 保留为兼容字段，统一文件关系 `rel_supported_by` 成为当前权威关系。

## 验收

- `KB-AC-36`：版本职责与兼容声明可确定性诊断。
- `KB-AC-37`：旧来源关系可无歧义等价转换且不改变业务版本。
- `KB-AC-38`：Codex 与 Claude Code 可使用相同 JSON 命令协议执行。

证据见[格式兼容、身份与主动采集](../验收证据/格式兼容身份与主动采集.md)。

