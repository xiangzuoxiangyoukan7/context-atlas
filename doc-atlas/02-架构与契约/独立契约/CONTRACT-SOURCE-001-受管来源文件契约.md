---
id: CONTRACT-SOURCE-001
type: independent_contract
title: 受管来源文件契约
status: approved
scope: project
independence_basis: cross_boundary
version: v1
sources:
  - user_statement:2026-08-22-managed-source-inbox-confirmation
  - existing_document:ADR-009
last_updated: 2026-08-22
---

# CONTRACT-SOURCE-001：受管来源文件契约

## 路径与状态

- 暂存入口固定为 `Clippings/`，标记文件不进入清单。
- 正式登记卡固定为 `05-知识治理/来源资料/SRC-EXT-*.md`。
- 受管原文件固定为 `05-知识治理/来源资料/files/SRC-EXT-*/<摘要前缀>-<安全文件名>`。
- 暂存文件只有 `eligible`、`duplicate` 或 `blocked` 分析状态；执行结果为 `saved`、`duplicate` 或 `blocked`。

## 安全与原子性

可执行文件、超限文件、含秘密或未脱敏个人数据的文本文件必须阻塞并保留。执行器拒绝路径逃逸、符号链接、目标覆盖和确认修订不一致。合格文件必须在目标摘要复核及知识库验证成功后才删除暂存原件；失败时回滚本次新目标。

## 知识边界

登记卡证明文件身份、来源、摘要、导入时间和保存位置。文件内容只有经过既有知识维护 Proposal 才能成为批准需求、功能、契约或决策。
