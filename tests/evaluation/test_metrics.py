from evaluation.metrics import calculate_metrics


def test_calculate_recall_mrr_citation_coverage_and_latency():
    rows = [{
        "expected_sources": ["after_sales.md"],
        "retrieved_sources": ["product.md", "after_sales.md"],
        "citations": ["after_sales.md"],
        "latency_ms": 12.0,
    }]
    metrics = calculate_metrics(rows, k=2)
    assert metrics["recall_at_k"] == 1.0
    assert metrics["mrr"] == 0.5
    assert metrics["citation_coverage"] == 1.0
    assert metrics["average_latency_ms"] == 12.0


def test_failed_rows_remain_visible_in_error_count():
    metrics = calculate_metrics([{"error": "timeout"}], k=5)
    assert metrics["total_questions"] == 1
    assert metrics["errors"] == 1
