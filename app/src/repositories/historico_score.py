"""Repositório do histórico de score dos clientes (trilha de auditoria)."""
from __future__ import annotations

from pathlib import Path

from src.core.constants import HEADER_HISTORICO_SCORE, HISTORICO_SCORE_CSV
from src.domain.models import RegistroScore
from src.repositories.base import CsvRepository


class HistoricoScoreRepository(CsvRepository):
    def __init__(self, path: Path | None = None) -> None:
        super().__init__(path or HISTORICO_SCORE_CSV)

    def append(self, registro: RegistroScore) -> None:
        self.append_dict(
            {
                "cpf_cliente": registro.cpf_cliente,
                "data_hora": registro.data_hora.isoformat(),
                "score_anterior": str(registro.score_anterior),
                "score_novo": str(registro.score_novo),
                "origem": registro.origem,
            },
            HEADER_HISTORICO_SCORE,
        )
