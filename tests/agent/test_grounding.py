from pathlib import Path

from agent.prompts import SYSTEM_PROMPT


def test_system_prompt_requires_retrieval_citations_and_refusal():
    assert "先检索" in SYSTEM_PROMPT
    assert "不得编造" in SYSTEM_PROMPT
    assert "页码" in SYSTEM_PROMPT
    assert "无法确认" in SYSTEM_PROMPT


def test_schema_uses_chinese_friendly_trigram_search():
    schema = Path("sql/schema.sql").read_text(encoding="utf-8")
    assert "similarity(c.content, query_text)" in schema
    assert "ILIKE" in schema
    assert "to_tsvector('english'" not in schema


def test_documented_embedding_dimension_matches_schema():
    schema = Path("sql/schema.sql").read_text(encoding="utf-8")
    env_example = Path(".env.example").read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "embedding vector(1024)" in schema
    assert "EMBEDDING_DIMENSION=1024" in env_example
    assert "EMBEDDING_DIMENSION=1024" in readme
