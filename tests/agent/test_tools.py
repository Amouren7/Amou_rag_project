import pytest

from agent.models import ChunkResult
from agent.tools import HybridSearchInput, hybrid_search_tool


@pytest.mark.asyncio
async def test_hybrid_tool_fuses_vector_and_keyword_results(monkeypatch):
    async def fake_embedding(_):
        return [0.1, 0.2]

    async def fake_vector(embedding, limit=10):
        return [
            {"chunk_id": "a", "document_id": "d", "content": "向量", "similarity": 0.9, "metadata": {}, "document_title": "产品", "document_source": "product.md", "page_number": 1},
            {"chunk_id": "b", "document_id": "d", "content": "共同", "similarity": 0.8, "metadata": {}, "document_title": "产品", "document_source": "product.md", "page_number": 2},
        ]

    async def fake_keyword(_query, limit=10):
        return [
            {"chunk_id": "b", "document_id": "d", "content": "共同", "text_similarity": 0.95, "metadata": {}, "document_title": "产品", "document_source": "product.md", "page_number": 2}
        ]

    monkeypatch.setattr("agent.tools.generate_embedding", fake_embedding)
    monkeypatch.setattr("agent.tools.vector_search", fake_vector)
    monkeypatch.setattr("agent.tools.keyword_search", fake_keyword)

    results = await hybrid_search_tool(HybridSearchInput(query="透气手套", limit=5))
    assert isinstance(results[0], ChunkResult)
    assert results[0].chunk_id == "b"
    assert results[0].page_number == 2
    assert results[0].search_type == "hybrid"
