"""Agente de Triagem: recepção, autenticação e direcionamento."""
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
from src.agents.prompts import INSTRUCAO_NAO_AUTENTICADO, PROMPT_TRIAGEM
from src.core.constants import MAX_TENTATIVAS_AUTH
from src.core.utils import interno
from src.orchestration.container import get_services
from src.services.auth_service import validar_cpf

NOME = "triagem"


@tool
def verificar_cpf(cpf: str) -> str:
    """Verifica se o CPF tem formato e dígitos verificadores válidos.
    Chame IMEDIATAMENTE após o cliente informar o CPF, antes de pedir a data de nascimento."""
    return ""


@tool
def autenticar_cliente(cpf: str, data_nascimento: str) -> str:
    """Autentica o cliente conferindo CPF e data de nascimento na base.
    Passe o CPF (com ou sem pontuação) e a data de nascimento informados pelo cliente."""
    return ""


@tool
def transferir_para_credito() -> str:
    """Direciona o cliente para atendimento de crédito. Só após autenticação bem-sucedida."""
    return ""


@tool
def transferir_para_cambio() -> str:
    """Direciona o cliente para cotação de moedas. Só após autenticação bem-sucedida."""
    return ""


def _handler_verificar_cpf(args: dict, _state: dict) -> tuple[str, dict]:
    """Valida o CPF assim que informado. Não consome tentativa de autenticação."""
    if validar_cpf(args.get("cpf", "")):
        return interno("CPF válido. Agora peça a data de nascimento do cliente."), {}
    return (
        interno(
            "CPF inválido (número de dígitos ou dígitos verificadores incorretos). Com suas "
            "palavras, avise o cliente que o CPF informado não é válido e peça que digite "
            "novamente. Não peça a data de nascimento ainda."
        ),
        {},
    )


def _handler_autenticar(args: dict, state: dict) -> tuple[str, dict]:
    resultado = get_services().auth.autenticar(
        args.get("cpf", ""), args.get("data_nascimento", "")
    )

    if resultado.ok and resultado.cliente is not None:
        cliente = resultado.cliente
        return (
            interno(
                f"Autenticação bem-sucedida. Nome do cliente: {cliente.nome} (trate-o por "
                f"'{cliente.primeiro_nome}'). Escreva com suas palavras uma saudação curta "
                "usando o primeiro nome e pergunte em que pode ajudar."
            ),
            {
                "authenticated": True,
                "cpf": cliente.cpf,
                "cliente": cliente.model_dump(mode="json"),
                "auth_attempts": 0,
            },
        )

    tentativas = state.get("auth_attempts", 0) + 1
    if tentativas >= MAX_TENTATIVAS_AUTH:
        return (
            interno(
                f"Autenticação falhou (motivo: {resultado.mensagem}). Foi a última tentativa "
                "permitida. Com suas palavras, informe o cliente de maneira agradável que não "
                "foi possível autenticar e encerre o atendimento."
            ),
            {"auth_attempts": tentativas, "finished": True},
        )

    return (
        interno(
            f"Autenticação falhou. Motivo: {resultado.mensagem} Restam "
            f"{MAX_TENTATIVAS_AUTH - tentativas} tentativas. Com suas palavras, explique o "
            "motivo ao cliente e peça novamente o CPF e a data de nascimento."
        ),
        {"auth_attempts": tentativas},
    )


def _transferencia_autenticada(destino: str) -> Handler:
    """Só permite direcionar depois que o cliente estiver autenticado."""
    transferir = make_handoff_handler(destino)

    def handler(args: dict, state: dict) -> tuple[str, dict]:
        if not state.get("authenticated"):
            return interno(INSTRUCAO_NAO_AUTENTICADO), {}
        return transferir(args, state)

    return handler


TOOLS = [
    verificar_cpf,
    autenticar_cliente,
    transferir_para_credito,
    transferir_para_cambio,
    consultar_base_conhecimento,
    encerrar_atendimento,
]

HANDLERS: dict[str, Handler] = {
    "verificar_cpf": _handler_verificar_cpf,
    "autenticar_cliente": _handler_autenticar,
    "transferir_para_credito": _transferencia_autenticada("credito"),
    "transferir_para_cambio": _transferencia_autenticada("cambio"),
    "consultar_base_conhecimento": handler_consultar_conhecimento,
    "encerrar_atendimento": handler_encerrar,
}


def node(state: dict) -> dict:
    return run_agent_turn(state, NOME, PROMPT_TRIAGEM, TOOLS, HANDLERS)
