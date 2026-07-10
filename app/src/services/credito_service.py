"""Serviço de crédito: consulta de limite e solicitação/avaliação de aumento."""
from __future__ import annotations

from src.core.utils import formatar_brl, formatar_percentual
from src.domain.enums import StatusPedido
from src.domain.models import Cliente, FaixaScore, SolicitacaoAumento
from src.domain.results import ResultadoAumento, ResumoLimite
from src.repositories.base import RepositoryError
from src.repositories.clientes import ClienteRepository
from src.repositories.score_limite import FaixaScoreRepository
from src.repositories.solicitacoes import SolicitacaoRepository


class CreditoService:
    """Regras de limite: consulta, avaliação por faixa de score e registro do pedido."""

    def __init__(
        self,
        faixa_repo: FaixaScoreRepository | None = None,
        solicitacao_repo: SolicitacaoRepository | None = None,
        cliente_repo: ClienteRepository | None = None,
    ) -> None:
        self.faixas = faixa_repo or FaixaScoreRepository()
        self.solicitacoes = solicitacao_repo or SolicitacaoRepository()
        self.clientes = cliente_repo or ClienteRepository()

    def _faixa_do_cliente(self, cliente: Cliente) -> FaixaScore | None:
        try:
            return self.faixas.faixa_para(cliente.score)
        except RepositoryError:
            return None

    def consultar_limite(self, cliente: Cliente) -> ResumoLimite:
        faixa = self._faixa_do_cliente(cliente)
        return ResumoLimite(
            limite_atual=cliente.limite_atual,
            score=cliente.score,
            limite_maximo=faixa.limite_maximo if faixa else None,
            taxa_juros_mensal=faixa.taxa_juros_mensal if faixa else None,
        )

    def solicitar_aumento(self, cliente: Cliente, novo_limite: float) -> ResultadoAumento:
        if novo_limite <= cliente.limite_atual:
            return ResultadoAumento(
                status=StatusPedido.INVALIDO,
                mensagem=(
                    f"O novo limite ({formatar_brl(novo_limite)}) precisa ser maior que o "
                    f"atual ({formatar_brl(cliente.limite_atual)})."
                ),
            )

        faixa = self._faixa_do_cliente(cliente)
        if faixa is None:
            return ResultadoAumento(
                status=StatusPedido.ERRO,
                mensagem="Não consegui consultar a política de crédito agora. Tente mais tarde.",
            )

        aprovado = novo_limite <= faixa.limite_maximo
        status = StatusPedido.APROVADO if aprovado else StatusPedido.REJEITADO
        solicitacao = SolicitacaoAumento(
            cpf_cliente=cliente.cpf,
            limite_atual=cliente.limite_atual,
            novo_limite_solicitado=novo_limite,
            status_pedido=status,
            score_no_momento=cliente.score,
            motivo=(
                "dentro do limite da faixa" if aprovado
                else f"acima do teto de {formatar_brl(faixa.limite_maximo)} "
                     f"para o score {cliente.score}"
            ),
        )

        try:
            self.solicitacoes.append(solicitacao)
        except RepositoryError:
            return ResultadoAumento(
                status=StatusPedido.ERRO,
                mensagem="Não consegui registrar sua solicitação agora. Tente em instantes.",
            )

        if not aprovado:
            return ResultadoAumento(
                status=status,
                mensagem=(
                    f"Sua solicitação de {formatar_brl(novo_limite)} foi REJEITADA. O limite "
                    f"máximo para seu score atual é {formatar_brl(faixa.limite_maximo)}."
                ),
                limite_maximo=faixa.limite_maximo,
                taxa_juros_mensal=faixa.taxa_juros_mensal,
                solicitacao=solicitacao,
                cliente_atualizado=cliente,
            )

        return ResultadoAumento(
            status=status,
            mensagem=(
                f"Boa notícia! Seu aumento para {formatar_brl(novo_limite)} foi APROVADO "
                f"(teto para seu score: {formatar_brl(faixa.limite_maximo)}, taxa "
                f"{formatar_percentual(faixa.taxa_juros_mensal)} a.m.)."
            ),
            limite_maximo=faixa.limite_maximo,
            taxa_juros_mensal=faixa.taxa_juros_mensal,
            solicitacao=solicitacao,
            cliente_atualizado=self._persistir_novo_limite(cliente, novo_limite),
        )

    def _persistir_novo_limite(self, cliente: Cliente, novo_limite: float) -> Cliente:
        """Aprovação atualiza o limite; falha ao gravar não invalida o pedido já registrado."""
        try:
            self.clientes.update_limite(cliente.cpf, novo_limite)
        except RepositoryError:
            return cliente
        return cliente.model_copy(update={"limite_atual": novo_limite})
