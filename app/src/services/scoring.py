"""Fórmula ponderada de score da entrevista (pesos do enunciado + clamp [0,1000])."""
from __future__ import annotations

from src.core.constants import (
    MAX_DEPENDENTES_TABELADO,
    PESO_DEPENDENTES,
    PESO_DIVIDAS,
    PESO_EMPREGO,
    PESO_RENDA,
    SCORE_MAXIMO,
    SCORE_MINIMO,
)
from src.domain.models import DadosEntrevista


def _peso_dependentes(quantidade: int) -> int:
    """3 ou mais dependentes usam o mesmo peso da tabela."""
    return PESO_DEPENDENTES[min(quantidade, MAX_DEPENDENTES_TABELADO)]


def calcular_score(dados: DadosEntrevista) -> int:
    """Retorna o novo score de crédito pela fórmula do enunciado, com clamp [0, 1000].

    score = (renda / (despesas + 1)) * peso_renda + peso_emprego + peso_dependentes
            + peso_dividas
    """
    contribuicao_renda = (dados.renda_mensal / (dados.despesas_fixas + 1)) * PESO_RENDA

    bruto = (
        contribuicao_renda
        + PESO_EMPREGO[dados.tipo_emprego]
        + _peso_dependentes(dados.num_dependentes)
        + PESO_DIVIDAS[dados.tem_dividas]
    )
    return int(max(SCORE_MINIMO, min(SCORE_MAXIMO, round(bruto))))
