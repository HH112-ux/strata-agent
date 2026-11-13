# ADR-0004：存储与中间件选型 PostgreSQL + pgvector、Redis 与 Docker Compose

- **Status**: Accepted
- **Date**: 2026-11-13
- **Deciders**: Caspian
- **Related**: `specs/001-strata-platform/spec.md`、`specs/001-strata-platform/plan.md`

## 背景（Context）

平台需要同时承载关系数据（任务、工具调用、审计、评测基线）、向量检索（记忆与 RAG）、会话态与分布式锁（并发任务、工作流恢复）。单人开发与 43–63 人日预算要求组件数量少、启动路径短、备份与排障简单；同时所有连接串必须外部化，不能写死。

## 决策（Decision）

我们采用 PostgreSQL + pgvector 作为关系数据与向量检索的统一存储，采用 Redis 承载会话记忆与分布式锁，并以 Docker Compose 一键启动全套依赖；所有连接串通过环境变量注入，代码中不写死。

## 备选方案（Alternatives Considered）

| 方案 | 优点 | 缺点 | 为什么未选 |
| --- | --- | --- | --- |
| A（选中）PostgreSQL + pgvector + Redis | 关系数据与向量检索同库，事务与备份统一；Redis 承载会话与锁，延迟低 | 需要维护 pgvector 扩展版本；Compose 增加本地资源占用 | — |
| B MySQL + 独立向量库 | 组件各自成熟，向量检索可独立扩容 | 两套存储的备份、一致性、排障成本翻倍 | 与单人维护和 43–63 人日预算不匹配 |
| C 仅嵌入式数据库（H2 / SQLite） | 零依赖，启动最快 | 无法验证并发、持久化与恢复路径 | 与"可一键启动且能跑通真实链路"的验收冲突 |
| D 嵌入式向量索引（文件型） | 无需额外服务 | 与关系数据分离，备份与扩容复杂，事务不可用 | 记忆与评测数据需要统一备份与清理 |

## 后果（Consequences）

**正面**

- 一个数据库同时承载关系数据与向量检索，减少连接与迁移复杂度。
- Redis 承担会话与锁，工作流并发恢复有明确落点。
- Docker Compose 把依赖启动收敛为一条命令，便于演示与回归。

**负面 / 代价**

- 本地需要 Docker 运行时；首次拉取镜像与初始化扩展有时延。
- pgvector 扩展版本需与 PostgreSQL 主版本匹配，升级时要先验证索引兼容性。
- Redis 中的数据为非唯一事实源，键设计不当会造成状态漂移。

**需要跟进的动作**

- [ ] 提供 `docker-compose.yml`，含 PostgreSQL（启用 pgvector）、Redis、应用服务与健康检查（Caspian，tasks T018）
- [ ] 定义连接串环境变量清单与缺失时启动失败策略（Caspian，tasks T019）
- [ ] 数据迁移采用纯增量脚本，回滚使用 `DROP TABLE`，禁止修改既有列（Caspian，plan §6）
- [ ] Redis 只存会话记忆与锁，权威状态落 PostgreSQL（Caspian，代码评审检查点）

## 合规性（Compliance）

- 与 `constitution.md` 的关系：符合 Article III（连接串外部化、零密钥入库）；Article VI（存储合并的取舍已在 plan 复杂度登记表留痕）。
- 如何验证执行：Compose 启动后健康检查通过；CI 密钥扫描与硬编码连接串扫描通过；迁移脚本评审确认 expand-only。

## 备注（Notes）

失效条件：若向量规模或检索延迟超出 PostgreSQL + pgvector 的承受范围，需新增 ADR 评估独立向量库；在此之前不引入第二套存储。
