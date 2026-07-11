from __future__ import annotations

from statistics import mean


def calculate_metrics(rows: list[dict], k: int = 5) -> dict:
    total = len(rows)
    recalls: list[float] = []
    reciprocal_ranks: list[float] = []
    citation_hits: list[float] = []
    latencies: list[float] = []
    errors = 0
    for row in rows:
        if row.get("error"):
            errors += 1
            recalls.append(0.0)
            reciprocal_ranks.append(0.0)
            citation_hits.append(0.0)
            continue
        expected = set(row.get("expected_sources", []))
        retrieved = list(row.get("retrieved_sources", []))[:k]
        citations = set(row.get("citations", []))
        recalls.append(1.0 if expected.intersection(retrieved) else 0.0)
        first_rank = next((index for index, source in enumerate(retrieved, 1) if source in expected), None)
        reciprocal_ranks.append(1.0 / first_rank if first_rank else 0.0)
        citation_hits.append(1.0 if expected and expected.issubset(citations) else 0.0)
        if row.get("latency_ms") is not None:
            latencies.append(float(row["latency_ms"]))
    return {
        "total_questions": total,
        "errors": errors,
        "k": k,
        "recall_at_k": mean(recalls) if recalls else 0.0,
        "mrr": mean(reciprocal_ranks) if reciprocal_ranks else 0.0,
        "citation_coverage": mean(citation_hits) if citation_hits else 0.0,
        "average_latency_ms": mean(latencies) if latencies else 0.0,
    }
