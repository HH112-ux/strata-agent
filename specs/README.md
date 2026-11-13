# SDD 规格目录约定（specs/）

本仓库采用规格驱动开发（SDD）：先在 `specs/` 写清行为契约，再写实现。规格是事实源，代码是派生物。
目录沿用 `.specify/` + 根级 `specs/` 的结构（与 Spec Kit 一致），不另建 `docs/specs/`。

## 1. 目录形态

```text
specs/
├── README.md                        # 本文件：判定与流程
├── _templates/                      # 裁剪后的模板，复制后填写
│   ├── spec.md                      # 行为契约（必填）
│   ├── plan.md                      # 技术方案（必填）
│   ├── tasks.md                     # 任务清单（必填）
│   └── adr.md                       # 架构决策记录（可选，产物放 docs/adr/）
└── <NNN-feature-slug>/              # 一个 feature 一个目录，三位编号
    ├── spec.md
    ├── plan.md
    ├── tasks.md
    ├── research.md                  # 选型调研（有技术未知时）
    ├── data-model.md                # 数据模型（有持久化时）
    ├── contracts/                   # 接口契约（有外部消费方时）
    ├── quickstart.md                # 人工验证步骤
    └── checklists/                  # 需求质量清单（评审人勾选）
```

当前 feature：[`001-strata-platform/`](001-strata-platform/)。
归档目录：`specs/_archive/<year>/`；归档不等于删除，链接仍可追溯。

**统一字段**：`spec.md` 头部写 `Feature ID`、`Owner`、`Status`、`Version`、`Created`、`Last Updated`、`Related`。
**Task 格式**：`- [ ] T<NNN> [P?] [US?] <动作> in <精确路径>（AC: <AC-ID>）`。
**AC 句式**：EARS（`When/While/Where/If ... the <system> shall ...`），一条只描述一个可判定结果。
**禁止**：`spec.md` 写框架、库、表结构、API 路径、代码片段；`plan.md` 写 spec 未定义的新行为；`tasks.md` 出现“优化”“完善”这类无法验收的动词。

## 2. 什么时候必须写 spec

| 变更特征 | 走法 |
| --- | --- |
| 新能力、跨模块、有外部契约、多个示例/场景要复用 | 完整路径：spec → plan → tasks → 实现 → converge |
| 单模块功能、需求清晰 | 短路径：spec → plan → tasks → 实现 |
| 缺陷修复，且现有 spec 已定义期望行为 | 不走 feature 流程：先补失败测试，再修复；不改 spec（除非 spec 本身有歧义） |
| 纯重构、行为不变 | 不走 SDD：以“现有测试一行不改且全部通过”为验收 |
| 探索性原型 / Spike | 不走 SDD：先出结论，再补 ADR 或 spec 片段 |
| 文案、格式、注释、依赖补丁 | 不走 SDD：直接改，按 `AGENTS.md` 验证与审查 |

判断口径：**会改变可观测行为，且现有 spec 没有覆盖 → 必须写 spec**；只改实现、不改可观测行为 → 记 ADR 或 `plan.md` 备注即可。

## 3. 从 spec 到 tasks 的实际顺序

1. **立项判定**：按第 2 节选路径，分配 `NNN-feature-slug`，指定 Owner。说不出“不做会怎样”就不开工。
2. **复制模板**：`specs/_templates/spec.md` → `specs/<NNN-slug>/spec.md`，状态置 `Draft`。
3. **写 spec**：问题、范围、用户故事（含 AC）、FR/NFR、实体、边界、成功标准。不确定项写 `[NEEDS CLARIFICATION: 具体问题]`，禁止猜。
4. **G1 规格评审**：待澄清项清零；每条 AC 能判定 PASS/FAIL，并有测试或 `quickstart.md` 步骤承载。
5. **写 plan**：复制模板；填技术上下文、Constitution Check、架构与数据流、契约、数据模型、复杂度登记。每个新依赖/新抽象要么链接 ADR，要么写明被否决的更简方案。
6. **写 tasks**：按 Phase 拆分，每个任务带 ID、精确路径、AC 追溯、依赖；同一文件的任务不标 `[P]`。
7. **G2 一致性检查**：每条 FR/AC 至少被一个任务覆盖；没有孤立任务；无宪法冲突。
8. **实现**：一次只跑一个 Phase 或明确的任务区间，测试先行，完成后勾选任务。
9. **收敛核对**：对照 spec 检查覆盖缺口，缺口只追加任务，不改代码、不改规格；同一 AC 连续两轮未覆盖则回到 spec/plan 修根因。
10. **交付**：PR 正文写 Feature ID、变更的 AC、验证结果、未覆盖项；spec 状态改 `Implemented`。

追溯链必须闭合：

```text
FR/AC → Task → 测试或 quickstart 步骤 → PR → commit
```

## 4. 变更管理

| 类型 | 判定 | 处理 |
| --- | --- | --- |
| 缺陷 | 实现违反已批准的 spec/AC | 先写失败测试，再修实现；不改 spec |
| 意图变更 | 业务期望的行为变了 | 先改 spec（单独提交），再改 plan/tasks，最后改代码 |
| 实现发现 | 写代码时发现更简做法或技术限制 | 不改变可观测行为：记 ADR 或 plan 备注；改变行为：按意图变更处理 |

**红线**：不允许“代码先改、spec 后补”作为默认路径。确有紧急情况时，必须在同一 PR 内补齐 spec 变更，并在 PR 正文标注 `spec-sync: emergency`。

**状态机**：`Draft → InReview → Approved → Implementing → Implemented`；被替代时置 `Superseded` 并写明替代者路径，旧文件保留只读。

## 5. 责任边界

- 写规格与批准规格不能是同一次 Agent 会话；Agent 不得批准自己的 spec。
- Agent 不得删除、弱化或改写 AC 来迁就实现；不得勾选 `checklists/`。
- 评审人对 G1/G2 结论负责；Agent 产出的核对报告需人工复核后才能作为门禁证据。
- 宪法（[.specify/memory/constitution.md](../.specify/memory/constitution.md)）优先于 spec；冲突时停止实现并报告。

## 6. 模板使用

| 模板 | 复制到 | 何时用 |
| --- | --- | --- |
| [`_templates/spec.md`](_templates/spec.md) | `specs/<NNN-slug>/spec.md` | 每个需要规格的 feature |
| [`_templates/plan.md`](_templates/plan.md) | 同目录 `plan.md` | spec 通过 G1 后 |
| [`_templates/tasks.md`](_templates/tasks.md) | 同目录 `tasks.md` | plan 完成后 |
| [`_templates/adr.md`](_templates/adr.md) | `docs/adr/NNNN-slug.md` | 出现架构取舍时，一个决策一条 |

模板中的占位符必须全部替换，保留占位符的产物不得合并。
