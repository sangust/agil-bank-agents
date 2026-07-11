"""Agente de Câmbio: consulta de cotação de moedas em tempo real."""
from __future__ import annotations

from langchain_core.tools import tool

from src.agents.base import run_agent_turn
from src.agents.common import (
    Handler,
    consultar_base_conhecimento,
    encerrar_atendimento,
    handler_consultar_conhecimento,
    handler_encerrar,
    make_handoff_handler,
)
from src.agents.prompts import PROMPT_CAMBIO
from src.core.constants import MOEDA_DESTINO_PADRAO, MOEDA_PADRAO
from src.core.utils import interno
from src.orchestration.container import get_services

NOME = "cambio"


@tool("consultar_cotacao")
def consultar_cotacao_tool(moeda: str = "USD", destino: str = "BRL") -> str:
    """Consulta a cotação atual de uma moeda. Converta o nome dito pelo cliente para o
    código ISO 4217 de 3 letras (dólar=USD, real=BRL, euro=EUR, iene=JPY, yuan=CNY,
    libra=GBP...). destino: código da moeda de destino (padrão BRL)."""
    return ""


@tool
def transferir_para_credito() -> str:
    """Direciona o cliente para atendimento de crédito (limite/aumento)."""
    return ""


def _handler_consultar_cotacao(args: dict, _state: dict) -> tuple[str, dict]:
    resultado = get_services().cambio.consultar(
        args.get("moeda") or MOEDA_PADRAO,
        args.get("destino") or MOEDA_DESTINO_PADRAO,
    )
    if not resultado.ok or resultado.cotacao is None:
        return (
            resultado.mensagem + " " + interno(
                "Informe o cliente com clareza e ofereça tentar novamente."
            ),
            {},
        )

    atualizado_em = resultado.cotacao.atualizado_em or "agora"
    return f"Cotação atual: {resultado.mensagem} (atualizado em {atualizado_em}).", {}


TOOLS = [
    consultar_cotacao_tool,
    transferir_para_credito,
    consultar_base_conhecimento,
    encerrar_atendimento,
]

HANDLERS: dict[str, Handler] = {
    "consultar_cotacao": _handler_consultar_cotacao,
    "transferir_para_credito": make_handoff_handler("credito"),
    "consultar_base_conhecimento": handler_consultar_conhecimento,
    "encerrar_atendimento": handler_encerrar,
}


def node(state: dict) -> dict:
    return run_agent_turn(state, NOME, PROMPT_CAMBIO, TOOLS, HANDLERS)
