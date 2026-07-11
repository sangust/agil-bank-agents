"""Testes do serviço de crédito: faixas e solicitação de aumento."""
import csv
from datetime import UTC, datetime

from src.domain.enums import StatusPedido
from src.domain.models import SolicitacaoAumento
from src.services.credito_service import CreditoService


def _service(repos):
    return CreditoService(repos.faixa, repos.solicitacao, repos.cliente)


def test_faixa_para(repos):
    assert repos.faixa.faixa_para(250).limite_maximo == 1000.0
    assert repos.faixa.faixa_para(720).limite_maximo == 15000.0
    assert repos.faixa.faixa_para(900).limite_maximo == 50000.0


def test_consultar_limite(repos):
    cliente = repos.cliente.get_by_cpf("10433218100")
    resumo = _service(repos).consultar_limite(cliente)
    assert resumo.limite_atual == 5000.0
    assert resumo.score == 720
    assert resumo.limite_maximo == 15000.0


def test_aumento_aprovado_registra_e_atualiza_limite(repos):
    cliente = repos.cliente.get_by_cpf("10433218100")  # score 720 -> teto 15000, limite 5000
    res = _service(repos).solicitar_aumento(cliente, 10000)
    assert res.status == StatusPedido.APROVADO

    linhas = list(csv.DictReader(repos.paths.sol.open(encoding="utf-8")))
    assert len(linhas) == 1
    assert linhas[0]["status_pedido"] == "aprovado"
    assert linhas[0]["novo_limite_solicitado"] == "10000.00"
    assert linhas[0]["score_no_momento"] == "720"

    # aprovação persiste o novo limite (coerência de estado)
    assert res.cliente_atualizado.limite_atual == 10000.0
    assert repos.cliente.get_by_cpf("10433218100").limite_atual == 10000.0


def test_aumento_rejeitado_nao_altera_limite(repos):
    cliente = repos.cliente.get_by_cpf("02654235114")  # score 250 -> teto 1000
    res = _service(repos).solicitar_aumento(cliente, 5000)
    assert res.status == StatusPedido.REJEITADO
    assert res.limite_maximo == 1000.0
    assert repos.cliente.get_by_cpf("02654235114").limite_atual == 800.0  # inalterado


def test_aumento_invalido_menor(repos):
    cliente = repos.cliente.get_by_cpf("10433218100")
    res = _service(repos).solicitar_aumento(cliente, 3000)
    assert res.status == StatusPedido.INVALIDO
    assert not repos.paths.sol.exists()


def test_pedido_registrado_e_transiciona_para_final(repos):
    # Pedido registrado como pendente e transicionado para o status final na mesma linha.
    cliente = repos.cliente.get_by_cpf("02654235114")  # score 250 -> teto 1000
    _service(repos).solicitar_aumento(cliente, 5000)  # acima do teto -> rejeitado
    linhas = list(csv.DictReader(repos.paths.sol.open(encoding="utf-8")))
    assert len(linhas) == 1
    assert linhas[0]["status_pedido"] == "rejeitado"


def test_repo_atualizar_transiciona_de_pendente(repos):
    ts = datetime(2026, 7, 11, 12, 0, tzinfo=UTC)
    ped = SolicitacaoAumento(
        cpf_cliente="00000000000", data_hora_solicitacao=ts, limite_atual=100.0,
        novo_limite_solicitado=200.0, status_pedido=StatusPedido.PENDENTE,
    )
    repos.solicitacao.append(ped)
    inicial = list(csv.DictReader(repos.paths.sol.open(encoding="utf-8")))
    assert inicial[0]["status_pedido"] == "pendente"

    repos.solicitacao.atualizar(ped.model_copy(update={"status_pedido": StatusPedido.APROVADO}))
    final = list(csv.DictReader(repos.paths.sol.open(encoding="utf-8")))
    assert len(final) == 1  # mesma linha, sem duplicar
    assert final[0]["status_pedido"] == "aprovado"
