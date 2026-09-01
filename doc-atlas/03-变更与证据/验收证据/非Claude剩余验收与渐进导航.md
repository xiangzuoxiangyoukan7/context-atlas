---
id: EVID-004
type: acceptance_evidence
title: 非Claude剩余验收与渐进导航
rel_classified_under:
  - "[[03-变更与证据/验收证据/README|IDX-EVIDENCE]]"
---
# 非 Claude 剩余验收与渐进导航

## 范围

本证据闭环除 Claude 确认后初始化之外的剩余产品验收，并核实此前标记为暂缓的渐进式加载能力。Claude 外部调用超时及 `KB-AC-27`～`KB-AC-29` 不在本次关闭范围内。

## 验收结论

| 验收项 | 结果 | 证据摘要 |
| --- | --- | --- |
| F01-AC-01 | passed | 初始化器和 Codex 确认后场景生成完整、自包含知识库；构建安装形态参与测试。 |
| F01-AC-02 | passed | 已有目标保留，初始化产物不包含 `AGENTS.md`、`CLAUDE.md`。 |
| F02-AC-01 | passed | 初始化及维护 Skill 加载缺失知识、Schema、来源和确认协议。 |
| F02-AC-02 | passed | Proposal 修订不匹配时保持零写入；来源、冲突和确认状态由 Schema 与检查器验证。 |
| F02-AC-03 | passed | `context-atlas-add`、`context-atlas-revise`、`context-atlas-retire` 职责分离，并共用确定性执行器和同修订确认门禁。 |
| F03-AC-01 | passed | 黄金样例中的批准知识包含来源、确认信息和有效版本，检查器验证追溯链。 |
| F03-AC-02 | passed | 替代、归档和双向替代关系已有生命周期测试；共享更新执行器在验证失败或异常时原子回滚。 |
| F05-AC-02 | passed | 单技术栈、多技术栈黄金样例通过，规定结构、追溯、冲突、安全和关系反例返回精确问题码。 |

## 渐进式加载核实

渐进式加载已经完成，不再属于暂缓范围：

1. `context-atlas-navigate` 默认从知识库入口使用 `children` 逐层发现，只返回直接子项摘要。
2. 定位稳定 ID 或路径后使用 `neighbors` 查询一跳正向与反向关系。
3. 多跳分析使用带 `--start`、`--depth` 和 `--max-nodes` 的有界 `graph`。
4. 全图查询必须显式使用 `--all`；`truncated: true` 表示结果不完整，不得据此推断遗漏节点。
5. `scripts/project_kb/navigation.py`、统一命令入口、安装包内置资产和 `tests/unit/test_navigation.py` 已覆盖上述行为。

## 实现与验证证据

- 原子更新异常回滚修复：`0c91abb`。
- 聚焦验收：31 个测试通过。
- 全量验收：231 个测试通过。
- 项目知识库检查：通过。
- 插件结构校验：通过。
- Claude 构建与 Codex 构建：通过。
- `git diff --check`：通过。

## 保留的未完成项

Claude Code 的 `initialize_after_confirmation` 仍因外部调用超时而没有可用结论；`KB-AC-27`、`KB-AC-28`、`KB-AC-29` 继续保持 `partial`，不得从本证据推断其通过或失败。

