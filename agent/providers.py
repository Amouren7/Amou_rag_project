
import os
from typing import Optional
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIChatModel
import openai
from dotenv import load_dotenv
from .config import Settings, get_settings


load_dotenv()


def get_llm_model(model_choice: Optional[str] = None, settings: Settings | None = None) -> OpenAIChatModel:
    """
    Get LLM model configuration based on environment variables.
    
    Args:
        model_choice: Optional override for model choice
    
    Returns:
        Configured OpenAI-compatible model
    """
    settings = settings or get_settings()
    llm_choice = model_choice or settings.llm_model
    provider = OpenAIProvider(api_key=settings.llm_api_key or "missing-api-key", base_url=settings.llm_base_url)
    return OpenAIChatModel(llm_choice, provider=provider)


def get_embedding_client(settings: Settings | None = None) -> openai.AsyncOpenAI:
    """
    Get embedding client configuration based on environment variables.
    
    Returns:
        Configured OpenAI-compatible client for embeddings
    """
    settings = settings or get_settings()
    return openai.AsyncOpenAI(
        api_key=settings.embedding_api_key or "missing-api-key",
        base_url=settings.embedding_base_url,
        timeout=settings.model_timeout_seconds,
    )


def get_embedding_model() -> str:
    """
    Get embedding model name from environment.
    
    Returns:
        Embedding model name
    """
    return get_settings().embedding_model
