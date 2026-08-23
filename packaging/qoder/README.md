# Context Atlas for Qoder

这是由 Context Atlas 唯一源码仓库构建的 Qoder 插件包。不要在发布包中直接修改 Skill 或运行资产。

## 项目级安装

在 Qoder 打开的目标项目中执行：

```powershell
npx skills add https://github.com/xiangzuoxiangyoukan7/context-atlas -a qoder
```

也可以把构建包安装到 Qoder 的插件目录。安装后重启 Qoder，在输入框中输入 `/` 检查八个 Context Atlas Skill 是否出现。

## 使用

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

初始化和维护只生成 Proposal；必须明确回复“确认”后才会写入正式知识库。
