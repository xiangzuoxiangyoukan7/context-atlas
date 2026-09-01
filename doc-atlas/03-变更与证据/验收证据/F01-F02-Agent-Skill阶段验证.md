---
id: EVID-015
type: acceptance_evidence
title: F01-F02-Agent-Skill阶段验证
rel_classified_under:
  - "[[03-变更与证据/验收证据/README|IDX-EVIDENCE]]"
---
# F01/F02 Agent Skill 阶段验证

## 结果

| 检查 | 结果 | 证据版本 |
| --- | --- | --- |
| Skill 渐进式结构、行为边界与 UTF-8 元数据 | passed | 0c91abb |
| 构建资产完整且与规范源一致 | passed | 0c91abb |
| 路径越界拒绝、未声明文件保留 | passed | 0c91abb |
| 初始化、采集、冲突、归档和报告协议 | passed | 0c91abb |
| 初始化产物、自包含性、覆盖保护及 Agent 专属文件排除 | passed | 0c91abb |
| 新增、修订和退役 Skill 路由及同修订确认门禁 | passed | 0c91abb |
| Codex 独立确认后初始化 | passed | a9c7563 |
| Claude 确认后初始化 | blocked | 外部调用超时，继续由 KB-AC-27～29 跟踪 |

## 复验命令

- `py -m unittest discover -s tests -p 'test_*.py'`：231 个测试通过。
- `py scripts/check_knowledge_base.py doc-atlas --schema-root schemas`：通过。
- 插件校验：通过。
- Claude 和 Codex 插件构建：通过。

本证据只将确定性测试和已有 Codex 真实执行用于 F01/F02 产品验收，不把 Claude 外部超时推断为通过或失败。Claude 剩余状态继续由跨 Agent 验收项独立追踪。
