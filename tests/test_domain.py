"""Testes dos modelos e enums de domínio."""
from src.domain.enums import StatusPedido, TipoEmprego
from src.domain.models import Cliente


def test_tipo_emprego_normalizar():
    assert TipoEmprego.normalizar("Formal") == TipoEmprego.FORMAL
    assert TipoEmprego.normalizar("CLT") == TipoEmprego.FORMAL
    assert TipoEmprego.normalizar("autônomo") == TipoEmprego.AUTONOMO
    assert TipoEmprego.normalizar("autonomo") == TipoEmprego.AUTONOMO
    assert TipoEmprego.normalizar("xyz") == TipoEmprego.DESEMPREGADO


def test_tipo_emprego_sinonimos():
    # frases livres devem mapear para a categoria mais próxima
    assert TipoEmprego.normalizar("empresário") == TipoEmprego.AUTONOMO
    assert TipoEmprego.normalizar("CEO da Nubank") == TipoEmprego.AUTONOMO
    assert TipoEmprego.normalizar("PJ") == TipoEmprego.AUTONOMO
    assert TipoEmprego.normalizar("trabalho de carteira assinada") == TipoEmprego.FORMAL
    assert TipoEmprego.normalizar("estou sem emprego") == TipoEmprego.DESEMPREGADO


def test_status_pedido_valores():
    assert StatusPedido.APROVADO.value == "aprovado"
    assert StatusPedido.REJEITADO.value == "rejeitado"


def test_cliente_score_clamp():
    c = Cliente(cpf="1", nome="Fulano de Tal", data_nascimento="1990-01-01", score=1500)
    assert c.score == 1000


def test_cliente_propriedades():
    c = Cliente(cpf="1", nome="Ana Souza", data_nascimento="1990-05-14")
    assert c.primeiro_nome == "Ana"
    assert c.idade >= 30


def test_cliente_roundtrip_dump():
    c = Cliente(cpf="1", nome="Ana Souza", data_nascimento="1990-05-14",
                tipo_emprego="formal", score=720, limite_atual=5000)
    dump = c.model_dump(mode="json")
    c2 = Cliente(**dump)
    assert c2.score == 720
    assert c2.data_nascimento == c.data_nascimento
