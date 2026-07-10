"""Ferramentas e handlers compartilhados: encerramento, handoff e consulta ao RAG."""
from __future__ import annotations

from collections.abc import Callable

from langchain_core.tools import tool

from src.agents.prompts import INSTRUCAO_DESPEDIDA, INSTRUCAO_SEM_CONHECIMENTO
from src.core.utils import interno
from src.domain.models import Cliente
from src.orchestration.container import get_services

# handler(args, state) -> (texto_para_o_LLM, efeitos_no_estado)
Handler = Callable[[dict, dict], tuple[str, dict]]


def cliente_do_estado(state: dict) -> Cliente | None:
    """Reconstrói o modelo Cliente a partir do dict serializado no estado."""
    dados = state.get("cliente")
    return Cliente(**dados) if dados else None


@tool
def encerrar_atendimento() -> str:
    """Encerra o atendimento. Use quando o cliente se despedir, disser que não precisa de
    mais nada, pedir para finalizar, ou quando o assunto se esgotar."""
    return ""


@tool
def consultar_base_conhecimento(pergunta: str) -> str:
    """Consulta a base de conhecimento do banco (políticas, tarifas, crédito, câmbio,
    segurança) para responder dúvidas do cliente com informações oficiais."""
    return ""


def handler_encerrar(_args: dict, _state: dict) -> tuple[str, dict]:
    return interno(INSTRUCAO_DESPEDIDA), {"finished": True}


def handler_consultar_conhecimento(args: dict, _state: dict) -> tuple[str, dict]:
    resultado = get_services().knowledge.consultar(args.get("pergunta", ""))
    if not resultado.ok or not resultado.trechos:
        return interno(INSTRUCAO_SEM_CONHECIMENTO), {}

    fontes = ", ".join(resultado.fontes)
    return (
        interno(
            f"Trechos da base de conhecimento (fontes: {fontes}):\n{resultado.contexto}\n\n"
            "Responda ao cliente com suas próprias palavras, de forma clara e resumida, "
            "usando apenas o conteúdo acima. Não cite este texto literalmente."
        ),
        {},
    )


def make_handoff_handler(destino: str) -> Handler:
    """Cria um handler que transfere o atendimento para outro agente (invisível ao cliente)."""

    def handler(_args: dict, _state: dict) -> tuple[str, dict]:
        return (
            interno(
                f"Assumindo o atendimento no contexto de {destino}. Continue a conversa "
                "naturalmente, sem avisar o cliente sobre a transição."
            ),
            {"_goto": destino, "current_agent": destino},
        )

    return handler
