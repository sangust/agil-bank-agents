"""Repositório da política de crédito (faixas de score)."""
from __future__ import annotations

from pathlib import Path

from src.core.constants import SCORE_LIMITE_CSV
from src.domain.models import FaixaScore
from src.repositories.base import CsvRepository


class FaixaScoreRepository(CsvRepository):
    def __init__(self, path: Path | None = None):
        super().__init__(path or SCORE_LIMITE_CSV)

    def list_all(self) -> list[FaixaScore]:
        return [
            FaixaScore(
                score_min=int(r["score_min"]),
                score_max=int(r["score_max"]),
                limite_maximo=float(r["limite_maximo"]),
                taxa_juros_mensal=float(r.get("taxa_juros_mensal", 0) or 0),
            )
            for r in self.read_dicts()
        ]

    def faixa_para(self, score: int) -> FaixaScore | None:
        for faixa in self.list_all():
            if faixa.contem(score):
                return faixa
        return None
