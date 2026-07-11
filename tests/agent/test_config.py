import pytest


def test_settings_support_independent_openai_compatible_endpoints(monkeypatch):
    from agent.config import Settings

    monkeypatch.setenv("LLM_API_KEY", "llm-test")
    monkeypatch.setenv("LLM_BASE_URL", "https://llm.example/v1")
    monkeypatch.setenv("LLM_MODEL", "chat-model")
    monkeypatch.setenv("EMBEDDING_API_KEY", "embed-test")
    monkeypatch.setenv("EMBEDDING_BASE_URL", "https://embed.example/v1")
    monkeypatch.setenv("EMBEDDING_MODEL", "embedding-model")
    monkeypatch.setenv("EMBEDDING_DIMENSION", "1024")

    settings = Settings.from_env()

    assert settings.llm_api_key == "llm-test"
    assert settings.llm_base_url == "https://llm.example/v1"
    assert settings.llm_model == "chat-model"
    assert settings.embedding_api_key == "embed-test"
    assert settings.embedding_dimension == 1024


def test_settings_reject_invalid_embedding_dimension(monkeypatch):
    from agent.config import Settings

    monkeypatch.setenv("EMBEDDING_DIMENSION", "not-a-number")
    with pytest.raises(ValueError, match="EMBEDDING_DIMENSION"):
        Settings.from_env()


def test_settings_never_uses_environment_variable_name_as_key(monkeypatch):
    from agent.config import Settings

    for key in ("OPENAI_API_KEY", "LLM_API_KEY", "EMBEDDING_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    settings = Settings.from_env()
    assert settings.llm_api_key is None
    assert settings.embedding_api_key is None
