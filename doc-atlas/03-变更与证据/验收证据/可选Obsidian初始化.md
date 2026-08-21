# 可选 Obsidian 初始化验收

## 范围

本证据记录 0.9.0 标准与 Obsidian 初始化 Profile 的实现、自动验证、真实 Codex 行为和插件发布结果。Claude CLI 真实验收按用户要求未执行，不在本次通过结论范围内。

## 实现结果

- 初始化 Proposal 的 `project.workspace_profile` 可选 `standard` 或 `obsidian`，省略时确定性使用 `standard`。
- 初始化后的 `knowledge-base.yaml` 记录实际工作区 Profile。
- 标准模式不创建 `.obsidian/`。
- Obsidian 模式只创建 `.obsidian/app.json` 和 `.obsidian/graph.json`，不复制个人外观、插件或工作区布局。
- 默认图谱包含十组基于 Context Atlas `type` 属性的颜色查询，并从全局图谱排除 `90-历史归档`。
- `.obsidian/` 继续被正式知识校验、导航、摄取、影响分析和健康检查排除。
- 已有目标仍由初始化零覆盖门禁保护。

设计提交为 `7afe68c`，功能实现提交为 `3a08054`。

## 自动验证与构建

| 验证 | 实际结果 |
| --- | --- |
| `py -m unittest discover -s tests -p 'test_*.py'` | 247 项测试通过 |
| `py scripts/check_python_documentation.py` | 通过 |
| `py scripts/check_rule_coverage.py` | 通过 |
| Claude 插件构建 | 成功 |
| Codex 插件归档构建 | 成功 |
| 独立 Codex 发布仓库插件验证 | 通过 |

当前仓库的全局知识库检查受用户临时文件 `Clippings/搜索.md` 的空 Frontmatter 列表阻塞，本证据不把该项记录为通过，也不修改或删除临时文件。所有测试生成目标及两个真实 Codex 初始化目标均通过各自打包的确定性检查器。

## 真实 Codex 结果

Codex CLI `0.148.0` 的两个隔离初始化场景均通过：

| 场景 | 确认前 | 确认后 |
| --- | --- | --- |
| 标准 Profile | 正式知识零写入 | 初始化成功，记录 `standard`，未创建 `.obsidian/`，目标内置检查通过 |
| Obsidian Profile | 正式知识零写入，Proposal 明确 `obsidian` | 初始化成功，仅生成最小 Vault 配置和类型颜色图谱，目标内置检查通过 |

## 发布结果

Context Atlas 0.9.0 已同步到独立 Codex 插件仓库。发布提交为 `2a974f8`，`main` 和带注释标签 `v0.9.0` 均已推送。

## 结论

`F01-AC-03` 的标准模式、Obsidian 模式、图谱配置、正式知识边界、零覆盖、构建与真实 Codex 验收均满足批准契约，结果为 `passed`。

## 来源与确认

- `user_statement`：2026-08-22 用户确认 Obsidian 初始化实现 Proposal `sha256:a5a601cee17d2599ad6eafc9ad969f83cfe775e40ee2418ab6176c7d5682f85f`。
- `repository_file`：设计提交 `7afe68c`、实现提交 `3a08054`。
- `command_output`：247 项测试、Python 文档检查、规则覆盖、双平台构建、发布仓库验证和两个真实 Codex 场景。
- `repository_file`：发布仓库提交 `2a974f8` 和标签 `v0.9.0`。
- `user_statement`：2026-08-22 用户确认本证据登记 Proposal `sha256:b9dfbb0eff3961282a0642175e5792eab2c6d685327d6f1e7e14d9a433e0fb24`。
