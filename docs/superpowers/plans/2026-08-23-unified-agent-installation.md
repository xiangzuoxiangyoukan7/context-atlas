# Qoder Marketplace 与 Trae 一键安装 Proposal

## 目标

将 Qoder 与 Trae 的用户安装体验收敛到 Codex/Claude Code 的简洁模式：Qoder 使用原生 Marketplace 的项目级安装；Trae 使用一条命令完成项目级 `.agents/` 安装。用户不再手工复制 Skill、运行资产或引用资料。

## 方案

- Qoder：增加 Qoder Marketplace 清单和生成型同步脚本；安装范围必须为 Project，插件包携带 `.qoder-plugin/plugin.json`、`skills/`、`assets/` 和 `references/`。
- Trae：增加项目安装脚本；脚本从 Trae 发布包解压并原子替换当前项目受管的 `.agents/skills`、`.agents/assets` 和 `.agents/references`，不覆盖其他 Agent 资产。
- 两个平台继续使用统一插件名 `context-atlas` 和版本 `0.11.0`。
- Codex、Claude、Qoder、Trae 继续共享唯一核心源码仓库，不创建平台专属源码分叉。

## 验收

- Qoder Marketplace 清单、插件清单、版本和来源通过契约校验。
- Qoder 项目级安装和更新命令可复现，用户级安装被文档明确禁止。
- Trae 安装脚本支持安装、更新、卸载前备份/回滚边界，不删除 `.agents/` 下其他内容。
- 四个平台构建和版本一致性通过；安装包包含完整运行资产。
- README 和安装文档只推荐正式安装入口，手工复制只作为故障排查方式。
