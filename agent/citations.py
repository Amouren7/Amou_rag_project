from __future__ import annotations

from collections.abc import Iterable, Mapping

from .models import Citation


def build_citations(rows: Iterable[Mapping], snippet_limit: int = 240) -> list[Citation]:
    citations: list[Citation] = []
    seen: set[str] = set()
    for row in rows:
        chunk_id = str(row.get("chunk_id") or "")
        source = str(row.get("document_source") or row.get("source_file") or "")
        if not chunk_id or not source or chunk_id in seen:
            continue
        seen.add(chunk_id)
        content = str(row.get("content") or "").strip()
        snippet = content if len(content) <= snippet_limit else content[:snippet_limit] + "…"
        citations.append(Citation(
            chunk_id=chunk_id,
            document_title=str(row.get("document_title") or source),
            document_source=source,
            page_number=row.get("page_number"),
            snippet=snippet,
            score=float(row.get("score") or row.get("combined_score") or 0.0),
            search_type=str(row.get("search_type") or "unknown"),
        ))
    return citations
