#!/usr/bin/env python3
"""Scaffold a ScientistTwo run directory.

Usage:
    python new_run.py <run-id> [--mode improve] [--tier B] [--root ./runs]
                      [--paper URL] [--repo PATH] [--gpu-hours 40] [--usd 500]

Creates:
    <root>/<run-id>/{state.json,trace.log,00_contract.md,01_limits ... 09_audit}
stdlib only.
"""
import argparse
import json
import os
import sys
from datetime import datetime

DIRS = [
    "01_limits", "02_ideas", "03_subset", "04_full",
    "05_ablation", "06_draft", "07_review", "08_meta", "09_audit",
]
MODES = ["ideate", "screen", "improve", "ablate", "review", "audit"]

CONTRACT_TMPL = """# 00 · 问题契约

- run_id: {run_id}
- mode: {mode}
- 档位 (A/B/C/D): {tier}
- 建立时间: {now}

## 1. 研究问题 P
（一句话：输入 / 输出 / 评测协议）

## 2. 人类 SOTA 基线
- 论文: {paper}
- 代码库: {repo}
- commit:
- 原报告主结果:（指标 | 数据集 | 数值）

## 3. 基准网格
| 数据集 | 划分 | 指标 | 方向(higher/lower) | 原 SOTA 数值 |
|---|---|---|---|---|
|  |  |  |  |  |

## 4. 冻结清单（I2 审计基准，事后补写无效）
- [ ] 评测脚本路径:
- [ ] metric 实现路径:
- [ ] 数据划分文件:
- [ ] 其他禁止改动项:

## 5. 预算
- GPU 小时: {gpu}
- 美元: {usd}
- 墙钟小时:
- 触发暂停阈值: 80%

## 6. G0 前置三问（任一不过 → 退出或降级到 ideate）
1. 该局限是否已有文献明确指出并解决？（检索结论 + 链接）
2. 预期增益量级是否可能来自机制创新而非调参？（判断依据）
3. 若失败，负结果是否有信息量？

## 7. 环境与可执行性自检
- baseline 能否跑通: yes / no / 未验证
- 单次子集实验耗时:
- 实际档位重评: A / B / C / D
"""

STATE_TMPL = {
    "run_id": "",
    "mode": "",
    "tier": "",
    "created": "",
    "problem": {
        "statement": "",
        "baseline_paper": "",
        "baseline_repo": "",
        "baseline_commit": "",
        "datasets": [],
        "metrics": [],
        "frozen": [],
    },
    "budget": {
        "max_gpu_hours": 0, "used_gpu_hours": 0,
        "max_wall_hours": 0, "used_wall_hours": 0,
        "max_usd": 0, "used_usd": 0,
    },
    "counters": {
        "limitation_rounds": 0,
        "idea_rounds": 0,
        "engineering_rounds": 0,
        "ablation_refine_rounds": 0,
        "review_rounds": 0,
        "meta_refine_rounds": 0,
    },
    "gates": {
        g: {"status": "pending", "evidence": [], "note": ""}
        for g in ["G0", "G1", "G2a", "G2b", "G3", "G4", "G5a", "G5b", "G6", "G7"]
    },
    "best": {"idea": None, "method_name": None, "gain": None,
             "code_ref": None, "source": None},
    "history": [],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_id")
    ap.add_argument("--mode", default="improve", choices=MODES)
    ap.add_argument("--tier", default="B", choices=list("ABCD"))
    ap.add_argument("--root", default="./runs")
    ap.add_argument("--paper", default="")
    ap.add_argument("--repo", default="")
    ap.add_argument("--gpu-hours", type=float, default=0)
    ap.add_argument("--usd", type=float, default=0)
    args = ap.parse_args()

    now = datetime.now().astimezone().isoformat(timespec="seconds")
    run_dir = os.path.normpath(os.path.join(args.root, args.run_id))
    if os.path.exists(run_dir):
        sys.exit(f"[x] {run_dir} 已存在。换一个 run-id，别覆盖正在跑的实验。")

    for d in DIRS:
        os.makedirs(os.path.join(run_dir, d), exist_ok=True)

    state = json.loads(json.dumps(STATE_TMPL))
    state["run_id"] = args.run_id
    state["mode"] = args.mode
    state["tier"] = args.tier
    state["created"] = now
    state["problem"]["baseline_paper"] = args.paper
    state["problem"]["baseline_repo"] = args.repo
    state["budget"]["max_gpu_hours"] = args.gpu_hours
    state["budget"]["max_usd"] = args.usd

    with open(os.path.join(run_dir, "state.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    with open(os.path.join(run_dir, "00_contract.md"), "w", encoding="utf-8") as f:
        f.write(CONTRACT_TMPL.format(
            run_id=args.run_id, mode=args.mode, tier=args.tier, now=now,
            paper=args.paper or "<待填>", repo=args.repo or "<待填>",
            gpu=args.gpu_hours or "<待填>", usd=args.usd or "<待填>",
        ))

    with open(os.path.join(run_dir, "trace.log"), "w", encoding="utf-8") as f:
        f.write(f"{now} | G0 | init | {run_dir} | pending | mode={args.mode} tier={args.tier}\n")

    print(f"[ok] {run_dir}")
    print("下一步：填 00_contract.md → 过 G0 → 再进 S1。不要跳闸门。")


if __name__ == "__main__":
    main()
