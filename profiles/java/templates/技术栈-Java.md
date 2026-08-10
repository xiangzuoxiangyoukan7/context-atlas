# Java 技术栈

| 字段 | 已确认值 | 发现位置/命令 | 来源 | 状态 |
| --- | --- | --- | --- | --- |
| JDK 厂商与版本 | 待确认 | `pom.xml`、Wrapper 或 CI | SRC-001 | missing |
| 构建系统与 Wrapper | 待确认 | 仓库根构建文件 | SRC-001 | missing |
| 可复现构建命令 | 待确认 | 项目脚本或 CI | SRC-001 | missing |
| 运行框架 | 待确认 | 依赖与入口 | SRC-001 | missing |

## 模块与契约

记录模块/包边界、依赖来源、公开 API/事件/数据库契约，以及单元和集成测试的边界。不得根据常见 Java 组合预设 Spring、Maven 或 Gradle。

## 验收补充

保存 JDK/Wrapper 版本、构建测试命令和安全扫描的可复核证据。未知项保持 `missing`，凭据只记录环境变量名。
