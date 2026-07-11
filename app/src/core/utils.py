"""Utilitários pequenos e reutilizáveis, sem estado e sem dependência de negócio."""
from __future__ import annotations

import re

from src.core.constants import MARCADOR_INTERNO

_NAO_DIGITO = re.compile(r"\D")
_SUFIXO_ALFA = re.compile(r"([a-zç]+)\s*$")
_MULTIPLICADORES = {"k": 1_000, "mil": 1_000, "m": 1_000_000, "mi": 1_000_000, "milhao": 1_000_000}


def somente_digitos(texto: str | None) -> str:
    """Remove tudo que não for dígito. '000.000.000-00' -> '00000000000'."""
    return _NAO_DIGITO.sub("", texto or "")


def parse_valor(entrada: str | float | int) -> float:
    """Converte uma quantia informada pelo cliente em float (reais).

    Aceita número puro, '10k', '10 mil', 'R$ 10.000,00', '1.250', '1250,50'.
    Levanta ValueError se não houver número reconhecível.
    """
    if isinstance(entrada, (int, float)):
        return float(entrada)

    texto = str(entrada).strip().lower()
    for lixo in ("r$", "reais", "real"):
        texto = texto.replace(lixo, "")
    texto = texto.strip()

    multiplicador = 1
    sufixo = _SUFIXO_ALFA.search(texto)
    if sufixo and sufixo.group(1) in _MULTIPLICADORES:
        multiplicador = _MULTIPLICADORES[sufixo.group(1)]
        texto = texto[: sufixo.start()].strip()

    texto = texto.replace(" ", "")
    if "," in texto:  # pt-BR: vírgula é decimal, pontos são milhar
        texto = texto.replace(".", "").replace(",", ".")
    else:
        partes = texto.split(".")
        # '10.000' / '1.234.567' são milhar; '10.5' é decimal
        if len(partes) > 2 or (len(partes) == 2 and len(partes[1]) == 3):
            texto = "".join(partes)

    return float(texto) * multiplicador


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
