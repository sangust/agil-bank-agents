"""Testes da API FastAPI (TestClient) com LLM falso e serviços temporários.

Valida /health e um fluxo /api/chat com persistência de sessão entre requisições
(o estado de autenticação sobrevive graças ao checkpointer, sem chamar nenhuma API).
"""
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

import src.agents.base as base
from api.main import app


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


def test_health():
    r = TestClient(app).get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_chat_autentica_e_persiste_sessao(services, monkeypatch):
    fake = SharedFakeLLM([
        # Requisição 1: autentica Ana e transfere para crédito
        _tool("autenticar_cliente",
              {"cpf": "104.332.181-00", "data_nascimento": "14/05/1990"}, "t1"),
        _tool("transferir_para_credito", {}, "t2"),
        AIMessage(content="Autenticada, Ana! Como posso te ajudar no crédito?"),
        # Requisição 2 (mesma sessão): consulta de limite
        _tool("consultar_limite", {}, "t3"),
        AIMessage(content="Seu limite atual é R$ 5.000,00 e o score é 720."),
    ])
    monkeypatch.setattr(base, "get_chat_model", lambda: fake)
    client = TestClient(app)

    r1 = client.post("/api/chat", json={"message": "Oi, CPF 104.332.181-00, nasci 14/05/1990"})
    assert r1.status_code == 200
    d1 = r1.json()
    sid = d1["session_id"]
    assert d1["authenticated"] is True
    assert d1["agent"] == "credito"
    assert d1["debug"]["cliente_nome"] == "Ana Souza"

    # Requisição 2 reusa a sessão: NÃO re-autentica e já começa no crédito
    r2 = client.post("/api/chat", json={"session_id": sid, "message": "qual meu limite?"})
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["session_id"] == sid
    assert d2["authenticated"] is True  # estado persistido pelo checkpointer
    assert d2["agent"] == "credito"
    assert "5.000" in d2["reply"]


def test_chat_sem_session_id_cria_uma(services, monkeypatch):
    fake = SharedFakeLLM([AIMessage(content="Olá! Por favor, informe seu CPF.")])
    monkeypatch.setattr(base, "get_chat_model", lambda: fake)
    r = TestClient(app).post("/api/chat", json={"message": "oi"})
    assert r.status_code == 200
    assert r.json()["session_id"]  # id gerado pelo servidor
    assert r.json()["agent"] == "triagem"


def test_reply_nao_vaza_mensagem_do_turno_anterior(services, monkeypatch):
    """Se o turno atual não gera texto, não pode repetir a resposta do turno anterior."""
    fake = SharedFakeLLM([
        AIMessage(content="Olá! Por favor, informe seu CPF."),  # turno 1: texto
        AIMessage(content=""),  # turno 2: LLM não produz texto algum
    ])
    monkeypatch.setattr(base, "get_chat_model", lambda: fake)
    client = TestClient(app)

    r1 = client.post("/api/chat", json={"message": "oi"})
    sid = r1.json()["session_id"]
    assert r1.json()["reply"] == "Olá! Por favor, informe seu CPF."

    r2 = client.post("/api/chat", json={"session_id": sid, "message": "e agora?"})
    reply2 = r2.json()["reply"]
    assert reply2 != "Olá! Por favor, informe seu CPF."  # não repete o turno anterior
    assert "não consegui formular" in reply2  # fallback explícito
