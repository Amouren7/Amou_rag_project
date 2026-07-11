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
