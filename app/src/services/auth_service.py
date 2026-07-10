"""Serviço de autenticação: normalização/validação de CPF e conferência na base."""
from __future__ import annotations

import re
from datetime import datetime

from src.core.constants import (
    FORMATO_ISO,
    FORMATOS_DATA,
    FORMATOS_DATA_SEM_SEPARADOR,
    MESES,
    TAMANHO_CPF,
    TAMANHO_DATA_SEM_SEPARADOR,
)
from src.core.utils import somente_digitos
from src.domain.enums import StatusConta
from src.domain.results import AuthResult
from src.repositories.base import RepositoryError
from src.repositories.clientes import ClienteRepository

_PADRAO_MES_EXTENSO = re.compile(rf"(\d{{1,2}})\D+({'|'.join(MESES)})\D+(\d{{4}})")
_SEPARADORES = re.compile(r"\D+")


def normalizar_cpf(cpf_raw: str) -> str:
    """Remove tudo que não for dígito."""
    return somente_digitos(cpf_raw)


def validar_cpf(cpf_raw: str) -> bool:
    """Valida os dígitos verificadores do CPF (aceita com/sem máscara)."""
    cpf = normalizar_cpf(cpf_raw)
    if len(cpf) != TAMANHO_CPF or cpf == cpf[0] * TAMANHO_CPF:
        return False
    for posicao in (9, 10):
        soma = sum(int(cpf[i]) * ((posicao + 1) - i) for i in range(posicao))
        digito = (soma * 10) % 11
        if (0 if digito == 10 else digito) != int(cpf[posicao]):
            return False
    return True


def _data_por_extenso(texto: str) -> str | None:
    """Interpreta datas com mês por extenso: '28 de setembro de 2000'."""
    achado = _PADRAO_MES_EXTENSO.search(texto)
    if not achado:
        return None
    dia, mes, ano = int(achado.group(1)), MESES[achado.group(2)], int(achado.group(3))
    try:
        return datetime(ano, mes, dia).strftime(FORMATO_ISO)
    except ValueError:
        return None


def _parse(texto: str, formatos: tuple[str, ...]) -> str | None:
    for formato in formatos:
        try:
            return datetime.strptime(texto, formato).strftime(FORMATO_ISO)
        except ValueError:
            continue
    return None


def normalizar_data(data_raw: str) -> str | None:
    """Normaliza data para ISO (YYYY-MM-DD), aceitando formatos livres.

    Exemplos: '14/05/1990', '14-05-1990', '14 05 1990', '14.05.1990', '1990-05-14',
    '14051990' e '14 de maio de 1990'.
    """
    if not data_raw:
        return None
    texto = data_raw.strip().lower()

    por_extenso = _data_por_extenso(texto)
    if por_extenso is not None:
        return por_extenso

    # Dia-primeiro (padrão BR) antes de ano-primeiro, para não confundir "28/09/2000".
    unificado = _SEPARADORES.sub("/", texto).strip("/")
    if (iso := _parse(unificado, FORMATOS_DATA)) is not None:
        return iso

    digitos = somente_digitos(texto)
    if len(digitos) == TAMANHO_DATA_SEM_SEPARADOR:
        return _parse(digitos, FORMATOS_DATA_SEM_SEPARADOR)
    return None


class AuthService:
    """Autentica o cliente contra a base, com mensagens de falha específicas."""

    def __init__(self, cliente_repo: ClienteRepository | None = None) -> None:
        self.clientes = cliente_repo or ClienteRepository()

    def autenticar(self, cpf_raw: str, data_nascimento_raw: str) -> AuthResult:
        if not validar_cpf(cpf_raw):
            return AuthResult(
                ok=False, motivo="cpf_invalido",
                mensagem="O CPF informado é inválido. Confira os números e tente novamente.",
            )

        data_iso = normalizar_data(data_nascimento_raw)
        if data_iso is None:
            return AuthResult(
                ok=False, motivo="data_invalida",
                mensagem="A data de nascimento não está em formato válido (use DD/MM/AAAA).",
            )

        try:
            cliente = self.clientes.get_by_cpf(normalizar_cpf(cpf_raw))
        except RepositoryError:
            return AuthResult(
                ok=False, motivo="erro_base",
                mensagem="Não consegui acessar a base de clientes agora. Tente em instantes.",
            )

        if cliente is None:
            return AuthResult(
                ok=False, motivo="nao_encontrado",
                mensagem="Não encontrei um cadastro com esse CPF.",
            )
        if cliente.data_nascimento.isoformat() != data_iso:
            return AuthResult(
                ok=False, motivo="data_divergente",
                mensagem="A data de nascimento não confere com o cadastro.",
            )
        if cliente.status_conta is not StatusConta.ATIVA:
            return AuthResult(
                ok=False, motivo="conta_inativa", cliente=cliente,
                mensagem="Sua conta não está ativa. Procure um de nossos canais de suporte.",
            )

        return AuthResult(
            ok=True, motivo="autenticado", cliente=cliente,
            mensagem=f"Autenticação bem-sucedida. Bem-vindo(a), {cliente.primeiro_nome}!",
        )
