# F06 Profile 阶段验证

## 结果

| 检查 | 结果 | 证据版本 |
| --- | --- | --- |
| 零/Java/Python/Java+Python 物化与校验 | passed | profile-v1 |
| 描述符 Schema 与增量模板 | passed | profile-v1 |
| 核心状态、权威路径、批准、验收结果和字段覆盖反例 | passed | profile-v1 |
| Profile 移除保留历史 | partial | 待 Skill 更新协议验证 |
| 四类黄金样例 | partial | 待 Task 6 |

## 命令

- `py -m unittest tests.unit.test_profiles -v`：3 个测试通过。
- `py -m unittest discover -s tests -v`：33 个测试通过。
- `py scripts/check_knowledge_base.py doc-xiangmuzhishikumoban --schema-root schemas`：通过。
- `git diff --check`：通过。

本证据不将阶段测试等同于 F06 最终完成。
