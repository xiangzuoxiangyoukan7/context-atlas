---
name: context-atlas
description: Use when a user asks an AI Agent to initialize, inspect, explain, update, migrate, or validate a self-contained project knowledge base, including doc-* directories and optional Java or Python project knowledge.
---

<!-- context-atlas-rules: [[rules/知识治理规则#RULE-AGENT-001|RULE-AGENT-001]] [[rules/知识治理规则#RULE-IMPACT-001|RULE-IMPACT-001]] -->

# Context Atlas

## Overview

Operate a tool-neutral project knowledge base on the user's behalf. Treat repository evidence, AI inference, user approval, stored knowledge, and structural validation as distinct things.

## Choose the operation

| Request | Required references |
| --- | --- |
| Initialize a knowledge base | Read [初始化协议](references/初始化协议.md) and [知识采集与确认](references/知识采集与确认.md). |
| Inspect or explain one | Read its root README and `knowledge-base.yaml`, then [知识采集与确认](references/知识采集与确认.md). |
| Update, resolve conflict, or supersede knowledge | Read [知识采集与确认](references/知识采集与确认.md) and [更新冲突与归档](references/更新冲突与归档.md). |
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
- Technology stacks are project facts. Record every confirmed stack in the shared technology document; never ask the user to select a stack-specific template.
- Never create or maintain `AGENTS.md`, `CLAUDE.md`, or another Agent-specific adapter. Explain this knowledge base so each Agent can create its own adapter if needed.
- Never store passwords, tokens, private keys, or unredacted personal data.
- Never treat validator success as content approval.

## Assets

Use `assets/templates/core/doc-project/` as the only source. Discover and record every confirmed technology in the shared `技术栈与版本.md`; do not ask the user to select a language or stack-specific template. Read the generated rule copy under `assets/rules/` and standard operations under `assets/operations/` as needed. Copy `assets/scripts/` and `assets/schemas/` into the target `.project-kb/` validation bundle during initialization. Do not use undeclared assets.
