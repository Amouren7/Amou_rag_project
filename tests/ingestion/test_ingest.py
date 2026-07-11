from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, Mock

import pytest

from ingestion.chunker import DocumentChunk
from ingestion.ingest import DocumentIngestionPipeline


class _Transaction:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_save_to_postgres_persists_source_metadata_columns(monkeypatch):
    conn = AsyncMock()
    conn.fetchrow.return_value = {"id": "document-id"}
    conn.transaction = Mock(return_value=_Transaction())

    @asynccontextmanager
    async def acquire():
        yield conn

    monkeypatch.setattr("ingestion.ingest.db_pool.acquire", acquire)
    pipeline = DocumentIngestionPipeline.__new__(DocumentIngestionPipeline)
    chunk = DocumentChunk(
        content="退换货规则",
        index=0,
        start_char=0,
        end_char=5,
        metadata={
            "page_number": 3,
            "source_file": "policy.pdf",
            "content_type": "pdf",
            "chunk_method": "semantic",
        },
    )
    chunk.embedding = [0.1, 0.2]

    await pipeline._save_to_postgres(
        "售后政策", "policy.pdf", "退换货规则", [chunk], {}
    )

    sql, *params = conn.execute.call_args.args
    assert "page_number, source_file, content_type, chunk_method" in sql
    assert params[-4:] == [3, "policy.pdf", "pdf", "semantic"]
