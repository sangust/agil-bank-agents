"""Sessões de conversa no servidor.

O estado do grafo é persistido por ``session_id`` num checkpointer do LangGraph
(Redis quando configurado; senão memória), mapeado por ``thread_id``. O cliente só envia
``{session_id, mensagem}``; o servidor mantém histórico e estado entre as requisições.
"""
from __future__ import annotations

import uuid
from functools import lru_cache

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph

from src.core.utils import texto_da_mensagem
from src.orchestration.graph import compile_graph
from src.orchestration.state import estado_inicial
from src.providers.checkpointer import get_checkpointer


@lru_cache(maxsize=1)
def get_graph() -> CompiledStateGraph:
    """Grafo compilado com o checkpointer de sessões (uma instância por processo)."""
    return compile_graph(get_checkpointer())


def novo_session_id() -> str:
    return uuid.uuid4().hex


def _config(session_id: str) -> dict:
    return {"configurable": {"thread_id": session_id}}


def _sessao_nova(session_id: str) -> bool:
    """Uma sessão é nova quando ainda não há checkpoint gravado para o thread."""
    return not get_graph().get_state(_config(session_id)).values


def chat(session_id: str, message: str) -> dict:
    """Processa uma mensagem na sessão e devolve o estado final do grafo."""
    mensagem = HumanMessage(content=message)
    entrada = (
        {**estado_inicial(), "messages": [mensagem]}
        if _sessao_nova(session_id)
        else {"messages": [mensagem]}
    )
    return get_graph().invoke(entrada, config=_config(session_id))


def ultima_resposta(estado: dict) -> str:
    """Texto do assistente gerado NESTE turno (após a última fala do cliente).

    Sem o recorte por turno, um turno sem texto faria o cliente ver de novo a mensagem
    do turno anterior.
    """
    mensagens = estado.get("messages", [])
    inicio = next(
        (i + 1 for i in range(len(mensagens) - 1, -1, -1)
         if isinstance(mensagens[i], HumanMessage)),
        0,
    )
    for mensagem in reversed(mensagens[inicio:]):
        if isinstance(mensagem, AIMessage) and (texto := texto_da_mensagem(mensagem.content)):
            return texto
    return ""
