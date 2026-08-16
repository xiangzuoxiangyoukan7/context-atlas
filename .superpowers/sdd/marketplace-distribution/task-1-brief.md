# Task 1 brief — 扩展插件契约测试，先固定 Marketplace 行为

读取仓库计划 `docs/superpowers/plans/2026-08-17-marketplace-distribution.md` 的 Task 1，但以本文件为本任务要求来源。

修改 `tests/unit/test_plugin_contract.py` 和 `scripts/project_kb/plugin_contract.py`，为 `.agents/plugins/marketplace.json` 与 `.claude-plugin/marketplace.json` 增加确定性读取和契约校验。

必须提供：

- `load_marketplace_manifests(root: Path) -> tuple[dict[str, object], dict[str, object]]`；
- `validate_plugin_contract(root: Path) -> list[str]` 继续作为统一入口；
- 缺失、JSON 错误、根节点类型错误、字段类型错误返回可读错误列表；
- 两个平台 Marketplace 的第一条插件条目名称必须是 `context-atlas`；
- 来源路径必须是 `./plugins/context-atlas`；
- 条目必须包含 `name`、`source`、`policy`、`category`；
- policy 必须包含 `installation`、`authentication`，并允许值分别为 `NOT_AVAILABLE|AVAILABLE|INSTALLED_BY_DEFAULT` 与 `ON_INSTALL|ON_USE`；
- 两个平台索引中的插件身份必须与两个插件清单的 name、version、repository 对齐；
- 先增加会因文件不存在而失败的测试，再实现最小代码；
- 不创建 Marketplace 文件，本任务只做读取和校验逻辑与测试。

运行：`py -m unittest tests.unit.test_plugin_contract`。

实现完成后提交本任务变更，并在 `.superpowers/sdd/marketplace-distribution/task-1-report.md` 写报告，包含提交 hash、测试命令、完整结果和剩余疑问。返回只需说明状态、提交、测试摘要和 concerns。
