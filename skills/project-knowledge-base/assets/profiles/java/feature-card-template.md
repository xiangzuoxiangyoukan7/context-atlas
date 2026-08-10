# Java 功能卡增量

| 字段 | 说明 | 未知时处理 |
| --- | --- | --- |
| `module_packages` | 涉及模块、包与依赖方向 | 标记 `missing` 并检查源码 |
| `runtime_framework` | 实际运行框架及版本 | 不预设 Spring |
| `public_contracts` | API、事件或数据库契约编号 | 创建待确认契约 |
| 测试边界 | 单元、集成测试范围与命令 | 从构建配置验证 |
