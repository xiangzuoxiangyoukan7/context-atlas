# Context Atlas for Trae

这是由 Context Atlas 唯一源码仓库构建的 Trae `0.11.0` Skill 包。Trae 从项目级 `.agents/skills/` 加载 Skill；本包同时携带 `.agents/assets/` 和 `.agents/references/`，保证运行时相对路径自包含。

## 项目级安装

必须安装到目标项目，不要写入用户级 Skill 目录。将构建包中的 `.agents/` 目录复制到目标项目根目录，或使用团队发布流程把该目录纳入目标项目。安装后重启 Trae，在 Skill 管理面板确认八个 Context Atlas Skill 已加载。

## 使用

可直接用自然语言请求，或在支持斜杠命令的 Trae 版本中使用对应 Skill 名称：

```text
请使用 context-atlas-init 初始化当前项目知识库
请使用 context-atlas-navigate 导航当前知识库
请使用 context-atlas-review 审查当前知识库
```

初始化和维护只生成 Proposal；必须明确回复“确认”后才会写入正式知识库。
