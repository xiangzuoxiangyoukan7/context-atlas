# Python 功能卡增量

| 字段 | 说明 | 未知时处理 |
| --- | --- | --- |
| `package_modules` | 涉及包、模块和依赖方向 | 标记 `missing` 并检查源码 |
| `entry_points` | 服务、任务或 CLI 入口 | 从包配置验证 |
| `configuration_sources` | 配置文件与环境变量名称 | 不记录秘密值 |
| 质量命令 | pytest、类型检查与 lint | 从项目脚本或 CI 验证 |
