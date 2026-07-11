from __future__ import annotations

from collections.abc import Iterable, Mapping


def reciprocal_rank_fusion(
    vector_results: Iterable[Mapping],
    keyword_results: Iterable[Mapping],
    *,
    k: int = 60,
) -> list[dict]:
    if k <= 0:
        raise ValueError("RRF k must be positive")
    combined: dict[str, dict] = {}
    origins: dict[str, set[str]] = {}
    for origin, rows in (("vector", vector_results), ("keyword", keyword_results)):
        for rank, raw in enumerate(rows, start=1):
            row = dict(raw)
            chunk_id = str(row.get("chunk_id") or "")
            if not chunk_id:
                continue
            if chunk_id not in combined:
                combined[chunk_id] = row
                combined[chunk_id]["rrf_score"] = 0.0
                origins[chunk_id] = set()
            combined[chunk_id]["rrf_score"] += 1.0 / (k + rank)
            origins[chunk_id].add(origin)
    for chunk_id, row in combined.items():
        row["score"] = row.pop("rrf_score")
        row["search_type"] = "hybrid" if len(origins[chunk_id]) == 2 else next(iter(origins[chunk_id]))
    return sorted(combined.values(), key=lambda item: item["score"], reverse=True)
