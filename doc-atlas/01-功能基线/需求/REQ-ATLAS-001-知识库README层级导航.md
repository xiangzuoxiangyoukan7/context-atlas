---
id: REQ-ATLAS-001
type: requirement
title: 知识库 README 层级导航
status: proposed
approval_status: proposed
lifecycle_status: candidate
spec_readiness: clarifying
priority: P1
stakeholders:
  - Context Atlas 项目维护者
business_rules:
  - 根 README 只直接关联一级子目录 README。
  - 子目录 README 只关联直接父目录 README、直接子目录 README 和本目录知识文件。
  - 不建立跨级或同级目录之间的导航依赖。
  - 具体知识文件的业务关系不因 README 导航而改变。
success_criteria:
  - 从知识库根 README 可以逐级遍历全部受管知识文件。
  - 初始化、更新和校验流程能够生成并检查上述 README 层级关系。
  - 发现缺失、跨级或断裂 README 关系时，校验器能够明确报告。
assumptions:
  - `.project-kb` 运行资产不属于业务知识 README 导航范围。
blocking_questions:
  - 是否需要为历史归档和 Clippings README 增加正式知识 ID，以便纳入机器导航图？
sources:
  - type: user_statement
    reference: "用户确认 Proposal P-20260901-REQ-ATLAS-README-NAV-01"
    observed_at: 2026-09-01T00:00:00+08:00
    confirmation_status: confirmed
    confirmed_at: 2026-09-01T00:00:00+08:00
  - type: repository_file
    reference: doc-landSurvey/README.md 及其子目录 README 层级导航现状
    observed_at: 2026-09-01T00:00:00+08:00
    confirmation_status: observed
rel_classified_under:
  - "[[01-功能基线/需求/README|IDX-REQUIREMENTS]]"
last_updated: 2026-09-01
---

# REQ-ATLAS-001：知识库 README 层级导航

## 背景

Context Atlas 生成的知识库需要以根 `README.md` 作为统一入口，并通过目录层级 README 找到全部受管知识文件。当前插件主要依赖文件布局和知识关系，不能稳定保证 README 的父子导航完整、一致且不跨级。

## 需求范围

插件应在初始化、更新和校验知识库时维护 README 导航层级：根 README 直接列出一级子目录 README；每个子目录 README 继续列出直接子目录 README 和本目录文件；末级 README 通过文件链接覆盖其目录内的知识文件。

## 非目标

- 不改变功能文件与需求文件之间的业务关系。
- 不把 README 导航关系当作业务事实关系。
- 不纳入 `.project-kb` 内部运行资产。
- 本需求当前只入库，不在本次操作中修改插件实现。

## 后续实现方向

后续升级应覆盖核心模板、初始化器、更新器、README 导航生成/修复逻辑、结构校验器、导航查询和跨平台验收测试，并保证重复执行幂等。
