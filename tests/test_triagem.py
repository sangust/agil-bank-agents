"""Testes dos handlers da Triagem (validação imediata de CPF e tentativas de auth)."""
from src.agents import triagem


def test_verificar_cpf_valido():
    conteudo, efeitos = triagem._handler_verificar_cpf({"cpf": "104.332.181-00"}, {})
    assert "válido" in conteudo.lower()
    assert "data de nascimento" in conteudo.lower()
    assert efeitos == {}  # não consome tentativa


def test_verificar_cpf_invalido_nao_pede_data():
    for cpf in ("000000000000000", "123", "11111111111", "32423444"):
        conteudo, efeitos = triagem._handler_verificar_cpf({"cpf": cpf}, {})
        assert "inválido" in conteudo.lower(), cpf
        assert "não peça a data" in conteudo.lower(), cpf
        assert efeitos == {}  # CPF malformado não gasta tentativa de autenticação


def test_ferramenta_verificar_cpf_registrada():
    nomes = {t.name for t in triagem.TOOLS}
    assert "verificar_cpf" in nomes
    assert "verificar_cpf" in triagem.HANDLERS


def test_autenticacao_falha_incrementa_tentativas(services):
    # CPF válido mas fora da base -> falha controlada, consome 1 tentativa
    conteudo, efeitos = triagem._handler_autenticar(
        {"cpf": "090.088.411-85", "data_nascimento": "28 09 2000"}, {"auth_attempts": 0}
    )
    assert "não encontrei" in conteudo.lower()
    assert efeitos["auth_attempts"] == 1
    assert not efeitos.get("finished")


def test_terceira_falha_encerra(services):
    _conteudo, efeitos = triagem._handler_autenticar(
        {"cpf": "090.088.411-85", "data_nascimento": "28 09 2000"}, {"auth_attempts": 2}
    )
    assert efeitos["auth_attempts"] == 3
    assert efeitos["finished"] is True
