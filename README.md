# Strata（智层）

通用智能体平台：能调模型、能用工具、能单干也能协作、能编排工作流，出了问题还能自己定位。

> 当前状态：仓库骨架与规格基线（2026-11-13），尚无业务代码。技术选型中的未定项标记为"待决策"，见 ADR 与计划文档。

## 六层能力栈

| 层 | 能力 | 状态 |
| --- | --- | --- |
| 1 框架层 | Spring AI 主线，LangChain4j 作模型接入层对照适配 | 待建设 |
| 2 工具调用 | Function Calling、MCP 工具接入 | 待建设 |
| 3 单 Agent | 任务分解、工具选择、终止判定 | 待建设 |
| 4 多 Agent | 角色分工、消息路由、冲突裁决与共识 | 待建设 |
| 5 Graph 工作流 | 节点编排、检查点、人工介入、修正回退 | 待建设 |
| 6 运维可观测 | traceId、任务级指标、心跳假死、成本归因 | 待建设 |

## 技术基座

- 模型接入：统一 provider 接口，默认对接火山方舟的 OpenAI 兼容端点；`base-url`、`model`、`api-key` 全部走环境变量。
- 存储与中间件：PostgreSQL + pgvector（关系与向量合一）、Redis（会话记忆与分布式锁）。
- 启动方式：Docker Compose 一键启动应用与依赖，连接串全部环境变量注入。

## 必做范围

- 六层能力全部具备可运行实现。
- 9 个示例模块覆盖六层能力面（清单与映射待确认）。
- 四个业务场景：智能问答、合同预审、内容创作、数据分析。
- 六项创新能力：MCP 工具网关（权限/审计/限流/沙箱）、可恢复 Graph 工作流、多 Agent 冲突裁决与共识、Agent 运行时可观测性、任务级评测与回归基线、持久记忆与高级 RAG。

## 文档索引

- [项目宪法](.specify/memory/constitution.md)：不可妥协的原则与质量闸门。
- [规格说明](specs/001-strata-platform/spec.md)：做什么、不做什么、验收口径。
- [实施计划](specs/001-strata-platform/plan.md)：分阶段路线、技术上下文、编码规范。
- [任务清单](specs/001-strata-platform/tasks.md)：可认领的任务与依赖关系。
- [docs/agent/](docs/agent/)：能力与权限契约、威胁模型、评测计划、可观测、版本登记、降级与回滚、runbook、数据与隐私边界。
- [ADR-0001](docs/adr/0001-six-layer-stack-and-docs-first.md)：六层能力栈与文档先行决策。
- [ADR-0002](docs/adr/0002-main-framework-spring-ai.md)：主线框架选择 Spring AI。
- [ADR-0003](docs/adr/0003-model-provider-abstraction.md)：模型接入统一为 provider 接口。
- [ADR-0004](docs/adr/0004-storage-and-middleware.md)：存储与中间件选型。

## 规划的仓库结构

```text
platform/      六层能力与创新模块
examples/      9 个示例模块
scenarios/     四个业务场景
specs/         规格、计划、任务
docs/          ADR、quickstart、错误码
scripts/       演示与验证脚本
```

结构已按 ADR-0002/0004 调整，Java 版本与构建工具确认后再微调。

## 开发约定

- 文档先行：每个能力面先完成 spec/plan/tasks，再写实现。
- 每层完成以"可运行命令 + 自动化测试"为唯一判据。
- 密钥零入库：所有外部配置经环境变量注入，仓库只保留 `.env.example`。
- 工具执行受控：白名单、超时、资源上限、审计，默认拒绝未登记工具。
- 代码注释与日志使用英文；公开类、接口、方法写英文 Javadoc 并标注 `@author Caspian`；中文仅出现在文档中。
- 文档统一中文 Markdown，图示使用 Mermaid，不产出 HTML。
