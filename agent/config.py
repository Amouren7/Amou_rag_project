from __future__ import annotations

from dataclasses import dataclass
import os


def _optional(name: str, fallback: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None and fallback:
        value = os.getenv(fallback)
    return value.strip() if value and value.strip() else None


@dataclass(frozen=True)
class Settings:
    llm_api_key: str | None
    llm_base_url: str
    llm_model: str
    embedding_api_key: str | None
    embedding_base_url: str
    embedding_model: str
    embedding_dimension: int
    model_timeout_seconds: float

    @classmethod
    def from_env(cls) -> "Settings":
        raw_dimension = os.getenv("EMBEDDING_DIMENSION", "1024")
        try:
            dimension = int(raw_dimension)
        except ValueError as exc:
            raise ValueError("EMBEDDING_DIMENSION must be an integer") from exc
        if dimension <= 0:
            raise ValueError("EMBEDDING_DIMENSION must be positive")

        return cls(
            llm_api_key=_optional("LLM_API_KEY", "OPENAI_API_KEY"),
            llm_base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
            llm_model=os.getenv("LLM_MODEL", os.getenv("LLM_CHOICE", "gpt-4o-mini")),
            embedding_api_key=_optional("EMBEDDING_API_KEY", "OPENAI_API_KEY"),
            embedding_base_url=os.getenv("EMBEDDING_BASE_URL", "https://api.siliconflow.cn/v1").rstrip("/"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3"),
            embedding_dimension=dimension,
            model_timeout_seconds=float(os.getenv("MODEL_TIMEOUT_SECONDS", "60")),
        )


def get_settings() -> Settings:
    return Settings.from_env()
