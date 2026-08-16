# Task 3：Marketplace plugin_root 兼容性报告

## 结论

`CodexRunner` 与 `ClaudeRunner` 原先将 `plugin_root` 固定解释为仓库根目录；直接传入 `marketplaces/context-atlas` 会重复拼接发布路径，且 Claude 无法找到根目录下的插件清单。现已做最小兼容：通过 Marketplace 索引及候选源目录中的实际插件资源（`.codex-plugin`/`skills`）解析源根目录，再构造临时运行包；不依赖目录名称特判，原有仓库根目录参数行为不变。未修改 `plugin_contract`。

## 变更与验证

- 修改：`scripts/agent_conformance/codex_runner.py`
- 修改：`scripts/agent_conformance/claude_runner.py`
- 补测：两个 unit test 各增加发布目录参数回归测试。
- 发布目录识别改为基于 Marketplace 索引和候选源目录资源（`.codex-plugin`/`skills`）解析，不依赖目录名称特判；运行时仍只复制发布索引及允许的插件资源到临时目录，不写回仓库。
- Codex 发布包边界断言已移入 `TemporaryDirectory` 上下文内，并验证 `AGENTS.md`、`tests/` 不进入临时发布包。
- 命令：`py -m unittest tests.unit.test_plugin_contract tests.unit.test_codex_runner tests.unit.test_claude_runner`
- 结果：37 个测试全部通过。

## 修正记录

- 根据 review 更新顶部结论，使其与当前基于索引和资源解析的实现一致；未改动代码。
