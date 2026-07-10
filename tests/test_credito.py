"""Testes do serviço de crédito: faixas e solicitação de aumento."""
import csv

from src.domain.enums import StatusPedido
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
