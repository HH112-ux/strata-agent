# Tasks：<功能名>

**Feature ID**: `<NNN-slug>`
**Inputs**: [`./spec.md`](./spec.md)、[`./plan.md`](./plan.md)
**Status**: Draft | Approved

## 格式约定

`- [ ] T<NNN> [P?] [US?] <动作> in <精确路径>（AC: <AC-ID>）`

- `[P]`：可与同阶段其他任务并行；同一文件的任务不得标 `[P]`。
- `[US?]`：所属用户故事编号，Setup / Foundational 阶段省略。
- 路径必须精确到模块或目录，构建工具确定后再统一调整前缀，不改变任务边界。

## 粒度

- 一个任务一次会话可完成并自测，目标 ≤ 2 个文件、≤ 200 行。
- 无法一次完成的，先拆任务，不得把整个 Phase 当一个任务。
- 无法验收的动词（“优化”“完善”“处理一下”）不算任务。

## Phase 0 — 规格与决策基线

- [ ] T001 <动作> in `<路径>`（AC: N/A）

**Checkpoint**：<可评审的文档基线>

## Phase 1 — Setup

- [ ] T010 <动作> in `<路径>`（AC: N/A）

**Checkpoint**：<可构建、可测试、可扫描>

## Phase 2 — Foundational

- [ ] T020 <动作> in `<路径>`（AC: <AC-ID>）

**Checkpoint**：<阻塞后续所有故事的底座能力就绪>

## Phase 3 — US-1 <故事名>（Priority: P1）

**Goal**：
**Independent Test**：

### 测试（先失败，后实现）

- [ ] T030 [P] [US1] 编写 <场景> 测试 in `<测试路径>`（AC: <AC-ID>）

### 实现

- [ ] T031 [US1] 实现 <行为> in `<源码路径>`（AC: <AC-ID>）

**Checkpoint**：<可独立演示与验证的判据>

## Phase 4 — Polish

- [ ] T090 [P] 补齐错误码与文档 in `docs/`（AC: <AC-ID>）

## 依赖与执行顺序

- Phase 0 → 1 → 2 → 3 → …；哪些阶段可并行在此写明。
- 未决的选型任务完成前，依赖该选型的实现任务不得启动。

## 完成定义（DoD）

- [ ] 任务对应的 AC 有自动化测试或 `quickstart.md` 手工步骤
- [ ] 测试在本地通过（CI 落地后以 CI 为准）
- [ ] 公开 API 有英文 Javadoc 且标注 `@author Caspian`；注释与日志无中文
- [ ] diff 与任务一致，未引入 spec 之外的行为
- [ ] 无明文密钥、无写死绝对路径
- [ ] 遗留缺口已登记为新任务
