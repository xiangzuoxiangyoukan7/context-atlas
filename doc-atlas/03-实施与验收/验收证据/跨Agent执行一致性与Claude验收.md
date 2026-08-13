# 跨 Agent 执行一致性与 Claude Code 验收

## 验收范围

本证据覆盖 [TASK-KB-006](../任务包/TASK-KB-006-跨Agent执行一致性与Claude验收.md) 的 `KB-AC-26`～`KB-AC-29`。实现基线为提交 `9372236`，插件版本为 `0.1.0`，执行日期为 2026-08-13。

## 平台与发布物

| 项目 | 实际值 | 结果 |
| --- | --- | --- |
| Codex | `codex-cli 0.147.0` | 四个真实场景全部通过 |
| Claude Code | `2.1.226 (Claude Code)` | CLI 可用；真实场景因 bare 凭据缺失而阻塞 |
| Codex 清单 | `.codex-plugin/plugin.json` | 静态契约测试通过 |
| Claude 发布包 | `.claude-plugin/` 与唯一 `skills/` | `claude plugin validate <临时发布包> --strict` 退出码 0 |

仓库根直接执行 Claude 严格校验会因根 `CLAUDE.md` 产生一条警告并返回非零；该文件是仓库开发入口，不属于插件发布物。将实际发布边界复制到临时目录后，严格校验输出 `Validation passed`。验证结束后临时目录已清理。

## 确定性验证

| 项目 | 命令 | 退出码 | 实际结果 |
| --- | --- | --- | --- |
| Python 全量测试 | `py -m unittest discover -s tests -p 'test_*.py'` | 0 | 107 个测试通过 |
| Skill 资产同步 | `py scripts/sync_skill_assets.py --check` | 0 | 资产同步 |
| 规则覆盖 | `py scripts/check_rule_coverage.py --root .` | 0 | 规则覆盖通过 |
| Python 注释与类型 | `py scripts/check_python_documentation.py --root .` | 0 | 注释与类型检查通过 |
| 单技术栈样例 | `py scripts/check_knowledge_base.py examples/single-stack --schema-root schemas` | 0 | 知识库检查通过 |
| 多技术栈样例 | `py scripts/check_knowledge_base.py examples/multi-stack --schema-root schemas` | 0 | 知识库检查通过 |
| 当前知识库 | `py scripts/check_knowledge_base.py doc-atlas --schema-root schemas` | 0 | 知识库检查通过 |
| 差异格式 | `git diff --check` | 0 | 无格式错误 |

## Codex 真实行为报告

运行命令：`py scripts/run_agent_conformance.py --agent codex --plugin-root . --output .agent-conformance-runs/codex-release.json`。报告状态为 `passed`，本地报告被忽略，不纳入 Git。

| 场景 ID | 状态 | 命令退出码 | 文件证据 |
| --- | --- | --- | --- |
| `initialize_requires_confirmation` | passed | `[0]` | 前后均 0 个文件，零正式写入 |
| `initialize_after_confirmation` | passed | `[0, 0, 0]` | 生成 65 个正式文件；第三个退出码是目标内置检查器结果 |
| `existing_target_is_preserved` | passed | `[0]` | 前后均 1 个文件，变化记录为 0，哨兵摘要不变 |
| `natural_language_triggers_skill` | passed | `[0]` | 前后均 0 个文件，零正式写入 |

Codex 运行使用临时 `CODEX_HOME` 和临时本地 marketplace，只复制认证文件到临时目录，不追加或覆盖用户插件与配置。Windows 临时配置只声明 `sandbox = "unelevated"`；每轮使用 `workspace-write` 与 `--ephemeral`，不使用危险权限绕过参数。Codex `0.147.0` 原生 `resume` 会恢复只读工具权限，因此两阶段场景使用内存中的最小结构上下文在新可写轮次续接，不持久化首轮模型正文。

## Claude Code 真实行为报告

运行命令：`py scripts/run_agent_conformance.py --agent claude --plugin-root . --output .agent-conformance-runs/claude-release.json`。CLI 版本读取成功，但当前环境不存在 `ANTHROPIC_API_KEY` 或受支持的 Bedrock、Vertex、Foundry bare 模式开关；运行器在模型调用前将四个场景全部标记为 `blocked`，没有伪装为通过。

Claude Code 的静态插件校验和模拟运行器测试不能替代这四个真实行为场景。

## 平台对照

执行 `py scripts/run_agent_conformance.py --compare .agent-conformance-runs/claude-release.json .agent-conformance-runs/codex-release.json` 返回非零。原因是 Claude 整体状态不是 `passed`，四个场景无法与 Codex 的真实通过结果形成同等级比较；这证明比较门禁会拒绝不完整证据。

## 验收项映射

| 验收编号 | 证据 | 结果 |
| --- | --- | --- |
| KB-AC-26 | 两个平台清单静态契约、唯一 Skill、发布包严格校验和 107 个测试通过 | passed |
| KB-AC-27 | Codex 确认前/后场景通过；Claude 真实场景因 bare 凭据缺失阻塞 | partial |
| KB-AC-28 | Codex 目标内置检查器和防覆盖场景通过；Claude 尚无真实结果 | partial |
| KB-AC-29 | 比较器实现并正确拒绝 Claude blocked 与 Codex passed 的报告组合 | partial |

## 证据边界

本证据不包含原始对话、会话编号、认证值、完整提示词或临时项目。结构与行为契约通过不等于业务内容真实；自动检查不能替代项目责任人对业务含义、完整性、时效性和安全性的人工确认。
