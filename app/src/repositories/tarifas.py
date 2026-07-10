"""Repositório de tarifas (usado como contexto e pela base de conhecimento)."""
from __future__ import annotations

from pathlib import Path

from src.core.constants import TARIFAS_CSV
from src.repositories.base import CsvRepository


class TarifaRepository(CsvRepository):
    def __init__(self, path: Path | None = None):
        super().__init__(path or TARIFAS_CSV)

    def list_all(self) -> list[dict[str, str]]:
        return self.read_dicts()
