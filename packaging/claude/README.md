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
/context-atlas-init
/context-atlas-navigate
/context-atlas-review
/context-atlas-ingest
/context-atlas-add
/context-atlas-revise
/context-atlas-retire
/context-atlas-upgrade
```

正式写入前必须得到对应 Proposal 的明确确认；没有明确调用 Skill 的自然语言不能触发正式写入。

## 项目级卸载

```powershell
claude plugin uninstall --scope project context-atlas@context-atlas
claude plugin marketplace remove --scope project context-atlas
```
