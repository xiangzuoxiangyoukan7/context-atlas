# Marketplace 安装与使用

Context Atlas 是 Agent Skill/插件，不是 Python 包，不需要 `pip install`。仓库根目录是唯一插件源码；
`.agents/plugins/marketplace.json` 是 Codex Marketplace 索引，`.claude-plugin/marketplace.json`
是 Claude Code Marketplace 索引，两者都指向根目录中的同一份 `context-atlas` Skill。

开发者从仓库根目录构建平台发布包：

```powershell
py scripts/build_plugin.py claude --output build/claude/context-atlas
py scripts/build_plugin.py codex --output build/codex/context-atlas.zip --archive
```

构建产物只包含目标平台清单、Skill、运行时资产和命令，不包含测试、设计文档或本项目知识库。

## Codex

1. 在终端执行：

   ```powershell
   codex plugin marketplace add D:\loong-workspace-python\context-atlas
   codex plugin add context-atlas@context-atlas-dev
   ```

2. 也可以打开 `/plugins`，找到并安装 `context-atlas`。
3. 安装后新建会话，使会话载入已安装的 Skill。

## Claude Code

1. 在终端执行：

   ```powershell
   claude plugin marketplace add D:\loong-workspace-python\context-atlas
   claude plugin install context-atlas@context-atlas-dev
   ```

2. 也可以在 Marketplace 界面中安装 `context-atlas`。
3. 安装后新建会话，使会话载入已安装的 Skill。

本地开发时使用仓库的实际克隆路径；正式发布时使用发布仓库或构建产物对应的 URL。

## 在目标项目中使用

在目标项目中，Skill 只负责生成 Proposal。初始化或更新必须调用命令；只有用户明确确认后才写入正式知识。
自动检查通过只代表
结构和引用满足规则，不能替代用户确认内容。

安装完成后，在 Agent 会话中使用短命令：

```text
/context-atlas:init
/context-atlas:update
```

命令会自动生成 Proposal；只有用户明确确认后才执行正式写入。底层 Python 执行器由插件内部调用，
不作为用户接口。

## 当前验收状态

Marketplace 清单和共享 Skill 契约已通过自动检查。Codex 执行链路已验证；Claude Code 当前真实确认后
初始化验收仍为 **partial**，因此不能表述为双平台完全通过。详见[验收矩阵](../doc-atlas/03-实施与验收/验收矩阵.md)
及其中的跨 Agent 验收证据。
