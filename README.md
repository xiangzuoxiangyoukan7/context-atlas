# 脉络地图（Context Atlas）

本项目提供一套供 Codex、Claude Code 和 Qoder 使用的项目知识库能力；核心协议、完整模板、Schema、多技术栈样例和确定性检查器与具体 Agent 解耦。

## 这个插件是做什么的

Context Atlas 是一个面向项目的知识治理插件。它把项目中的架构、约束、变更、验收证据、数据库信息和来源追溯整理成可持续维护的 `doc-<项目名>/` 知识库，让不同 Agent 在同一个项目中读取同一套事实。

它解决的不是“替 Agent 写代码”，而是解决以下问题：

- 项目知识散落在 README、源码、Issue、设计文档和会话中，难以持续读取。
- 不同 Agent 对项目结构和约束的理解不一致。
- AI 生成的推测被误当成正式事实。
- 知识写入缺少确认、来源、版本和校验边界。
- 项目更换 Codex、Claude Code 或 Qoder 后，知识库需要重新维护。

## 它是怎么做的

Context Atlas 采用“一主多适配”架构：核心 Skill、协议、模板、Schema 和 Python 执行器只有一份；Codex、Claude Code 和 Qoder 只提供平台清单、安装入口、路径布局和命令映射。

一次正式写入遵循固定状态机：

```text
inspect → propose → await_confirmation → apply → validate → report
```

Agent 负责调研、组织候选内容和展示 Proposal；用户负责确认；确定性执行器负责写入、版本、关系、来源和结构校验。没有用户明确确认，不会写入正式知识库。

## 典型使用场景

- 新项目初始化：扫描项目入口、源码、配置、测试和已有文档，生成初始化 Proposal。
- 接手旧项目：先通过 `navigate` 逐层阅读知识目录，再查询相关邻接关系和有限关系图。
- 需求或架构变化：使用 `add` 新增知识，使用 `revise` 修订或替代已有知识。
- 事实失效：使用 `retire` 通过替代、归档或受控删除退役知识。
- 外部资料进入项目：使用 `ingest` 读取明确来源，只生成候选路由，不直接写入正式知识。
- 规格或健康检查：使用 `review` 做只读审查，不自动批准或修复。
- 知识库格式变化：使用 `upgrade` 做结构和格式升级，不用它新增业务事实。
- 多 Agent 协作：在同一个目标项目中分别使用 Codex、Claude Code 或 Qoder，它们读取同一个 `doc-<项目名>/`。

## 当前版本

当前源码清单版本为 `0.11.0`，Codex、Claude Code 和 Qoder 共享产品名 `context-atlas`。源码清单版本不等于各 Marketplace 已发布版本；安装或升级后必须以宿主实际显示的版本为准。平台发布包由当前源码仓库构建，不维护平台专属源码分叉。

## 入口

- [本项目知识库](doc-atlas/README.md)
- [通用核心模板](./templates/core/README.md)
- [核心 Schema](./schemas/README.md)
- [Schema 逐文件字段说明](./schemas/字段说明.md)
- [知识库检查器](./scripts/check_knowledge_base.py)
- [初始化 Skill](./skills/context-atlas-init/SKILL.md)
- [渐进导航 Skill](./skills/context-atlas-navigate/SKILL.md)
- [规格审查 Skill](./skills/context-atlas-review/SKILL.md)
- [增强摄取 Skill](./skills/context-atlas-ingest/SKILL.md)
- [知识新增 Skill](./skills/context-atlas-add/SKILL.md)
- [知识修订 Skill](./skills/context-atlas-revise/SKILL.md)
- [知识退役 Skill](./skills/context-atlas-retire/SKILL.md)
- [知识库升级 Skill](./skills/context-atlas-upgrade/SKILL.md)
- [场景化使用指南](./templates/core/doc-project/05-知识治理/使用场景.md)
- [Marketplace 安装与使用](./packaging/marketplace-installation.md)

## Marketplace 安装

Context Atlas 是 Agent Skill/插件，不是 Python 包，不需要 `pip install`。仓库根目录就是唯一插件源码，
Codex Marketplace 位于 `.agents/plugins/marketplace.json`，Claude Code Marketplace 位于
`.claude-plugin/marketplace.json`。安装 `context-atlas` 后请新建会话，让 Agent 载入最新 Skill。正式写入必须通过
`init` 或 `update` 命令完成；Skill 只能生成 Proposal 并调用命令，不能直接写入知识库。

插件只支持安装到目标项目：Claude Code 必须使用 `--scope project`；Codex 当前没有原生 scope 参数，
必须把 `CODEX_HOME` 指向目标项目的 `.codex/`，并在同一环境下安装和启动 Codex。不要省略项目隔离参数。
安装后，Codex 使用 `$context-atlas-init`、`$context-atlas-navigate`、`$context-atlas-review`、`$context-atlas-ingest`、`$context-atlas-add`、`$context-atlas-revise`、`$context-atlas-retire`、`$context-atlas-upgrade`。Claude Code 的原生命令使用插件命名空间，例如
`/context-atlas:context-atlas-init`、`/context-atlas:context-atlas-navigate`；命令面板可能把已唯一解析的命令显示或补全为 `/context-atlas-init`。以面板实际补全结果为准，不要把显示别名当成另一个 Skill。两个平台共用同一组 Skills，不发布 `commands/`；
没有明确调用对应 Skill 的自然语言不得触发知识库写入。

Qoder 适配包也从同一源码仓库构建，使用 `.qoder-plugin/plugin.json`。完整的三平台安装、使用、升级步骤和当前验收状态见[Marketplace 安装与使用](./packaging/marketplace-installation.md)。Trae 适配仍保留为内部候选，不属于当前用户支持范围。

### 在团队业务仓库中安装

三位开发者可以分别使用 Claude Code、Codex 和 Qoder，但必须把 Context Atlas 安装到**同一个业务仓库的项目范围**。插件程序按平台分别安装；正式知识统一保存在业务仓库的 `doc-<项目目录名>/` 中并通过 Git 协作，不为每种 Agent 创建独立知识库。

以下命令都应在需要使用 Context Atlas 的业务仓库根目录执行，而不是在本源码仓库中执行。

#### 开发者 1：Claude Code

```powershell
cd D:\你的业务仓库
claude plugin marketplace add --scope project `
  https://github.com/xiangzuoxiangyoukan7/context-atlas-claude-plugin.git
claude plugin install --scope project context-atlas@context-atlas
```

安装后新建 Claude Code 会话，在命令面板确认 `/context-atlas:context-atlas-init` 等八个命令可用。不得省略 `--scope project`，否则可能安装到用户范围。

升级已有 Claude Code 插件：

```powershell
cd D:\你的业务仓库
claude plugin marketplace remove --scope project context-atlas
claude plugin marketplace add --scope project `
  https://github.com/xiangzuoxiangyoukan7/context-atlas-claude-plugin.git
claude plugin install --scope project context-atlas@context-atlas
```

升级后新建会话，并在插件管理界面确认实际安装版本。

#### 开发者 2：Codex

Codex 当前没有原生项目 scope 参数，必须先把 `CODEX_HOME` 指向业务仓库内的 `.codex/`，安装和以后启动 Codex 时都使用相同设置：

```powershell
cd D:\你的业务仓库
$env:CODEX_HOME = (Join-Path $PWD ".codex")
codex plugin marketplace add `
  https://github.com/xiangzuoxiangyoukan7/context-atlas-codex-plugin.git
codex plugin add context-atlas@context-atlas
codex
```

新建 Codex 会话后确认 `$context-atlas-init` 等八个 Skill 可用。以后从新终端进入该业务仓库时，也必须先设置相同的 `CODEX_HOME` 再启动 Codex。

升级已有 Codex 插件不能再次使用 `marketplace add`；必须先刷新 Marketplace，再替换旧安装：

```powershell
cd D:\你的业务仓库
$env:CODEX_HOME = (Join-Path $PWD ".codex")
codex plugin marketplace upgrade context-atlas
codex plugin remove context-atlas@context-atlas
codex plugin add context-atlas@context-atlas
codex plugin list
```

`marketplace upgrade` 只刷新插件源，`remove` 加 `add` 才会替换已安装插件。最后以 `codex plugin list` 显示的版本为准，并新建 Codex 会话。

#### 开发者 3：Qoder

在 Qoder 中打开业务仓库，把 Marketplace 的安装范围选择为 **Project**，然后在该项目终端执行：

```powershell
qoder plugins marketplace add `
  https://github.com/xiangzuoxiangyoukan7/context-atlas-qoder-plugin.git
qoder plugins install context-atlas@context-atlas
```

重启 Qoder，在输入框中输入 `/`，确认 `/context-atlas-init` 等八个 Skill 已加载。不要安装到用户级 `~/.qoder/skills/`，也不要只复制源码仓库中的 `skills/`。

升级已有 Qoder 插件时，仍须确认当前 Marketplace 范围为 **Project**：

```powershell
qoder plugins marketplace update context-atlas
qoder plugins update context-atlas@context-atlas
```

升级后重启 Qoder，在插件管理界面确认实际版本，并再次检查八个 Skill。

#### 团队首次启用检查

每位开发者安装后都应在同一个业务仓库中完成以下检查：

1. 三个平台显示的 Context Atlas 版本与团队准备验证的目标版本一致；不能用源码清单版本代替实际安装版本。
2. 初始化、导航、审查、摄取、新增、修订、退役和升级八个 Skill 全部可见。
3. 仓库中只存在一个 `doc-<项目目录名>/`，并将其纳入 Git；不得按 Agent 分成三套知识库。
4. Codex、Qoder 使用 `AGENTS.md`，Claude Code 使用 `CLAUDE.md`；两个入口都指向同一个知识库和协作规则。
5. 任一 Agent 正式写入前都必须展示 Proposal，并由用户明确确认；Git 分支、PR 和合并冲突仍按团队原有流程处理。

当前 Codex 真实执行链路已经验证；Claude Code 的确认后初始化验收仍为 `partial`，Qoder 已通过构建和静态契约检查但尚未完成真实 Agent 黑盒验收。三平台由用户继续验证；每个平台都应完成一次真实的“安装或升级 → 版本确认 → 初始化 Proposal → 确认 → 校验”和“读取既有知识库”试运行，不能只以命令退出成功作为可用性结论。

### 项目级卸载

Codex 必须在当初安装插件的目标项目中执行，并保持相同的项目级 `CODEX_HOME`：

```powershell
$env:CODEX_HOME = (Join-Path $PWD ".codex")
codex plugin remove context-atlas@context-atlas
codex plugin marketplace remove context-atlas
```

Claude Code 从项目作用域卸载开发仓库中的插件和 Marketplace：

```powershell
claude plugin uninstall --scope project context-atlas@context-atlas-dev
claude plugin marketplace remove --scope project context-atlas-dev
```

不要直接删除目标项目的整个 `.codex/` 或 `.claude/` 目录，其中可能还有该项目的其他配置和插件。

Plugin 发布包由根目录唯一源码构建，不直接运行或发布开发仓库。`templates/`、`schemas/`、
`scripts/`、`rules/`、`operations/` 和 `compatibility.json` 只维护一份；开发态 `assets/` 只保存
`manifest.json`。构建程序按清单把这些源码物化为安装包中的完整 `assets/`，测试也以构建后的安装形态为准。
构建命令为：

```powershell
py scripts/build_plugin.py claude --output build/claude/context-atlas
py scripts/build_plugin.py codex --output build/codex/context-atlas.zip --archive
py scripts/build_plugin.py qoder --output build/qoder/context-atlas
```

将 Codex 发布内容同步到独立发布仓库：

```powershell
py scripts/sync_to_codex_plugin.py `
  --destination D:\loong-workspace-python\context-atlas-codex-plugin
```

校验后，在独立发布仓库中提交并推送：

```powershell
py C:\Users\Seven\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py `
  D:\loong-workspace-python\context-atlas-codex-plugin
git -C D:\loong-workspace-python\context-atlas-codex-plugin add --all
git -C D:\loong-workspace-python\context-atlas-codex-plugin commit -m "release: context-atlas <版本号>"
git -C D:\loong-workspace-python\context-atlas-codex-plugin push origin main
```

将 Claude Code 发布内容同步到独立发布仓库：

```powershell
py scripts/sync_to_claude_plugin.py `
  --destination D:\loong-workspace-python\context-atlas-claude-plugin
git -C D:\loong-workspace-python\context-atlas-claude-plugin add --all
git -C D:\loong-workspace-python\context-atlas-claude-plugin commit -m "release: context-atlas 0.11.0"
git -C D:\loong-workspace-python\context-atlas-claude-plugin push origin main
```

将 Qoder 发布内容同步到独立发布仓库：

```powershell
py scripts/sync_to_qoder_plugin.py `
  --destination D:\loong-workspace-python\context-atlas-qoder-plugin
git -C D:\loong-workspace-python\context-atlas-qoder-plugin add --all
git -C D:\loong-workspace-python\context-atlas-qoder-plugin commit -m "release: context-atlas 0.11.0"
git -C D:\loong-workspace-python\context-atlas-qoder-plugin push origin main
```

Claude Code 正式安装使用独立发布仓库：

```powershell
claude plugin marketplace add --scope project `
  https://github.com/xiangzuoxiangyoukan7/context-atlas-claude-plugin.git
claude plugin install --scope project context-atlas@context-atlas
```

发布新版本时，再为同一提交创建并推送 `v<版本号>` 标签。发布仓库内容由同步脚本生成，不得直接维护。

## 原则

AI 负责调研、提问和组织候选知识；项目责任人负责确认内容；知识库负责存储、版本、关联和结构校验。自动检查不能替代人工确认内容是否正确。

本项目不调用或托管大模型。初始化时会根据当前运行的 Agent 选择入口文件：Codex、Qoder 使用 `AGENTS.md`，Claude Code 使用 `CLAUDE.md`；文件不存在时创建，文件存在时只追加或更新 Context Atlas 受管区块，绝不覆盖项目原有内容。入口文件的创建或修改必须出现在已确认的初始化 Proposal 中。

## 当前状态

产品方向、核心 Schema、检查器、统一核心模板、单/多技术栈样例和可安装 Skill 已进入实现；最终跨 Agent 验收仍待完成。
