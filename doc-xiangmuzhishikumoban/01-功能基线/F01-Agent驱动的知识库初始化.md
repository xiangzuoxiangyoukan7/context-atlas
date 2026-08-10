---
id: F01
type: feature
title: Agent 驱动的知识库初始化
status: baselined
phase: mvp
priority: P0
current_slice: included
depends_on: []
acceptance: [F01-AC-01, F01-AC-02]
contracts: [CONTRACT-INIT-001]
adr: [ADR-002]
last_updated: 2026-08-10
---

# F01：Agent 驱动的知识库初始化

## 目标

用户在项目根目录的 AI Agent 中提出初始化请求，Agent 根据可安装 Skill 创建 `doc-<项目目录名>/`。

## 包含

- 根据当前目录名生成默认知识库名称。
- 允许用户明确覆盖项目名称。
- 初始化通用知识库，不强制选择 Profile。
- 初始化前展示目录和首版候选内容。
- 目标存在时停止并转入更新流程。

## 排除

- 独立用户 CLI。
- 自动生成 Agent 专属入口文件。
- 未经用户确认直接建立批准基线。

## 验收

- `F01-AC-01`：Agent 能按初始化产物契约生成完整、自包含的 `doc-<项目名>/`。
- `F01-AC-02`：初始化不会覆盖已有目录，也不会生成 `AGENTS.md`、`CLAUDE.md` 等专属文件。
