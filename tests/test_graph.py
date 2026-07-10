"""Teste de orquestração do grafo (LLM falso + serviços temporários).

Cobre a fiação ponta a ponta sem chamar nenhuma API: autenticação, handoff implícito,
rejeição de aumento, entrevista, recálculo/persistência de score e reavaliação aprovada.
"""
import csv

import pytest
from langchain_core.messages import AIMessage, HumanMessage

import src.agents.base as base
from src.orchestration.graph import build_graph
from src.orchestration.state import estado_inicial


class SharedFakeLLM:
    def __init__(self, script):
        self.script = script
        self.i = 0

    def bind_tools(self, _tools):
        return self

    def invoke(self, _convo):
        msg = self.script[self.i]
        self.i += 1
        return msg


def _tool(name, args, tid):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": tid}])


@pytest.fixture
def fake_llm(monkeypatch):
    def instalar(script):
        fake = SharedFakeLLM(script)
        monkeypatch.setattr(base, "get_chat_model", lambda: fake)
        return fake

    return instalar


def _turno(grafo, estado, texto):
    estado["messages"].append(HumanMessage(content=texto))
    return grafo.invoke(estado)


def test_autenticacao_e_handoff(services, fake_llm):
    fake_llm([
        _tool("autenticar_cliente",
              {"cpf": "104.332.181-00", "data_nascimento": "14/05/1990"}, "a1"),
        _tool("transferir_para_credito", {}, "a2"),
        AIMessage(content="Autenticada, Ana! Como posso ajudar no seu crédito?"),
    ])
    grafo = build_graph()
    estado = _turno(grafo, estado_inicial(), "Olá, quero falar de crédito")

    assert estado["authenticated"] is True
    assert estado["current_agent"] == "credito"
    assert estado["cliente"]["nome"] == "Ana Souza"
    textos = [m.content for m in estado["messages"] if isinstance(m, AIMessage) and m.content]
    assert "Ana" in textos[-1]


def test_fluxo_rejeicao_entrevista_aprovacao(services, fake_llm):
    fake_llm([
        # A: autentica Diego (score 250) e vai para crédito
        _tool("autenticar_cliente",
              {"cpf": "026.542.351-14", "data_nascimento": "19/07/1995"}, "a1"),
        _tool("transferir_para_credito", {}, "a2"),
        AIMessage(content="Autenticado, Diego! Seu limite é R$ 800,00. O que deseja?"),
        # B: pede 5000 -> rejeitado
        _tool("solicitar_aumento", {"novo_limite": 5000}, "b1"),
        AIMessage(content="Rejeitado. Deseja uma entrevista para melhorar o score?"),
        # C: aceita -> entrevista -> volta -> reavalia -> aprovado
        _tool("transferir_para_entrevista", {}, "c1"),
        _tool("registrar_entrevista",
              {"renda_mensal": 5000, "tipo_emprego": "formal", "despesas_fixas": 1000,
               "num_dependentes": 0, "tem_dividas": False}, "c2"),
        _tool("solicitar_aumento", {"novo_limite": 5000}, "c3"),
        AIMessage(content="Boa notícia, Diego! Aumento para R$ 5.000,00 aprovado!"),
    ])
    grafo = build_graph()

    estado = _turno(grafo, estado_inicial(), "CPF 026.542.351-14, nasci 19/07/1995")
    assert estado["authenticated"] and estado["current_agent"] == "credito"

    estado = _turno(grafo, estado, "Quero aumentar para 5000")
    assert estado["pending_increase"]["novo_limite"] == 5000

    estado = _turno(grafo, estado, "Sim, quero a entrevista")
    assert int(estado["cliente"]["score"]) >= 601  # score subiu de 250

    # score persistido no CSV temporário
    assert services.entrevista.clientes.get_by_cpf("02654235114").score == int(
        estado["cliente"]["score"]
    )
    # duas solicitações: rejeitada e aprovada
    linhas = list(csv.DictReader(services.credito.solicitacoes.path.open(encoding="utf-8")))
    assert [r["status_pedido"] for r in linhas] == ["rejeitado", "aprovado"]
    textos = [m.content for m in estado["messages"] if isinstance(m, AIMessage) and m.content]
    assert "aprovado" in textos[-1].lower()
