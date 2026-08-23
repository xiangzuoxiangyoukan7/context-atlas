# Context Atlas for Qoder

这是由 Context Atlas 唯一源码仓库构建的 Qoder `0.11.0` 插件包。不要在发布包中直接修改 Skill 或运行资产。

## 项目级安装

必须在目标项目范围安装，不要安装到用户级 `~/.qoder/skills/`。先在源码仓库构建 Qoder 包：

```powershell
py scripts/build_plugin.py qoder --output build/qoder/context-atlas
```

进入目标项目，将构建包的运行目录复制到项目级 `.qoder/`：

```powershell
$source = "D:\loong-workspace-python\context-atlas\build\qoder\context-atlas"
$target = Join-Path $PWD ".qoder"
New-Item -ItemType Directory -Force $target | Out-Null
Copy-Item (Join-Path $source "skills") (Join-Path $target "skills") -Recurse -Force
Copy-Item (Join-Path $source "assets") (Join-Path $target "assets") -Recurse -Force
Copy-Item (Join-Path $source "references") (Join-Path $target "references") -Recurse -Force
```

安装后重启 Qoder，在输入框中输入 `/` 检查八个 Context Atlas Skill 是否出现。

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
