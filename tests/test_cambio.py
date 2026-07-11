"""Testes do serviço de câmbio (validação de código + API mockada)."""
import requests_mock

from src.services.cambio_service import CambioService, resolver_moeda

BASE = "https://economia.awesomeapi.com.br/json/last"


def test_resolver_moeda_normaliza_codigo_iso():
    assert resolver_moeda("usd") == "USD"
    assert resolver_moeda("Eur") == "EUR"
    assert resolver_moeda("CNY") == "CNY"


def test_resolver_moeda_invalida_retorna_none():
    # Nome por extenso ou lixo não é código ISO; o LLM deve enviar o código de 3 letras.
    # Nunca substituir silenciosamente por outra moeda.
    assert resolver_moeda("yuan") is None
    assert resolver_moeda("dracma") is None
    assert resolver_moeda("") is None


def test_cotacao_moeda_invalida_nao_chama_api():
    # Sem um código válido, retorna erro honesto e nem chega a bater na API.
    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, status_code=500)
        res = CambioService(BASE).consultar("dracma", "BRL")
    assert res.ok is False
    assert res.cotacao is None


def test_cotacao_yuan_consulta_par_correto():
    payload = {"CNYBRL": {"name": "Yuan Chinês/Real", "bid": "0.7560",
                          "create_date": "2026-07-10 17:33:37"}}
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/CNY-BRL", json=payload)
        res = CambioService(BASE).consultar("CNY", "BRL")
    assert res.ok is True
    assert res.cotacao.moeda == "CNY"
    assert res.cotacao.valor == 0.7560


def test_cotacao_sucesso():
    payload = {"USDBRL": {"name": "Dólar/Real", "bid": "5.4321",
                          "create_date": "2026-07-06 10:00:00"}}
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/USD-BRL", json=payload)
        res = CambioService(BASE).consultar("USD", "BRL")
    assert res.ok is True
    assert res.cotacao.valor == 5.4321
    assert res.cotacao.moeda == "USD"


def test_cotacao_falha_rede():
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/USD-BRL", status_code=500)
        res = CambioService(BASE).consultar("USD", "BRL")
    assert res.ok is False


def test_cotacao_par_ausente():
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/EUR-BRL", json={})
        res = CambioService(BASE).consultar("EUR", "BRL")
    assert res.ok is False
