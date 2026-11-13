# ADR-0003：模型接入统一为 provider 接口并对接 OpenAI 兼容端点

- **Status**: Accepted
- **Date**: 2026-11-13
- **Deciders**: Caspian
- **Related**: `specs/001-strata-platform/spec.md`、`specs/001-strata-platform/plan.md`、ADR-0002

## 背景（Context）

模型供应商可能因区域、成本或可用性调整而更换，平台不希望把供应商写死在代码里。默认接入点为火山方舟的 OpenAI 兼容端点；同时需要保证本地开发与 CI 在没有真实 Key 时也能跑通。现有风险是：直接依赖厂商专属 starter 时，默认值隐式生效、配置散落、切换供应商需要改代码。

## 决策（Decision）

我们将模型接入统一抽象为 provider 接口，默认实现对接火山方舟的 OpenAI 兼容端点；`base-url`、`model`、`api-key` 全部通过环境变量注入，更换供应商只改配置不改代码，且不使用厂商专属 starter 的默认值。

## 备选方案（Alternatives Considered）

| 方案 | 优点 | 缺点 | 为什么未选 |
| --- | --- | --- | --- |
| A（选中）provider 接口 + OpenAI 兼容端点 + 环境变量 | 切换供应商只改配置；CI 可用桩实现；配置来源单一 | 需要自行定义请求/响应映射与错误语义 | — |
| B 直接使用厂商专属 starter 及默认值 | 接入快，样板代码少 | 默认值隐式生效，配置分散，切换供应商往往要改代码 | 与"可配置"验收项冲突 |
| C 为每家供应商编写独立适配类 | 可针对厂商特性优化 | 重复实现、测试矩阵膨胀，新增供应商成本高 | 维护成本超出单人项目承受范围 |
| D 只支持 OpenAI 官方端点 | 实现最简单 | 不满足默认接入点与部署区域要求 | 与既定接入方式不符 |

## 后果（Consequences）

**正面**

- 供应商替换收敛为配置变更，代码与测试不受影响。
- 所有敏感配置从环境变量进入，仓库只保留占位样例。
- 桩 provider 可让全部自动化测试在不接触真实服务的情况下运行。

**负面 / 代价**

- 需要维护 OpenAI 兼容协议的请求与响应映射，兼容性差异由平台自身吸收。
- 环境变量缺失时必须在启动阶段失败并给出明确提示，否则问题会延迟到首次调用。

**需要跟进的动作**

- [ ] 定义 provider 接口与错误码映射，缺失配置时启动即失败（Caspian，tasks T019、T020）
- [ ] 提供 `.env.example`，列出 `base-url`、`model`、`api-key` 等占位项（Caspian，tasks T019）
- [ ] 桩 provider 与真实 provider 共用同一接口，保证测试与演示一致（Caspian，tasks T014）

## 合规性（Compliance）

- 与 `constitution.md` 的关系：符合 Article III（敏感信息零入库、外部化配置）；Article II（provider 必须有可运行证据与测试）。
- 如何验证执行：CI 密钥扫描；代码评审检查是否存在厂商 starter 默认值或硬编码端点；启动校验测试覆盖缺失配置场景。

## 备注（Notes）

默认值只允许出现在 `.env.example` 的占位说明中，不得在代码里提供可用的默认 Key、默认生产端点或默认账号。若未来需要多供应商路由或灰度，另立 ADR。
