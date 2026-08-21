# SDD 后续能力实施设计

## 目标

完成 ADR-005 第一阶段遗留的三项能力：全链路覆盖检查、格式 7 确定性迁移、Review/SDD 适配器跨 Agent 验收。本文是开发设计，不是 Context Atlas 正式事实批准。

## 一、全链路覆盖检查

### 图模型

以稳定 ID 建立有向图：`requirement -> feature -> contract/interface/module -> external task -> acceptance contract -> evidence`。现有 `rel_satisfies`、`rel_uses`、`rel_exposes`、`rel_primary_module`、`rel_participating_modules`、`rel_executes`、`rel_verified_by`、`rel_evidenced_by` 为权威边；`subject_id` 和任务的 `feature` 是受控引用，不从正文推断关系。

### 规则

- `ready` 或当前交付切片中的需求必须至少有一个活动功能通过 `rel_satisfies` 覆盖。
- `ready` 功能必须有实现契约或模块关系，并至少有一个 `acceptance_contract.subject_id` 指向它。
- 具有外部任务引用的变更必须保证任务可回溯到变更或功能，任务描述必须包含验证方式。
- `passed` 验收必须存在证据路径和版本；活动证据不得只引用历史归档。
- 断链为确定性错误；间接覆盖、多个候选实现或业务充分性为 `review_required`。

### 接口

默认 `--level all` 执行；`--level spec` 检查规范与覆盖，`--level readiness` 只检查阻塞项及进入下一阶段的必要覆盖。问题代码使用 `KB_COVERAGE_*`，不得改变外部任务状态。

## 二、格式 7 迁移

### 格式边界

`format_version: 7` 表示知识库具备验收契约与变更工作区目录、规格状态字段兼容语义及格式 7 自包含运行资产。兼容策略读取 1—7，新初始化创建 7，1—6 均提供到 7 的直接转换。

### 迁移内容

- 创建缺失的 `03-变更与证据/变更/README.md`、`03-变更与证据/验收契约/README.md`，内容取自插件当前核心模板。
- 不批量改写现有需求、功能、模块和接口的业务正文；三个新状态字段继续可选，在首次正式修订时补充。
- 将 `knowledge-base.yaml` 更新到 7，不改变 `project_version`。
- 将当前插件的 schemas、scripts、rules、operations、compatibility 和模板同步到 `.project-kb/`，确保迁移后可以确定性复验。

### 原子性和幂等

Proposal 必须包含每个创建/替换文件的原摘要或“不存在”状态。确认后先在同文件系统暂存完整结果，验证通过再替换；任一摘要漂移、目标冲突或验证失败则回滚。已经是 7 时不生成迁移；重复应用同一 Proposal 被拒绝。

## 三、跨 Agent 行为验收

### 场景

1. `review_is_read_only`：显式审查 ready/blocked 规格，正式知识文件摘要保持不变。
2. `review_reports_blockers`：含阻塞问题的规格必须报告 blocked，不能自行补值。
3. `openspec_mapping_is_read_only`：映射 Proposal、Delta、Design、Tasks，输出 `writes_performed=false`。
4. `spec_kit_mapping_is_read_only`：映射 spec、plan、contracts、tasks、checklists，输出 `writes_performed=false`。
5. `external_status_is_not_approval`：外部任务 completed/archive 不得改变 Context Atlas approval 状态。

### 判定

Codex 与 Claude 比较结构化不变量，不比较自然语言全文。每个场景记录文件摘要变化、命令退出码、ready/blocked、工件角色集合和 writes_performed。平台缺失、状态不同、正式知识变化或角色集合不同均失败。

## 实施顺序

1. 新增覆盖检查模块与隔离测试。
2. 升级兼容声明、模板格式和迁移数据结构，补 1—7 迁移与回滚测试。
3. 扩展场景模型、断言、运行器输入和报告比较。
4. 运行全量测试、知识库检查、Skill 校验、Codex/Claude 构建和插件校验。

## 完成标准

- 新增反例分别稳定触发覆盖、迁移和跨 Agent 问题代码。
- 格式 6 样例可迁移到 7，重复应用、摘要漂移和目标冲突保持零部分写入。
- 五个新场景在平台报告中具有相同结构化不变量。
- 现有测试和旧知识库读取保持兼容。
