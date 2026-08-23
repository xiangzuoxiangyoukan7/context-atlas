# Qoder 与 Trae 多 Agent 适配实施 Proposal

## 目标

在不复制 Context Atlas 核心 Skill、协议、模板、Schema 和运行脚本的前提下，增加 Qoder 与 Trae 的平台适配，使同一份源码可以构建并验收 Codex、Claude Code、Qoder 和 Trae 四种 Agent 发布物。

## 已确认架构

- `skills/`、`schemas/`、`templates/`、`scripts/` 和共享运行资产保持唯一来源。
- 平台差异只进入清单、安装入口、路径解析、命令映射和真实 Agent 运行器。
- Qoder 与 Trae 不创建独立源码仓库，也不创建 `context-atlas-qoder` 或 `context-atlas-trae` 这种产品分叉名称。
- 如平台 Marketplace 强制独立发布仓库，只允许由同步脚本生成发布镜像，禁止直接维护生成文件。
- 所有平台使用统一版本号和统一机器名 `context-atlas`。

## 实施范围

1. 增加 Qoder、Trae 的平台清单与发布目录契约。
2. 扩展构建器和发布同步器，生成平台自包含运行资产，保证 Skill 中的相对路径在安装后仍有效。
3. 增加平台安装与更新说明；明确项目级安装、重启新会话和 Proposal 确认流程。
4. 增加静态契约、构建产物、资产完整性和路径自包含测试。
5. 增加 Qoder、Trae 的最小真实场景验收：确认前零写入、确认后初始化、防覆盖、导航 smoke check 和结果报告。
6. 更新验收矩阵；平台真实场景未完成前保持 `partial`，不提前宣称正式支持。

## 不在本 Proposal 内

- 不修改核心知识库格式和治理语义。
- 不恢复已删除的通用 `update` Skill。
- 不处理 Obsidian API Key 问题。
- 不为每个 Agent 建立新的源码仓库。

## 验收门槛

- 四个平台清单的共享身份、版本和 Skill 来源一致。
- 每个平台发布包均可脱离开发仓库运行，运行资产和 Schema 路径完整。
- 全量自动化测试、知识库校验和平台官方清单校验通过。
- Qoder、Trae 的确认前与确认后真实场景均有脱敏报告。
- 任一平台阻塞时，报告阻塞原因并保持对应验收项为 `partial`。

## 变更边界

预计修改构建/同步脚本、平台清单、安装文档、测试和验收证据；不修改用户已有的 `.obsidian`、术语表、治理规则或历史归档改动。
