# Task 2 brief — 增加双平台 Marketplace 发布索引

读取计划 `docs/superpowers/plans/2026-08-17-marketplace-distribution.md` 的 Task 2。当前 Task 1 已完成并修改了 `scripts/project_kb/plugin_contract.py`、`tests/unit/test_plugin_contract.py`；当前工作区尚未有 Marketplace JSON。

由于当前执行环境禁止写入仓库根 `.agents` 目录，本任务使用仓库内的可发布 Marketplace 包目录 `marketplaces/context-atlas/`。用户后续添加该 Marketplace 根目录即可。

本任务创建：

- `marketplaces/context-atlas/.agents/plugins/marketplace.json`
- `marketplaces/context-atlas/.claude-plugin/marketplace.json`

两个索引必须可解析，且包含：

- 非空顶层 `name`；
- `interface.displayName`；
- 非空 `plugins` 数组；
- 第一条插件条目 `name == "context-atlas"`；
- `source.source == "local"`；
- `source.path == "./plugins/context-atlas"`；
- `policy.installation == "AVAILABLE"`；
- `policy.authentication == "ON_INSTALL"`；
- `category == "Productivity"`。

Marketplace 条目不得增加 `version` 或 `repository` 等非标准字段；版本和仓库地址由两个 `plugin.json` 的既有契约校验负责。

先运行当前测试，确认 Marketplace 相关测试因文件缺失而失败；再创建两个 JSON；最后运行：

```powershell
py -m unittest tests.unit.test_plugin_contract
```

同时更新 Task 1 的加载路径与测试 fixture，使其读取 `marketplaces/context-atlas/.agents/plugins/marketplace.json` 和 `marketplaces/context-atlas/.claude-plugin/marketplace.json`。预期 11 个测试全部通过。不要修改 Skill、插件清单或运行器。由于当前环境无法写入 `.git/index.lock`，不必强行提交；把报告写入 `.superpowers/sdd/marketplace-distribution/task-2-report.md`，包含 status、测试命令完整结果和提交/权限说明。返回简短状态。
