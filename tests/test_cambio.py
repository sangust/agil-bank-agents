"""Testes do serviço de câmbio (parsing + API mockada)."""
import requests_mock

from src.services.cambio_service import CambioService, resolver_moeda

BASE = "https://economia.awesomeapi.com.br/json/last"


def test_resolver_moeda():
    assert resolver_moeda("dolar") == "USD"
    assert resolver_moeda("Euro") == "EUR"
    assert resolver_moeda("gbp") == "GBP"
    assert resolver_moeda("") == "USD"


def test_cotacao_sucesso():
    payload = {"USDBRL": {"name": "Dólar/Real", "bid": "5.4321",
                          "create_date": "2026-07-06 10:00:00"}}
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/USD-BRL", json=payload)
        res = CambioService(BASE).consultar("dolar", "real")
    assert res.ok is True
    assert res.cotacao.valor == 5.4321
    assert res.cotacao.moeda == "USD"


def test_cotacao_falha_rede():
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/USD-BRL", status_code=500)
        res = CambioService(BASE).consultar("dolar", "real")
    assert res.ok is False


def test_cotacao_par_ausente():
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/EUR-BRL", json={})
        res = CambioService(BASE).consultar("euro", "real")
    assert res.ok is False
