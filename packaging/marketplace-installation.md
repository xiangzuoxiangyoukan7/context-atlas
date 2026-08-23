# Marketplace 安装与使用

Context Atlas 是 Agent Skill/插件，不是 Python 包，不需要 `pip install`。仓库根目录是唯一插件源码；
`.agents/plugins/marketplace.json` 是 Codex Marketplace 索引，`.claude-plugin/marketplace.json`
是 Claude Code Marketplace 索引，两者都指向根目录中的同一份 `context-atlas` Skill。

开发者从仓库根目录构建平台发布包：

```powershell
py scripts/build_plugin.py claude --output build/claude/context-atlas
py scripts/build_plugin.py codex --output build/codex/context-atlas.zip --archive
py scripts/build_plugin.py qoder --output build/qoder/context-atlas
py scripts/build_plugin.py trae --output build/trae/context-atlas
```

开发仓库不作为 Skill 运行目录。模板、Schema、脚本、规则、操作定义和兼容策略均只在各自根目录维护；
`assets/manifest.json` 是运行资产白名单，构建时才生成插件内的完整 `assets/`。开发测试必须先构建插件，
再对安装形态中的运行资产和行为进行验证，不能回退为直接读取开发仓库的 `assets/` 副本。

Codex 的正式发布仓库不是手工打包目录。完成源码修改和检查后执行：

```powershell
py scripts/sync_to_codex_plugin.py `
  --destination D:\loong-workspace-python\context-atlas-codex-plugin
py C:\Users\Seven\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py `
  D:\loong-workspace-python\context-atlas-codex-plugin
git -C D:\loong-workspace-python\context-atlas-codex-plugin add --all
git -C D:\loong-workspace-python\context-atlas-codex-plugin commit -m "release: context-atlas <版本号>"
git -C D:\loong-workspace-python\context-atlas-codex-plugin push origin main
```

正式版本标签使用 `v<版本号>`，并指向上述发布仓库提交。不得直接修改发布仓库中的生成文件。

构建产物只包含目标平台清单、Skill、构建生成的运行时资产和命令，不包含测试、设计文档或本项目知识库。

## 安装范围

Context Atlas 只支持项目级安装，不应写入用户级插件配置。先进入需要使用知识库能力的目标项目，后续命令
都在目标项目根目录执行。

## Codex（项目级）

Codex 当前没有原生 `--scope project` 参数。使用目标项目内的 `.codex/` 作为独立 `CODEX_HOME`，
可以把 Marketplace、插件缓存和配置限制在该项目。以下示例中的 Marketplace 路径是 Context Atlas
源码仓库路径，不是目标项目路径。

1. 在终端执行：

   ```powershell
   cd D:\你的目标项目
   $env:CODEX_HOME = (Join-Path $PWD ".codex")
   codex plugin marketplace add D:\loong-workspace-python\context-atlas
   codex plugin add context-atlas@context-atlas-dev
   codex
   ```

2. 以后从新终端进入该项目时，必须先重新设置相同的 `CODEX_HOME`，再启动 Codex：

   ```powershell
   cd D:\你的目标项目
   $env:CODEX_HOME = (Join-Path $PWD ".codex")
   codex
   ```

3. 首次使用这个项目隔离环境时，如果 Codex 要求认证，请在设置 `CODEX_HOME` 后按提示完成登录。

不要在未设置项目 `CODEX_HOME` 的终端执行 `codex plugin marketplace add` 或 `codex plugin add`；否则会安装到
用户级 Codex 环境。

## Claude Code（项目级）

1. 在终端执行：

   ```powershell
   cd D:\你的目标项目
   claude plugin marketplace add --scope project D:\loong-workspace-python\context-atlas
   claude plugin install --scope project context-atlas@context-atlas-dev
   ```

2. 安装后新建 Claude Code 会话，使会话载入已安装的 Skill。

不要省略两个命令中的 `--scope project`；Claude Code 默认 scope 是 `user`。

## Qoder（项目级 Skill）

Qoder 支持从 GitHub 或 skills.sh 安装 Skill，也支持项目级 `.qoder/skills/`。正式发布包应包含 `.qoder-plugin/plugin.json`、`skills/`、`assets/` 和 `references/`，不能只复制 `SKILL.md`。

在 Qoder 打开的目标项目终端中执行：

```powershell
npx skills add https://github.com/xiangzuoxiangyoukan7/context-atlas -a qoder
```

安装后重启 Qoder，在输入框中输入 `/`，确认八个 Context Atlas Skill 已加载。也可以直接使用本仓库构建的 `build/qoder/context-atlas` 作为本地插件目录。

## Trae（项目级 Skill）

Trae 从项目级 `.agents/skills/` 加载 Skill。Trae 构建包把共享 Skill、运行资产和引用资料分别放在 `.agents/skills/`、`.agents/assets/` 和 `.agents/references/`，以保持安装后的相对路径有效。

将 `build/trae/context-atlas/.agents/` 目录复制到目标项目根目录的 `.agents/` 下，重启 Trae，然后在 Skill 管理面板确认八个 Context Atlas Skill 已加载。当前 Trae 官方入口是项目级 Skill 目录，不额外虚构 Marketplace 清单。

## 更新已安装插件

Codex 本地 Marketplace 更新时，在目标项目的隔离环境中重新登记并安装：

```powershell
cd D:\你的目标项目
$env:CODEX_HOME = (Join-Path $PWD ".codex")
codex plugin remove context-atlas@context-atlas-dev
codex plugin marketplace remove context-atlas-dev
codex plugin marketplace add D:\loong-workspace-python\context-atlas
codex plugin add context-atlas@context-atlas-dev
```

Claude Code 正式发布仓库为 `context-atlas-claude-plugin`，使用原生项目级更新：

```powershell
cd D:\你的目标项目
claude plugin marketplace remove --scope project context-atlas
claude plugin marketplace add --scope project `
  https://github.com/xiangzuoxiangyoukan7/context-atlas-claude-plugin.git
claude plugin install --scope project context-atlas@context-atlas
```

更新后必须新建 Agent 会话，旧会话不会重新载入 Skill。

本地开发时使用 Context Atlas 仓库的实际克隆路径；正式发布时 Codex 使用
`context-atlas-codex-plugin`，Claude Code 使用 `context-atlas-claude-plugin`。无论来源是本地路径
还是远程仓库，安装范围仍必须保持为目标项目级。
Qoder 和 Trae 使用同一源码仓库构建，不创建新的源码仓库；只有平台明确要求独立发布镜像时，才由同步脚本生成镜像。
正式发布时请使用发布仓库对应的 URL，不要把开发仓库路径当作生产 Marketplace 来源。

## 在目标项目中使用

在目标项目中，Skill 只负责生成 Proposal。初始化或维护必须调用命令；只有用户明确确认后才写入正式知识。
自动检查通过只代表
结构和引用满足规则，不能替代用户确认内容。

安装完成后，Codex 使用固定 Skill 操作符：

```text
$context-atlas-init
$context-atlas-navigate
$context-atlas-review
$context-atlas-add
$context-atlas-revise
$context-atlas-retire
$context-atlas-upgrade
```

Claude Code 使用带插件命名空间的原生命令：

```text
/context-atlas:context-atlas-init
/context-atlas:context-atlas-navigate
/context-atlas:context-atlas-review
/context-atlas:context-atlas-ingest
/context-atlas:context-atlas-add
/context-atlas:context-atlas-revise
/context-atlas:context-atlas-retire
/context-atlas:context-atlas-upgrade
```

Claude Code 的命令面板在名称可唯一解析时，可能显示或接受不带 Marketplace 前缀的短形式，例如 `/context-atlas-init`；会话记录仍可能展开成 `/context-atlas:context-atlas-init`。这两种显示指向同一个 Skill，以当前安装后的命令面板补全为准。

`init`、`add`、`revise`、`retire` 和 `upgrade` 是相互独立的正式写入入口：`add` 新增知识，`revise` 修订、同步或替代知识，`retire` 通过替代、归档或受控删除退役知识，`upgrade` 只升级知识库格式和结构。通用 `update` Skill 已删除，不作为兼容入口。`navigate` 只读支持逐层目录浏览、一跳正反向邻接查询，以及有深度和节点数量边界的关系图查询，不生成 Proposal，并由 Agent 决定是否读取候选文件正文。完整图只有在明确需要全局分析时才查询，不作为会话默认上下文。没有固定写入操作符的自然语言不能触发正式写入。写入命令会先生成
Proposal，只有用户明确确认后才执行；底层 Python 参数由插件负责，不作为用户接口。

`ingest` 支持一个来源或最多 20 个分别定位的来源，并支持一个明确 HTTP/HTTPS URL；网页正文视为不可信数据且不递归爬取。历史默认关闭，只有显式要求时才保存脱敏的非正式运行报告。`review` 的 `knowledge_health` 模式调用确定性只读健康检查，不自动修复或批准知识。

## 当前验收状态

Marketplace 清单和共享 Skill 契约已通过自动检查。Codex 执行链路已验证；Claude Code 当前真实确认后
初始化验收仍为 **partial**，因此不能表述为双平台完全通过。详见[验收矩阵](../doc-atlas/03-变更与证据/验收矩阵.md)
及其中的跨 Agent 验收证据。Qoder 与 Trae 已完成构建包、资产路径和静态契约检查，真实 Agent 场景尚未完成，当前保持候选适配状态。
