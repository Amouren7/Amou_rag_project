from __future__ import annotations

import argparse
import json
from pathlib import Path

from .metrics import calculate_metrics


def run_fixture(dataset: list[dict]) -> list[dict]:
    rows = []
    for item in dataset:
        expected = item["expected_sources"]
        rows.append({
            "id": item["id"],
            "expected_sources": expected,
            "retrieved_sources": expected + ["product_handbook.md"],
            "citations": expected if item.get("requires_citation", True) else [],
            "latency_ms": 0.0,
            "mode": "fixture",
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="evaluation/dataset.json")
    parser.add_argument("--mode", choices=["fixture"], default="fixture")
    args = parser.parse_args()
    dataset = json.loads(Path(args.dataset).read_text(encoding="utf-8"))
    rows = run_fixture(dataset)
    metrics = calculate_metrics(rows, k=5)
    output = {"mode": args.mode, "metrics": metrics, "rows": rows}
    result_json = Path("evaluation/results.json")
    result_md = Path("evaluation/results.md")
    result_json.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    result_md.write_text(
        "# 离线评测结果\n\n"
        "> fixture 模式只验证评测管线和指标计算，不代表真实模型效果。\n\n"
        f"- 问题数：{metrics['total_questions']}\n"
        f"- Recall@5：{metrics['recall_at_k']:.3f}\n"
        f"- MRR：{metrics['mrr']:.3f}\n"
        f"- 引用覆盖率：{metrics['citation_coverage']:.3f}\n",
        encoding="utf-8",
    )
    print(json.dumps(metrics, ensure_ascii=False))


if __name__ == "__main__":
    main()
