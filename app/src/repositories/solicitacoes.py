"""Repositório de solicitações de aumento de limite."""
from __future__ import annotations

from pathlib import Path

from src.core.constants import HEADER_SOLICITACOES, SOLICITACOES_CSV
from src.domain.models import SolicitacaoAumento
from src.repositories.base import CsvRepository


class SolicitacaoRepository(CsvRepository):
    def __init__(self, path: Path | None = None) -> None:
        super().__init__(path or SOLICITACOES_CSV)

    def append(self, solicitacao: SolicitacaoAumento) -> None:
        self.append_dict(
            {
                "cpf_cliente": solicitacao.cpf_cliente,
                "data_hora_solicitacao": solicitacao.data_hora_solicitacao.isoformat(),
                "limite_atual": f"{solicitacao.limite_atual:.2f}",
                "novo_limite_solicitado": f"{solicitacao.novo_limite_solicitado:.2f}",
                "status_pedido": solicitacao.status_pedido.value,
                "score_no_momento": str(solicitacao.score_no_momento),
                "motivo": solicitacao.motivo,
            },
            HEADER_SOLICITACOES,
        )
