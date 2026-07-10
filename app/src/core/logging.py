"""Configuração de logging da aplicação."""
from __future__ import annotations

import logging
from functools import lru_cache

from src.core.constants import LOGS_DIR

FORMATO = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


@lru_cache(maxsize=1)
def _configurar() -> None:
    """Configura o logging uma única vez (o cache substitui a flag global)."""
    LOGS_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format=FORMATO,
        handlers=[
            logging.FileHandler(LOGS_DIR / "banco_agil.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger nomeado, configurando o logging na primeira chamada."""
    _configurar()
    return logging.getLogger(name)
