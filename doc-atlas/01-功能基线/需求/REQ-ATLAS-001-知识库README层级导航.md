---
id: REQ-ATLAS-001
type: requirement
title: 知识库 README 层级导航
status: approved
readiness: ready
priority: P1
rel_classified_under:
  - "[[01-功能基线/需求/README|IDX-REQUIREMENTS]]"
last_updated: 2026-09-02
---

# REQ-ATLAS-001：知识库 README 层级导航

## 问题与价值

Context Atlas 生成的知识库需要让 Agent 稳定判断知识文件的类型、直接分类和查询边界，同时避免 README 人工维护成员清单。当前插件主要依赖文件布局和知识关系，尚未完整约束 README 的目录职责、分类关系、反向成员发现和图遍历停止规则。

本需求面向 Context Atlas 项目维护者，期望在知识项持续新增、移动和归档时保持分类关系可验证、查询范围有边界，并避免因重复维护 README 成员列表产生不一致。

## 范围

插件应在初始化、知识维护、格式升级和校验知识库时维护 README 分类节点及知识项向上的直接分类关系。知识项通过 `rel_classified_under` 主动指向所在目录 README，README 再指向直接父目录 README；成员通过反向索引动态查询，不在 README 中维护文件清单。

## README 的职责

每个正式知识目录的 README 同时承担以下职责：

- **分类节点**：使用稳定 `IDX-*` 身份表示一个知识分类。
- **目录契约**：说明本目录保存什么、允许和禁止什么、命名与身份规则以及如何查询。
- **查询边界**：普通图查询沿分类关系到达 README 后默认停止，只有明确请求分类成员时才反向展开。

文档自身的 `type` 用于识别知识类型，`rel_classified_under` 用于识别其直接分类；两者不能互相替代。

## 分类与查询模型

```text
知识项 ──rel_classified_under──> 直接目录 README
目录 README ──rel_classified_under──> 直接父目录 README
```

- 根 README 是唯一没有父分类的分类节点。
- `children` 用于发现真实目录内容。
- `neighbors` 用于读取直接关系和分类反向成员。
- bounded `graph` 用于有限范围的关系分析。
- 分类成员反向展开继续受查询深度和最大节点数限制。

## 纳入范围

- 根 README。
- `00-项目总览` 至 `05-知识治理` 中的正式知识目录 README 和受 Schema 管理的知识 Markdown。
- `90-历史归档` 的 README 和归档知识；归档内容只能提供历史背景，不能成为当前事实来源。

## 排除范围

- `Clippings`：待摄取外部资料暂存箱，不纳入正式知识图、不要求 `IDX-*`。
- `knowledge-base.yaml`：知识库机器入口，不是知识图节点。
- `.project-kb`：包含脚本、Schema、模板、操作定义、规则、清单和兼容策略，受系统管理但不属于业务知识图。
- `.obsidian`：可选工作区配置，不属于业务知识图。
- 无 Front Matter 的未知 Markdown：不自动猜测归属，应报告为待处理项。

## 维护规则

- 新增普通知识项时，由新文件建立指向直接分类 README 的关系，README 不增加成员清单。
- 普通知识正文修订且分类不变时，不处理导航关系。
- 移动或归档知识项时，更新知识项的物理路径和直接分类关系。
- 新增知识目录时，创建该目录 README 并由它指向直接父级，父级 README 不维护新成员清单。
- 只有目录职责、允许内容、分类父级、查询方式或遍历边界变化时，才修订 README。
- 移动或重命名 README 时，必须修复所有指向它的路径链接。

## 业务规则

| ID | 规则 | 来源 |
| --- | --- | --- |
| BR-ATLAS-001 | 每个正式知识目录必须具有一个带稳定 `IDX-*` 身份的 README 分类节点，根 README 是唯一没有父分类的节点。 | 用户确认 |
| BR-ATLAS-002 | `type` 表示知识类型；普通知识文件通过 `rel_classified_under` 指向所在目录 README，README 指向直接父目录 README。 | 用户确认 |
| BR-ATLAS-003 | README 不维护子目录或成员文件清单，成员通过反向索引动态获得。 | 用户确认 |
| BR-ATLAS-004 | README 正文必须说明目录职责、允许和禁止的知识、命名与身份规则、查询方式和图遍历边界。 | 用户确认 |
| BR-ATLAS-005 | 普通图查询到达 README 后默认停止；明确查询分类成员时才反向展开，并受深度和最大节点数限制。 | 用户确认 |
| BR-ATLAS-006 | `00` 至 `05` 及 `90-历史归档` 纳入正式分类；归档内容不得成为当前事实来源。 | 用户确认 |
| BR-ATLAS-007 | `Clippings`、`knowledge-base.yaml`、`.project-kb` 和 `.obsidian` 不属于业务知识图。 | 用户确认 |
| BR-ATLAS-008 | 无 Front Matter 的未知 Markdown 不自动纳入，应报告为待处理项。 | 用户确认 |
| BR-ATLAS-009 | 新增或修订普通知识项不修改 README；移动或归档时由知识项更新自己的路径与分类关系。 | 用户确认 |
| BR-ATLAS-010 | 只有目录契约或分类节点本身变化时才修订 README；移动 README 时修复全部入向路径。 | 用户确认 |

## 成功标准

| ID | 可观察结果 | 验证方式 | 来源 |
| --- | --- | --- | --- |
| SC-ATLAS-001 | 可以通过 `type` 和 `rel_classified_under` 判断知识类型及直接分类。 | 结构检查与 `neighbors` 查询 | 用户确认 |
| SC-ATLAS-002 | 分类 README 可通过反向索引获得直接成员，新增 `F02` 时 README 内容不变化。 | 新增知识项回归测试 | 用户确认 |
| SC-ATLAS-003 | 普通图查询到达 README 后停止，显式分类查询受 `depth` 和 `max-nodes` 限制。 | bounded `graph` 回归测试 | 用户确认 |
| SC-ATLAS-004 | 检查器能报告缺失、重复、跨级、断裂、循环及物理目录不一致的分类。 | 结构反例测试 | 用户确认 |
| SC-ATLAS-005 | `.project-kb`、`.obsidian` 和 `Clippings` 不被误判为正式分类成员。 | 范围反例测试 | 用户确认 |
| SC-ATLAS-006 | 重复执行检查和查询不会修改正式知识。 | 执行前后摘要对比 | 用户确认 |

## 约束与依赖

- 目录物理归属必须与 `rel_classified_under` 指向的直接分类保持一致。
- 静态结构检查不能替代 `children`、`neighbors` 和 bounded `graph` 的运行时验证。

## 假设

当前没有未确认假设。

## 待澄清问题

| ID | 问题 | 影响范围 | 状态 |
| --- | --- | --- | --- |

## 来源与确认

| 类型 | 精确定位 | 观察时间 | 确认状态 | 确认时间 |
| --- | --- | --- | --- | --- |
| user_statement | Proposal `P-20260901-REQ-ATLAS-README-NAV-01` | 2026-09-01T00:00:00+08:00 | confirmed | 2026-09-01T00:00:00+08:00 |
| repository_file | `doc-landSurvey/README.md` 及其子目录 README 层级导航现状 | 2026-09-01T00:00:00+08:00 | observed | — |
| user_statement | 当前会话对 `BQ-README-NAV-001` 至 `008` 的逐项回答 | 2026-09-01T23:02:05+08:00 | confirmed | 2026-09-01T23:02:05+08:00 |
| user_statement | Proposal `CA-REQUIREMENT-SIMPLIFICATION-20260901-R1` | 2026-09-01 | confirmed | 2026-09-01 |
| command_output | `py -m unittest discover -s tests -p 'test_*.py'`、知识库导航冒烟与三平台构建 | 2026-09-02 | observed | — |

## 校验与运行时验证

静态检查必须报告缺少 README、缺少或重复分类关系、跨级分类、路径或目标 ID 断裂、重复 `IDX-*`、分类循环以及物理目录与直接分类不一致。

查询冒烟或自动化测试必须分别证明：`children` 能发现真实目录成员，`neighbors` 能通过反向索引获得分类成员，普通图查询到达 README 后按边界规则停止，显式分类查询可以在深度和节点数量限制内展开成员。静态结构检查不能替代运行时查询验证。

## 非目标

- 不改变功能文件与需求文件之间的业务关系。
- 不把 README 导航关系当作业务事实关系。
- 不把 `.project-kb`、`.obsidian` 或 `Clippings` 转换成业务知识分类。
- 不在 README 中生成人工成员清单。
- 本需求的实现结果由 F04、F05 及 `EVID-REQ-ATLAS-001` 追溯，知识结构检查通过不替代业务确认。

## 实现范围

实现覆盖核心模板、初始化和升级使用的自包含资产、结构校验器、导航查询及跨平台构建验证，并保证查询与检查不会修改正式知识。实现不重新引入 README 成员清单。
