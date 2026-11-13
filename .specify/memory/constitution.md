# 项目宪法（Constitution）：Strata（智层）

**Version**: 1.1.0 | **Ratified**: 2026-11-13 | **Last Amended**: 2026-11-13
**Owner**: Caspian | **Reviewers**: Caspian（单人仓库阶段，评审人待扩充）

## 1. 适用范围与优先级

- 适用于：Strata 通用智能体平台仓库内的全部能力实现，包括六层能力栈、9 个示例模块、四个业务场景与六项创新能力。
- 冲突裁决顺序：本宪法 > `specs/<feature>/plan.md` > `specs/<feature>/spec.md` 中的实现性描述 > 代码注释。
- 本宪法不规定具体 feature 的行为；feature 行为只写在 `spec.md`。

## 2. 核心原则（Core Principles）

### Article I — 文档先行与规格即契约（Docs-First, Spec is the Contract）

**规则（MUST/MUST NOT）**

- MUST：任一能力面（六层中的任一层、任一业务场景、任一项创新能力）在写实现之前，必须先在 `specs/<feature>/` 完成 `spec.md`、`plan.md`、`tasks.md`，并通过 G1 规格评审与 G2 一致性分析。
- MUST：实现必须能追溯到编号的 FR 或 AC；PR 正文引用 Feature ID 与任务 ID。
- MUST NOT：不得在 `spec.md` 中写框架、库、表结构、目录结构等实现细节；实现中不得引入 spec 未定义的行为。
- 判定方式：PR 中 spec 的每条 AC 能映射到至少一个测试或 `quickstart.md` 步骤；diff 与 `tasks.md` 条目一致。

### Article II — 每层必须有可运行证据与测试（Runnable Evidence per Layer）

**规则**

- MUST：六层能力中的每一层都必须同时具备三件套——可运行的最小实现、至少一个自动化测试、一条可在本地复现的启动或验证命令（记录在 `docs/quickstart.md` 或 README）。
- MUST：9 个示例模块与四个业务场景必须运行在同一套底座上，不得为通过验收而另起旁路。
- MUST NOT：不得以"接口已就绪""骨架已搭好""示例后续补"声索某层完成。
- 判定方式：每层交付的 PR 附带命令与输出片段（或 CI job 链接）；缺任一证据即视为未完成。

### Article III — 敏感信息零入库与受控执行（Secrets Never Committed, Controlled Execution）

**规则**

- MUST：所有密钥、token、凭据、连接串一律通过环境变量注入；仓库只保留 `.env.example` 占位文件。
- MUST：工具执行必须受白名单、超时、资源上限与审计四类约束；默认拒绝未登记工具。
- MUST NOT：不得提交任何真实凭据；不得写死本机绝对路径；不得提供可执行任意 shell 命令（包括 `kill -9`、任意 `mvn` 等）的对外工具。
- 判定方式：CI 密钥扫描通过；工具注册表逐项列出命令白名单与超时；代码评审检查配置来源与路径写法。

### Article IV — 自主设计与对外口径一致（Original Design, Consistent Public Wording）

**规则**

- MUST：README、文档、commit、PR 与演示材料统一按"自主设计 / 自主实现"口径书写，只陈述方案、决策与实现理由。
- MUST NOT：不得出现任何指向外部资料来源的表述；不得引用未获授权的外部素材。
- 判定方式：对外发布前做一次文案走查；评审人对新增对外文案逐段确认。

### Article V — 可观测优先（Observability First）

**规则**

- MUST：每次 Agent 运行必须生成 traceId，并贯穿模型调用、工具调用与工作流节点。
- MUST：核心链路必须产出结构化日志与任务级指标（耗时、token、成本、状态、心跳）。
- MUST NOT：不得以"后续统一接入监控"为由合并无日志、无指标的核心链路。
- 判定方式：核心链路 PR 附一条真实 trace 或指标输出；`NFR-4` 所列指标在 `plan.md` 中齐全。

### Article VI — 简约与复杂度留痕（Simplicity & Complexity Tracking）

**规则**

- MUST：新增模块、依赖或抽象层，必须在 `plan.md` 的复杂度登记表中写明理由与被否决的更简方案，并给出批准人。
- MUST NOT：不得为假设中的未来需求预留扩展点；不得为演示效果引入无法维护的临时代码。
- 判定方式：`plan.md` §7 的每一项能与 diff 对应；评审人有权要求删减。

### Article VII — 代码注释与语言规范（Code Comments & Language Convention）

**规则**

- MUST：所有公开类、接口、方法一律编写英文 Javadoc，说明职责、参数、返回值与关键副作用；作者统一标注 `@author Caspian`。
- MUST：代码注释与日志文案一律使用英文；日志必须包含可独立排查问题的上下文（traceId、任务 ID、工具名、状态等）。
- MUST：中文只出现在文档（`spec.md`、`plan.md`、ADR、README 及同类说明文档）中。
- MUST NOT：不得在代码注释或日志中出现中文；不得留有无注释的公开 API。
- 判定方式：CI 静态检查（Javadoc 与语言规则）通过；评审人抽查新增公开类型与方法，逐项确认注释存在且为英文。

## 3. 工程约束（Engineering Constraints）

- 语言/运行时：JVM 生态；Java 版本待决策（见 ADR-0002 待定项）。
- 主线框架：Spring AI 与 LangChain4j 二选一作为主线，待决策（ADR-0002）；不得双主线并行维护。
- 存储与中间件：待决策（ADR-0003）；决策前不得在实现中锁定具体产品。
- 允许的依赖来源：公开 Maven 仓库，版本锁定；不得引入来源不明的二进制或脚本。
- 测试分层要求：单元测试覆盖核心分支；集成测试覆盖跨层调用；模型调用使用桩模型或可回放记录，自动化测试不得依赖真实付费 Key。
- 提交与分支规范：遵循 `/Users/caspian/.trae-cn/memory/references/git-convention.md`，Conventional Commits，分支模型 `main + develop`。
- 文档格式：统一中文 Markdown，图示使用 Mermaid 代码块，不产出 HTML 文档。
- 代码语言：代码注释与日志文案统一英文；公开类、接口、方法必须带英文 Javadoc 与 `@author Caspian`；中文仅用于文档。
- 禁止事项：明文密钥、写死绝对路径、任意命令执行工具、无测试的核心链路、在 `spec.md` 中写实现细节。

## 4. 质量闸门（Quality Gates）

| 闸门 | 触发时机 | 通过条件 | 证据位置 |
| --- | --- | --- | --- |
| G1 规格评审 | `spec.md` 完成 | 无 `[NEEDS CLARIFICATION]`；AC 全部可判定 | PR 评论 / 评审记录 |
| G2 一致性分析 | `tasks.md` 完成、实现前 | 任务均可追溯到 FR/AC；无孤立任务 | PR 中粘贴的一致性核对结果 |
| G3 实现完成 | 合并前 | 自动化测试通过；每层附可运行证据；密钥扫描 0 命中；Javadoc 与注释语言检查通过 | CI + PR |
| G4 交付核对 | 发布或演示前 | 变更记录、回滚说明、监控项齐备 | 发布单 / demo 清单 |

## 5. 治理（Governance）

- 修订提案：任何维护者可提 PR，标题 `docs(constitution): <变更摘要>`。
- 通过条件：单人阶段由 Owner 批准并记录；扩充评审人后需 2 名核心维护者批准且无未解决反对意见。
- 版本规则：破坏既有原则语义 → MAJOR；新增或收紧原则 → MINOR；措辞澄清 → PATCH。
- 生效方式：合并即生效；受影响的进行中 feature 必须在 `plan.md` 的 Constitution Check 重新评估并记录。
- 例外机制：允许在 `plan.md` 的复杂度登记表记录"经批准的例外"，必须写明期限与补救计划；不得在代码注释里私自豁免。

## 6. 修订记录（Amendment Log）

| 版本 | 日期 | 变更摘要 | 提案人 | 批准人 |
| --- | --- | --- | --- | --- |
| 1.0.0 | 2026-11-13 | 初始版本 | Caspian | Caspian |
| 1.1.0 | 2026-11-13 | 新增 Article VII：代码注释与语言规范（英文 Javadoc、`@author Caspian`、中文仅用于文档） | Caspian | Caspian |
