"""Estado compartilhado do grafo de atendimento."""
from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages

from src.core.constants import AGENTE_PADRAO


class AgentState(TypedDict, total=False):
    """Estado único que trafega entre todos os agentes.

    Para o cliente há um só atendente; ``current_agent`` é interno, assim como ``_goto``
    (sinal de handoff dentro de um mesmo turno).
    """

    messages: Annotated[list, add_messages]
    authenticated: bool
    cpf: str
    cliente: dict | None
    current_agent: str
    auth_attempts: int
    pending_increase: dict | None
    finished: bool
    _goto: str | None


def estado_inicial() -> AgentState:
    """Estado zerado no início de um atendimento."""
    return AgentState(
        messages=[],
        authenticated=False,
        cpf="",
        cliente=None,
        current_agent=AGENTE_PADRAO,
        auth_attempts=0,
        pending_increase=None,
        finished=False,
        _goto=None,
    )
