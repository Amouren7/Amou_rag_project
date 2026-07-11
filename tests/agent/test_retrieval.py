from agent.retrieval import reciprocal_rank_fusion


def test_rrf_rewards_chunks_found_by_both_retrievers():
    vector = [{"chunk_id": "a", "score": 0.9}, {"chunk_id": "b", "score": 0.8}]
    keyword = [{"chunk_id": "b", "score": 0.95}, {"chunk_id": "c", "score": 0.7}]
    merged = reciprocal_rank_fusion(vector, keyword, k=60)
    assert merged[0]["chunk_id"] == "b"
    assert merged[0]["search_type"] == "hybrid"


def test_rrf_preserves_source_metadata():
    vector = [{"chunk_id": "a", "document_source": "a.md", "page_number": 3, "score": 0.9}]
    merged = reciprocal_rank_fusion(vector, [], k=60)
    assert merged[0]["document_source"] == "a.md"
    assert merged[0]["page_number"] == 3
    assert merged[0]["search_type"] == "vector"
