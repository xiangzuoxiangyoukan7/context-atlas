---
id: F01
type: feature
title: Agent 驱动的知识库初始化
status: baselined
phase: mvp
priority: P0
current_slice: included
depends_on: []
acceptance: [F01-AC-01, F01-AC-02, F01-AC-03]
contracts: [CONTRACT-INIT-001]
adr: [ADR-002, ADR-008]
last_updated: 2026-08-22
---

# F01：Agent 驱动的知识库初始化

## 目标

用户在项目根目录的 AI Agent 中提出初始化请求，Agent 根据可安装 Skill 创建 `doc-<项目目录名>/`。

## 包含

- 根据当前目录名生成默认知识库名称。
- 允许用户明确覆盖项目名称。
- 初始化统一知识库，不选择技术栈或技术栈模板。
- 默认使用标准工作区；用户可明确选择 Obsidian 模式并获得最小 Vault 与关系图谱颜色配置。
- 初始化前展示目录和首版候选内容。
- 目标存在时停止并转入更新流程。
- 根据当前宿主 Agent 创建或补充对应的 `AGENTS.md` 或 `CLAUDE.md` 入口说明。

## 排除

- 独立用户 CLI。
- 覆盖项目已有的 Agent 入口文件内容。
- 未经用户确认直接建立批准基线。

## 验收

- `F01-AC-01`：Agent 能按初始化产物契约生成完整、自包含的 `doc-<项目名>/`。
- `F01-AC-02`：初始化不会覆盖已有目录；若 Proposal 明确了当前宿主，则只创建或补充对应入口文件的 Context Atlas 受管区块，并保留原内容。
- `F01-AC-03`：标准和 Obsidian 初始化模式均产生可验证且不覆盖已有配置的目标，Obsidian 展示配置不进入正式知识治理。
