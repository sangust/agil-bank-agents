"""Testes de autenticação (funções puras + AuthService)."""
from src.services.auth_service import (
    AuthService,
    normalizar_cpf,
    normalizar_data,
    validar_cpf,
)


def test_normalizar_cpf():
    assert normalizar_cpf("104.332.181-00") == "10433218100"
    assert normalizar_cpf(" 104 332 181 00 ") == "10433218100"


def test_validar_cpf_valido():
    assert validar_cpf("10433218100") is True
    assert validar_cpf("104.332.181-00") is True


def test_validar_cpf_invalido():
    assert validar_cpf("11111111111") is False
    assert validar_cpf("12345678900") is False
    assert validar_cpf("123") is False


def test_normalizar_data():
    assert normalizar_data("14/05/1990") == "1990-05-14"
    assert normalizar_data("1990-05-14") == "1990-05-14"
    assert normalizar_data("bla") is None


def test_normalizar_data_formatos_flexiveis():
    # o cliente digita de qualquer jeito — separadores variados
    assert normalizar_data("14 05 1990") == "1990-05-14"
    assert normalizar_data("14-05-1990") == "1990-05-14"
    assert normalizar_data("14.05.1990") == "1990-05-14"
    assert normalizar_data("28 09 2000") == "2000-09-28"
    # sem separador
    assert normalizar_data("14051990") == "1990-05-14"
    # mês por extenso
    assert normalizar_data("14 de maio de 1990") == "1990-05-14"
    assert normalizar_data("3 de setembro 2006") == "2006-09-03"
    assert normalizar_data("28 de março de 1978") == "1978-03-28"


def test_normalizar_data_invalida():
    assert normalizar_data("00/00/0000") is None
    assert normalizar_data("32/13/1990") is None
    assert normalizar_data("") is None


def test_autenticar_sucesso(repos):
    res = AuthService(repos.cliente).autenticar("104.332.181-00", "14/05/1990")
    assert res.ok is True
    assert res.cliente.nome == "Ana Souza"


def test_autenticar_data_divergente(repos):
    res = AuthService(repos.cliente).autenticar("10433218100", "01/01/2000")
    assert res.ok is False
    assert res.motivo == "data_divergente"


def test_autenticar_cpf_nao_encontrado(repos):
    res = AuthService(repos.cliente).autenticar("96001338914", "02/11/1985")
    assert res.ok is False
    assert res.motivo == "nao_encontrado"


def test_autenticar_cpf_invalido(repos):
    res = AuthService(repos.cliente).autenticar("11111111111", "14/05/1990")
    assert res.ok is False
    assert res.motivo == "cpf_invalido"


def test_autenticar_conta_bloqueada(repos):
    res = AuthService(repos.cliente).autenticar("81618495950", "08/09/1988")
    assert res.ok is False
    assert res.motivo == "conta_inativa"
