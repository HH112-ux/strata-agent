# Tasks：Strata 通用智能体平台

**Feature ID**: `001-strata-platform`
**Inputs**: [`./spec.md`](./spec.md), [`./plan.md`](./plan.md), [`../../docs/adr/0001-six-layer-stack-and-docs-first.md`](../../docs/adr/0001-six-layer-stack-and-docs-first.md)
**Status**: Draft

## 格式约定

`- [ ] T<NNN> [P?] [US?] <动作> in <精确路径>（AC: <AC-ID>）`

路径约定：本期路径基于 `plan.md` §4 的提议结构。构建工具与框架选型确认后统一调整路径前缀，调整不改变任务边界与验收条件。

## Phase 0 — 规格与决策基线（S0）

**目的**：先把规格、计划、任务与第一条 ADR 落盘，不写业务代码。

- [x] T001 建立仓库骨架（README、.gitignore、文档目录）in `README.md`（AC: N/A）
- [x] T002 [P] 编写项目宪法 in `.specify/memory/constitution.md`（AC: N/A）
- [x] T003 [P] 编写总规格 in `specs/001-strata-platform/spec.md`（AC: N/A）
- [x] T004 [P] 编写实施计划与编码规范 in `specs/001-strata-platform/plan.md`（AC: N/A）
- [x] T005 [P] 编写任务清单 in `specs/001-strata-platform/tasks.md`（AC: N/A）
- [x] T006 [P] 编写 ADR-0001（六层能力栈 + 文档先行）in `docs/adr/0001-six-layer-stack-and-docs-first.md`（AC: N/A）
- [ ] T007 确认 9 个示例模块清单与六层映射，回填 spec §3 与本文件 Phase 3 补充任务 in `specs/001-strata-platform/spec.md`（AC: FR-14）——负责人：Caspian，阻塞后续示例模块任务
- [x] T008 决策主线框架，补写 ADR-0002 in `docs/adr/0002-main-framework-spring-ai.md`（AC: FR-1）
- [x] T009 决策存储与中间件，补写 ADR-0004 in `docs/adr/0004-storage-and-middleware.md`（AC: NFR-12）
- [x] T016 [P] 决策模型接入抽象，补写 ADR-0003 in `docs/adr/0003-model-provider-abstraction.md`（AC: NFR-9）
- [ ] T017 决策 Java 版本与构建工具，补写 ADR-0005 in `docs/adr/0005-java-version-and-build-tool.md`（AC: N/A）——阻塞 T010

**Checkpoint**：文档基线可评审；T007、T017 未决时不得启动涉及选型的实现任务。

## Phase 1 — Setup（S1，共享基础设施）

**目的**：让后续任务可构建、可测试、可扫描；不含业务行为。

- [ ] T010 建立多模块构建配置 in `platform/pom.xml`（构建工具待 ADR-0005，路径随之调整）（AC: N/A）
- [ ] T011 [P] 配置代码格式化与静态检查 in `platform/pom.xml`（AC: N/A）
- [ ] T012 [P] 建立环境变量占位与配置加载约定（模型 provider、PostgreSQL、Redis）in `.env.example`（AC: NFR-9）
- [ ] T013 [P] 配置 CI：编译、单测、密钥扫描、Javadoc 与注释语言检查、覆盖率门槛（核心 ≥ 70%，其余 ≥ 60%）in `.github/workflows/ci.yml`（AC: NFR-3, NFR-7, NFR-10）
- [ ] T014 [P] 建立桩 provider 与测试夹具 in `platform/framework-adapter/src/test/java`（AC: AC-1.4）
- [ ] T015 [P] 建立统一错误码与异常基类 in `platform/agent-core/src/main/java`（AC: AC-1.2）
- [ ] T018 [P] 建立 Docker Compose（应用、PostgreSQL + pgvector、Redis）与健康检查、冒烟脚本 in `docker-compose.yml`（AC: NFR-12）
- [ ] T019 [P] 实现启动配置校验：必填环境变量缺失即失败并输出字段名 in `platform/framework-adapter/src/main/java`（AC: NFR-9）

**Checkpoint**：本地可构建、可跑空测试；CI 可执行密钥扫描、注释语言检查与覆盖率门槛；Compose 可启动且健康检查通过。

## Phase 2 — Foundational（S2，阻塞前置）

**目的**：框架层与工具调用层的最小能力；未完成不得开始任何 US 阶段。

- [ ] T020 定义 provider 接口与 Spring AI 主线适配（默认 OpenAI 兼容端点）in `platform/framework-adapter/src/main/java`（AC: FR-1, AC-1.1, NFR-9）
- [ ] T021 实现工具注册表（名称/参数/权限/超时声明）in `platform/tool-runtime/src/main/java`（AC: FR-2）
- [ ] T022 实现受控工具执行器（白名单、超时、拒绝路径）in `platform/tool-runtime/src/main/java`（AC: AC-1.2, AC-1.3）
- [ ] T023 [P] 编写沙箱与命令白名单测试 in `platform/tool-runtime/src/test/java`（AC: AC-1.2）
- [ ] T024 [P] 实现 traceId 透传与结构化日志 in `platform/agent-observability/src/main/java`（AC: AC-1.5）
- [ ] T025 编写"模型 + 工具"闭环集成测试 in `platform/tool-runtime/src/test/java`（AC: AC-1.1）
- [ ] T026 [P] 实现 LangChain4j 模型接入对照适配，并断言与主线同一请求输出一致 in `platform/framework-adapter/src/main/java`（AC: FR-1）
- [ ] T027 [P] 编写 provider 配置缺失与切换测试 in `platform/framework-adapter/src/test/java`（AC: NFR-9）

**Checkpoint**：一次带工具调用的任务可跑通并输出 traceId；无真实 Key 时测试全绿。

## Phase 3 — US-1 单 Agent 与示例模块底座（Priority: P1，MVP）

**Goal**：单 Agent 自主完成任务，示例模块具备统一骨架与运行入口。
**Independent Test**：提交一个需要工具的任务，轨迹含任务分解、工具调用与终止原因。

### 测试（先失败，后实现）

- [ ] T030 [P] [US1] 编写单 Agent 任务循环测试 in `platform/agent-core/src/test/java`（AC: AC-2.1）
- [ ] T031 [P] [US1] 编写工具失败回填与步数上限测试 in `platform/agent-core/src/test/java`（AC: AC-1.3, AC-2.4）

### 实现

- [ ] T032 [US1] 实现任务循环与终止判定 in `platform/agent-core/src/main/java`（AC: AC-2.1, FR-4）
- [ ] T033 [US1] 实现短期上下文与超长裁剪 in `platform/agent-core/src/main/java`（AC: AC-2.1）
- [ ] T034 [US1] 实现工具选择与失败回填 in `platform/agent-core/src/main/java`（AC: AC-1.3）
- [ ] T035 [US1] 建立 9 个示例模块目录骨架与统一运行入口 in `examples/pom.xml`（AC: FR-14）

### 补充任务（T007 完成后生成）

- [ ] T110–T118 逐个实现 9 个示例模块，每个模块一个任务、一个 PR（AC: 随模块对应层确定）

**Checkpoint**：单 Agent 可独立演示，测试全绿；示例模块骨架可运行空实现。

## Phase 4 — US-2 多 Agent 协作（Priority: P1）

**Goal**：多个 Agent 分工协作，冲突时输出唯一结论。
**Independent Test**：在 T032 已交付前提下，运行双 Agent 协作任务，轨迹可区分各自输入输出与裁决记录。

### 测试

- [ ] T040 [P] [US2] 编写消息路由与超时降级测试 in `platform/agent-collab/src/test/java`（AC: AC-2.2, AC-2.4）
- [ ] T041 [P] [US2] 编写冲突裁决测试 in `platform/agent-collab/src/test/java`（AC: AC-2.3）

### 实现

- [ ] T042 [US2] 实现角色注册与消息路由 in `platform/agent-collab/src/main/java`（AC: AC-2.2）
- [ ] T043 [US2] 实现裁决器与共识输出 in `platform/agent-collab/src/main/java`（AC: AC-2.3）
- [ ] T044 [US2] 实现单 Agent 失败降级与待人工标记 in `platform/agent-collab/src/main/java`（AC: AC-2.4）

**Checkpoint**：协作任务可独立演示；裁决理由可查。

## Phase 5 — US-3 可恢复 Graph 工作流（Priority: P2）

**Goal**：工作流可分支、可暂停、可恢复、可回退。
**Independent Test**：在 T032 已交付前提下，运行含人工介入与条件分支的工作流，暂停后恢复完成。

### 测试

- [ ] T050 [P] [US3] 编写定义解析与条件分支测试 in `platform/workflow-graph/src/test/java`（AC: AC-3.1）
- [ ] T051 [P] [US3] 编写检查点恢复幂等测试 in `platform/workflow-graph/src/test/java`（AC: AC-3.3）
- [ ] T052 [P] [US3] 编写人工介入与修正回退测试 in `platform/workflow-graph/src/test/java`（AC: AC-3.2, AC-3.4）

### 实现

- [ ] T053 [US3] 实现工作流定义解析与节点执行 in `platform/workflow-graph/src/main/java`（AC: AC-3.1）
- [ ] T054 [US3] 实现检查点存储与恢复 in `platform/workflow-graph/src/main/java`（AC: AC-3.3, FR-7）
- [ ] T055 [US3] 实现人工介入暂停/继续 in `platform/workflow-graph/src/main/java`（AC: AC-3.2）
- [ ] T056 [US3] 实现修正回退 in `platform/workflow-graph/src/main/java`（AC: AC-3.4）

**Checkpoint**：暂停状态可查询，恢复后副作用次数不变。

## Phase 6 — US-4 MCP 工具网关（Priority: P2）

**Goal**：MCP 工具经网关接入，具备权限、审计、限流、沙箱。
**Independent Test**：分别以有权限、无权限、超限流三种方式调用同一工具，行为与审计均符合预期。

### 测试

- [ ] T060 [P] [US4] 编写权限拒绝与限流测试 in `platform/mcp-gateway/src/test/java`（AC: AC-4.2, AC-4.3）
- [ ] T061 [P] [US4] 编写审计记录测试 in `platform/mcp-gateway/src/test/java`（AC: AC-4.4）

### 实现

- [ ] T062 [US4] 实现 MCP 工具注册与调用客户端 in `platform/mcp-gateway/src/main/java`（AC: AC-4.1）
- [ ] T063 [US4] 实现权限模型 in `platform/mcp-gateway/src/main/java`（AC: AC-4.2）
- [ ] T064 [US4] 实现限流器 in `platform/mcp-gateway/src/main/java`（AC: AC-4.3）
- [ ] T065 [US4] 实现审计记录 in `platform/mcp-gateway/src/main/java`（AC: AC-4.4）
- [ ] T066 [US4] 实现调用沙箱隔离 in `platform/mcp-gateway/src/main/java`（AC: AC-4.1, NFR-3）

**Checkpoint**：审计字段齐全；无权限调用不泄露工具是否存在。

## Phase 7 — US-5 运行时可观测与评测基线（Priority: P2）

**Goal**：按 traceId 还原全链路，指标可按任务与 Agent 拆分，评测可对比基线。
**Independent Test**：运行一次任务后查全链路；对固定评测集跑两次得到对比报告。

### 测试

- [ ] T070 [P] [US5] 编写 trace 串联与查询测试 in `platform/agent-observability/src/test/java`（AC: AC-5.1）
- [ ] T071 [P] [US5] 编写心跳假死检测测试 in `platform/agent-observability/src/test/java`（AC: AC-5.3）
- [ ] T072 [P] [US5] 编写评测基线与退化对比测试 in `platform/eval-harness/src/test/java`（AC: AC-5.4）

### 实现

- [ ] T073 [US5] 实现 trace 模型与查询接口 in `platform/agent-observability/src/main/java`（AC: AC-5.1）
- [ ] T074 [US5] 实现任务级指标（耗时、token、成本、状态）in `platform/agent-observability/src/main/java`（AC: AC-5.2）
- [ ] T075 [US5] 实现心跳检测与假死处置 in `platform/agent-observability/src/main/java`（AC: AC-5.3）
- [ ] T076 [US5] 实现成本归因 in `platform/agent-observability/src/main/java`（AC: AC-5.2）
- [ ] T077 [US5] 实现评测集、基线与回归报告 in `platform/eval-harness/src/main/java`（AC: AC-5.4）

**Checkpoint**：一条 traceId 可还原完整链路；报告能列出退化项。

## Phase 8 — US-6 持久记忆与高级 RAG（Priority: P3）

**Goal**：跨会话记忆可召回，回答带可核查出处。
**Independent Test**：会话 A 写入偏好，会话 B 召回；知识库提问的回答带引用。

### 测试

- [ ] T080 [P] [US6] 编写记忆写入与召回测试 in `platform/memory-rag/src/test/java`（AC: AC-6.1）
- [ ] T081 [P] [US6] 编写引用出处与无命中兜底测试 in `platform/memory-rag/src/test/java`（AC: AC-6.2, AC-6.3）

### 实现

- [ ] T082 [US6] 实现持久记忆存储 in `platform/memory-rag/src/main/java`（AC: AC-6.1）
- [ ] T083 [US6] 实现知识切分与索引 in `platform/memory-rag/src/main/java`（AC: AC-6.2）
- [ ] T084 [US6] 实现检索重排与出处拼装 in `platform/memory-rag/src/main/java`（AC: AC-6.2）
- [ ] T085 [US6] 实现无命中兜底 in `platform/memory-rag/src/main/java`（AC: AC-6.3）

**Checkpoint**：无伪造引用；记忆可按会话删除。

## Phase 9 — US-7 四个业务场景端到端（Priority: P2）

**Goal**：四个场景复用同一底座跑通。
**Independent Test**：T042、T053、T073、T082 交付后，逐个运行场景演示脚本。

- [ ] T090 [P] [US7] 智能问答场景端到端 in `scenarios/qa-assistant`（AC: AC-7.1）
- [ ] T091 [P] [US7] 合同预审场景端到端 in `scenarios/contract-review`（AC: AC-7.2）
- [ ] T092 [P] [US7] 内容创作场景端到端 in `scenarios/content-studio`（AC: AC-7.3）
- [ ] T093 [P] [US7] 数据分析场景端到端 in `scenarios/data-analyst`（AC: AC-7.4）
- [ ] T094 [US7] 校验场景无底座旁路（不得直连模型客户端）in `scenarios/README.md`（AC: AC-7.5）

**Checkpoint**：四个场景各有可重复执行的演示；场景代码中无独立模型客户端。

## Phase 10 — Polish（S10，跨故事收尾）

- [ ] T100 [P] 补齐错误码表 in `docs/error-codes.md`（AC: NFR-4）
- [ ] T101 [P] 编写分层 quickstart 验证步骤 in `docs/quickstart.md`（AC: 全部）
- [ ] T102 [P] 密钥扫描、依赖检查与注释语言检查复核 in `.github/workflows/ci.yml`（AC: NFR-3, NFR-7）
- [ ] T103 编写示例与场景演示脚本 in `scripts/demo.sh`（AC: SC-1, SC-2）
- [ ] T104 收尾 README 与文档一致性走查 in `README.md`（AC: SC-3）

## 依赖与执行顺序

- Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 / Phase 5（可并行）→ Phase 6 / Phase 7 / Phase 8（在 Phase 2、3 之后可并行）→ Phase 9 → Phase 10。
- 故事间依赖：US-2 依赖 T032；US-3 依赖 T032；US-4 依赖 T021/T022；US-5 依赖 T024；US-6 依赖 T032；US-7 依赖 T042、T053、T073、T082。
- T007 完成前，T035 与 T110–T118 不得启动；T017 完成前，T010 与构建相关任务不得启动；T008、T009、T016 已完成，作为选型依据。
- 同一文件的任务不得标 `[P]`。

## 实现策略

- **MVP 优先**：完成 Phase 1–3 即停下验证、可演示。
- **增量交付**：每个故事完成后独立验证、独立合并；单 PR 不超过 400 行。
- **单次运行边界**：一次实现只跑一个 Phase 或明确的任务区间；完成后报告进度再继续。

## 完成定义（Definition of Done）

- [ ] 任务对应的 AC 有自动化测试或 `quickstart.md` 手工步骤
- [ ] 相关测试在本地与 CI 通过
- [ ] 公开类、接口、方法均有英文 Javadoc 且标注 `@author Caspian`；注释与日志无中文
- [ ] 外部配置全部来自环境变量，无硬编码连接串、密钥与绝对路径；缺失必填项启动即失败
- [ ] 覆盖率达标（核心模块 ≥ 70%，其余 ≥ 60%）；Compose 一键启动与冒烟脚本通过
- [ ] 未引入 spec 之外的行为（diff 与任务一致）
- [ ] 无明文密钥、无写死绝对路径、无任意命令执行工具
- [ ] 遗留缺口已登记为新任务
