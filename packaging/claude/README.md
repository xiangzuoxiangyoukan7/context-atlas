# Context Atlas for Claude Code

这是由 [`context-atlas`](https://github.com/xiangzuoxiangyoukan7/context-atlas) 源码仓库自动生成的 Claude Code 独立发布仓库。请勿直接修改本仓库中的生成文件。

## 项目级安装

在目标项目中执行：

```powershell
claude plugin marketplace add --scope project https://github.com/xiangzuoxiangyoukan7/context-atlas-claude-plugin.git
claude plugin install --scope project context-atlas@context-atlas
```

安装后新建 Claude Code 会话，然后使用：

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

命令面板可能把可唯一解析的命令显示为 `/context-atlas-init` 等短形式；会话记录中的 `/context-atlas:context-atlas-init` 是同一 Skill 的原生命名空间形式。

普通开发目标可由 `context-atlas-work` 自动编排；正式写入前仍必须得到对应 Proposal 当前修订的明确确认。

## 升级插件

在原目标项目中执行：

```powershell
claude plugin marketplace remove --scope project context-atlas
claude plugin marketplace add --scope project `
  https://github.com/xiangzuoxiangyoukan7/context-atlas-claude-plugin.git
claude plugin install --scope project context-atlas@context-atlas
```

不要省略 `--scope project`。升级后新建 Claude Code 会话，并在插件管理界面确认实际安装版本。

## 项目级卸载

```powershell
claude plugin uninstall --scope project context-atlas@context-atlas
claude plugin marketplace remove --scope project context-atlas
```
