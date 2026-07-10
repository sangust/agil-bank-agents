"""Rota de chat: recebe uma mensagem e devolve a resposta do atendente."""
from __future__ import annotations

from fastapi import APIRouter

from api import session
from api.schemas import ChatRequest, ChatResponse
from src.core.constants import MSG_SEM_RESPOSTA
from src.core.logging import get_logger
from src.providers.llm import LLMConfigError

router = APIRouter(tags=["chat"])
logger = get_logger(__name__)


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    session_id = req.session_id or session.novo_session_id()

    try:
        estado = session.chat(session_id, req.message)
    except LLMConfigError as exc:
        return ChatResponse.de_erro(session_id, f"Configuração de LLM ausente: {exc}")
    except Exception as exc:  # nunca vaza 500 cru para o cliente
        logger.error("Erro inesperado no /chat (sessão %s): %s", session_id, exc)
        return ChatResponse.de_erro(
            session_id, "Desculpe, ocorreu um erro inesperado. Pode tentar novamente?"
        )

    return ChatResponse.from_estado(
        session_id, session.ultima_resposta(estado) or MSG_SEM_RESPOSTA, estado
    )
