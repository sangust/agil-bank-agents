"""Provider de embeddings (Gemini), usado pelo vector store do RAG."""
from __future__ import annotations

from functools import lru_cache

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_embeddings() -> GoogleGenerativeAIEmbeddings | None:
    """Embeddings do Gemini. Retorna None (RAG desabilitado) se não houver GOOGLE_API_KEY."""
    settings = get_settings()
    if not settings.tem_gemini:
        logger.warning("RAG desabilitado: GOOGLE_API_KEY ausente para embeddings.")
        return None
    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model, google_api_key=settings.google_api_key
    )
