"""Configuração da aplicação via pydantic-settings (variáveis de ambiente / infra/.env)."""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.constants import ENV_FILE


class Settings(BaseSettings):
    """Configurações lidas do ambiente.

    Em Docker, o compose injeta as variáveis via ``env_file`` (o arquivo não é copiado
    para a imagem); localmente, são lidas de ``infra/.env``.
    """

    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore"
    )

    # LLM
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash-lite", alias="GEMINI_MODEL")
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")
    embedding_model: str = Field(default="models/gemini-embedding-001", alias="EMBEDDING_MODEL")
    temperatura: float = Field(default=0.1, alias="LLM_TEMPERATURE")

    # Câmbio
    awesomeapi_base_url: str = Field(
        default="https://economia.awesomeapi.com.br/json/last", alias="AWESOMEAPI_BASE_URL"
    )

    # RAG
    rag_top_k: int = Field(default=3, alias="RAG_TOP_K")

    # Sessões: vazio -> MemorySaver (em memória)
    redis_url: str = Field(default="", alias="REDIS_URL")

    @property
    def tem_gemini(self) -> bool:
        return bool(self.google_api_key)

    @property
    def tem_groq(self) -> bool:
        return bool(self.groq_api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Instância única de configurações."""
    return Settings()
