"""Testes dos utilitários — foco no parsing de valores informados pelo cliente."""
import pytest

from src.core.utils import parse_valor


def test_parse_valor_numeros_simples():
    assert parse_valor("10000") == 10000.0
    assert parse_valor(10000) == 10000.0
    assert parse_valor("1250,50") == 1250.5


def test_parse_valor_abreviacoes():
    # "10k", "10 mil" — o modelo costuma repassar o que o cliente digitou.
    assert parse_valor("10k") == 10000.0
    assert parse_valor("10 mil") == 10000.0
    assert parse_valor("2mil") == 2000.0


def test_parse_valor_formatado_ptbr():
    assert parse_valor("R$ 10.000,00") == 10000.0
    assert parse_valor("1.250") == 1250.0
    assert parse_valor("1.234.567,89") == 1234567.89


def test_parse_valor_invalido_levanta():
    with pytest.raises(ValueError):
        parse_valor("não sei")
    with pytest.raises(ValueError):
        parse_valor("")
