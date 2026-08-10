---
name: project-knowledge-base
description: Use when a user asks an AI Agent to initialize, inspect, explain, update, migrate, or validate a self-contained project knowledge base, including doc-* directories and optional Java or Python project knowledge.
---

# Project Knowledge Base

## Overview

Operate a tool-neutral project knowledge base on the user's behalf. Treat repository evidence, AI inference, user approval, stored knowledge, and structural validation as distinct things.

## Choose the operation

| Request | Required references |
| --- | --- |
| Initialize a knowledge base | Read [初始化协议](references/初始化协议.md) and [知识采集与确认](references/知识采集与确认.md). |
| Inspect or explain one | Read its root README and `knowledge-base.yaml`, then [知识采集与确认](references/知识采集与确认.md). |
| Update, resolve conflict, supersede, add/remove Profile | Read [知识采集与确认](references/知识采集与确认.md) and [更新冲突与归档](references/更新冲突与归档.md). |
| Validate or report results | Read [验证与结果报告](references/验证与结果报告.md). |

For combined requests, read every referenced file before writing.

## Core workflow

1. Resolve and verify the user-selected project root.
2. Inspect the repository and existing knowledge base without changing either.
3. Separate confirmed facts, repository observations, AI inference, unknowns, and conflicts.
4. Present the exact target paths and a Proposal; obtain explicit confirmation（显式确认）before formal writes.
5. Materialize or update only the confirmed scope using bundled `assets/`.
6. Run the bundled deterministic validator.
7. Return the report contract from [验证与结果报告](references/验证与结果报告.md).

## Non-negotiable boundaries

- Derive the default target as `doc-<项目目录名>`; accept a safe single-directory override only when the user states it.
- If the target already exists（目标已存在）, stop initialization and use the update workflow. Never overwrite or reinitialize it.
- Profiles are optional and composable. Recommend them from evidence, but include only confirmed selections.
- Never create or maintain `AGENTS.md`, `CLAUDE.md`, or another Agent-specific adapter. Explain this knowledge base so each Agent can create its own adapter if needed.
- Never store passwords, tokens, private keys, or unredacted personal data.
- Never treat validator success as content approval.

## Assets

Use `assets/templates/core/doc-project/` as the core source. Use only `java.v1` and `python.v1` from `assets/profiles/`. Copy `assets/scripts/` and `assets/schemas/` into the target `.project-kb/` validation bundle during initialization. Do not use undeclared assets.
