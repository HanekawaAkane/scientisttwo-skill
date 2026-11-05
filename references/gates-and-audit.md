# 闸门、状态与完整性审计

## 1. 闸门表

| Gate | 名称 | 通过条件（客观可查） | 证据文件 | 不通过时 |
|---|---|---|---|---|
| G0 | 契约 | 问题/基线(含 commit)/指标/数据集/预算五要素齐全；禁止改动清单非空 | `00_contract.md` | 补全，不猜 |
| G1 | 局限 | ≥3 条合格局限，≥2 条机制层，Verifier 写 `sufficient: yes` | `01_limits/` | 回到抽取，≤16 轮 |
| G2a | 想法 | ≥6 个想法，全有 novelty 与机制 delta，≥3 个 high | `02_ideas/` | 继续生成或降级目标 |
| G2b | 子集 | ≥1 个想法 `ACCEPT`（显著优于自复现基线） | `03_subset/I<k>/critic.md` | 回 S2；二次全灭 → 终止 |
| G3 | 全量 | ≥2 数据集 × ≥2 指标严格优于原 SOTA；有 seed 重复 | `04_full/results_matrix.md` | 见 §4 失败处理 |
| G4 | 归因 | `component_breakdown: clean`；A4 通用旋钮不能复现同等增益 | `05_ablation/attribution.md` | 精修 1 轮；仍 dirty → 降级 claim |
| G5a | 稿件 | 无未标注 `TBD`；每个 claim 可定位到表/图行号 | `06_draft/` | 回写 |
| G5b | 评审 | 主评审 ≥ 阈值 且 held-out 评审 ≥ 阈值-0.5；≤2 轮 | `07_review/` | 记 `best_effort` |
| G6 | 元审 | `accept`，或 `best_effort` 且已回退历史最优 | `08_meta/` | 回 S5 |
| G7 | 审计 | I1–I4 全绿（真实执行） | `09_audit/` | 修代码或删 claim |

阈值默认：评审 8/10（ICLR 标度）。

---

## 2. state.json 结构

```json
{
  "run_id": "2026-11-05-procrustes",
  "mode": "improve",
  "tier": "B",
  "created": "2026-11-05T14:00:00+08:00",
  "problem": {
    "statement": "",
    "baseline_paper": "",
    "baseline_repo": "",
    "baseline_commit": "",
    "datasets": [],
    "metrics": [{"name": "", "direction": "higher|lower"}],
    "frozen": ["eval script", "metric impl", "data split"]
  },
  "budget": {"max_gpu_hours": 0, "used_gpu_hours": 0, "max_wall_hours": 0, "used_wall_hours": 0, "max_usd": 0, "used_usd": 0},
  "counters": {"limitation_rounds": 0, "idea_rounds": 0, "engineering_rounds": 0, "ablation_refine_rounds": 0, "review_rounds": 0, "meta_refine_rounds": 0},
  "gates": {"G0": {"status": "pending", "evidence": [], "note": ""}},
  "best": {"idea": null, "method_name": null, "gain": null, "code_ref": null, "source": "seed|evolved"},
  "history": [{"round": 1, "idea": "I3", "source": "seed", "subset": "ACCEPT", "full": "0.0", "verdict": "kept"}]
}
```

`status` 取值：`pending / pass / fail / best_effort / blocked`。只允许 `pass` 才允许进入下一闸门。

`[+ ]` **预算闸门**：每完成一个阶段更新 `used_*`。任一用量到 80% 时暂停并让用户决定（继续 / 降级 / 终止）。论文单篇 $3,765、2.5 天是参照量级，不是目标——超支之前先问一句"这题值不值"。

---

## 3. 完整性审计 I1–I4

来源：Meng et al. (2026) 的 CoE Integrity Audit，ScientistTwo 用它做了四维校验。**核心原则：审计对象是"稿子 vs 它自己的产物"，不是"稿子 vs 审稿人感受"。**

### I1 分数复现（Score Verification）

- 从干净环境（新容器/新 venv）按稿中命令重跑主表。
- 逐数字比对。允许误差：≤0.5% 或 ≤1 个标准差（取大者），且必须写在 `09_audit/I1.md` 里说明容差来源。
- 不通过常见原因：随机种子没固定、数据预处理顺序不同、`torch` 版本差异、把 best-of-N 写成了 single-run。
- 判定：`pass` / `fail(哪些数字) ` / `not_run(原因)`。

### I2 规格合规（Specification Compliance）

- 对照 `00_contract.md` 的 `frozen` 清单，检查代码与提交物的 diff：
  - 评测脚本、metric 实现、数据划分是否被改动；
  - 是否有通过读取测试标签、缓存预测、提前停止在测试集上选点等方式"优化评测器"；
  - 是否引入 contract 未允许的外部数据/预训练权重。
- 用 `git diff <baseline_commit> -- <frozen paths>` 逐条核对，**必须贴 diff 片段作为证据**，不能只写"已检查"。
- 判定：`pass` / `fail(违规项)`。一票否决：任何一项违规，该方法不得作为贡献报告，即使分数好看。

### I3 引用核实（Reference Verification）

- 每条参考文献过一遍检索：标题是否存在、作者/年份/venue 是否对得上、DOI/arXiv id 是否指向该文。
- 论文的实测基准是 1,814 条引用 0 条幻觉。达不到这个标准就把不确定的引用删掉，别留着赌。
- 输出 `09_audit/I3.md`：总数、核实通过数、删除/替换数、存疑清单。判定：`pass` 仅当存疑 = 0。

### I4 方法-代码对齐（Method-Code Alignment）

- 逐段读方法节，逐条落到代码行。产出对齐表：

| 稿件中的描述 | 代码位置 | 一致? | 差异说明 |
|---|---|---|---|
| "引入频率门控 g_t 对每个频带加权" | `model/gate.py:44-71` | ✓ | |
| "使用验证集做安全回退" | 未找到 | ✗ | 代码里是固定权重 |

- 高频失败点：稿子里写的损失项代码里没加、稿子里的默认超参与 config 不一致、稿子描述的模块实际被 disable 了。
- 判定：`pass` 仅当不一致项 = 0（或已在稿中如实降级描述）。

---

## 4. 失败处理

| 情形 | 处理 |
|---|---|
| G3 全灭（无方法超过 SOTA） | 终止。输出：负结果报告 + 死因分析（哪类机制在这个问题上无效）+ 下一步建议。**这是合格产出**，不是失败。 |
| 只在一个数据集上赢 | 不算 G3。写进局限，继续找机制或收工。 |
| G4 dirty 且精修无效 | 把方法降级为"工程改进"，贡献改为"实践观察"。不许留"我们提出了 X"的表述。 |
| G5b 两轮未达标 | 记 `best_effort`，把最尖锐的 2 条 weakness 写进稿子的 Limitation 节。 |
| G6 revise 且修改无效 | 回退到历史最优版本，收尾。 |
| G7 任一红 | 优先修代码复现；修不动就删对应 claim 并在 Results 里标注。**禁止**保留 claim 而删审计记录。 |

---

## 5. trace.log 格式

append-only，一行一条，便于事后复盘（复盘的价值高于过程本身）：

```
2026-11-05T14:12:03+08:00 | S3 | I2 subset | 03_subset/I2/results.csv | ACCEPT | gain +4.1% (std 0.6) | 3 seeds
2026-11-05T15:20:41+08:00 | S3 | I5 subset | 03_subset/I5/critic.md | REJECT | death: 频率门控在高频数据上无差别
```

必含：时间、阶段、动作、产物路径、判定、关键数字。不含：思考过程、客套话。
