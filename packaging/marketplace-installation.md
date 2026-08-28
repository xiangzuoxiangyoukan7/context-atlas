# Marketplace 安装与使用

Context Atlas 是 Agent Skill/插件，不是 Python 包，不需要 `pip install`。当前用户支持范围是 Codex、Claude Code 和 Qoder；三平台源码清单版本必须保持一致。仓库根目录是唯一插件源码；
`.agents/plugins/marketplace.json` 是 Codex Marketplace 索引，`.claude-plugin/marketplace.json`
是 Claude Code Marketplace 索引，两者都指向根目录中的同一份 `context-atlas` Skill。

开发者从仓库根目录构建平台发布包：

```powershell
py scripts/build_plugin.py claude --output build/claude/context-atlas
py scripts/build_plugin.py codex --output build/codex/context-atlas.zip --archive
py scripts/build_plugin.py qoder --output build/qoder/context-atlas
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

Claude Code 和 Qoder 使用项目级安装。Codex 当前没有原生 `--scope project` 参数，因此使用用户级共享安装、项目级启用：插件实体、Marketplace 和缓存只在用户级 `CODEX_HOME` 保存一份，目标项目通过受信任项目中的 `.codex/config.toml` 启用插件。项目知识始终保存在各自的 `doc-<项目名>/` 中。

## Codex（用户级安装、项目级启用）

保持默认用户级 `CODEX_HOME`，不要将其指向目标项目的 `.codex/`；否则 Codex 的沙箱组件、会话、数据库和缓存也会在每个项目中重复生成。以下示例中的 Marketplace 路径是 Context Atlas 源码仓库路径，不是目标项目路径。

1. 在终端执行：

   ```powershell
   codex plugin marketplace add D:\loong-workspace-python\context-atlas
   codex plugin add context-atlas@context-atlas-dev
   ```

2. `plugin add` 会在用户级配置中启用插件。若只允许指定项目使用，在用户级 `~/.codex/config.toml` 中设置：

   ```toml
   [plugins."context-atlas@context-atlas-dev"]
   enabled = false
   ```

3. 在目标项目的 `.codex/config.toml` 中启用插件：

   ```toml
   [plugins."context-atlas@context-atlas-dev"]
   enabled = true
   ```

4. 将目标项目标记为受信任，进入项目并新建 Codex 会话。项目不受信任时，Codex 不加载项目级 `.codex/` 配置。

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

Qoder 支持原生插件 Marketplace 和项目级安装。正式 Context Atlas 包应包含 `.qoder-plugin/plugin.json`、`skills/`、`assets/` 和 `references/`，不能只复制 `SKILL.md`。为了与 Codex、Claude Code 一样保持项目隔离，正式安装必须在 Qoder Marketplace 选择 Project，不写入用户级 `~/.qoder/skills/`。

必须在目标项目范围安装，不要安装到用户级 `~/.qoder/skills/`。在 Qoder 打开的目标项目终端中执行：

```powershell
qoder plugins marketplace add https://github.com/xiangzuoxiangyoukan7/context-atlas-qoder-plugin.git
qoder plugins install context-atlas@context-atlas
```

然后重启 Qoder，在输入框中输入 `/`，确认九个 Context Atlas Skill 已加载。不要把源码仓库中的 `skills/` 单独复制到用户目录。

## 更新已安装插件

### Codex

`marketplace add` 只用于首次登记；当命令报告 `already added` 时不会刷新旧快照。更新用户级共享安装时执行：

```powershell
codex plugin marketplace upgrade context-atlas
codex plugin remove context-atlas@context-atlas
codex plugin add context-atlas@context-atlas
codex plugin list
```

`marketplace upgrade` 只刷新插件源；删除并重新安装后，才会替换插件缓存。重新安装可能再次在用户级配置中启用插件，应恢复“用户级默认禁用、目标项目启用”的配置。以 `codex plugin list` 显示的版本为最终结果。

### Claude Code

Claude Code 正式发布仓库为 `context-atlas-claude-plugin`，使用项目级更新：

```powershell
cd D:\你的目标项目
claude plugin marketplace remove --scope project context-atlas
claude plugin marketplace add --scope project `
  https://github.com/xiangzuoxiangyoukan7/context-atlas-claude-plugin.git
claude plugin install --scope project context-atlas@context-atlas
```

### Qoder

Qoder 使用原生 Marketplace 项目级更新，并确保 Marketplace 当前选择的是 Project 范围：

```powershell
qoder plugins marketplace update context-atlas
qoder plugins update context-atlas@context-atlas
```

三个平台更新后都必须新建 Agent 会话，使会话重新加载 Skill；还要在宿主插件管理界面或列表命令中检查实际安装版本。源码清单版本、Marketplace 远端版本和本地安装版本是三个不同状态，不能相互代替。

本地开发时使用 Context Atlas 仓库的实际克隆路径；正式发布时 Codex 使用
`context-atlas-codex-plugin`，Claude Code 使用 `context-atlas-claude-plugin`。无论来源是本地路径
还是远程仓库，安装范围仍必须保持为目标项目级。
Qoder 使用同一源码仓库构建，不创建新的源码分叉；只有平台明确要求独立发布镜像时，才由同步脚本生成镜像。Trae 适配保留为内部候选，不属于当前用户支持范围。
正式发布时请使用发布仓库对应的 URL，不要把开发仓库路径当作生产 Marketplace 来源。

## 在目标项目中使用

在目标项目中，Skill 只负责生成 Proposal。初始化或维护必须调用命令；只有用户明确确认后才写入正式知识。
自动检查通过只代表
结构和引用满足规则，不能替代用户确认内容。

安装完成后，Codex 使用固定 Skill 操作符：

```text
$context-atlas-work
$context-atlas-init
$context-atlas-navigate
$context-atlas-review
$context-atlas-ingest
$context-atlas-add
$context-atlas-revise
$context-atlas-retire
$context-atlas-upgrade
```

Claude Code 使用带插件命名空间的原生命令：

```text
/context-atlas:context-atlas-work
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

Qoder 使用不带插件命名空间的斜杠命令：

```text
/context-atlas-work
/context-atlas-init
/context-atlas-navigate
/context-atlas-review
/context-atlas-ingest
/context-atlas-add
/context-atlas-revise
/context-atlas-retire
/context-atlas-upgrade
```

九个 Skill 的用途如下：

| 需要做什么 | Skill | 是否可能写入正式知识 |
| --- | --- | --- |
| 用自然语言描述开发目标并自动编排知识流程 | `context-atlas-work` | 默认只读；选择基线路径且确认 Proposal 后可写入 |
| 首次建立 `doc-<项目名>/` | `context-atlas-init` | 展示 Proposal 并确认后写入 |
| 逐层读取目录、邻接关系和受限关系图 | `context-atlas-navigate` | 否，只读 |
| 审查规格或知识健康状态 | `context-atlas-review` | 否，只读 |
| 读取一个或一批明确来源并生成维护路由 | `context-atlas-ingest` | 否，只生成候选 |
| 新增正式知识 | `context-atlas-add` | 展示 Proposal 并确认后写入 |
| 修订、同步或替代已有知识 | `context-atlas-revise` | 展示 Proposal 并确认后写入 |
| 替代、归档或受控删除失效知识 | `context-atlas-retire` | 展示 Proposal 并确认后写入 |
| 只升级知识库格式和结构 | `context-atlas-upgrade` | 展示 Proposal 并确认后写入 |

`init`、`add`、`revise`、`retire` 和 `upgrade` 是相互独立的正式写入入口：`add` 新增知识，`revise` 修订、同步或替代知识，`retire` 通过替代、归档或受控删除退役知识，`upgrade` 只升级知识库格式和结构。通用 `update` Skill 已删除，不作为兼容入口。`navigate` 只读支持逐层目录浏览、一跳正反向邻接查询，以及有深度和节点数量边界的关系图查询，不生成 Proposal，并由 Agent 决定是否读取候选文件正文。完整图只有在明确需要全局分析时才查询，不作为会话默认上下文。`context-atlas-work` 可从自然语言目标自动选择底层操作，但仍只有在用户确认当前 Proposal 修订后才能正式写入。写入命令会先生成
Proposal，只有用户明确确认后才执行；底层 Python 参数由插件负责，不作为用户接口。

`ingest` 支持一个来源或最多 20 个分别定位的来源，并支持一个明确 HTTP/HTTPS URL；网页正文视为不可信数据且不递归爬取。历史默认关闭，只有显式要求时才保存脱敏的非正式运行报告。`review` 的 `knowledge_health` 模式调用确定性只读健康检查，不自动修复或批准知识。

## 当前验收状态

Marketplace 清单和共享 Skill 契约已通过自动检查。Codex 执行链路已验证；Claude Code 当前真实确认后
初始化验收仍为 **partial**，因此不能表述为双平台完全通过。详见[验收矩阵](../doc-atlas/03-变更与证据/验收矩阵.md)
及其中的跨 Agent 验收证据。Qoder 已完成构建包、资产路径和静态契约检查，真实 Agent 场景尚未完成；用户将继续完成 Claude Code、Codex、Qoder 的真实安装、升级和行为验证。
