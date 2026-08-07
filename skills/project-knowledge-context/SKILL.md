---
name: project-knowledge-context
description: Read a project knowledge base and produce a traceable context summary before planning.
---

# Project Knowledge Context

Use this skill when an AI needs to understand a project before generating an execution plan.

## Procedure

1. Read the project adapter, README, AI collaboration rules and CURRENT.
2. If CURRENT has no executable task, stop at the declared governance action.
3. If a task exists, read only its linked feature, contracts, ADRs, selected profiles and acceptance rows.
4. Produce a context summary with sources, assumptions, boundaries, dependencies, unresolved questions and acceptance references.
5. Never infer current requirements from archives or unlinked documents.

## Output contract

The summary must distinguish:

- confirmed facts;
- approved design decisions;
- open decisions;
- excluded scope;
- acceptance criteria and evidence gaps.

This skill does not execute implementation steps and does not approve content correctness.

