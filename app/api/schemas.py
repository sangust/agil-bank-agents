"""Schemas (Pydantic) de requisição/resposta da API de chat."""
from __future__ import annotations

from pydantic import BaseModel, Field

from src.core.constants import AGENTE_PADRAO


class ChatRequest(BaseModel):
    message: str = Field(..., description="Mensagem do cliente")
    session_id: str | None = Field(default=None, description="Sessão; se ausente, é criada")


class DebugInfo(BaseModel):
    """Estado interno exposto ao painel de debug da UI (não visível ao cliente)."""

    current_agent: str = AGENTE_PADRAO
    authenticated: bool = False
    auth_attempts: int = 0
    cliente_nome: str | None = None
    score: int | None = None
    limite: float | None = None
    pending_increase: float | None = None

    @classmethod
    def from_estado(cls, estado: dict) -> DebugInfo:
        cliente = estado.get("cliente") or {}
        pendencia = estado.get("pending_increase") or {}
        return cls(
            current_agent=estado.get("current_agent", AGENTE_PADRAO),
            authenticated=bool(estado.get("authenticated")),
            auth_attempts=int(estado.get("auth_attempts", 0)),
            cliente_nome=cliente.get("nome"),
            score=cliente.get("score"),
            limite=cliente.get("limite_atual"),
            pending_increase=pendencia.get("novo_limite"),
        )


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    agent: str
    authenticated: bool
    finished: bool
    debug: DebugInfo

    @classmethod
    def from_estado(cls, session_id: str, reply: str, estado: dict) -> ChatResponse:
        debug = DebugInfo.from_estado(estado)
        return cls(
            session_id=session_id,
            reply=reply,
            agent=debug.current_agent,
            authenticated=debug.authenticated,
            finished=bool(estado.get("finished")),
            debug=debug,
        )

    @classmethod
    def de_erro(cls, session_id: str, mensagem: str) -> ChatResponse:
        return cls(
            session_id=session_id,
            reply=mensagem,
            agent=AGENTE_PADRAO,
            authenticated=False,
            finished=False,
            debug=DebugInfo(),
        )
