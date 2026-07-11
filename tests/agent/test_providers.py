def test_embedding_client_uses_independent_endpoint(monkeypatch):
    from agent.config import Settings
    from agent.providers import get_embedding_client

    settings = Settings(
        llm_api_key="llm",
        llm_base_url="https://llm.example/v1",
        llm_model="chat",
        embedding_api_key="embed",
        embedding_base_url="https://embed.example/v1",
        embedding_model="embedding",
        embedding_dimension=1536,
        model_timeout_seconds=30.0,
    )
    client = get_embedding_client(settings)
    assert str(client.base_url) == "https://embed.example/v1/"
