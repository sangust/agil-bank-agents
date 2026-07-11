"""Testes da fórmula de score da entrevista (clamp 0–1000)."""
from src.domain.enums import TipoEmprego
from src.domain.models import DadosEntrevista
from src.services.scoring import calcular_score


def _dados(renda, emprego, despesas, dep, dividas):
    return DadosEntrevista(
        renda_mensal=renda,
        tipo_emprego=TipoEmprego.normalizar(emprego),
        despesas_fixas=despesas,
        num_dependentes=dep,
        tem_dividas=dividas,
    )


def test_score_dentro_do_intervalo():
    assert 0 <= calcular_score(_dados(5000, "formal", 2000, 1, False)) <= 1000


def test_score_clampado_em_1000():
    # Fórmula literal do PDF (sem teto no termo de renda): renda alta satura no clamp de 1000.
    assert calcular_score(_dados(1_000_000, "formal", 0, 0, False)) == 1000


def test_score_formula_literal():
    # (3000/(1000+1))*30 + 300 (formal) + 100 (0 dep) + 100 (sem dívidas) = 589.9 -> 590
    assert calcular_score(_dados(3000, "formal", 1000, 0, False)) == 590


def test_score_minimo_nao_negativo():
    assert calcular_score(_dados(0, "desempregado", 5000, 4, True)) == 0


def test_dividas_reduzem_score():
    com = calcular_score(_dados(3000, "formal", 1000, 0, True))
    sem = calcular_score(_dados(3000, "formal", 1000, 0, False))
    assert sem > com


def test_dependentes_3_ou_mais_igual():
    assert calcular_score(_dados(3000, "formal", 1000, 3, False)) == calcular_score(
        _dados(3000, "formal", 1000, 5, False)
    )


def test_emprego_influencia():
    formal = calcular_score(_dados(3000, "formal", 1000, 0, False))
    autonomo = calcular_score(_dados(3000, "autonomo", 1000, 0, False))
    desempregado = calcular_score(_dados(3000, "desempregado", 1000, 0, False))
    assert formal > autonomo > desempregado
