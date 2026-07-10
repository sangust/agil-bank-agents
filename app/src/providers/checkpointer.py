"""Provider do checkpointer do LangGraph — onde vive o estado das sessões de conversa.

Com ``REDIS_URL`` configurada, usa Redis (sessões sobrevivem a restart e escalam entre
workers). Sem Redis, cai para ``MemorySaver`` (em memória, útil em testes e dev local).
"""
from __future__ import annotations

from functools import lru_cache

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.redis import RedisSaver

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)


def _build_redis_saver(url: str) -> BaseCheckpointSaver | None:
    try:
        saver = RedisSaver(redis_url=url)
        saver.setup()
    except Exception as exc:  # Redis fora do ar — não derruba a API
        logger.error("Redis indisponível em %s (%s). Usando MemorySaver.", url, exc)
        return None
    logger.info("Checkpointer: Redis (%s).", url)
    return saver


@lru_cache(maxsize=1)
def get_checkpointer() -> BaseCheckpointSaver:
    """Checkpointer das sessões: Redis quando configurado, senão memória."""
    url = get_settings().redis_url
    if url:
        saver = _build_redis_saver(url)
        if saver is not None:
            return saver

    logger.info("Checkpointer: MemorySaver (sessões não sobrevivem a restart).")
    return MemorySaver()
