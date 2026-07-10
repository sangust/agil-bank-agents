"""Serviço de câmbio: cotação de moedas via AwesomeAPI."""
from __future__ import annotations

import requests

from src.core.config import get_settings
from src.core.constants import (
    MOEDA_DESTINO_PADRAO,
    MOEDA_PADRAO,
    MOEDAS,
    TAMANHO_CODIGO_MOEDA,
    TIMEOUT_CAMBIO_S,
)
from src.core.logging import get_logger
from src.domain.models import Cotacao
from src.domain.results import ResultadoCotacao

logger = get_logger(__name__)


def resolver_moeda(texto: str) -> str:
    """Traduz uma referência de moeda (nome em pt ou código ISO) para o código ISO."""
    if not texto:
        return MOEDA_PADRAO
    chave = texto.strip().lower()
    if chave in MOEDAS:
        return MOEDAS[chave]
    if len(chave) == TAMANHO_CODIGO_MOEDA and chave.isalpha():
        return chave.upper()
    return MOEDA_PADRAO


class CambioService:
    """Consulta cotações em tempo real, tratando falhas de rede de forma controlada."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or get_settings().awesomeapi_base_url

    def consultar(
        self, moeda: str = MOEDA_PADRAO, destino: str = MOEDA_DESTINO_PADRAO
    ) -> ResultadoCotacao:
        origem, alvo = resolver_moeda(moeda), resolver_moeda(destino)
        par = f"{origem}-{alvo}"

        try:
            resposta = requests.get(f"{self.base_url}/{par}", timeout=TIMEOUT_CAMBIO_S)
            resposta.raise_for_status()
            dados = resposta.json()
        except requests.RequestException as exc:
            logger.warning("Falha ao consultar cotação %s: %s", par, exc)
            return ResultadoCotacao(
                ok=False,
                mensagem="Não consegui consultar a cotação agora. Tente novamente em instantes.",
            )
        except ValueError as exc:
            logger.warning("Resposta inválida da API de câmbio para %s: %s", par, exc)
            return ResultadoCotacao(
                ok=False, mensagem="Recebi uma resposta inesperada do serviço de câmbio."
            )

        item = dados.get(f"{origem}{alvo}")
        if item is None:
            return ResultadoCotacao(
                ok=False, mensagem=f"Não encontrei cotação para o par {origem}/{alvo}."
            )

        cotacao = Cotacao(
            moeda=origem,
            destino=alvo,
            valor=float(item["bid"]),
            nome=item.get("name", par),
            atualizado_em=item.get("create_date", ""),
        )
        return ResultadoCotacao(
            ok=True,
            mensagem=f"1 {origem} = R$ {cotacao.valor:,.4f} {alvo}",
            cotacao=cotacao,
        )
