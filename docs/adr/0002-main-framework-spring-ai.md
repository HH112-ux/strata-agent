# ADR-0002：主线框架选择 Spring AI

- **Status**: Accepted
- **Date**: 2026-11-13
- **Deciders**: Caspian
- **Related**: `specs/001-strata-platform/spec.md`、`specs/001-strata-platform/plan.md`、ADR-0003

## 背景（Context）

平台需要在同一技术栈内闭环四项能力：模型接入、工具调用、Graph 工作流编排、运行时可观测。候选主线为 Spring AI 与 LangChain4j：前者与 Spring 生态的配置、指标、健康检查天然一致，并提供 Graph 编排与工具调用的配套能力；后者在模型接入层提供了另一种抽象。单人开发、总工作量 43–63 人日，要求维护成本低、测试矩阵可控、后续可演示多框架抽象能力。框架选择同时决定工具层、编排层与可观测层的集成方式，必须先定。

## 决策（Decision）

我们采用 Spring AI 作为全平台主线框架，覆盖模型接入、工具调用、Graph 工作流与可观测集成；LangChain4j 仅作为模型接入层的对照实现，提供一个薄适配器，不参与工具、编排、记忆等其余层。

## 备选方案（Alternatives Considered）

| 方案 | 优点 | 缺点 | 为什么未选 |
| --- | --- | --- | --- |
| A（选中）Spring AI 主线 + LangChain4j 薄适配 | 配置、指标、健康检查与 Spring 生态一致；Graph 编排有配套实现；保留多框架抽象展示 | 需要额外维护一个适配器；需约束 LangChain4j 的使用边界 | — |
| B LangChain4j 作主线 | 模型接入抽象成熟，链式调用直观 | Graph 编排与可观测需额外自建集成；与 Spring 生态的配置与指标需二次适配 | 跨栈集成成本高于收益，且会拉长 S2–S5 阶段 |
| C Spring AI 与 LangChain4j 双主线 | 两条路线都可演示 | 工具、编排、记忆需要双份实现，测试矩阵翻倍 | 违背简约原则，43–63 人日预算无法覆盖 |
| D 自研模型与编排抽象 | 完全可控，无框架约束 | 工具调用、编排、记忆、可观测均需自建 | 超出项目预算，且偏离"通用智能体平台"的能力重点 |

## 后果（Consequences）

**正面**

- 工具调用、Graph 编排、指标与健康检查在同一生态内闭环，跨层集成成本最低。
- LangChain4j 适配器把多框架抽象收敛在模型接入层，可作为架构展示点。
- 后续新增能力优先复用 Spring 生态既有组件，减少自研面。

**负面 / 代价**

- 需要为 LangChain4j 适配器维护独立的依赖与兼容性测试。
- 主线与对照实现并存，需在代码结构上明确边界，避免被误用为第二条主线。
- 框架升级会同时影响多层，需要回归测试兜底。

**需要跟进的动作**

- [ ] 在 `platform/framework-adapter` 内划分 `spring-ai` 主线与 `langchain4j` 对照适配，禁止后者向上层暴露工具/编排能力（Caspian）
- [ ] 适配器需有独立单元测试，并对同一组请求断言两条实现的行为一致（Caspian）
- [ ] 在 plan 的复杂度登记表登记该适配器的维护成本（Caspian）

## 合规性（Compliance）

- 与 `constitution.md` 的关系：符合 Article VI（新增抽象需登记复杂度与被否方案）；Article II 要求两条实现均有可运行测试。
- 如何验证执行：代码评审检查 LangChain4j 依赖只出现在模型接入层；测试覆盖"同一请求、两种实现、一致输出"的对照用例。

## 备注（Notes）

边界约束：LangChain4j 适配器只实现 ChatModel 相关的 provider 接口，不实现工具注册、工作流编排、记忆与评测。若后续需要把 LangChain4j 提升为主线，必须新增 ADR 取代本决策。
