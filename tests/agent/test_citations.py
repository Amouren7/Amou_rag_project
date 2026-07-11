from agent.citations import build_citations


def test_build_citations_deduplicates_and_keeps_best_ranked_source():
    rows = [
        {"chunk_id": "c1", "document_title": "售后规则", "document_source": "after_sales.md", "page_number": 2, "content": "七天内可申请退换", "score": 0.9, "search_type": "hybrid"},
        {"chunk_id": "c1", "document_title": "售后规则", "document_source": "after_sales.md", "page_number": 2, "content": "重复内容", "score": 0.8, "search_type": "vector"},
    ]
    citations = build_citations(rows)
    assert len(citations) == 1
    assert citations[0].page_number == 2
    assert citations[0].search_type == "hybrid"


def test_build_citations_truncates_long_snippets():
    citations = build_citations([{"chunk_id": "c1", "document_title": "规则", "document_source": "r.md", "content": "中" * 400, "score": 1.0}])
    assert len(citations[0].snippet) == 241
    assert citations[0].snippet.endswith("…")
