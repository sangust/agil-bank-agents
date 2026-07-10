"""Agente de Crédito: consulta de limite e solicitação de aumento."""
from __future__ import annotations

from langchain_core.tools import tool

from src.agents.base import run_agent_turn
from src.agents.common import (
    Handler,
    cliente_do_estado,
    consultar_base_conhecimento,
    encerrar_atendimento,
    handler_consultar_conhecimento,
    handler_encerrar,
    make_handoff_handler,
)
from src.agents.prompts import PROMPT_CREDITO
from src.core.utils import formatar_brl, interno
from src.domain.enums import StatusPedido
from src.orchestration.container import get_services

NOME = "credito"

MSG_NAO_AUTENTICADO = "Cliente não autenticado; a operação de crédito não é permitida."


@tool("consultar_limite")
def consultar_limite_tool() -> str:
    """Consulta o limite de crédito atual e o score do cliente autenticado."""
    return ""


@tool("solicitar_aumento")
def solicitar_aumento_tool(novo_limite: float) -> str:
    """Solicita aumento do limite de crédito para o valor informado (em reais). Registra o
    pedido e avalia contra a política de score. Retorna aprovado ou rejeitado."""
    return ""


@tool
def transferir_para_entrevista() -> str:
    """Direciona para uma entrevista financeira que recalcula o score. Use quando o cliente
    aceitar a entrevista após um aumento rejeitado."""
    return ""


@tool
def transferir_para_cambio() -> str:
    """Direciona o cliente para cotação de moedas (câmbio)."""
    return ""


def _handler_consultar_limite(_args: dict, state: dict) -> tuple[str, dict]:
    cliente = cliente_do_estado(state)
    if cliente is None:
        return interno(MSG_NAO_AUTENTICADO), {}

    resumo = get_services().credito.consultar_limite(cliente)
    texto = (
        f"Limite atual: {formatar_brl(resumo.limite_atual)}. Score atual: {resumo.score}."
    )
    if resumo.limite_maximo is not None:
        texto += f" Teto para o score: {formatar_brl(resumo.limite_maximo)}."
    return texto, {}


def _handler_solicitar_aumento(args: dict, state: dict) -> tuple[str, dict]:
    cliente = cliente_do_estado(state)
    if cliente is None:
        return interno(MSG_NAO_AUTENTICADO), {}

    try:
        novo_limite = float(args["novo_limite"])
    except (KeyError, TypeError, ValueError):
        return interno("Valor de novo limite inválido. Peça ao cliente um número em reais."), {}

    resultado = get_services().credito.solicitar_aumento(cliente, novo_limite)

    if resultado.status is StatusPedido.REJEITADO:
        return (
            resultado.mensagem + " " + interno(
                "Comunique o resultado com suas palavras e ofereça, com gentileza, uma "
                "entrevista financeira para tentar melhorar o score."
            ),
            {
                "pending_increase": {
                    "novo_limite": novo_limite,
                    "limite_maximo": resultado.limite_maximo,
                }
            },
        )

    if resultado.status is StatusPedido.APROVADO:
        efeitos: dict = {"pending_increase": None}
        if resultado.cliente_atualizado is not None:
            efeitos["cliente"] = resultado.cliente_atualizado.model_dump(mode="json")
        return resultado.mensagem, efeitos

    return resultado.mensagem, {}


TOOLS = [
    consultar_limite_tool,
    solicitar_aumento_tool,
    transferir_para_entrevista,
    transferir_para_cambio,
    consultar_base_conhecimento,
    encerrar_atendimento,
]

HANDLERS: dict[str, Handler] = {
    "consultar_limite": _handler_consultar_limite,
    "solicitar_aumento": _handler_solicitar_aumento,
    "transferir_para_entrevista": make_handoff_handler("entrevista"),
    "transferir_para_cambio": make_handoff_handler("cambio"),
    "consultar_base_conhecimento": handler_consultar_conhecimento,
    "encerrar_atendimento": handler_encerrar,
}


def node(state: dict) -> dict:
    return run_agent_turn(state, NOME, PROMPT_CREDITO, TOOLS, HANDLERS)
