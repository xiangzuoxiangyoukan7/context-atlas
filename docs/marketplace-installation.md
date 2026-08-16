# Marketplace 安装与使用

Context Atlas 是 Agent Skill/插件，不是 Python 包，不需要 `pip install`。当前发布包位于仓库相对路径
`marketplaces/context-atlas`，其中包含 Codex 和 Claude Code 各自的 Marketplace 清单，并指向同一个
`context-atlas` Skill。

## Codex

1. 将 `marketplaces/context-atlas` 添加为 Marketplace。
2. 打开 `/plugins`，找到并安装 `context-atlas`。
3. 安装后新建会话，使会话载入已安装的 Skill。

## Claude Code

1. 添加同一个 Marketplace 根 `marketplaces/context-atlas`。
2. 在 Marketplace 中安装 `context-atlas`。
3. 安装后新建会话，使会话载入已安装的 Skill。

如果发布到外部仓库，`marketplaces/context-atlas` 只是本仓库相对路径；请替换为实际克隆路径或 URL。

## 在目标项目中使用

在目标项目中用自然语言请求脉络地图，或使用 `/context-atlas:context-atlas`。初始化或更新前，Agent
必须先展示 Proposal、来源和待确认问题；只有用户明确确认后才写入正式知识。自动检查通过只代表
结构和引用满足规则，不能替代用户确认内容。

## 当前验收状态

Marketplace 清单和共享 Skill 契约已通过自动检查。Codex 执行链路已验证；Claude Code 当前真实确认后
初始化验收仍为 **partial**，因此不能表述为双平台完全通过。详见[验收矩阵](../doc-atlas/03-实施与验收/验收矩阵.md)
及其中的跨 Agent 验收证据。
