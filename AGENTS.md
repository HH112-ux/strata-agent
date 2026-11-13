# AGENTS.md — Strata 仓库工作规则

> 面向在本仓库工作的人类工程师与 AI Agent，同等适用。只写能被执行和检查的条款，不写口号。
> 优先级：用户当轮明确指令 > 本文件 > `docs/conventions/git-convention.md` > 其他仓库约定。冲突时停止操作，写明冲突点交负责人裁决，不自行取舍。

## 1. 开工前必读

按顺序读完再动手，缺一份不得开始写操作：

1. 本文件。
2. [README.md](README.md)：仓库定位与当前状态。
3. [.specify/memory/constitution.md](.specify/memory/constitution.md)：项目宪法，冲突时优先级最高。
4. [specs/README.md](specs/README.md)：什么时候必须写 spec、从 spec 到 tasks 怎么走。
5. 当前 feature 的 `spec.md`、`plan.md`、`tasks.md`，以及相关的 `docs/adr/`。
6. [docs/conventions/git-convention.md](docs/conventions/git-convention.md)：提交、分支、评审、回滚的完整规范。
7. [docs/conventions/repo-hygiene.md](docs/conventions/repo-hygiene.md)：什么必须提交、什么绝不能提交、什么要先评审。
8. [docs/agent/](docs/agent/)：运行时与风险侧制品。改动工具、权限、模型、数据流前，先读对应文件——
   [capability-contract.yaml](docs/agent/capability-contract.yaml)（工具与权限、护栏、HITL）、
   [threat-model.md](docs/agent/threat-model.md)、[eval-plan.md](docs/agent/eval-plan.md)、
   [observability.yaml](docs/agent/observability.yaml)、[releases.yaml](docs/agent/releases.yaml)、
   [degradation-and-rollback.md](docs/agent/degradation-and-rollback.md)、[runbook.md](docs/agent/runbook.md)、
   [data-boundary.md](docs/agent/data-boundary.md)。

## 2. 开工前检查

任何写操作前执行并读取输出：

```bash
git status
git branch --show-current
git log --oneline -5
git remote -v
```

| 检查结果 | 必须动作 |
| --- | --- |
| 当前在 `main` | 先切分支再改：`git switch -c <type>/<slug> origin/main` |
| 工作区有未提交改动 | 保留，不 `stash`、不丢弃；报告中列出文件清单。若属于其他会话或并行 Agent，改用独立 worktree，不在同一工作区改动 |
| 远端有新提交 | `git fetch origin` 后再开分支或同步 |
| 工作区干净 | 按任务执行 |

禁止在未读 `git status` 时 `git add`，禁止在不确定当前分支时提交。

## 3. 分支与提交

**分支**：`feat/<NNN-slug>`、`fix/<NNN-slug>`、`spec/<NNN-slug>`、`docs/<短语>`、`chore/<短语>`；全小写、短横线分隔，不含中文、空格、下划线。`main` 受保护，只接受 PR。

**提交信息**：英文 Conventional Commits，与 `git-convention.md` 第二章一致。

```text
<type>(<scope>): <subject>

<body：写为什么，每行 ≤ 72 字符>

<footer：BREAKING CHANGE / Closes #123 / Refs: #456>
```

- `type` 白名单：`feat`、`fix`、`docs`、`style`、`refactor`、`perf`、`test`、`chore`、`revert`；`build`、`ci` 并入 `chore`。
- 本仓库 `scope` 白名单（替代 `git-convention.md` §2.3 的 Spring 分层表）：`framework`、`tool`、`agent`、`collab`、`workflow`、`mcp`、`observability`、`memory`、`eval`、`examples`、`scenarios`、`specs`、`docs`、`ci`、`deps`、`db`。新增 scope 先改本节并单独提交。
- `subject`：祈使句动词原形、首词小写、≤ 50 字符、结尾无句号、不重复 type 与 scope。
- 一 commit 一事：文档、格式化、依赖、业务逻辑、规格变更不得混在同一提交。
- 暂存按文件名精确 `git add <file>`；禁止 `git add -A`、`git add .`。
- 规格变更与实现变更分开提交，便于单独回滚。

## 4. 改动粒度

- 一个 PR 只对应一个 Feature ID 或一件独立的事；单 PR 变更 ≤ 400 行。
- 超出 400 行：先报告实际行数与增长位置，等裁定；不得删减测试或压缩验收条件凑数。
- 一个任务应能在一次会话内完成并自测，目标 ≤ 2 个文件、≤ 200 行。
- 需要 spec 未定义的行为时停止并报告，不顺手实现。

## 5. 测试与验证

- 核心行为必须有自动化测试；测试名或注释标注对应 AC ID。
- 模型调用使用桩模型或可回放记录；自动化测试不得依赖真实付费 Key。
- 新增或修改公开 API 时，必须有英文 Javadoc 且标注 `@author Caspian`；代码注释与日志仅用英文。
- 文档改动至少核对：相对链接可解析、Mermaid 语法正确、无遗留 `<...>` 占位符、无 HTML 产物。`docs/agent/` 下的 `待补：<缺什么>` 是允许的显式缺口写法，但每处必须写明缺的是什么，空标题与空小节不允许。
- 报告中必须区分「已运行并通过」「已运行但失败」「未运行」，禁止用推测替代验证。
- 仓库已有 CI（`.github/workflows/ci.yml`，2026-11-13 接入），但尚无构建工具与测试（ADR-0005 未出）。构建与行为验证在此之前仍以人工核对加第 7 节代码审查为准；报告中必须注明哪些检查未运行。

## 6. SDD 门禁

- 是否必须写 spec 按 [specs/README.md](specs/README.md) 的判定表执行。
- 顺序：`spec.md` → G1 规格评审 → `plan.md` → `tasks.md` → G2 一致性检查 → 实现 → converge（收敛核对）→ PR。
- 实现 PR 不得修改 `spec.md` 中的 AC；需求变化先改 spec 并单独提交。
- 只实现指派的任务 ID 区间（如 `T010–T015`），越界改动视为缺陷。
- `checklists/` 由评审人勾选，Agent 不得自批，也不得修改勾选状态。
- 代码行为变化导致 AC 状态变化时，在同一 PR 内更新 spec；禁止只改代码不改规格。

### 6.1 各阶段必须产出 / 更新的制品

档位：**prototype（原型）**。判据与裁剪见《Agent 开发标准》§1.2、§4；升档触发为"接触生产数据、有写操作、对外可见、有 SLA"，任一命中必须补齐上线档全部制品，不得带着原型状态上线。

**成熟度：L1 已达成（2026-11-13）。** 判定依据是 `.github/workflows/ci.yml` 的两个 job，在 `push` 到 `main`、面向 `main` 的 `pull_request` 与 `workflow_dispatch` 时运行：

- `secret-scan`：gitleaks 以 `--log-opts="--all"` 扫全部提交历史，命中任一规则即非零退出，PR 显示失败。
- `docs-check`：YAML 可解析且顶层为映射（`.github/workflows/*.yml` 另按原文核对顶层 `on`/`jobs` 键）、Markdown 相对链接可解析、`specs/_templates/` 必填小节齐全，任一不满足即退出 1。

**尚未达成 L2**：无可运行 eval、无可用降级开关、无线上观测。构建与测试检查等 ADR-0005 选定构建工具后再加，不以占位任务充数。

**边界说明**：两项检查会在 PR 上真实运行并显示失败，但仓库尚未配置 required status checks，因此"红叉能否拦住合并"当前依赖评审人遵守；要变成强制拦截，需在仓库设置中把 `Secret scan (full history)` 与 `Docs integrity` 设为 required。

| 阶段 | 必须产出 / 更新 | 不做的后果 |
| --- | --- | --- |
| 立项 | 在 `spec.md` 写档位与三元组结论（私有数据 / 不可信内容 / 外部通信） | 后面的裁剪没有依据 |
| G1 规格评审 | `spec.md` 的 NFR 与 Scope Out → 同步 `docs/agent/data-boundary.md` 一页、`capability-contract.yaml` 的 `forbidden` 清单 | "不做什么"没变成"不提供哪些工具" |
| `plan.md`（G2 前） | `docs/agent/capability-contract.yaml`（D1 + D4）、`docs/agent/threat-model.md`（D3） | 新增工具未经登记就进实现；护栏凭空抄 |
| `tasks.md`（G2） | 把 D2 / D4 / D6 / D7 / D8 拆成任务并挂 AC；D 类任务 ID 与实现任务并列 | 制品永远"下次再补" |
| 实现 | `observability.yaml` 的 span 与字段、`capability-contract.yaml` 的 `guardrails`、开关 | trace 与护栏事后补不进 core 链路 |
| converge（收敛核对） | 核对 D1–D11 缺口，写入收敛报告 | 规格收敛了但工程上不可上线 |
| 发布 / 交付 | `releases.yaml` 登记三元组（模型快照 / prompt hash / 工具版本）；`runbook.md` 与 `eval-plan.md` 回归集同步 | 出事后无法反查版本、无处置步骤 |

**退出条件**：converge 阶段 D 类制品缺口为零，或在 `plan.md` 的复杂度登记表中登记为显式豁免（含 owner 与结案条件）。缺一项不得声明"规格已收敛"。

## 7. 交付前代码审查

- 任何改动在交付或合并前，必须用 `code-review-report-plugin` 的 `review-code-report` 技能对本次 diff 跑一次审查；文档类改动同样执行。
- Blocker 级问题必须修掉再交付；Major / Minor 如实列出并说明处理或遗留原因，不得隐藏。
- 审查结论（发现、修复、遗留）写入 PR 正文或交付报告。审查不替代测试。

## 8. 红线

以下行为无条件禁止，唯一例外是负责人当轮明确点名该具体命令：

| 编号 | 禁止行为 |
| --- | --- |
| F1 | 对 `main` 或任何他人分支 force push（含 `--force-with-lease`） |
| F2 | 在 `main` 上直接 commit 或 push |
| F3 | `git reset --hard`、`git clean -fdx`、`git checkout -- .`、`git restore .` |
| F4 | `git commit --no-verify`，或临时禁用钩子与密钥检查 |
| F5 | 提交密钥、证书、`.env`、IDE 配置、大于 5MB 的二进制 |
| F6 | 擅自改与本任务无关的文件：顺手格式化、升级依赖、重构无关代码、删除“看起来无用”的文件 |
| F7 | 未实际运行就声称“已验证”“测试通过” |
| F8 | 未经授权合并 PR、把 draft 转 ready、打 tag、删除分支 |
| F9 | 新增或扩大工具权限却不更新 `docs/agent/capability-contract.yaml`，或注册未登记的工具 |

已推送的违规提交用 `git revert` 修复并留痕，禁止用 reset 改写历史。发现疑似密钥立即停止，报告文件与行号范围及密钥类型，不回显明文。

## 9. 交付报告

每次交付至少包含：

1. 当前分支（`git branch --show-current`）。
2. 本次 commit 短 hash 与 header；无提交则写“未提交”及原因。
3. 改动文件清单。
4. 实际执行的验证命令与结果（通过 / 失败 / 未运行）。
5. 未做与待确认事项。
6. 需要人类执行的动作（推送、建 PR、合并、打 tag）。
