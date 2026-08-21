---
id: CONTRACT-INGEST-001
type: independent_contract
title: 单来源摄取与维护路由契约
status: approved
scope: project
version: v1
sources:
  - user_statement:2026-08-21-ingest-design-confirmation
  - existing_document:ADR-006
  - existing_document:knowledge-capture-and-confirmation
rel_verified_by:
  - "[[03-变更与证据/验收契约/F02-AC-04-单来源摄取与路由.md|F02-AC-04]]"
last_updated: 2026-08-21
---

# CONTRACT-INGEST-001：单来源摄取与维护路由契约

## 目的与边界

`context-atlas-ingest` 是显式调用的只读摄取与维护路由入口。它读取一个可定位来源，结合知识库中直接相关的当前知识，输出候选映射和路由计划；它不创建或修改知识文件、不写待确认队列、不调用正式维护 Skill，也不生成确认状态或执行共享更新器。

自然语言“摄取”不构成正式知识写入授权。用户查看摄取报告后，必须显式调用 `context-atlas-add`、`context-atlas-revise` 或 `context-atlas-retire` 的一个或多个组合，维护流程重新检查当前知识库状态并生成一个原子复合 Proposal。摄取报告不是批准事实、正式 Proposal 或写入许可。

## 单来源输入

第一版一次只接受一个主来源：一个仓库文件、一条带稳定定位的已有或外部文档、一次用户陈述，或一份可定位的命令输出。输入多个独立来源时返回 `blocked` 并要求拆分，不静默批处理。

主来源必须包含来源类型、精确定位、观察时间，以及可用的摘要、版本、日期或内容摘要值。允许的类型沿用现有来源目录；`ai_inference` 不能作为主来源，只能作为候选中的显式推断。

来源不可读取或无法稳定定位时返回 `blocked`。来源包含密码、Token、私钥或未脱敏个人数据时停止分析，报告不得回显敏感值。

## 渐进读取

开始时读取目标知识库 `README.md`、`knowledge-base.yaml` 和协作规则。知识库不存在时只路由 `context-atlas-init`；格式不兼容时只路由 `context-atlas-upgrade`。

读取范围从来源指向的直接相关知识开始，采用 `children → neighbors → bounded graph`。不得默认递归读取整个知识库；`truncated: true` 不能当作完整结果。

## 候选分类

摄取前先检查稳定 ID、语义重复和当前权威，再为每个候选分配会话内 `candidate_id` 和以下一种 `candidate_action`：

| 动作 | 含义 |
| --- | --- |
| `add` | 发现此前不存在且值得正式维护的新身份或知识 |
| `revise` | 同一稳定身份的内容需要修订、同步或替代 |
| `retire` | 当前权威可能需要替代、归档或受控删除 |
| `conflict` | 来源与当前知识或其他已知来源竞争，必须保留双方并等待裁决 |
| `ignore` | 内容临时、重复、无稳定项目价值或不应保存；必须说明理由 |

不得根据来源“看起来更新”自动覆盖冲突。查询结果只有满足稳定、可复用、来源可定位且非重复时才能作为候选；第一版不自动把普通查询答案转入摄取流程。

## 报告契约

摄取结果是会话内结构化报告，至少包含：

- `source_identity`、`observed_at`、`source_digest_or_version` 和 `scope`；
- 每个候选的 `candidate_id`、`candidate_action`、`target_id_or_path`、`facts`、`inferences`、`unknowns`、`conflicts`、`relation_candidates`、`impact_candidates`、`route_skill` 和 `rationale`；
- 汇总所有候选的单一 `route_plan`；
- `writes_performed: false`、`confirmation_state: not_applicable` 和 `next_action`。

同一来源可以产生多个候选。`route_plan` 只建议用户显式调用一个或多个维护 Skill，不自动触发它们。同一来源涉及新增、修订和退役时，后续维护必须形成一个原子复合 Proposal。

## 兼容与后续演进

第一版不保存 ingest 日志，不新增全局 `index.md` 或 `log.md`，不支持批量来源、自动网页抓取、自动写待确认队列或自动批准。批量确认粒度、持久日志、网页摄取和查询结论主动转候选必须另行提案、确认和验收。

## 来源

- `user_statement`：2026-08-21 用户确认本契约 Proposal `sha256:e26e8c2e435c3e1f37b37b7059c3e56e8a243cf552cd04dc683d7a75ca489133`。
- `existing_document`：ADR-006、F02、ADR-003、ADR-004、知识采集与确认、身份与主动采集、关系与影响分析及执行状态机。
- `repository_file`：当前七个 Skill 的只读与写入职责边界。
- `command_output`：首次应用被 `KB_TYPE_DIRECTORY` 和 `KB_REL_DIRECTION` 拒绝并原子回滚。
