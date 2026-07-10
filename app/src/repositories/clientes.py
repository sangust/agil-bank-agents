"""Repositório de clientes."""
from __future__ import annotations

from pathlib import Path

from src.core.constants import CLIENTES_CSV
from src.core.logging import get_logger
from src.domain.models import Cliente
from src.repositories.base import CsvRepository, RepositoryError

logger = get_logger(__name__)


class ClienteRepository(CsvRepository):
    def __init__(self, path: Path | None = None):
        super().__init__(path or CLIENTES_CSV)

    def _to_model(self, row: dict) -> Cliente:
        return Cliente(
            cpf=row["cpf"],
            nome=row["nome"],
            data_nascimento=row["data_nascimento"],
            email=row.get("email", ""),
            telefone=row.get("telefone", ""),
            profissao=row.get("profissao", ""),
            tipo_emprego=row.get("tipo_emprego", "formal"),
            renda_declarada=float(row.get("renda_declarada", 0) or 0),
            limite_atual=float(row.get("limite_atual", 0) or 0),
            score=int(row.get("score", 0) or 0),
            status_conta=row.get("status_conta", "ativa"),
            data_abertura=row.get("data_abertura") or None,
        )

    def list_all(self) -> list[Cliente]:
        return [self._to_model(r) for r in self.read_dicts()]

    def get_by_cpf(self, cpf: str) -> Cliente | None:
        for row in self.read_dicts():
            if row["cpf"] == cpf:
                return self._to_model(row)
        return None

    def update_score(self, cpf: str, novo_score: int) -> None:
        """Atualiza o score preservando as demais colunas."""
        rows = self.read_dicts()
        if not rows:
            raise RepositoryError("Base de clientes vazia.")
        encontrado = False
        for row in rows:
            if row["cpf"] == cpf:
                row["score"] = str(int(novo_score))
                encontrado = True
                break
        if not encontrado:
            raise RepositoryError(f"CPF {cpf} não encontrado para atualização de score.")
        self.write_dicts(rows, list(rows[0].keys()))
        logger.info("Score do CPF %s atualizado para %s", cpf, novo_score)

    def update_limite(self, cpf: str, novo_limite: float) -> None:
        rows = self.read_dicts()
        for row in rows:
            if row["cpf"] == cpf:
                row["limite_atual"] = f"{float(novo_limite):.2f}"
                self.write_dicts(rows, list(rows[0].keys()))
                logger.info("Limite do CPF %s atualizado para %.2f", cpf, novo_limite)
                return
        raise RepositoryError(f"CPF {cpf} não encontrado para atualização de limite.")
