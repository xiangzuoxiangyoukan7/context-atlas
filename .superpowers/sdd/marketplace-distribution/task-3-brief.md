# Task 3 brief — 发布包边界与平台运行器

读取计划 `docs/superpowers/plans/2026-08-17-marketplace-distribution.md` 的 Task 3。用户已确认由于根 `.agents` 只读，仓库内 Marketplace 发布包根为 `marketplaces/context-atlas/`。Task 1/2 已在当前工作区完成：契约读取两个索引，13 个插件契约测试通过。

本任务目标：

1. 为发布包增加确定性边界检查：不得把仓库根 `AGENTS.md`、`CLAUDE.md`、测试夹具、`.worktrees/` 或第二份命名为 context-atlas 的物理 Skill 带入运行时发布物。
2. 让 Codex conformance runner 从 `marketplaces/context-atlas/.agents/plugins/marketplace.json` 读取 Marketplace，并在临时 Marketplace 根下复制实际插件发布边界。
3. 让 Claude conformance runner 使用 `marketplaces/context-atlas/` 作为插件发布边界；保留现有 `--plugin-dir`、安全权限和临时会话策略。

约束：

- 不复制第二份物理 `SKILL.md` 到仓库；如果平台运行器需要自包含临时发布包，可以在临时目录复制，不能落回仓库。
- 不改变用户知识库初始化确认协议。
- 不使用危险权限或覆盖用户配置。
- 保持现有 Codex/Claude runner 的测试安全边界。

按 TDD：先增加临时发布包包含开发文件或重复 Skill 时失败的测试，并运行确认失败；再实现最小边界检查和 runner 路径接入；最后运行：

```powershell
py -m unittest tests.unit.test_plugin_contract tests.unit.test_codex_runner tests.unit.test_claude_runner
```

当前环境不能写 `.git/index.lock`，不必强行提交。把报告写入 `.superpowers/sdd/marketplace-distribution/task-3-report.md`，包含 status、测试命令完整结果、未解决问题和提交/权限说明。返回简短状态。
