"""Repositório CSV base: leitura/escrita segura com lock e erros controlados."""
from __future__ import annotations

import csv
import threading
from pathlib import Path

from src.core.logging import get_logger

logger = get_logger(__name__)


class RepositoryError(Exception):
    """Erro esperado de acesso a dados (arquivo ausente, corrompido, I/O)."""


class CsvRepository:
    """Acesso genérico a um arquivo CSV, serializando escritas com lock."""

    def __init__(self, path: Path, header: list[str] | None = None):
        self.path = Path(path)
        self.header = header
        self._lock = threading.Lock()

    def read_dicts(self) -> list[dict[str, str]]:
        try:
            with self.path.open(newline="", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        except FileNotFoundError as exc:
            raise RepositoryError(f"Arquivo não encontrado: {self.path.name}") from exc
        except (OSError, csv.Error) as exc:
            raise RepositoryError(f"Falha ao ler {self.path.name}: {exc}") from exc

    def write_dicts(self, rows: list[dict], fieldnames: list[str]) -> None:
        with self._lock:
            try:
                with self.path.open("w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
            except OSError as exc:
                raise RepositoryError(f"Falha ao gravar {self.path.name}: {exc}") from exc

    def append_dict(self, row: dict, header: list[str]) -> None:
        with self._lock:
            novo = not self.path.exists()
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                with self.path.open("a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=header)
                    if novo:
                        writer.writeheader()
                    writer.writerow(row)
            except OSError as exc:
                raise RepositoryError(f"Falha ao gravar {self.path.name}: {exc}") from exc
