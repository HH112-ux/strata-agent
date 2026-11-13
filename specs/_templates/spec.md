# Feature Specification：<功能名>

**Feature ID**: `<NNN-slug>`
**Owner**: <负责人>
**Status**: Draft | InReview | Approved | Implementing | Implemented | Superseded
**Version**: 0.1.0
**Created**: <YYYY-MM-DD> | **Last Updated**: <YYYY-MM-DD>
**Input**: <需求来源：issue / 场景 / 事故复盘>
**Related**: <ADR 路径、关联 feature>

> 只写行为与验收，不写框架、库、表结构、API 路径与代码片段。

## 1. 背景与问题

- **现状**：
- **要解决的问题**：
- **不做的后果**：
- **成功的样子**：

## 2. 范围

**In scope**

- [ ]

**Out of scope**

- [ ]

**边界与依赖**

- 上游依赖：
- 下游影响：

## 3. 用户故事

### US-1 — <一句话价值>（Priority: P1）

作为 <角色>，我希望 <能力>，以便 <价值>。

- **Why P1**：
- **Independent Test**：<不依赖其他故事即可验证的方式>
- **Acceptance Criteria（EARS）**

| ID | 场景/句式 | 期望结果 |
| --- | --- | --- |
| AC-1.1 | When <触发>, the <系统> shall <响应> | <可观测结果> |
| AC-1.2 | If <异常>, then the <系统> shall <响应> | <错误码或状态> |

> P1 单独交付必须是可用 MVP；每个 US 必须能独立测试。

## 4. 功能需求

- **FR-1**：The system MUST <能力>。
  - 追溯：AC-1.1
- **FR-2**：The system MUST NOT <禁止行为>。
  - 追溯：AC-1.2

## 5. 非功能需求

- **NFR-1（性能）**：<数字或可观测信号，无数字视为未定义>
- **NFR-2（可用性/降级）**：
- **NFR-3（安全/隐私）**：
- **NFR-4（可观测性）**：
- **NFR-5（可复现性）**：

## 6. 关键实体

- **<实体>**：<职责与关键属性>。

## 7. 边界与异常场景

- [ ] <超时 / 限流 / 空输入 / 越权 / 重复调用 / 恢复幂等>

## 8. 成功标准

- **SC-1**：<可度量、技术无关>；验证方式：<测试 / 命令 / 报告>

## 9. 假设与待澄清

**Assumptions**

- [ ] <已默认成立的前提，若不成立需改规格>

**Clarifications**

- [ ] <问题> —— 负责人：<姓名>，截止：<日期>，阻塞：是/否

> 未决项写 `[NEEDS CLARIFICATION: 具体问题]`，禁止用猜测填充。

## 10. 验收方式

- 自动化：<测试层级与路径>
- 人工：<`quickstart.md` 步骤编号>
- 上线观察：<指标与周期>

## 11. 变更记录

| 日期 | 版本 | 变更 | 变更人 | 影响的 FR/AC |
| --- | --- | --- | --- | --- |
| <YYYY-MM-DD> | 0.1.0 | 初稿 | <姓名> | — |
