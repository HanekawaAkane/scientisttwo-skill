# ScientistTwo Skill

把「在某个 SOTA 上做出可归因的改进，并写成能过评审的稿子」这件事，拆成一条带闸门的流水线，做成可被 AI agent 直接执行的 skill。

方法来源：[ScientistTwo: Pioneering the Human Knowledge Frontier with Autonomous AI](https://arxiv.org/abs/2609.19644)（Nam et al., Google Cloud AI Research + University of Waterloo, 2026）。**本仓库不是论文官方实现，也不是 Google 的项目。** 它是把论文里的流程抽象成一套可执行的 agent 协议，并补了论文缺的几块工程约束。

---

## 它解决什么

大多数"AI 做科研"的实际失败模式不是想不出 idea，而是：

- 想法没落在机制层，只是调参换个说法
- 只在单数据集单指标上赢，恰好是唯一变好的那个
- 增益来自 EMA / label smoothing / 更大骨干，却写成了新方法
- 被评审质疑后改措辞，不补实验
- 编引用、编数字、改评测脚本

这个 skill 用十道闸门把这些挡住。闸门靠产物判定，不靠自述。

## 安装

WorkBuddy（用户级，跨项目可用）：

```bash
git clone https://github.com/HanekawaAkane/scientisttwo-skill.git \
  ~/.workbuddy/skills/scientisttwo
```

项目级：

```bash
git clone https://github.com/HanekawaAkane/scientisttwo-skill.git \
  <project>/.workbuddy/skills/scientisttwo
```

装完重启会话，说「用 scientisttwo 跑 ideate」或 `/scientisttwo` 触发。

## 结构

```
SKILL.md                       # 路由 + 硬规则 + 预期管理
references/
  pipeline.md                  # S1–S9 阶段规格，含论文原装超参
  agents.md                    # 10 个角色的提示词骨架
  gates-and-audit.md           # 10 道闸门 + state.json 结构 + I1–I4 审计
  critique.md                  # 论文的软肋，以及本 skill 偏离论文的记账
scripts/
  new_run.py                   # 一键初始化 run 目录（stdlib，无依赖）
```

## 六种模式

| mode | 输入 | 输出 | 成本 |
|---|---|---|---|
| `ideate` | 论文 + 代码 | 局限清单 + 种子想法 + novelty 打分 | 极低 |
| `screen` | 已有想法 | 子集实验结果 + 淘汰名单 | 低 |
| `improve` | baseline | 全流程 | 高 |
| `ablate` | 已有方法 | 消融表 + 归因结论 | 中 |
| `review` | 稿件 + 代码 | 评审 + rebuttal 实验计划 | 中低 |
| `audit` | 稿件 + 代码 | I1–I4 审计报告 | 低 |

默认别跑 `improve`。论文单篇成本约 $3,765、2.5 天；`ideate` 十分钟能省掉这笔钱。

## 流程

```
G0 契约 → G1 局限 → G2a 想法 → G2b 子集 → G3 全量
        → G4 归因 → G5a 稿件 → G5b 评审 → G6 元审 → G7 审计
```

几条值得单独拎出来的规矩：

- **子集先筛。** 想法先在代表性切片上跑，过了才给全量算力。
- **消融是闸门，不是附录。** 增益能被通用训练技巧复现 → 不算贡献，即使分数更高。
- **rebuttal 要跑实验。** 被质疑就补实验，不改措辞。
- **结构约束优于提示词禁令。** 靠 diff、重跑、对齐审计，不靠"禁止 XX"的 prompt。
- **失败是合法输出。** 全灭就交负结果 + 死因分析，不搬数字。

## 相对论文补了什么

| 补充 | 原因 |
|---|---|
| G0 前置三问（值不值得做） | 论文没有前置筛选，会花 $3,765 解文献检索就能回答的问题 |
| 双评审器（held-out 校验） | 论文的 ScholarPeer 既是改稿器又是评测器，91.9% 接受率是 in-distribution |
| 3 seed + 显著性门槛 | 论文未公开 seed 协议，单 seed 提升常被方差吃掉 |
| A4 消融（通用旋钮复现） | 论文是事后才发现这类问题（DMC-TeCh 案例），改为固定项更省 |
| A/B/C/D 四档算力降级 | 没算力时产「可执行队列 + TBD(blocked:)」，不产假数字 |
| 80% 预算熔断 | 论文只在 limitation 里承认贵，没有运行时熔断 |

完整记账见 `references/critique.md` §5。


论文的 80.4% / 25.2% 是在 107 道真实题目、有完整 GPU 执行环境下得到的。held-out 评审器上只有 5.7/10，人工评审里方法严谨性 2.9 还略低于人类。**这个 skill 给你的是流程纪律，不是性能保证。** 没有算力就老实降级，别让 agent 编数字。

## License

MIT，见 [LICENSE](LICENSE)。论文本身版权归原作者，本仓库只包含对其方法的文字性重构与工程化描述。
