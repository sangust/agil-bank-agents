"""Construção do grafo LangGraph com roteamento e handoffs implícitos.

Fluxo de um turno:
- A entrada condicional envia o estado ao ``current_agent`` (padrão: triagem).
- Após cada nó de agente:
  - ``finished`` -> END (encerra o atendimento);
  - handoff (``_goto``) -> vai ao agente de destino no MESMO turno (invisível ao cliente);
  - caso contrário -> END do turno (aguarda a próxima mensagem do cliente).
"""
from __future__ import annotations

from functools import lru_cache

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.agents import cambio, credito, entrevista, triagem
from src.core.constants import AGENTE_PADRAO, AGENTES
from src.orchestration.state import AgentState

NOS = {
    "triagem": triagem.node,
    "credito": credito.node,
    "entrevista": entrevista.node,
    "cambio": cambio.node,
}


def _selecionar_agente(state: AgentState) -> str:
    return state.get("current_agent") or AGENTE_PADRAO


def _apos_agente(state: AgentState) -> str:
    if state.get("finished"):
        return END
    return state.get("_goto") or END


def _montar_grafo() -> StateGraph:
    builder = StateGraph(AgentState)
    for nome, no in NOS.items():
        builder.add_node(nome, no)

    rotas = {agente: agente for agente in AGENTES}
    builder.set_conditional_entry_point(_selecionar_agente, rotas)

    for agente in AGENTES:
        builder.add_conditional_edges(agente, _apos_agente, {**rotas, END: END})
    return builder


def compile_graph(checkpointer=None) -> CompiledStateGraph:
    """Compila o grafo, opcionalmente com um checkpointer (sessões persistentes)."""
    return _montar_grafo().compile(checkpointer=checkpointer)


@lru_cache(maxsize=1)
def build_graph() -> CompiledStateGraph:
    """Grafo compilado sem checkpointer (invocações in-process e testes)."""
    return compile_graph()
