"""Utilitários pequenos e reutilizáveis, sem estado e sem dependência de negócio."""
from __future__ import annotations

import re

from src.core.constants import MARCADOR_INTERNO

_NAO_DIGITO = re.compile(r"\D")


def somente_digitos(texto: str | None) -> str:
    """Remove tudo que não for dígito. '000.000.000-00' -> '00000000000'."""
    return _NAO_DIGITO.sub("", texto or "")


def formatar_brl(valor: float) -> str:
    """Formata um valor monetário em reais: 5000 -> 'R$ 5.000,00'."""
    inteiro = f"{float(valor):,.2f}"
    # en-US (1,234.56) -> pt-BR (1.234,56)
    return "R$ " + inteiro.replace(",", "_").replace(".", ",").replace("_", ".")


def formatar_percentual(taxa: float) -> str:
    """Formata uma taxa decimal como percentual: 0.0499 -> '4,99%'."""
    return f"{taxa * 100:.2f}".replace(".", ",") + "%"


def interno(texto: str) -> str:
    """Marca um texto como instrução interna, dirigida ao modelo (nunca ao cliente)."""
    return f"{MARCADOR_INTERNO} {texto}"


def texto_da_mensagem(conteudo: str | list | None) -> str:
    """Normaliza o conteúdo de uma mensagem do LLM (string ou lista de blocos) para texto."""
    if isinstance(conteudo, str):
        return conteudo.strip()
    if isinstance(conteudo, list):
        partes = (
            bloco.get("text", "") if isinstance(bloco, dict) else str(bloco)
            for bloco in conteudo
        )
        return " ".join(parte for parte in partes if parte).strip()
    return ""
