"""Serviço da entrevista de crédito: recalcula e persiste o score."""
from __future__ import annotations

from src.domain.models import Cliente, DadosEntrevista, RegistroScore
from src.domain.results import ResultadoEntrevista
from src.repositories.base import RepositoryError
from src.repositories.clientes import ClienteRepository
from src.repositories.historico_score import HistoricoScoreRepository
from src.services.scoring import calcular_score


class EntrevistaService:
    """Recalcula o score a partir dos dados da entrevista e grava a trilha de auditoria."""

    def __init__(
        self,
        cliente_repo: ClienteRepository | None = None,
        historico_repo: HistoricoScoreRepository | None = None,
    ) -> None:
        self.clientes = cliente_repo or ClienteRepository()
        self.historico = historico_repo or HistoricoScoreRepository()

    def registrar(self, cliente: Cliente, dados: DadosEntrevista) -> ResultadoEntrevista:
        score_anterior = cliente.score
        novo_score = calcular_score(dados)

        try:
            self.clientes.update_score(cliente.cpf, novo_score)
            self.historico.append(
                RegistroScore(
                    cpf_cliente=cliente.cpf,
                    score_anterior=score_anterior,
                    score_novo=novo_score,
                )
            )
        except RepositoryError as exc:
            return ResultadoEntrevista(
                ok=False,
                mensagem=f"Não consegui salvar o novo score agora ({exc}). Tente mais tarde.",
            )

        return ResultadoEntrevista(
            ok=True,
            mensagem=f"Entrevista concluída. Score recalculado de {score_anterior} "
                     f"para {novo_score}.",
            novo_score=novo_score,
            cliente=cliente.model_copy(update={"score": novo_score}),
        )
