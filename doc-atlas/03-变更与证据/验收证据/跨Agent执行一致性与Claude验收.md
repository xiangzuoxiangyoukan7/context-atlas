# 跨 Agent 执行一致性与 Claude Code 验收

## 验收范围

本证据覆盖历史任务 `TASK-KB-006` 的 `KB-AC-26`～`KB-AC-29`，并追加 2026-08-21 对规格驱动改造场景的复验。插件版本仍为 `0.1.0`。

## 2026-08-13 基线

实现基线为提交 `9372236`。Codex CLI 0.147.0 的四个基础场景全部通过；Claude Code 2.1.226 的确认前、防覆盖和自然语言场景通过，但确认后初始化未落盘。比较门禁正确拒绝了平台差异。该历史结果保留用于说明问题演进，不覆盖后续复验。

## 2026-08-21 确定性验证

| 项目 | 结果 |
| --- | --- |
| Python 全量测试 | 230 个测试通过，退出码 0 |
| 当前知识库 | 源码检查器和格式 7 内置检查器均通过，退出码 0 |
| Skill 与插件校验 | 通过 |
| Codex 与 Claude 构建 | 通过 |
| 差异格式 | `git diff --check` 通过 |

## Codex CLI 0.148.0 真实行为

| 场景 | 状态 | 命令退出码 | 文件证据 |
| --- | --- | --- | --- |
| `initialize_after_confirmation` | passed | `[0, 0, 0]` | 生成 123 个自包含文件，目标内置检查器退出码 0 |
| `review_is_read_only` | passed | `[0]` | 正式知识摘要不变 |
| `review_reports_blockers` | passed | `[0]` | 正式知识摘要不变 |
| `openspec_mapping_is_read_only` | passed | `[0]` | 正式知识摘要不变 |
| `spec_kit_mapping_is_read_only` | passed | `[0]` | 正式知识摘要不变 |
| `external_status_is_not_approval` | passed | `[0]` | 正式知识摘要不变 |

确认后初始化报告为 `build/agent-conformance/codex-init-confirmed.json`。五项 SDD 报告为 `build/agent-conformance/codex-sdd-readonly.json`；这些脱敏本地报告受 Git 忽略，不作为提交文件。

## Claude Code 2.1.237 真实行为

| 场景 | 状态 | 命令退出码 | 文件证据 |
| --- | --- | --- | --- |
| `initialize_requires_confirmation` | passed | `[0]` | 确认前零正式写入 |
| `initialize_after_confirmation` | blocked | `[]` | 两次外部调用超时，未进入确认后写入，不能判断行为通过或失败 |
| `existing_target_is_preserved` | passed | `[0]` | 已有目标和哨兵摘要不变 |
| `natural_language_triggers_skill` | passed | `[0]` | 未确认时零正式写入 |
| `review_is_read_only` | passed | `[0]` | 正式知识摘要不变 |
| `review_reports_blockers` | passed | `[0]` | 正式知识摘要不变 |
| `openspec_mapping_is_read_only` | passed | `[0]` | 正式知识摘要不变 |
| `spec_kit_mapping_is_read_only` | passed | `[0]` | 正式知识摘要不变 |
| `external_status_is_not_approval` | passed | `[0]` | 正式知识摘要不变 |

相关脱敏报告为 `build/agent-conformance/claude-core.json`、`claude-core-readonly.json` 和 `claude-sdd-readonly.json`，均受 Git 忽略。

## 平台对照

五项 SDD 场景使用相同场景集合执行：

```text
py scripts/run_agent_conformance.py --compare build/agent-conformance/claude-sdd-readonly.json build/agent-conformance/codex-sdd-readonly.json
```

结果为 `passed` 且 `issues: []`。基础四场景尚不能形成完整通过对照，因为 Claude 的 `initialize_after_confirmation` 受外部调用超时阻塞。

## 验收项映射

| 验收编号 | 证据 | 结果 |
| --- | --- | --- |
| KB-AC-26 | 两个平台清单静态契约、唯一 Skills、构建校验和 230 个测试通过 | passed |
| KB-AC-27 | Codex 确认后初始化通过；Claude 确认前通过，但确认后初始化受外部调用超时阻塞 | partial |
| KB-AC-28 | 两个平台防覆盖通过；Codex 自包含目标内置检查通过，Claude 确认后目标尚无可用证据 | partial |
| KB-AC-29 | 五项 SDD 场景平台对照通过；基础初始化场景仍缺 Claude 确认后结果 | partial |

## 证据边界

本证据不包含原始对话、会话编号、认证值、完整提示词或临时项目。结构与行为契约通过不等于业务内容真实；自动检查不能替代项目责任人对业务含义、完整性、时效性和安全性的人工确认。外部调用超时只表示验收环境阻塞，不能伪装成功，也不能推断功能失败。

## 来源与确认

- `repository_file`：提交 `a68523e`、`a9c7563`、`0c18ee1`、`7a37403` 及对应运行器、迁移实现和测试。
- `command_output`：本记录列出的测试、检查、构建、真实场景和平台比较结果。
- `user_statement`：用户确认本次修订 Proposal `sha256:f2351b6a4f52ba2bbd801acfdbf8d3bf80659441089adeefb002bca7afb5846b`。
- 确认日期：2026-08-21。
