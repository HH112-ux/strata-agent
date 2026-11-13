# 行业高标准 Git 规范（团队定稿版）

> 适用范围：Java / Spring Boot 后端团队（单体与微服务仓库）
> 托管平台：默认 GitHub，GitLab 差异见 [4.6](#46-gitlab-对应配置差异)
> 版本：v1.0（团队定稿）· 生效日期：以仓库合并该文档的日期为准
> 维护人：后端架构组 + DevOps

本文档的每一条款都采用 **【必须】/【建议】/【禁止】** 三级措辞，便于 Code Review、季度审计和新人评审时逐条引用。所有可直接落地的配置文件均以完整代码块内嵌，复制到仓库根目录即可生效。

## 目录

- [一、总则与适用范围](#一总则与适用范围)
- [二、提交信息规范](#二提交信息规范)
- [三、分支管理规范](#三分支管理规范)
- [四、评审与合并规范](#四评审与合并规范)
- [五、标签与版本（SemVer）](#五标签与版本semver)
- [六、禁止行为红线清单](#六禁止行为红线清单)
- [七、配套工具与自动化](#七配套工具与自动化)
- [八、CHANGELOG 自动生成](#八changelog-自动生成)
- [九、回滚规范](#九回滚规范)
- [十、备选 GitFlow 分支模型](#十备选-gitflow-分支模型)
- [十一、落地路径与检查清单](#十一落地路径与检查清单)

---

## 一、总则与适用范围

### 1.1 适用范围

【必须】本文档适用于所有 Java / Spring Boot 仓库，包括：

| 仓库类型 | 是否适用 | 说明 |
| --- | --- | --- |
| 单体应用（单 module） | 适用 | 全量条款 |
| 多 module / 多服务 Monorepo | 适用 | 用 `scope` 区分模块，见 2.3 |
| 微服务单仓（每服务一仓） | 适用 | `scope` 取服务内分层名 |
| 公共二方库（SDK / starter） | 适用 | 发布流程按 SemVer 严格执行第五章 |
| 纯前端 / 纯脚本仓库 | 部分适用 | 提交规范与分支模型适用，第七章 Java 门禁不适用 |

【建议】前端、文档、运维类仓库复用本文档的第二章（提交信息）、第三章（分支）、第四章（评审），Java 专项门禁按需裁剪。

### 1.2 分支模型定位（重要）

【必须】本文档采用 **主干强保护 + 短生命周期特性分支（GitHub Flow 变体）**。

这**不是**纯 Trunk Based Development（TBD），两者差异必须被团队理解，避免在评审时说"我们不是 TBD 吗，为什么还要 PR"：

| 维度 | 纯 Trunk Based Development | 本文档（GitHub Flow 变体） |
| --- | --- | --- |
| 代码进入 main 的方式 | 直接提交 main，或极短 PR | **必须经 PR 合并，禁止直推 main** |
| 分支寿命 | < 1 天，理想是小时级 | ≤ 3 个工作日，鼓励更短 |
| 未完成功能的隐藏手段 | feature flag 为**必要**手段 | feature flag 为**补充**手段 |
| 发布方式 | 持续发布，main 即生产 | main 稳定 + 少量 `release/*` 冻结窗口 |
| 评审强制程度 | 可异步、可事后 | **合并前强制 approve + CI 全绿** |
| 适合团队 | 高成熟度、强自动化、能按请求灰度 | 需要评审留痕、有版本交付要求的团队 |

【必须】因此本模型的三个硬性支柱是：**主干保护（分支保护规则）**、**短分支（≤ 3 天）**、**PR + CI 门禁**。任何一条缺失，该模型都会退化为"带 PR 的散乱开发"。

### 1.3 feature flag 补充约定

【建议】预计无法在 3 个工作日内完成的功能，必须引入开关（Spring Boot 侧可用 `@ConditionalOnProperty`、配置中心或 `FeatureFlagService`），而不是维持一个长期分支。

【必须】feature flag 的清理要留痕：开关上线后 **2 个迭代内**必须提 PR 移除，并在 PR 描述中关联原始 feature PR。

【禁止】用注释掉代码的方式"隐藏未完成功能"，这会污染代码库并让静态分析失真。

示例（Spring Boot）：

```java
@RestController
@RequestMapping("/api/v2/recommend")
@ConditionalOnProperty(name = "feature.recommend-v2.enabled", havingValue = "true")
public class RecommendV2Controller {
    // 未完成能力默认关闭，main 可随时发布
}
```

### 1.4 平台差异总览

| 能力 | GitHub | GitLab |
| --- | --- | --- |
| 主干保护 | Branch protection / Rulesets | Protected branches |
| 评审强制 | Required reviewers + CODEOWNERS | Approval rules + Code Owners |
| 状态门禁 | Required status checks | Merge request pipelines + "Pipelines must succeed" |
| 合并队列 | Merge queue | Merge trains |
| 提交信息校验 | Actions + commitlint | CI job + commitlint |
| 密钥扫描 | Secret scanning + push protection | Secret detection（需 Ultimate 或接入 gitleaks） |

【必须】同一组织内所有仓库的规则必须一致，禁止出现"这个仓库能直推 main、那个不能"的例外，例外需架构组书面批准并写进仓库 README。

---

## 二、提交信息规范

采用 [Conventional Commits 1.0.0](https://www.conventionalcommits.org/zh-hans/v1.0.0/)（下称 CC），**强制**执行。

### 2.1 提交格式

```text
<type>(<scope>): <subject>
<空行>
<body>
<空行>
<footer>
```

【必须】四段结构如下：

| 部分 | 要求 | 校验方式 |
| --- | --- | --- |
| header（type） | 只能取 2.2 表格中的固定值 | commitlint `type-enum` + CI |
| header（scope） | 只能取 2.3 白名单；`feat/fix/refactor/perf/test` 必填 | commitlint `scope-enum` + 自定义规则 |
| header（subject） | 祈使句、首词小写、≤ 50 字符、结尾无句号 | commitlint `subject-max-length` / `subject-full-stop` |
| body | 每行 ≤ 72 字符，只写"为什么" | commitlint `body-max-line-length` |
| footer | `BREAKING CHANGE:` / `Closes #123` / `Refs: #456` | 人工评审 + CI 提示 |

【必须】header 与 body、body 与 footer 之间各留**一个空行**，否则 footer 不会被解析为 footer（`Closes #123` 会退化为普通正文，GitHub 不会自动关单）。

### 2.2 type 固定表

| type | 语义 | 是否进 CHANGELOG | 典型场景 |
| --- | --- | --- | --- |
| `feat` | 新功能 | 是 | 新增接口、新增查询能力 |
| `fix` | 缺陷修复 | 是 | 修复评分过滤、修复 NPE |
| `docs` | 仅文档 | 否 | README、接口文档、本文档 |
| `style` | 格式/空白，不影响语义 | 否 | 缩进、换行、import 顺序 |
| `refactor` | 重构，不改行为 | 是（按需筛选） | 抽 service、换实现 |
| `perf` | 性能优化 | 是 | 批量写入、索引优化 |
| `test` | 测试相关 | 否 | 补单测、修 flaky 用例 |
| `chore` | 杂务：构建、CI、依赖、版本 | 否 | 升级依赖、改流水线 |
| `revert` | 回滚既有提交 | 是 | `git revert` 产出的提交 |

【必须】**`build` 与 `ci` 已并入 `chore`**，不再单列。理由：Spring Boot 仓库里"改 pom"与"改流水线"经常同时发生，拆两个 type 只会让作者纠结。区分场景请用 scope：`chore(deps): ...`、`chore(github-actions): ...`、`chore(gitlab-ci): ...`。

【禁止】新增自定义 type：`update`、`temp`、`improve`、`wip`、`bugfix`、`hotfix`、`change` 一律禁止。这类 type 一旦出现，CHANGELOG 分组会失效、`chore` 会被滥用成"什么都塞"。

【建议】`revert` 使用 `git revert` 生成的提交，并按 9.1 的格式手工改为 `revert: <被回滚的原始 header>`，以保留可追溯性。

### 2.3 scope 白名单

【必须】scope 只能从下表取（Spring Boot 项目基线白名单）：

| 分类 | 可用 scope |
| --- | --- |
| 分层/组件 | `controller`、`service`、`repository`、`mapper`、`entity`、`dto`、`es`、`springai`、`embedding`、`ollama`、`security`、`cache`、`mq`、`scheduler` |
| 基础设施 | `config`、`docker`、`k8s`、`db`、`migration`、`logging`、`monitor` |
| 工程化 | `deps`、`build`、`github-actions`、`gitlab-ci`、`docs`、`test`、`release` |
| 平台级 | `api`、`auth`、`gateway`、`bom`、`parent` |

【必须】`scope-enum` 白名单是**需要持续维护的资产**。团队必须明确一个 owner（默认架构组），并约定扩白名单的流程：提 PR 修改 `commitlint.config.js` 的 `scopeWhitelist` → 1 人 approve → 合并。

【建议】若某次提交确实无法归类，说明白名单已过期，**先去扩白名单**，不要临时写一个从未出现过的 scope。否则会频繁出现"开发觉得合理、lint 判定非法"的摩擦，团队最终会关掉 lint——这是最常见的失败路径。

【必须】微服务或多 module 仓库，可将 `scope` 从"分层名"改为"模块名 + 分层名"（如 `order-service`、`user-controller`），但必须整体统一，禁止混用两套命名。

### 2.4 subject 规则

| 条款 | 级别 | 说明 |
| --- | --- | --- |
| 使用祈使句动词原形 | 【必须】 | `add` / `fix` / `remove` / `rename` / `raise` / `correct`，不写 `added` / `adds` / `fixing` |
| 首个单词全小写 | 【必须】 | 由自定义规则 `subject-first-word-lower` 校验 |
| 结尾不加句号 | 【必须】 | 由 `subject-full-stop: never` 校验 |
| 长度 ≤ 50 字符 | 【必须】 | 由 `subject-max-length` 校验 |
| 专有名词保留原大小写 | 【必须】 | Elasticsearch、Ollama、SpringAI、Flyway、JaCoCo 等 |

【必须】关于专有名词的**坑**：`@commitlint/config-conventional` 内置的 `subject-case: [2, 'never', ['sentence-case','start-case','pascal-case','upper-case']]` 会把 `use Elasticsearch index` 判为非法（含 PascalCase 单词），也会把 `add SpringAI chat memory` 判掉。因此本规范在 [7.1](#71-commitlint-完整配置) 中**关闭 `subject-case`**，改用自定义规则 `subject-first-word-lower`——只校验首个单词是否小写，允许后续单词保留专有名词大小写。

【禁止】为了绕过该规则而把专有名词写成 `elasticSearch`、`springai chat`（全小写）或 `spring-ai`（改名）。名称必须与官方文档一致，搜索引擎和新人才能对上。

【建议】subject 里不要重复 type 的语义，也不要重复 scope：

- 错误：`fix(es): fix vector query score filter bug`（`fix` 出现两次）
- 正确：`fix(es): correct score filter in vector query`

- 错误：`chore(ollama): update ollama max loaded models env`（`ollama` 出现两次，且 `update` 是禁用的模糊动词）
- 正确：`chore(ollama): raise max loaded models`

### 2.5 body 规则

【必须】body 说明 **why（为什么改、解决什么问题）**，不描述 how（代码细节本身在 diff 里）。

【必须】每行 ≤ 72 字符（`body-max-line-length`），保证 `git log` 在 80 列表宽终端下不折行。

【建议】body 用 `-` 列点，一条一件事；涉及取舍时写清"为什么不选另一种方案"。

【必须】关闭工单的关键字（`Closes` / `Fixes` / `Resolves`）**只能写在 footer**。写在 body 里 GitHub 不会识别，工单不会自动关闭。

### 2.6 footer 规则

| 场景 | 写法 | 要求 |
| --- | --- | --- |
| 破坏性变更 | `BREAKING CHANGE: <说明>` | 【必须】全大写，且 header 必须带 `!`，如 `feat(api)!: remove legacy v1 endpoint` |
| 关闭工单 | `Closes #123` | 【必须】写在 footer；大小写敏感，`closes #123` 不生效 |
| 仅关联不关闭 | `Refs: #456` | 【建议】用于背景关联、后续跟进 |
| 多人协作 | `Co-authored-by: Name <email>` | 【建议】成对开发时使用 |

【必须】`BREAKING CHANGE:` 与 header 中的 `!` **必须成对出现**。只有 `!` 没有 footer 说明，等于让下游只看到"坏了"却不知道"怎么改"；只有 footer 没有 `!`，自动化工具（semantic-release、git-cliff）可能识别不到破坏性变更，导致版本号该升 major 却升成 minor。

### 2.7 正例与反例

三个正确示例（覆盖 springai / es / ollama 场景）：

```text
feat(springai): add streaming chat memory advisor

Introduce a chat memory advisor so multi-turn conversations keep
context across requests without client-side session storage.

Closes #241
```

```text
fix(es): correct score filter in vector query

The min_score filter was applied after top-k truncation, dropping
relevant documents ranked just below the threshold.

Refs: #268
```

```text
chore(ollama): raise max loaded models

Bump OLLAMA_MAX_LOADED_MODELS from 1 to 3 so parallel evaluation
jobs stop evicting each other's models during batch tests.
```

破坏性变更的正确写法：

```text
feat(api)!: drop deprecated /v1/chat endpoint

BREAKING CHANGE: clients must migrate to /v2/chat; /v1/chat now returns 410.
```

错误示例与修正：

| 错误写法 | 问题 | 正确写法 |
| --- | --- | --- |
| `fix(es): fix vector query score filter bug` | subject 重复 type 动词；`bug` 冗余 | `fix(es): correct score filter in vector query` |
| `chore(ollama): update ollama max loaded models env` | scope 与 subject 重复；`update` 模糊 | `chore(ollama): raise max loaded models` |
| `update(service): 修改了一些逻辑` | 自定义 type；中文；无信息量 | `refactor(service): extract order pricing policy` |
| `feat: 新增用户导出功能。` | 缺 scope；中文；带句号 | `feat(controller): add user export endpoint` |
| `feat(api): add /v2/chat and drop v1` | 一提交多事；破坏性变更未标注 | 拆两个提交，破坏性的那个用 `feat(api)!:` + footer |
| `fix(es): Fix Score Filter.` | 首词大写；带句号；Title Case | `fix(es): correct score filter` |

【必须】一个提交只做一件事。若发现提交里混了格式化与逻辑修改，必须在合并前用 `git rebase -i` 拆开（仅限自己的特性分支，见 3.5）。

### 2.8 语言约定

| 载体 | 语言 | 理由 |
| --- | --- | --- |
| commit message | 英文 | CHANGELOG、git-cliff、semantic-release、IDE 插件、`git log --grep` 都基于英文 type/动词；中文提交会让自动分组与检索失效 |
| PR 标题 | 英文（需通过 commit 规范校验），见 4.3 | squash 后它就是 main 上的 commit message |
| PR 描述、文档、注释 | 中文 | 面向团队阅读；注释解释"为什么"用中文更准确 |

【必须】禁止中英混排的 type（如 `修复(service): ...`）——`type-enum` 会直接拒绝。

【建议】英文表达不熟练时，先用一句话写清"改了什么、为什么"，再套模板；语法不完美可以接受，不可接受的是无信息量。

---

## 三、分支管理规范

### 3.1 分支清单

| 分支 | 来源 | 合入目标 | 生命周期 | 命名示例 |
| --- | --- | --- | --- | --- |
| `main` | — | —（受保护） | 永久 | `main` |
| `feature/*` | `main` | `main` | ≤ 3 个工作日 | `feature/user-export-241` |
| `fix/*` | `main` | `main` | ≤ 2 个工作日 | `fix/es-score-filter-268` |
| `hotfix/*` | `main`（或 release tag） | `main` + `release/vX.Y.Z` | ≤ 1 天 | `hotfix/token-expired-911` |
| `release/vX.Y.Z` | `main` | 打 tag 后归档 | 一个发布窗口（≤ 1 周） | `release/v1.4.0` |

【必须】`main` 为唯一长期分支，永不删除、永不直接提交。

【建议】不设 `develop` 分支。多一条长期分支就多一份合并负担，且极易演化成"事实上的主干"。

### 3.2 命名规则

【必须】命名规则：

- 全小写，单词用短横线 `-` 分隔；禁止下划线、空格、驼峰
- 禁止中文、禁止 emoji
- 建议格式：`feature/<短语义>-<工单号可选>`
- 短语义 ≤ 4 个单词，能看出做什么（`user-export` 好，`new-stuff`、`temp`、`test1` 差）

【禁止】个人名前缀分支（`zhangsan/xxx`）、日期前缀（`20261029-xxx`）、无意义分支（`dev`、`tmp`、`branch1`）。分支应按"意图"命名，而不是按"人"或"时间"。

### 3.3 生命周期与拆分

【必须】特性分支寿命 ≤ 3 个工作日。到期未合并，按下列顺序处理：

1. 能拆则拆：把已完成且可独立发布的部分先合并（配合 feature flag）
2. 不能拆则引入开关（1.3），让未完成代码以关闭状态进入 main
3. 仍不行则升级到架构组评审，并登记"长分支例外"（含原因、预计合并日期）

【必须】合并后自动删除远端分支（开启 `Auto-delete head branches`，见 4.5）。

【禁止】长期存活的"巨型分支"（> 1 周或涉及 > 200 文件改动）。它会导致：review 无法有效进行、冲突呈指数增长、CI 反复红、合并即事故。

### 3.4 同步策略（按分支类型区分）

**这条必须按分支类型区分，否则会自相矛盾。** 历史改写只允许发生在"自己独占、别人不基于它开发"的分支上。

| 分支类型 | 允许 rebase main | 允许 force push | 说明 |
| --- | --- | --- | --- |
| 自己的 `feature/*` / `fix/*` | 【必须】允许，推荐 | 允许（`--force-with-lease`） | 独占分支，rebase 可保持线性历史 |
| 多人共用的特性分支 | 【禁止】rebase | 【禁止】force push | 改写会让同事的本地分支全部失效 |
| `main` | 【禁止】 | 【禁止】 | 公共主干 |
| `release/vX.Y.Z` | 【禁止】 | 【禁止】 | 多人 + 发布基线 |
| `hotfix/*` | 【禁止】rebase（寿命极短，直接 merge） | 仅允许 `--force-with-lease` | 需要保留止血过程 |

【必须】合并前（提交 PR 后、点 Merge 前）必须把分支同步到**最新 `main`**：

```bash
# 自己独占的分支：rebase 方式（推荐，历史线性）
git fetch origin
git rebase origin/main

# 多人共用分支：merge 方式（不改写历史）
git merge origin/main
```

【必须】如果不做这一步，就会出现经典的"本地绿、合完红"：CI 只在旧 main 上验证过你的分支，合并后的组合状态从未被测试。

【禁止】用 `git push --force`（无 `--force-with-lease`）；`--force-with-lease` 会在远端被别人更新时拒绝推送，是唯一允许的强推形式。

### 3.5 commit 整理（仅限独占分支）

【建议】PR 提交前用 `git rebase -i origin/main` 整理：合并 WIP 提交、按"一提交一事"拆分、修正提交信息。

【禁止】在已有人基于你的分支开发、或 PR 已有评审意见正在讨论时改写历史——会让评审的 diff 锚点全部失效。改写前先看 `git log origin/<branch>` 是否已推送并被他人拉取。

### 3.6 release 分支与回合并策略

【必须】`release/vX.Y.Z` 的定位是**发布冻结窗口**，不是第二个开发主干：

- 从 `main` 拉出，只接受 `fix` / `hotfix` / 版本号与 CHANGELOG 提交
- 【禁止】在 release 分支上开发新功能
- 打 tag 并发布后，release 分支归档（保留只读，不删除，便于追溯）

回合并（back-merge）有两种做法，本规范**默认采用 A**：

| 方案 | 做法 | 优点 | 代价 |
| --- | --- | --- | --- |
| **A. 双 PR 移植（默认，推荐）** | hotfix 分别对 `main` 与 `release/vX.Y.Z` 各提一个 PR | 兼容 `Require linear history`；历史干净；不产生跨分支 merge 提交 | 需要两次 PR（可用同一分支 cherry-pick，见下） |
| B. 整分支回合并 | 把 `release/vX.Y.Z` 整体 merge/PR 回 `main` | 一次搞定 | 会产生 merge 提交，与 `Require linear history` 冲突；长期使用会让 main 历史出现大量无意义合并 |

方案 A 的操作方式（同一个修复分支，产出两个 PR）：

```bash
# 1) 修复在 hotfix 分支完成，先合入 main（squash）
# 2) 再对 release 分支提 PR，只 cherry-pick 该修复
git checkout release/v1.4.0
git cherry-pick <main 上 squash 后的 hash>
git push origin release/v1.4.0
```

【必须】若确实需要方案 B（例如 release 分支已积累多个必须整体带回的提交），必须在 PR 中说明原因，并由管理员通过 ruleset bypass 执行，同时在 PR 描述里记录"linear history 例外"。

【必须】同时维护的版本数 **≤ 2 个**（当前版本 + 上一个 LTS）。每多维护一个版本，hotfix 的 PR 数量、回归测试矩阵、CHANGELOG 合并成本都会翻倍。超过 2 个必须走架构评审。

### 3.7 分支操作速查

```bash
# 从最新 main 开分支
git fetch origin
git switch -c feature/user-export-241 origin/main

# 保持同步（独占分支）
git rebase origin/main

# 推送到远端并建立跟踪
git push -u origin feature/user-export-241

# 合并后清理本地
git switch main && git pull --ff-only
git branch -d feature/user-export-241
git fetch --prune
```

---

## 四、评审与合并规范

### 4.1 硬门槛

以下条件**全部满足**才可以合并，缺一不可（在 GitHub 上通过分支保护强制，见表 4.5）：

| 门槛 | 级别 | 具体要求 |
| --- | --- | --- |
| 禁止自审 | 【必须】 | 作者不能 approve 自己的 PR，也不能用管理员权限自行合并 |
| 至少 1 人 approve | 【必须】 | 普通改动 1 人；`security`、`migration`、`payment` 等高风险管理模块 2 人 |
| 驳回状态清零 | 【必须】 | 存在 "Request changes" 时不可合并 |
| 旧 approval 失效 | 【必须】 | 新提交推上来后，之前的 approve 自动失效（`Dismiss stale approvals`） |
| CI 全绿 | 【必须】 | `commitlint`、`lint-pr-title`、`build`、`test`、`static-analysis`、`secret-scan` 全部通过 |
| 会话已解决 | 【必须】 | 所有 review comment 标记 resolved |
| CODEOWNERS 覆盖 | 【必须】 | 核心模块改动必须由 owner  approve |

【必须】`Dismiss stale approvals` 必须开启。否则会出现"approve 后偷偷追加一个提交"的绕过，这是真实发生过的安全事故路径。

### 4.2 合并策略

默认 **Squash and merge**。三种策略对比：

| 策略 | main 上的历史形态 | 适用场景 | 不适用场景 |
| --- | --- | --- | --- |
| **Squash and merge（默认）** | 一个 PR = 一个提交 | 绝大多数 `feature/*`、`fix/*`；提交琐碎（含 WIP、review fixup） | 需要保留每个提交独立回滚点的场景 |
| Merge commit | 保留分支内所有提交 + 一个合并提交 | 仅用于 release 整体回合并（3.6 方案 B，需管理员 bypass）；未启用 linear history 的仓库 | 分支内充满 `wip`、`fix typo`；启用 `Require linear history` 的仓库（会被直接拦下） |
| Rebase and merge | 分支提交逐个搬到 main，无合并提交，线性 | 多人长分支且每个提交都有独立价值；提交已被作者精心整理 | 提交未整理；提交无法独立编译 |

【必须】"多人长分支"的判定标准（用于决定是否放弃 squash）：

1. 分支存活 **> 3 个工作日**，或
2. 分支上有 **≥ 2 名开发者**并行提交（`git shortlog -s` 可查）

超过任一条件时，改用 **Rebase and merge** 保留提交粒度；【禁止】用 Merge commit 承担这一职责——它与 4.5 中开启的 `Require linear history` 直接冲突，会被分支保护拦下。不满足条件却要求保留历史，属于无必要地污染 main；判定要用数据说话，否则该条款形同虚设。

### 4.3 Squash 的关键约束

Squash 后 main 上只保留 **PR 标题**作为 commit message，因此：

【必须】PR 标题必须与 commit header 遵守完全相同的规范（`type(scope): subject`），由 `semantic-pull-request` 类动作在 CI 中校验（配置见 [7.3](#73-服务端兜底ci-必须校验)）。

【必须】仓库设置中把 squash 默认消息设为 **PR 标题**：

- GitHub：`Settings → General → Pull requests → Default to PR title for squash merge commits`（勾选）
- 同时把 `Default commit message` 设为 `Pull request title`

【必须】PR 标题使用英文，规则同 2.4/2.5；不要写成 `[WIP] 用户导出功能` 或 `Update code`。

【建议】PR 描述可以中文。注意关单关键字有两套规则：commit footer 必须严格写在 footer（见 2.5）；而 PR 描述由 GitHub 整段解析，`Closes #123` 写在描述任意独立行都可生效，建议统一放在末尾。

### 4.4 PR 模板

【必须】PR 使用固定六段模板，缺段视为未完成自测：

```markdown
## 变更说明

<!-- 做了什么、为什么做。对应 CC 的 body：写 why，不写 how。 -->

## 自测情况

- [ ] 本地 `mvn -B verify` 通过
- [ ] 新增/修改逻辑已有单元测试（覆盖率不低于基线）
- [ ] 手动验证场景（接口/页面/SQL）：
- [ ] 已在预发环境验证（如适用）

## 关联工单

Closes #<工单号>
Refs: #<相关工单>

## 风险点

<!-- 是否触及核心链路、是否有性能影响、是否需要开关、并发与幂等是否变化 -->
- 影响范围：
- 是否需要 feature flag：
- 兼容性（接口/序列化/缓存 key）：

## 数据库变更说明

<!-- 有 Flyway/Liquibase 迁移时必须填；无则写"无" -->
- 迁移文件：
- 变更类型：新增字段 / 加索引 / 改类型 / 数据订正
- 是否可回滚：是（可逆） / 否（需前滚修复）
- 是否兼容旧代码（expand-contract 阶段）：
- 预估执行时长与锁影响：

## 回滚方案

<!-- 代码回滚方式 + 数据补偿方式，必须能被值班同学照着做 -->
- 代码：`git revert <hash>`（是否可无冲突 revert）
- 数据：是否需要补偿脚本 / 是否需要回填
- 开关：关闭哪个 flag 可止血
```

【必须】"数据库变更说明"和"回滚方案"两段是**硬性要求**：代码能 revert，schema 不会自己退回去（详见 9.2）。

### 4.5 GitHub 分支保护配置清单

【必须】`main` 与 `release/*` 逐项按下列清单配置（GitHub 的 Rulesets 或经典 Branch protection 均可）：

| # | 配置项 | 值 | 说明 |
| --- | --- | --- | --- |
| 1 | Require a pull request before merging | 开启 | 禁止直推 |
| 2 | Required approvals | 1（高风险 2） | 配合 CODEOWNERS |
| 3 | Dismiss stale pull request approvals when new commits are pushed | 开启 | 新提交使旧 approve 失效 |
| 4 | Require review from Code Owners | 开启 | 核心模块必须 owner 审 |
| 5 | Require status checks to pass | 开启，勾选 `commitlint`、`lint-pr-title`、`build`、`test`、`static-analysis`、`secret-scan` | 检查项名称必须与 workflow job 名称完全一致 |
| 6 | Require branches to be up to date before merging | 开启 | 防"本地绿、合完红" |
| 7 | Require conversation resolution before merging | 开启 | 评论必须 resolved |
| 8 | Require linear history | 开启 | 只允许 squash / rebase；Merge commit 仅作为 3.6 方案 B 的 bypass 例外 |
| 9 | Do not allow bypassing the above settings | 开启 | 管理员也受限（release 回合并走 ruleset bypass 白名单） |
| 10 | Restrict force pushes | 开启（Block force push） | 禁止强推 |
| 11 | Restrict deletions | 开启 | 禁止删除分支 |
| 12 | Require signed commits | 【建议】开启 | 可选；团队统一配置 GPG/SSH 签名后再开，否则会堵死提交 |
| 13 | Automatically delete head branches | 开启 | 合并后自动删分支 |
| 14 | Merge queue | 【建议】高频团队开启 | 并行 PR 多时避免 main 反复红 |

【必须】受保护 tag：`v*` 单独配置规则（禁止删除、禁止更新、仅 release 角色可推送），见 5.3。

【建议】状态检查名称一次性对齐，改动 workflow job 名时同步改保护规则——这是最容易"看起来保护了其实没保护"的坑：job 改名后，保护规则里仍是旧名称，required check 永远处于 "Expected — Waiting for status" 或直接被跳过。

### 4.6 GitLab 对应配置差异

| GitHub 概念 | GitLab 对应 | 差异要点 |
| --- | --- | --- |
| Protected branches | `Settings → Repository → Protected branches` | 可设置 `Allowed to merge` / `Allowed to push` 角色 |
| Required approvals | `Approval rules`（Merge request approvals） | 支持按规则指定审批人、按路径审批 |
| CODEOWNERS | `Code Owners`（`CODEOWNERS` 文件） | 需要 `Approval rules` 中的 Code Owner 审批才强制 |
| Required status checks | `Pipelines must succeed` + `Merge request pipelines` | 只校验 MR pipeline，注意不要遗漏 post-merge 流水线 |
| Merge queue | `Merge trains` | 需开启，配合 fast-forward merge 使用 |
| Dismiss stale approvals | `Remove approvals by Code Owners if their files changed` + `Reset approvals on push` | 在 Settings → Merge requests 中开启 |
| Linear history | `Merge method: Fast-forward` + `Squash` 设置 | 用 `Fast-forward merge` 等价实现线性历史 |
| Force push 限制 | `Push rules`（`Reject unsigned commits`、`Prevent force push`） | 需要 Maintainer 权限配置 |
| Secret scanning | Secret Detection（Ultimate）或接入 gitleaks CI job | CE 版本建议走 gitleaks |
| Squash | `Squash commits when merging`（可设为默认/必须） | 建议设为 "Require" |

【必须】GitLab 侧 `Push rules` 至少开启：`Prevent force push`、`Reject commit messages not matching a pattern`（正则可写 `^(feat|fix|docs|style|refactor|perf|test|chore|revert)(\([a-z0-9-]+\))?!?:`，注意 `:` 之后必须紧跟一个空格）。

【必须】两平台都要在服务端跑 commitlint（见 7.3），不能只依赖 GitLab 的 push rule 正则——正则无法校验 scope 白名单与 subject 长度。

---

## 五、标签与版本（SemVer）

### 5.1 版本号规则

采用 [SemVer 2.0.0](https://semver.org/lang/zh-CN/)，格式 `vX.Y.Z`：

| 位 | 含义 | 何时升 |
| --- | --- | --- |
| `X`（major） | 不兼容的 API 变更 | 有 `BREAKING CHANGE:` footer |
| `Y`（minor） | 向下兼容的新功能 | 有 `feat` |
| `Z`（patch） | 向下兼容的问题修复 | 仅有 `fix` / `perf` / `revert` |

| 变体 | 格式 | 说明 |
| --- | --- | --- |
| 预发布 | `v1.2.0-rc.1`、`v1.2.0-beta.2` | 优先级低于正式版；`rc` 为发布候选，`beta` 为内测 |
| 构建元数据 | `v1.2.0+build.45` | **不参与优先级比较**，仅用于标记构建批次，不要用它表示"第几次修复" |
| 无前缀 | `1.2.0` | 【禁止】与 `v` 前缀混用；团队统一使用 `v` |

【必须】版本号单一来源：`pom.xml` 的 `<version>` 与 tag 必须一致，由流水线自动校验（见 5.4）。

### 5.2 tag 类型与命令

【必须】使用 **annotated tag**（带作者、日期、说明），禁止 lightweight tag：

```bash
# 在 main 的稳定提交点上创建 annotated tag
git switch main
git pull --ff-only
git tag -a v1.4.0 -m "release v1.4.0"

# 推送单个 tag（不要用 git push --tags 批量推，容易误推本地临时 tag）
git push origin v1.4.0
```

签名 tag（团队已统一配置 GPG 时推荐）：

```bash
git tag -s v1.4.0 -m "release v1.4.0"
git tag -v v1.4.0   # 验证签名
```

【禁止】移动或删除已发布的 tag。已发布 tag 是对外契约，重打会让下游依赖解析、镜像 tag、CHANGELOG 锚点全部错位。若必须撤回，只能发布**新的 patch 版本**（如 `v1.4.1`）。

【必须】tag 只能打在 `main` 上的稳定提交点；【禁止】在 `feature/*`、`release/*` 中间提交上打正式 tag（预发布 tag `-rc.N` 例外，允许打在 release 分支）。

【必须】tag push 触发发布流水线（见 7.6 与 8.4），不允许本地手工构建产物上传。

### 5.3 受保护 tag

【必须】GitHub 的 Rulesets 中对 `v*` 配置：

- Restrict creations / updates / deletions：仅 `release` 团队（或指定 App）可创建与更新
- 禁止 force push 到 tag
- 【建议】开启 `Require signed commits` 后，tag 也要求签名

GitLab 对应：`Settings → Repository → Protected tags`，设置 `v*` 的 `Allowed to create` 为 Maintainer 及以上。

### 5.4 发布检查清单

打 tag 前逐项确认（建议做成流水线的前置 job，人工只做确认）：

- [ ] `pom.xml` 版本号与将要打的 tag 完全一致（`v1.4.0` ↔ `1.4.0`）
- [ ] `CHANGELOG.md` 已由 git-cliff 生成并随 PR 合入（含 Breaking 段落）
- [ ] 数据库迁移脚本已 review，且符合 expand-contract（见 9.2）
- [ ] `mvn -B verify` 在最新 main 上通过，覆盖率达标
- [ ] 依赖漏洞扫描无 High/Critical（或有书面豁免）
- [ ] 部署清单 / 配置项差异（新增环境变量已在配置中心登记）
- [ ] 回滚方案已写入 release PR 描述
- [ ] tag 打在 main 的稳定提交点，且该提交的 CI 为绿

---

## 六、禁止行为红线清单

以下十条为**红线**，违反一次即在团队内通报，重复违反需在复盘会上说明。

| # | 红线 | 级别 | 为什么 |
| --- | --- | --- | --- |
| 1 | 对 `main` / `release/*` 执行 force push | 【禁止】 | 会静默覆盖他人提交，且无法从 reflog 之外恢复 |
| 2 | 一个提交混入多件事（功能 + 格式化 + 依赖升级） | 【禁止】 | 无法单独 revert，评审失焦，CHANGELOG 失真 |
| 3 | 提交敏感信息（密码、token、私钥、连接串、`.env`） | 【禁止】 | 一旦进入历史，删文件不等于删除；只能轮换密钥 |
| 4 | 中文或无意义提交信息（`修改`、`update`、`1`、`.`） | 【禁止】 | 破坏 CHANGELOG 生成与历史检索 |
| 5 | 直接修改 `main`（含在网页端直接编辑文件） | 【禁止】 | 绕过评审与 CI，是绝大多数事故的直接原因 |
| 6 | 提交 IDE / 本地配置文件（`.idea/`、`*.iml`、`.vscode/settings.json`、`.classpath`、`.project`） | 【禁止】 | 个人环境差异会持续制造冲突与噪音 |
| 7 | 提交大二进制（> 5 MB 的 jar、zip、dump、模型文件） | 【禁止】 | 永久膨胀仓库，clone 时间线性恶化；应走 LFS 或制品库 |
| 8 | 用 `--no-verify` / `-n` 绕过本地钩子 | 【禁止】 | 绕过的是格式与密钥检查，代价由全团队承担 |
| 9 | 长期存活的巨型分支（> 1 周、> 200 文件） | 【禁止】 | 合并即事故；应拆分为小 PR + feature flag |
| 10 | 未经评审的 hotfix，或事后不补 main/release 与 PR 留痕 | 【禁止】 | 修复会"消失"在下个版本，事故重复发生 |

【必须】第 3 条的补救流程：发现即视为泄露事件，立即轮换密钥 → 用 `gitleaks` 全历史扫描确认范围 → 评估是否需要 `git filter-repo` 清理历史（需全员重新 clone，走架构组审批）→ 记录事件报告。**不要只删文件再提交一次**。

【必须】第 8 条的配套：本地钩子只是"提前发现"，真正的门禁在服务端（7.3）。任何"钩子能绕过所以不必装"的说法都不成立，但也不能反过来只靠钩子。

---

## 七、配套工具与自动化

本章所有配置都可在仓库根目录直接落地。原则是：**本地钩子负责"早发现"，服务端 CI 负责"真拦截"**。

### 7.1 commitlint 完整配置

【必须】在仓库根目录放置 `commitlint.config.js`，并在 `package.json` 中声明 devDependencies：

```json
{
  "name": "backend-git-convention",
  "private": true,
  "devDependencies": {
    "@commitlint/cli": "^19.5.0",
    "@commitlint/config-conventional": "^19.5.0"
  }
}
```

完整配置（对应 2.2 ~ 2.6 全部条款）：

```js
// commitlint.config.js —— 仓库根目录
// Node >= 18；安装：npm i -D @commitlint/cli @commitlint/config-conventional
const TYPES = ['feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'chore', 'revert'];

// scope 白名单：需要维护的资产，扩白名单走 PR 评审（见 2.3）
const SCOPES = [
  // 分层 / 组件
  'controller', 'service', 'repository', 'mapper', 'entity', 'dto',
  'es', 'springai', 'embedding', 'ollama', 'security', 'cache', 'mq', 'scheduler',
  // 基础设施
  'config', 'docker', 'k8s', 'db', 'migration', 'logging', 'monitor',
  // 工程化
  'deps', 'build', 'github-actions', 'gitlab-ci', 'docs', 'test', 'release',
  // 平台级
  'api', 'auth', 'gateway', 'bom', 'parent'
];

// 这些 type 必须写 scope；revert 与 chore/docs/style 允许省略
const CODE_TYPES = ['feat', 'fix', 'refactor', 'perf', 'test'];

module.exports = {
  extends: ['@commitlint/config-conventional'],

  // 依赖机器人 / 平台自动生成的提交不受人工规范约束（否则 dependabot 永远红）
  ignores: [
    (message) => /^chore\(deps\): (bump|update|pin)/i.test(message),
    (message) => /^Merge (branch|pull request|remote-tracking)/i.test(message),
    (message) => /^Revert ".+"$/.test(message)
  ],

  // 本地自定义规则：解决 config-conventional 的 subject-case 误杀专有名词问题
  plugins: [
    {
      rules: {
        // 只校验 subject 的首个单词是否小写，允许后续 Elasticsearch / Ollama 等保留原大小写
        'subject-first-word-lower': ({ subject }) => {
          if (!subject) return [true];
          const firstWord = subject.trim().split(/\s+/)[0];
          return [
            firstWord === firstWord.toLowerCase(),
            'subject 的第一个单词必须全小写（专有名词不要放在首位）'
          ];
        },
        // feat/fix/refactor/perf/test 必须有 scope
        'scope-required-for-code-types': ({ type, scope }) => {
          if (!CODE_TYPES.includes(type)) return [true];
          return [
            Boolean(scope && scope.trim()),
            `${type} 类型必须填写 scope（白名单见 2.3）`
          ];
        }
      }
    }
  ],

  rules: {
    // type
    'type-empty': [2, 'never'],
    'type-case': [2, 'always', 'lower-case'],
    'type-enum': [2, 'always', TYPES],

    // scope
    'scope-case': [2, 'always', 'lower-case'],
    'scope-enum': [2, 'always', SCOPES],
    'scope-empty': [0], // 由 scope-required-for-code-types 按 type 决定

    // subject
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    'subject-max-length': [2, 'always', 50],
    'subject-case': [0], // 关闭：会误杀 Elasticsearch / SpringAI / Ollama
    'subject-first-word-lower': [2, 'always'],
    'scope-required-for-code-types': [2, 'always'],

    // header / body / footer
    'header-max-length': [2, 'always', 100],
    'header-trim': [2, 'always'],
    'body-leading-blank': [2, 'always'],
    'body-max-line-length': [2, 'always', 72],
    'footer-leading-blank': [2, 'always'],
    'footer-max-line-length': [2, 'always', 72]
  }
};
```

本地/手动校验：

```bash
# 校验最近一条提交
npx --no -- commitlint --edit .git/COMMIT_EDITMSG

# 校验从 main 分叉以来的所有提交（CI 用法）
npx --no -- commitlint --from origin/main --to HEAD --verbose
```

【必须】`scope-empty` 设为 `[0]` 而不是 `[2, 'never']`。原因：`git revert` 产出的 `revert: feat(springai): ...` 没有 scope，若强制所有提交都带 scope，回滚提交必然被拦；同时 `chore(deps):` 之外的 `docs:`、`style:` 也常不需要 scope。scope 的必填性由 `scope-required-for-code-types` 按 type 精准控制。

### 7.2 提交钩子选型

| 方案 | 依赖 | 跨语言 | 只跑变更文件 | 结论 |
| --- | --- | --- | --- | --- |
| **lefthook** | 单个 Go 二进制 | 是 | 支持（`glob` / `{staged_files}`） | **推荐** |
| husky | Node + `package.json` + 包管理器 | 否（绑定前端工程） | 需自己写脚本 | 不推荐用于 Java 仓库 |
| pre-commit（Python） | Python + pip | 是 | 支持 | 可用，但需维护 Python 环境 |
| 手写 `.git/hooks/*.sh` | 无 | 是 | 否 | 不可版本化，团队无法统一 |

【必须】**不要用 husky 作为 Java 仓库的钩子底座**。husky 的安装依赖 Node 与包管理器（npm / yarn / pnpm 各自不同的 install 钩子），一个纯后端仓库为装钩子而引入 Node 工程，等于凭空多维护一套前端工具链；`npm install` 失败时钩子会静默失效，且不同人的 `nvm` 版本差异会带来难排查的 `commit-msg` 失败。

【必须】推荐 lefthook（单二进制、`brew install lefthook` 或 mise/asdf 安装），钩子定义版本化在 `lefthook.yml` 中，`lefthook install` 写入 `.git/hooks`。

【必须】但必须诚实说明一个事实：**commitlint 本身是 Node 工具**，lefthook 只解决"钩子框架"，不解决"commitlint 需要 Node"。三种处置方式，团队任选其一并在 README 注明：

| 方式 | 做法 | 适用 |
| --- | --- | --- |
| **A. 固定 Node 版本（推荐）** | 用 mise / asdf 声明 `.tool-versions`（`nodejs 20.x`），开发者 `mise install` 一次 | 团队愿意装 Node |
| B. 本地不跑 commitlint | 只跑 spotless + gitleaks，提交信息交给服务端 CI（7.3）拦截 | 完全不想引入 Node |
| C. 换 Rust 实现 | 用 `convco check` 校验 CC 格式（注意：不支持 scope 白名单，白名单仍需 CI 跑 commitlint） | 强约束"零 Node" |

完整 `lefthook.yml`：

```yaml
# lefthook.yml —— 仓库根目录
# 安装：brew install lefthook && lefthook install
min_version: 1.6.0

commit-msg:
  commands:
    commitlint:
      run: npx --no -- commitlint --edit {1}

pre-commit:
  parallel: true
  commands:
    spotless:
      glob: "**/*.java"
      run: ./mvnw -q -DskipTests spotless:check
    gitleaks:
      # gitleaks >= 8.19：新子命令；更早版本用 gitleaks protect --staged --verbose
      run: gitleaks git --pre-commit --staged --no-banner --redact

pre-push:
  commands:
    # 可选：推送前跑一次编译，避免把明显编译失败的分支推上去触发无意义 CI
    compile:
      run: ./mvnw -q -DskipTests compile
```

【建议】`pre-push` 的编译检查可按团队机器性能裁剪；如果本地编译超过 30 秒，会促使大家用 `--no-verify`，反而更糟。宁可少一道钩子，也不要让人习惯性绕过。

### 7.3 服务端兜底（CI 必须校验）

【必须】**本地钩子可被 `git commit --no-verify` 直接绕过，也可以在网页端或 IDE 里不经过钩子提交，因此服务端校验是唯一的真实门禁。** 只配本地钩子等于没配。

三层兜底，缺一不可：

| 层 | 校验对象 | 落地方式 |
| --- | --- | --- |
| 1. 分支内每条提交 | commit message | CI 执行 `commitlint --from origin/main --to HEAD` |
| 2. PR 标题 | squash 后的 main 提交信息 | `amannn/action-semantic-pull-request` |
| 3. 合并放行 | 以上两项 + 测试 + 静态检查 + 密钥扫描 | 分支保护 required status checks（4.5） |

```yaml
# .github/workflows/pr-title.yml
name: pr-title

on:
  pull_request_target:
    types: [opened, edited, synchronize, reopened]

permissions:
  pull-requests: read

jobs:
  lint-title:
    name: lint-pr-title
    runs-on: ubuntu-latest
    steps:
      - uses: amannn/action-semantic-pull-request@v5
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          types: |
            feat
            fix
            docs
            style
            refactor
            perf
            test
            chore
            revert
          requireScope: false
          subjectPattern: ^[a-z](?:.{0,48}[^.])?$
          subjectPatternError: |
            PR 标题的 subject 必须以小写单词开头、≤ 50 字符、结尾不加句号。
```

【必须】`pr-title.yml` 使用 `pull_request_target` 而不是 `pull_request`，否则来自 fork 的 PR 不会触发标题校验。

【必须】该 job 的名称 `lint-pr-title` 必须加入 `main` 的 required status checks，否则 PR 标题校验只是"提示"。

【建议】`requireScope: false` 是为了兼容 `revert`、`chore` 类 PR 标题；分支内 `feat` / `fix` 的 scope 必填仍由 7.1 的 `scope-required-for-code-types` 强制，两层不会互相放松。

【建议】GitLab 侧等价做法：在 MR pipeline 中加一个 job 调用 `npx commitlint` 校验 `CI_MERGE_REQUEST_TITLE`，或开启 `Push rules → Reject commit messages not matching a pattern`（正则能力有限，仍需 commitlint 补 scope 白名单）。

### 7.4 Java 代码格式化：Spotless

【必须】Java 格式化使用 **Spotless + google-java-format**（团队也可统一换成 palantir-java-format，二者只能选一个，禁止混用，否则 diff 会来回震荡）。

```xml
<!-- pom.xml（parent 或聚合模块的 <build><plugins> 中） -->
<plugin>
  <groupId>com.diffplug.spotless</groupId>
  <artifactId>spotless-maven-plugin</artifactId>
  <version>2.43.0</version>
  <configuration>
    <java>
      <googleJavaFormat>
        <version>1.22.0</version>
        <style>GOOGLE</style>
        <reflowLongStrings>true</reflowLongStrings>
      </googleJavaFormat>
      <removeUnusedImports/>
      <formatAnnotations/>
      <trimTrailingWhitespace/>
      <endWithNewline/>
    </java>
  </configuration>
  <executions>
    <execution>
      <id>spotless-check</id>
      <phase>verify</phase>
      <goals>
        <goal>check</goal>
      </goals>
    </execution>
  </executions>
</plugin>
```

```bash
# 只检查（CI 与 pre-commit 使用，失败即阻断）
./mvnw -B spotless:check

# 自动修复（开发者本地使用），修复后需重新提交
./mvnw -B spotless:apply
```

【必须】**prettier 不能格式化 Java**。prettier 没有 Java 解析器，`prettier --write "**/*.java"` 不会格式化 Java（只会报 "No parser could be inferred" 或直接跳过），而且 Java 的换行、缩进、import 顺序只有 Spotless（google-java-format / palantir）能正确做。

| 文件类型 | 工具 | 命令 |
| --- | --- | --- |
| `.java` | Spotless + google-java-format | `./mvnw spotless:check` |
| `.xml`（pom） | Spotless（`<formats>` 或 `sortPom`） | `./mvnw spotless:check` |
| `.yml` / `.yaml` / `.json` / `.md` | prettier | `npx prettier --check "**/*.{yml,yaml,json,md}"` |
| `.sql`（迁移脚本） | 【禁止】自动格式化 | 手工 review，格式化会破坏 diff 可读性 |

【必须】格式化提交必须**独立成一个 `style` 提交**。首次接入 Spotless 会产生全仓库 diff，必须单独 PR（`style: apply spotless to whole repo`），并在 `.git-blame-ignore-revs` 登记该提交 hash，避免污染 `git blame`：

```bash
# .git-blame-ignore-revs 内容示例（首次全量格式化的提交）
# style: apply spotless to whole repo
<commit-hash>

# 本地启用
git config blame.ignoreRevsFile .git-blame-ignore-revs
```

### 7.5 密钥检测：gitleaks

【必须】使用 **gitleaks** 做密钥检测。**不要用 git-secrets**：它自 2019 年后基本停止维护，规则集陈旧，对现代云厂商 token（OpenAI/Ollama 风格 key、GitHub PAT、AWS STS）覆盖不足，已被 gitleaks / trufflehog 取代。

`.gitleaks.toml` 基础配置（基于官方默认规则集扩展，需 gitleaks ≥ 8.19）：

```toml
# .gitleaks.toml —— 仓库根目录
title = "backend-git-convention"

[extend]
# 继承 gitleaks 内置规则（AWS / GCP / GitHub / Slack / 私钥等）
useDefault = true

[[rules]]
id = "spring-datasource-password"
description = "Spring Boot 数据源密码硬编码"
regex = '''(?i)(spring\.datasource\.password|datasource\.password|DB_PASSWORD)\s*[=:]\s*[^\s"']{6,}'''
tags = ["password", "spring"]

[[rules]]
id = "spring-ai-api-key"
description = "Spring AI / LLM 服务密钥"
regex = '''(?i)(spring\.ai\.(openai|ollama|anthropic)\.api[-_]key|SPRING_AI_[A-Z_]*API_KEY)\s*[=:]\s*[A-Za-z0-9\-_]{12,}'''
tags = ["api-key", "springai"]

[[rules]]
id = "jwt-signing-secret"
description = "JWT 签名密钥"
regex = '''(?i)(jwt\.(secret|signing[-_]key)|JWT_SECRET)\s*[=:]\s*[A-Za-z0-9+/=_\-]{16,}'''
tags = ["jwt", "secret"]

[allowlist]
description = "全局白名单：测试夹具与示例占位符"
paths = [
  '''src/test/resources/.*''',
  '''docs/.*'''
]
regexes = [
  '''password\s*[=:]\s*(changeme|example|placeholder|<[^>]+>)''',
  '''api[-_]key\s*[=:]\s*(xxx+|your-key-here)'''
]
```

本地与 CI 用法：

```bash
# 提交前只扫暂存区（pre-commit 使用，>= 8.19）
gitleaks git --pre-commit --staged --no-banner --redact

# 旧版本（<= 8.18）等价命令
gitleaks protect --staged --verbose --redact

# 全历史扫描（接入时做一次，之后每月定时扫描）
gitleaks git --no-banner --redact --report-format sarif --report-path gitleaks.sarif

# 扫描工作区（未提交文件）
gitleaks dir . --no-banner
```

【必须】GitHub 侧同时开启平台能力：`Settings → Code security → Secret scanning` 与 **Push protection**（推送时即拦截，不依赖 CI）。GitLab 无 Ultimate 时用 gitleaks CI job 兜底。

【必须】`allowlist` 只允许放测试夹具与占位符，**禁止**为了"让流水线绿"把真实路径加进白名单——这是密钥检测最常见的失效方式。

### 7.6 CI 门禁清单（Java 专项）

| 门禁 | 命令 | 级别 | 说明 |
| --- | --- | --- | --- |
| 构建与测试 | `./mvnw -B verify` | 【必须】 | 包含编译、单测、集成测试（`*IT` 可拆分） |
| 覆盖率门槛 | JaCoCo `check`（行覆盖 ≥ 70%，核心模块 ≥ 80%） | 【必须】 | 低于门槛直接 fail |
| 代码格式 | `./mvnw -B spotless:check` | 【必须】 | 见 7.4 |
| 静态检查 | `checkstyle:check` / `spotbugs:check` / `pmd:check` | 【必须】 | SpotBugs 建议 `-Dspotbugs.threshold=Medium` |
| 依赖漏洞 | `org.owasp:dependency-check-maven:check` | 【必须】 | 需配置 `NVD_API_KEY`，无 key 会限流失败 |
| 依赖收敛 | `maven-enforcer-plugin`（`dependencyConvergence`） | 【必须】 | 防止同一依赖多版本共存 |
| 质量门 | `sonar:sonar` + Sonar Quality Gate | 【建议】 | 新代码覆盖率与重复率需达标 |
| 密钥扫描 | `gitleaks` | 【必须】 | 见 7.5 |

JaCoCo 与 Enforcer 片段（追加到 `pom.xml`）：

```xml
<plugin>
  <groupId>org.jacoco</groupId>
  <artifactId>jacoco-maven-plugin</artifactId>
  <version>0.8.12</version>
  <executions>
    <execution>
      <id>prepare-agent</id>
      <goals>
        <goal>prepare-agent</goal>
      </goals>
    </execution>
    <execution>
      <id>report</id>
      <phase>verify</phase>
      <goals>
        <goal>report</goal>
      </goals>
    </execution>
    <execution>
      <id>check-coverage</id>
      <phase>verify</phase>
      <goals>
        <goal>check</goal>
      </goals>
      <configuration>
        <rules>
          <rule>
            <element>BUNDLE</element>
            <limits>
              <limit>
                <counter>LINE</counter>
                <value>COVERAGE</value>
                <minimum>0.70</minimum>
              </limit>
            </limits>
          </rule>
        </rules>
      </configuration>
    </execution>
  </executions>
</plugin>

<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-enforcer-plugin</artifactId>
  <version>3.5.0</version>
  <executions>
    <execution>
      <id>enforce</id>
      <goals>
        <goal>enforce</goal>
      </goals>
      <configuration>
        <rules>
          <dependencyConvergence/>
          <requireJavaVersion>
            <version>[21,)</version>
          </requireJavaVersion>
          <requireMavenVersion>
            <version>[3.9,)</version>
          </requireMavenVersion>
        </rules>
      </configuration>
    </execution>
  </executions>
</plugin>
```

GitHub Actions workflow 骨架（job 名必须与 4.5 的 required checks 一一对应）：

```yaml
# .github/workflows/ci.yml
name: ci

on:
  pull_request:
    branches: [main, 'release/**']
  push:
    branches: [main]

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read
  pull-requests: read

jobs:
  commitlint:
    name: commitlint
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - name: Lint every commit since main
        run: |
          npx --no -- commitlint \
            --from "origin/${{ github.base_ref }}" \
            --to "${{ github.event.pull_request.head.sha }}" \
            --verbose

  secret-scan:
    name: secret-scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  build:
    name: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '21'
          cache: maven
      - name: Compile and package
        run: ./mvnw -B -DskipTests package

  test:
    name: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '21'
          cache: maven
      - name: Verify with coverage gate
        run: ./mvnw -B verify
      - name: Upload test reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: surefire-reports
          path: '**/target/surefire-reports/**'
          retention-days: 7

  static-analysis:
    name: static-analysis
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '21'
          cache: maven
      - name: Spotless
        run: ./mvnw -B spotless:check
      - name: Checkstyle / SpotBugs / PMD
        run: ./mvnw -B checkstyle:check spotbugs:check pmd:check
      - name: Enforcer (dependency convergence)
        run: ./mvnw -B enforcer:enforce
      - name: OWASP dependency-check
        run: ./mvnw -B org.owasp:dependency-check-maven:check
        env:
          NVD_API_KEY: ${{ secrets.NVD_API_KEY }}
```

【必须】`fetch-depth: 0` 不能省。`commitlint --from origin/main` 需要完整历史与远端分支引用；浅克隆会让"从 main 分叉以来的提交"判定为空，校验形同虚设。

### 7.7 仓库卫生

`.gitattributes`（统一换行符，杜绝 Windows 开发者产生全文件 diff）：

```gitattributes
# .gitattributes —— 仓库根目录
* text=auto eol=lf

# Java / 脚本：强制 LF
*.java   text eol=lf
*.xml    text eol=lf
*.yml    text eol=lf
*.yaml   text eol=lf
*.json   text eol=lf
*.md     text eol=lf
*.sql    text eol=lf
*.sh     text eol=lf
mvnw     text eol=lf

# Windows 批处理：强制 CRLF
*.bat    text=crlf
*.cmd    text=crlf

# 二进制：禁止文本转换与行内 diff
*.jar    binary
*.war    binary
*.zip    binary
*.png    binary
*.jpg    binary
*.pdf    binary
*.bin    binary

# 生成物不参与语言统计
target/** linguist-generated=true
```

【必须】`.gitignore` 至少覆盖 IDE 与本地文件：

```gitignore
# .gitignore
.idea/
*.iml
*.ipr
*.iws
.vscode/
.classpath
.project
.settings/
.factorypath
*.log
.env
.env.*
!.env.example
target/
```

【必须】仓库保留 `mvnw` / `mvnw.cmd` / `.mvn/wrapper/`。理由：CI 与实际构建必须使用同一 Maven 版本，且 `mvnw` 让新人无需预装 Maven；删除 wrapper 会导致"本地能编、CI 编不过"的版本漂移问题。

【必须】大文件（> 5 MB 的非源码二进制、模型文件、dump）走 **Git LFS**，并在 `.gitattributes` 登记：

```bash
git lfs install
git lfs track "*.psd" "*.zip" "*.bin" "*.onnx"
git add .gitattributes
```

【禁止】用 LFS 存构建产物（jar/war）——产物应进制品库（Nexus/Artifactory/GitHub Packages），LFS 只用于确实需要版本化的二进制素材。

【建议】仓库设置 `Settings → General → Merge button` 只保留 "Allow squash merging"（如需 release 回合并再临时开启 merge commit），从界面层消除误用其它策略的可能。

---

## 八、CHANGELOG 自动生成

### 8.1 哪些 type 进入 CHANGELOG

| type | 是否进入 | 分组名 | 说明 |
| --- | --- | --- | --- |
| `feat` | 是 | Features | 面向使用者的新能力 |
| `fix` | 是 | Bug Fixes | 缺陷修复 |
| `perf` | 是 | Performance | 性能优化 |
| `refactor` | 是 | Refactor（可配置排除） | 内部结构调整；对下游有可见影响时才需要 |
| `revert` | 是 | Reverts | 回滚必须在版本说明中可见 |
| `BREAKING CHANGE` | 是 | **BREAKING CHANGES（置顶）** | 无论 type 是什么，只要有该 footer 就必须置顶 |
| `docs` / `style` / `test` / `chore` | 否 | — | 不影响使用者，进入只会稀释信息密度 |

【必须】`BREAKING CHANGE` 必须单独置顶，且优先级高于所有分组。理由：升级者第一眼要看到"会不会炸"，而不是"加了什么功能"。

### 8.2 推荐方案：git-cliff

选型对比：

| 工具 | 依赖 | 适用 | 结论 |
| --- | --- | --- | --- |
| **git-cliff** | 单个 Rust 二进制 | 任意语言、任意托管平台 | **推荐**，Java 仓库零额外运行时 |
| semantic-release | Node + 插件生态 | 全自动发版（含 npm 发布） | 备选；Java 仓库要额外写 maven 发布插件 |
| conventional-changelog-cli | Node | 只生成 changelog | 备选，配置比 git-cliff 繁琐 |

完整 `cliff.toml`：

```toml
# cliff.toml —— 仓库根目录
# 安装：brew install git-cliff   （或 cargo install git-cliff）
# 生成：git cliff -o CHANGELOG.md

[changelog]
header = """
# Changelog\n
All notable changes to this project are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/) and
[Semantic Versioning](https://semver.org/).\n
"""
body = """
{% if version %}\
## [{{ version | trim_start_matches(pat="v") }}] - {{ timestamp | date(format="%Y-%m-%d") }}
{% else %}\
## [Unreleased]
{% endif %}\
{% set breaking = commits | filter(attribute="breaking", value=true) %}\
{% if breaking | length > 0 %}\
### BREAKING CHANGES

{% for commit in breaking %}\
- {% if commit.scope %}**{{ commit.scope }}**: {% endif %}{{ commit.message }}
{% endfor %}\

{% endif %}\
{% for group, commits in commits | group_by(attribute="group") %}\
### {{ group }}

{% for commit in commits %}\
- {% if commit.scope %}**{{ commit.scope }}**: {% endif %}{{ commit.message }}{% if commit.hash %} ({{ commit.hash | truncate(length=7, end="") }}){% endif %}
{% endfor %}\

{% endfor %}\
"""
footer = ""
trim = true
render_always = true

[git]
conventional_commits = true
filter_unconventional = true
split_commits = false
commit_parsers = [
  { message = "^feat", group = "Features" },
  { message = "^fix", group = "Bug Fixes" },
  { message = "^perf", group = "Performance" },
  { message = "^refactor", group = "Refactor" },
  { message = "^revert", group = "Reverts" },
  { message = "^docs|^style|^test|^chore", skip = true },
  { message = "^.*", group = "Other" },
]
protect_breaking_commits = false
filter_commits = false
tag_pattern = "v[0-9]*"
sort_commits = "oldest"
```

常用命令：

```bash
# 全量生成
git cliff -o CHANGELOG.md

# 只生成最新一个 tag 的段落（发版时用）
git cliff --latest --strip header

# 预览不写文件（本地检查用）
git cliff --unreleased
```

【必须】`commit_parsers` 的顺序是有意义的：git-cliff 按数组顺序匹配，因此 `skip: true` 的规则必须放在兜底 `^.*` 之前，否则 `docs`/`chore` 会先被兜底规则捕走进 "Other" 分组。

【必须】`Breaking 置顶`由模板中的 `{% set breaking = ... %}` 实现，而不是靠 `commit_parsers` 分组——这样无论提交 type 是 `feat` 还是 `refactor`，只要有 `BREAKING CHANGE:` footer 都会被抽取到顶部。

### 8.3 备选：semantic-release

【建议】只有在同时需要"自动决定版本号 + 自动发版 + 自动发布产物"时才用 semantic-release。Java 仓库的注意点：

- 需要 `.releaserc` 配置 `@semantic-release/commit-analyzer`、`@semantic-release/release-notes-generator`、`@semantic-release/changelog`、`@semantic-release/git`、`@semantic-release/github`
- 发布 Maven 产物需要额外插件（或干脆由 tag 触发的 Maven 流水线负责，semantic-release 只管打 tag 与写 CHANGELOG）
- 它会直接 commit `CHANGELOG.md` 与 `pom.xml` 版本到 main，需给机器人账号 ruleset bypass 权限

综合成本高于 git-cliff，因此本项目默认 git-cliff。

### 8.4 集成到发布流水线

推荐形态：**tag 由人手工创建（annotated、受保护）**，tag push 触发流水线自动生成 CHANGELOG、创建 GitHub Release，并把该版本段落回写 `main` 的 `CHANGELOG.md`。

```yaml
# .github/workflows/release.yml
name: release

on:
  push:
    tags: ['v*']

permissions:
  contents: write

jobs:
  release:
    name: release
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Generate changelog for this tag
        uses: orhun/git-cliff-action@v4
        id: cliff
        with:
          config: cliff.toml
          args: --latest --strip header
        env:
          OUTPUT: CHANGELOG_LATEST.md

      - name: Verify tag matches pom version
        run: |
          TAG_VERSION="${GITHUB_REF_NAME#v}"
          POM_VERSION="$(./mvnw -q help:evaluate -Dexpression=project.version -DforceStdout)"
          if [ "$TAG_VERSION" != "$POM_VERSION" ]; then
            echo "tag $TAG_VERSION != pom $POM_VERSION" >&2
            exit 1
          fi

      - name: Append to CHANGELOG.md and commit back to main
        run: |
          cat CHANGELOG_LATEST.md >> CHANGELOG.md
          git config user.name "release-bot"
          git config user.email "release-bot@example.com"
          git add CHANGELOG.md
          git commit -m "chore(release): update changelog for ${GITHUB_REF_NAME}"
          git push origin HEAD:main

      - name: Create GitHub Release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh release create "${GITHUB_REF_NAME}" \
            --title "${GITHUB_REF_NAME}" \
            --notes-file CHANGELOG_LATEST.md \
            --verify-tag
```

【必须】流水线中必须有"tag 与 `pom.xml` 版本一致"的校验步骤（8.4 示例中的 `Verify tag matches pom version`），否则会出现镜像标 `v1.4.0`、代码实际是 `1.3.0` 的情况。

【建议】`git push origin HEAD:main` 需要机器人账号具备 ruleset bypass；若团队不接受机器人直推 main，可改为"创建 PR 更新 CHANGELOG"，由人合并。

---

## 九、回滚规范

### 9.1 代码回滚

【必须】回滚公共分支（`main`、`release/*`）**只能使用 `git revert`**，禁止 `git reset --hard` + force push。

| 场景 | 命令 | 说明 |
| --- | --- | --- |
| Squash 合并后（最常见） | `git revert <squash-hash>` | main 上是单个提交，直接 revert 即可 |
| Merge commit（多人长分支） | `git revert -m 1 <merge-hash>` | `-m 1` 表示保留第一父提交（即主干侧） |
| 一次回滚多个提交 | `git revert --no-commit <old>..<new>` 然后一次提交 | 便于写统一的回滚说明 |
| 回滚后又想恢复 | `git revert <revert-hash>` | 恢复"回滚的回滚"，不要再直接改代码 |

```bash
# 找到要回滚的提交
git log --oneline -20

# 回滚 squash 后的单提交
git revert --no-edit <hash>

# 回滚 merge 提交（保留主干侧）
git revert -m 1 <merge-hash>
```

【必须】revert 提交信息按下列格式，保留被回滚提交的原始 header：

```text
revert: feat(springai): add embeddinggemma support

This reverts commit 3f9a2c1.

Reason: embeddinggemma model is unavailable in the staging cluster and
blocks the 1.4.0 release window.
```

【必须】回滚 PR 同样要走评审与 CI（除紧急止损外，见 9.4）。回滚不是"免检通道"。

【禁止】用 `git reset --hard` 后 force push 到公共分支来"回滚"。这会让其他人的本地分支与远端脱节，且 CI 缓存、镜像 tag、发布记录全部错乱。

### 9.2 数据库回滚（关键）

**代码 revert 不会回滚 schema。** 这是生产事故里最常见的二次伤害：应用回滚成功，但新加的 `NOT NULL` 字段让旧代码写入直接失败。

【必须】数据库变更遵循 **expand-contract（扩展-收缩）**，保证任意时刻"新旧代码都能在同一份 schema 上运行"：

| 阶段 | 动作 | 代码状态 | 可回滚性 |
| --- | --- | --- | --- |
| 1. Expand（扩展） | 只加不改：新增字段/新表/新索引，字段允许 NULL | 新旧代码均可运行 | 可 revert（旧代码忽略新字段） |
| 2. Dual write（双写） | 新代码同时写新旧字段，读仍走旧字段 | 新旧代码均可运行 | 可 revert |
| 3. Switch read（切读） | 新代码改读新字段，旧字段继续写 | 新旧代码均可运行 | 可 revert（切回读旧字段） |
| 4. Contract（收缩） | 停止写旧字段 → 删除旧字段 | **只有新代码可运行** | 不可 revert（删除不可逆） |

【必须】第 4 阶段（删除字段/改类型/加 `NOT NULL`）**必须与代码发布分开**，且至少晚一个发布窗口。理由：一旦删除，回滚旧代码就会立刻报错。

Flyway 示例（三个独立迁移文件，分三次发布）：

```sql
-- V20261001_01__add_order_channel.sql   （阶段 1：expand，只加字段）
ALTER TABLE orders ADD COLUMN channel VARCHAR(32) NULL;
CREATE INDEX idx_orders_channel ON orders (channel);
```

```sql
-- V20261015_02__backfill_order_channel.sql  （阶段 2：双写 + 数据回填）
-- 注意：大表回填必须分批，禁止一条 UPDATE 扫全表
UPDATE orders SET channel = 'web' WHERE channel IS NULL AND id < 1000000;
-- 后续批次由定时任务或人工分批执行，直到全量完成
```

```sql
-- V20261101_03__drop_legacy_order_source.sql  （阶段 4：contract，需独立发布并确认）
ALTER TABLE orders DROP COLUMN legacy_source;
```

【必须】迁移脚本的向前兼容要求：

- 只允许"加"（列、表、索引、可空约束），禁止在同一个发布里"加 + 改 + 删"
- 新列必须允许 `NULL` 或有 `DEFAULT`，否则旧代码的 INSERT 会失败
- 重命名列必须走"新增 → 双写 → 切读 → 删除旧列"，禁止 `RENAME COLUMN` 直接上线
- 数据回填必须可重复执行（幂等），并分批执行
- 【禁止】在迁移脚本里写业务逻辑或依赖外部服务

【必须】Flyway 版本注意事项：**Flyway Community 版不支持 undo 迁移（`U__` 脚本属于商业版能力）**，因此回滚策略只能是"前滚修复"（新增一个补偿迁移）或依赖 expand-contract 的兼容性。Liquibase 提供 `rollback` 块，但也要求迁移语句本身可逆，同样推荐 expand-contract。

【必须】任何删列、改类型、加非空约束的迁移，都必须在 PR 的"数据库变更说明"中标注 **"不可回滚"**，并在发布前确认旧代码已下线（见 4.4）。

【建议】生产环境迁移前先在预发执行一次全量脚本，并记录执行时长；`ALTER TABLE` 在千万级表上可能锁表，需评估在线 DDL 工具（如 pt-online-schema-change / gh-ost）。

### 9.3 配置与开关回滚

【必须】止血优先级：**关开关 > 回滚代码 > 回滚数据**。凡是可能引发故障的变更，都应设计成"可一键关闭"（feature flag、限流开关、降级开关），因为关开关通常秒级生效，而回滚代码要走构建 + 发布。

### 9.4 紧急 hotfix 流程与时限

【必须】线上故障的止血时限：

| 时间窗 | 要求 |
| --- | --- |
| 发现后 **30 分钟内** | 确认影响面，决定"关开关止血"还是"hotfix" |
| 发现后 **2 小时内** | 必须完成止血（开关关闭或 hotfix 上线） |
| 止血后 **24 小时内** | 补 main 与 release 的 PR 留痕（若 hotfix 走了紧急通道） |
| 止血后 **3 个工作日内** | 完成复盘，输出根因、改进项与责任人 |

hotfix 允许的紧急通道：

1. 从 `main` 拉 `hotfix/<语义>-<工单号>`，改动最小化（只改止血必需部分）
2. PR 仍要创建，允许"1 人 approve + 管理员合并"，但 **PR 必须存在**
3. 合并后立即按 3.6 方案 A 把同一修复 cherry-pick 到 `release/vX.Y.Z` 并重新打 patch tag
4. 事后补：`hotfix` 的复盘文档、缺失的测试用例、CHANGELOG（`fix` 会被自动收录）

【禁止】"直接在服务器上手改配置/手改 jar"作为常规手段。若确实执行了，必须在 2 小时内把改动回写到仓库，否则下次发布就会把它覆盖掉——这类"修复消失"是重复故障的头号原因。

---

## 十、备选 GitFlow 分支模型

GitFlow 并非本团队默认模型。仅在下列场景评估采用：

- 固定版本迭代、发版节奏由客户合同约束（如每季度一个大版本）
- 需要同时长期维护多个版本（> 2 个），且每个版本都有独立客户
- 交付物是有版本号的产品（SDK、二方库、私有化部署包），而非持续发布的服务

### 10.1 分支角色与流向

| 分支 | 来源 | 合入目标 | 生命周期 | 说明 |
| --- | --- | --- | --- | --- |
| `main`（或 `master`） | — | — | 永久 | 只存已发布的生产版本 |
| `develop` | `main` | `release/*` | 永久 | 集成分支，日常开发合入此处 |
| `feature/*` | `develop` | `develop` | 数天 ~ 数周 | 功能开发 |
| `release/*` | `develop` | `main` + `develop` | 一个发布周期 | 发布冻结、只修 bug |
| `hotfix/*` | `main` | `main` + `develop` | ≤ 1 天 | 生产紧急修复 |
| `bugfix/*` | `develop` | `develop` | 数天 | 非紧急缺陷 |

流向：`feature → develop → release → main`，`hotfix → main → develop`。

### 10.2 与主方案的取舍

| 维度 | 主方案（GitHub Flow 变体） | GitFlow |
| --- | --- | --- |
| 长期分支数 | 1（main） | 2（main + develop） |
| 合并次数 | 每 PR 一次 | 每功能至少 2 次（进 develop、进 release） |
| 发布节奏 | 持续 / 按需 | 固定窗口 |
| 多版本并行 | 最多 2 个 | 天然支持多个 release 分支 |
| 合并冲突风险 | 低 | 高（develop 与 release 长期双写） |
| 对 CI 的要求 | 高（必须全绿才可合并） | 高（且要覆盖多分支矩阵） |
| 新人上手成本 | 低 | 中 |

【建议】不要"混用"：既保留 `develop` 又要求 `main` 线性历史 + squash，会导致 `develop → main` 的合并无法 squash（会丢失版本边界），团队会陷入规则冲突。选一种并写进 README。

【必须】若采用 GitFlow，本文档第二、四、五、六、七、八、九章**全部继续适用**，仅第三章的分支清单替换为 10.1 的表格。

---

## 十一、落地路径与检查清单

### 11.1 三阶段落地

| 阶段 | 时间 | 落地内容 | 验收标准 |
| --- | --- | --- | --- |
| 第一阶段 | 第 1 周 | 只上 `commitlint.config.js` + `lefthook.yml` + PR 模板 + 分支命名约定 | 新提交 100% 通过 lint；PR 模板被实际填写 |
| 第二阶段 | 第 2 周 | 分支保护 + required checks + CODEOWNERS + gitleaks + Spotless | 无法直推 main；跳过检查无法合并；首次全量格式化 PR 已合并 |
| 第三阶段 | 第 3 周 | git-cliff + `cliff.toml` + tag 发布流水线 + 受保护 tag + 回滚演练 | 一次真实 tag 发布走完全流程；回滚演练在预发完成 |

【必须】第一阶段不要一次性上全部门禁。原因：全量静态检查会让历史代码整片失败，团队会立刻要求"先关掉"，之后再开启的阻力更大。顺序应为 **提交规范 → 评审与门禁 → 发布自动化**。

【建议】把"首次接入 Spotless 的全量格式化"和"首次依赖漏洞扫描的豁免清单"作为**独立的 PR** 处理，避免与功能改动混在一起。

### 11.2 团队落地自检清单

#### 提交与评审

- [ ] 每个仓库根目录都有 `commitlint.config.js`，`type-enum` 与本文档 2.2 完全一致
- [ ] `scope` 白名单已按仓库实际分层调整，并指定了维护 owner
- [ ] `subject-case` 已关闭，改用 `subject-first-word-lower`（专有名词不再被误杀）
- [ ] PR 标题在 CI 中被 `lint-pr-title` 校验，且该 check 已加入 required checks
- [ ] 仓库的 squash 默认消息已设为 PR 标题
- [ ] PR 模板包含六段（含数据库变更说明与回滚方案）
- [ ] 禁止自审、至少 1 人 approve、Dismiss stale approvals 已开启
- [ ] CODEOWNERS 覆盖 `security`、`migration`、`api` 等核心路径

#### 分支与合并

- [ ] `main` 开启 Require PR、Require linear history、Block force push、Restrict deletions
- [ ] 分支命名规则已写进 README，CI 或 push rule 中可选校验
- [ ] 特性分支寿命 ≤ 3 天，超期分支已登记
- [ ] Auto-delete head branches 已开启
- [ ] release 回合并策略确定为"双 PR 移植"（3.6 方案 A）并已写入发布文档

#### 工具与门禁

- [ ] `lefthook install` 后 `commit-msg` 与 `pre-commit` 钩子实际生效（用一条错误信息验证）
- [ ] 服务端 CI 的 `commitlint --from origin/main` 使用 `fetch-depth: 0`
- [ ] `gitleaks` 在 pre-commit 与 CI 均生效，GitHub push protection 已开启
- [ ] `spotless:check` 进入 CI，`spotless:apply` 已写进开发文档
- [ ] JaCoCo 覆盖率门槛与 `dependencyConvergence` 已生效
- [ ] `NVD_API_KEY` 已在仓库 secrets 中配置
- [ ] `.gitattributes` 已统一 LF，`mvnw` 已保留

#### 版本与回滚

- [ ] tag 使用 annotated（`git tag -a`），`v*` 已受保护
- [ ] tag 与 `pom.xml` 版本一致由流水线自动校验
- [ ] `CHANGELOG.md` 由 git-cliff 生成，Breaking 置顶
- [ ] 所有数据库迁移遵循 expand-contract，删列类脚本已标注"不可回滚"
- [ ] 完成一次 `git revert` 演练与一次"关开关止血"演练，并记录耗时
- [ ] 事故复盘模板与 hotfix 时限（2 小时）已公告到团队

### 11.3 面试精简背诵版（修订版）

> 我们团队用的不是纯 Trunk Based Development，而是 **主干强保护 + 短生命周期特性分支（GitHub Flow 变体）**：`main` 受分支保护、禁止直推，所有改动必须走 PR，特性分支寿命控制在 3 天内，未完成功能用 feature flag 隐藏而不是养巨型分支，发布期才拉少量 `release/vX.Y.Z` 冻结窗口。
>
> 提交信息强制 Conventional Commits：type 固定九类（`feat/fix/docs/style/refactor/perf/test/chore/revert`，build 与 ci 并入 chore），scope 有白名单，subject 祈使句、首词小写、≤ 50 字符，破坏性变更用 `!` + `BREAKING CHANGE:` footer。校验分两层：本地 lefthook 跑 commitlint + gitleaks + spotless，服务端 CI 再跑 `commitlint --from origin/main` 和 PR 标题校验，因为 `--no-verify` 能绕过本地钩子，只有 required checks 才是真门禁。
>
> 合并默认 squash，所以 PR 标题必须同样符合提交规范；squash 后 main 上一 PR 一提交，回滚就是一次 `git revert`，merge 提交则用 `-m 1`。数据库不能靠 revert，必须 expand-contract：先加字段、双写、切读，最后一个版本再删旧字段，删列类脚本标记为不可回滚。
>
> 版本用 SemVer 的 annotated tag（`v1.4.0`，`git tag -a`），tag 受保护、不可移动，push tag 触发发布流水线，git-cliff 按 type 自动生成 CHANGELOG 并把 Breaking 置顶。紧急故障 2 小时内止血，优先关开关，其次 revert，事后必须补 main/release 的 PR 留痕并复盘。

<!-- end -->
