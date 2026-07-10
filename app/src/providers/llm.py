"""Provider de chat model: Gemini (primário) com fallback automático para Groq."""
from __future__ import annotations

from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)

# 1 tentativa: falha rápido no Gemini para acionar o fallback sem longa espera.
MAX_RETRIES_GEMINI = 1


class LLMConfigError(RuntimeError):
    """Nenhuma credencial de LLM configurada."""


def _build_gemini() -> BaseChatModel | None:
    settings = get_settings()
    if not settings.tem_gemini:
        return None
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=settings.temperatura,
        max_retries=MAX_RETRIES_GEMINI,
    )


def _build_groq() -> BaseChatModel | None:
    settings = get_settings()
    if not settings.tem_groq:
        return None
    return ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=settings.temperatura,
    )


@lru_cache(maxsize=1)
def get_chat_model() -> BaseChatModel:
    """Chat model com fallback Gemini -> Groq (via ``with_fallbacks``)."""
    primario = _build_gemini()
    fallback = _build_groq()

    if primario is not None and fallback is not None:
        logger.info("LLM: Gemini (primário) com fallback para Groq.")
        return primario.with_fallbacks([fallback])
    if primario is not None:
        logger.info("LLM: apenas Gemini configurado.")
        return primario
    if fallback is not None:
        logger.info("LLM: apenas Groq configurado.")
        return fallback

    raise LLMConfigError(
        "Nenhuma chave de LLM configurada. Defina GOOGLE_API_KEY e/ou GROQ_API_KEY em infra/.env."
    )
