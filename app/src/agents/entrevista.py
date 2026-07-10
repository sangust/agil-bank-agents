"""Agente de Entrevista de Crédito: coleta dados financeiros e recalcula o score."""
from __future__ import annotations

from langchain_core.tools import tool

from src.agents.base import run_agent_turn
from src.agents.common import (
    Handler,
    cliente_do_estado,
    encerrar_atendimento,
    handler_encerrar,
)
from src.agents.prompts import PROMPT_ENTREVISTA
from src.core.utils import formatar_brl, interno
from src.domain.enums import TipoEmprego
from src.domain.models import DadosEntrevista
from src.orchestration.container import get_services

NOME = "entrevista"
DESTINO_APOS_ENTREVISTA = "credito"


@tool("registrar_entrevista")
def registrar_entrevista_tool(
    renda_mensal: float,
    tipo_emprego: str,
    despesas_fixas: float,
    num_dependentes: int,
    tem_dividas: bool,
) -> str:
    """Registra os dados da entrevista e recalcula o score (0 a 1000).
    tipo_emprego: 'formal', 'autonomo' ou 'desempregado'. tem_dividas: true/false."""
    return ""


def _montar_dados(args: dict) -> DadosEntrevista:
    return DadosEntrevista(
        renda_mensal=float(args.get("renda_mensal", 0)),
        tipo_emprego=TipoEmprego.normalizar(str(args.get("tipo_emprego", ""))),
        despesas_fixas=float(args.get("despesas_fixas", 0)),
        num_dependentes=int(args.get("num_dependentes", 0)),
        tem_dividas=bool(args.get("tem_dividas", False)),
    )


def _instrucao_pendencia(state: dict) -> str:
    """Se havia um aumento rejeitado, manda o crédito reavaliá-lo com o novo score."""
    pendencia = state.get("pending_increase") or {}
    valor = pendencia.get("novo_limite")
    if not valor:
        return ""
    return (
        f" Havia uma solicitação de aumento pendente para {formatar_brl(valor)}: reavalie-a "
        "agora chamando `solicitar_aumento` com esse valor."
    )


def _handler_registrar(args: dict, state: dict) -> tuple[str, dict]:
    cliente = cliente_do_estado(state)
    if cliente is None:
        return interno("Cliente não autenticado; não é possível registrar a entrevista."), {}

    try:
        dados = _montar_dados(args)
    except (TypeError, ValueError):
        return interno(
            "Algum dado da entrevista veio inválido. Confirme os valores e tente de novo."
        ), {}

    resultado = get_services().entrevista.registrar(cliente, dados)
    if not resultado.ok or resultado.cliente is None:
        return resultado.mensagem, {}

    return (
        interno(
            f"{resultado.mensagem} Retornando para a análise de crédito."
            + _instrucao_pendencia(state)
        ),
        {
            "cliente": resultado.cliente.model_dump(mode="json"),
            "_goto": DESTINO_APOS_ENTREVISTA,
            "current_agent": DESTINO_APOS_ENTREVISTA,
        },
    )


TOOLS = [registrar_entrevista_tool, encerrar_atendimento]

HANDLERS: dict[str, Handler] = {
    "registrar_entrevista": _handler_registrar,
    "encerrar_atendimento": handler_encerrar,
}


def node(state: dict) -> dict:
    return run_agent_turn(state, NOME, PROMPT_ENTREVISTA, TOOLS, HANDLERS)
