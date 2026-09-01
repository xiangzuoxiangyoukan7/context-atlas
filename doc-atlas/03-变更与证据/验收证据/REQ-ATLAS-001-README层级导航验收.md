---
id: EVID-REQ-ATLAS-001
type: acceptance_evidence
title: REQ-ATLAS-001 README 层级导航实现验收
rel_classified_under:
  - "[[03-变更与证据/验收证据/README|IDX-EVIDENCE]]"
---
# REQ-ATLAS-001 README 层级导航实现验收

## 范围

验证 README 分类节点、直接目录关系、目录契约、反向成员查询、图遍历停止边界、排除范围以及自包含运行资产的一致性。本证据记录实现验证结果，不替代项目责任人的业务确认。

## 验收结论

| 验收项 | 结果 | 证据摘要 |
| --- | --- | --- |
| SC-ATLAS-001 | passed | `neighbors` 能从 `IDX-REQUIREMENTS` 反向定位 `REQ-ATLAS-001`，并返回类型、路径和关系。 |
| SC-ATLAS-002 | passed | README 不维护成员清单；成员由 `rel_classified_under` 反向索引获得。 |
| SC-ATLAS-003 | passed | 普通 `graph` 在 README 停止；`--expand-classification-members` 显式展开并受 `depth`、`max-nodes` 限制，截断时返回 `truncated: true`。 |
| SC-ATLAS-004 | passed | 结构测试覆盖缺失 README、直接父级错误、重复分类、循环和物理目录不一致。 |
| SC-ATLAS-005 | passed | `children` 显示 `90-历史归档`，排除 `Clippings`、`.project-kb`、`.obsidian`；Clippings README 不再声明 `IDX-*`。 |
| SC-ATLAS-006 | passed | 检查与导航均为只读操作，重复执行不修改正式知识。 |
| F04-AC-06 | passed | 20 个正式分类 README 模板包含保存边界、身份规则和查询边界。 |
| F05-AC-07 | passed | 分类结构反例测试和真实知识库检查通过。 |

## 实现与验证证据

- 全量测试：`py -m unittest discover -s tests -p 'test_*.py'`，283 项通过，1 项跳过。
- 知识结构：`py scripts/check_knowledge_base.py doc-atlas --schema-root doc-atlas/.project-kb/schemas --format json`，0 个问题。
- 使用验证：内置 `children`、`neighbors`、普通 bounded `graph`、显式分类成员 `graph` 均成功并返回可解析 JSON。
- 构建验证：Claude、Codex、Qoder 三个平台构建成功。
- 差异检查：`git diff --check` 通过。
- 验证日期：2026-09-02。

## 未覆盖边界

本轮没有在三个真实宿主中重新安装插件并执行黑盒验收；构建成功证明发布资产可生成，不等于目标宿主运行环境已经业务验收。
