"""Cliente HTTP da UI para a API do Banco Ágil.

A UI não conhece o grafo nem os serviços — tudo passa por requisições à API.
"""
from __future__ import annotations

import os

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT_CHAT_S = 90
TIMEOUT_HEALTH_S = 5


class APIError(Exception):
    """Falha de comunicação com a API."""


def enviar(session_id: str | None, texto: str) -> dict:
    """Envia a mensagem ao endpoint /api/chat e retorna o JSON de resposta."""
    try:
        resposta = requests.post(
            f"{API_BASE_URL}/api/chat",
            json={"session_id": session_id, "message": texto},
            timeout=TIMEOUT_CHAT_S,
        )
        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException as exc:
        raise APIError(str(exc)) from exc


def health() -> bool:
    """Indica se a API está respondendo (usado no painel lateral)."""
    try:
        return requests.get(f"{API_BASE_URL}/health", timeout=TIMEOUT_HEALTH_S).ok
    except requests.RequestException:
        return False
