# Task 4 brief — 用户安装与发布说明

读取计划 Task 4。当前 Marketplace 发布包根为 `marketplaces/context-atlas/`，因为仓库根 `.agents` 只读。两个索引已存在，插件契约测试 13 个通过。

修改 `README.md`，创建 `docs/marketplace-installation.md`，并在 `doc-atlas/03-实施与验收/验收矩阵.md` 增加 Marketplace 验收项。文档必须明确：

- 这是 Agent Skill/插件，不是 Python 包，不需要 `pip install`；
- Codex 用户添加 `marketplaces/context-atlas` 作为 Marketplace，打开 `/plugins` 安装 `context-atlas`，安装后新建会话；
- Claude Code 用户添加同一个 Marketplace 根并安装 `context-atlas`，安装后新建会话；
- 目标项目中使用自然语言或 `/context-atlas:context-atlas`；
- 初始化先展示 Proposal，用户确认后才写入；
- Claude 当前真实确认后初始化验收仍为 partial，不能写成双平台完全通过；
- 当前 Marketplace 包路径是仓库相对路径，发布到外部仓库时替换为实际克隆路径或 URL。

先增加文档检查测试（可在 `tests/unit/test_plugin_contract.py` 中加入静态文本断言），运行确认失败；再实现 README/文档和验收矩阵；最后运行文档测试、插件契约测试和 `git diff --check`。当前无法写 `.git/index.lock`，不必提交；报告写入 task-4-report.md。
