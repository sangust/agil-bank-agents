"""Testes dos repositórios (CSV -> modelos de domínio)."""
import csv

import pytest

from src.domain.enums import StatusPedido
from src.domain.models import RegistroScore, SolicitacaoAumento
from src.repositories.base import RepositoryError


def test_get_by_cpf(repos):
    assert repos.cliente.get_by_cpf("10433218100").nome == "Ana Souza"
    assert repos.cliente.get_by_cpf("00000000000") is None


def test_list_all(repos):
    assert len(repos.cliente.list_all()) == 3


def test_update_score_preserva_colunas(repos):
    repos.cliente.update_score("02654235114", 640)
    diego = repos.cliente.get_by_cpf("02654235114")
    assert diego.score == 640
    assert diego.profissao == "Vend"  # demais colunas intactas
    assert repos.cliente.get_by_cpf("10433218100").score == 720


def test_update_score_cpf_inexistente(repos):
    with pytest.raises(RepositoryError):
        repos.cliente.update_score("00000000000", 500)


def test_faixa_score_repo(repos):
    faixas = repos.faixa.list_all()
    assert len(faixas) == 4
    assert faixas[2].taxa_juros_mensal == 0.0499


def test_solicitacao_append_cria_header(repos):
    repos.solicitacao.append(
        SolicitacaoAumento(
            cpf_cliente="10433218100", limite_atual=5000, novo_limite_solicitado=8000,
            status_pedido=StatusPedido.APROVADO, score_no_momento=720, motivo="ok",
        )
    )
    linhas = list(csv.DictReader(repos.paths.sol.open(encoding="utf-8")))
    assert linhas[0]["status_pedido"] == "aprovado"
    assert linhas[0]["motivo"] == "ok"


def test_historico_append(repos):
    repos.historico.append(
        RegistroScore(cpf_cliente="02654235114", score_anterior=250, score_novo=650)
    )
    linhas = list(csv.DictReader(repos.paths.hist.open(encoding="utf-8")))
    assert linhas[0]["score_anterior"] == "250"
    assert linhas[0]["score_novo"] == "650"
    assert linhas[0]["origem"] == "entrevista"
