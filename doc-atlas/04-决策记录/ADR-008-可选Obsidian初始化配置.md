---
id: ADR-008
type: adr
title: 可选 Obsidian 初始化配置
status: accepted
date: 2026-08-22
last_updated: 2026-08-22
---

# ADR-008：可选 Obsidian 初始化配置

## 背景

Context Atlas 的 Markdown、属性和关系链接可以由 Obsidian 展示，但现有初始化无法声明目标知识库是否需要作为 Obsidian Vault 使用，也不会生成图谱颜色配置。Obsidian 配置属于本地展示状态，不能改变正式知识语义或进入知识治理判断。

## 决策

- 初始化增加可选 `workspace_profile`，取值为 `standard` 或 `obsidian`；缺省为 `standard`。
- 只有用户明确要求 Obsidian 模式时，初始化 Proposal 才记录 `workspace_profile: obsidian`。
- Obsidian 模式在知识库根创建最小 `.obsidian/app.json` 和 `.obsidian/graph.json`，并在 `knowledge-base.yaml` 记录所选配置。
- 默认图谱按 Context Atlas 的 `type` 属性设置颜色组，并从全局图谱排除 `90-历史归档`。
- `.obsidian/` 是非正式展示配置，继续被校验、导航、摄取、影响分析和健康检查排除。
- 已有知识库或已有 Obsidian 配置不得被初始化流程覆盖。
- 临时网页剪藏不是产品规则、初始化资产或发布内容。

## 版本与验收

目标版本为 0.9.0，由 `F01-AC-03` 验收标准模式、Obsidian 模式、零覆盖和运行资产一致性。真实 Codex 覆盖本轮新增场景；Claude 真实验收除非用户另行要求，不作为当前门禁。

## 来源与确认

- `user_statement`：2026-08-22 用户要求完成 Obsidian 初始化功能。
- `repository_file`：`doc-atlas/.obsidian/graph.json`。
- `temporary_reference`：`doc-atlas/Clippings/搜索.md`，仅用于本轮观察。
- `user_statement`：2026-08-22 用户确认 Proposal `sha256:a5a601cee17d2599ad6eafc9ad969f83cfe775e40ee2418ab6176c7d5682f85f`。
