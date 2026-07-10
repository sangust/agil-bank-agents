"""Fixtures de teste: repositórios CSV temporários e container de serviços isolado."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.orchestration.container import Services, set_services
from src.repositories.clientes import ClienteRepository
from src.repositories.historico_score import HistoricoScoreRepository
from src.repositories.score_limite import FaixaScoreRepository
from src.repositories.solicitacoes import SolicitacaoRepository
from src.services import knowledge_service
from src.services.auth_service import AuthService
from src.services.cambio_service import CambioService
from src.services.credito_service import CreditoService
from src.services.entrevista_service import EntrevistaService
from src.services.knowledge_service import KnowledgeService

CLIENTES = (
    "cpf,nome,data_nascimento,email,telefone,profissao,tipo_emprego,renda_declarada,"
    "limite_atual,score,status_conta,data_abertura\n"
    "10433218100,Ana Souza,1990-05-14,ana@e.com,(11) 90000-0001,Eng,formal,9500,5000.00,720,ativa,2018-03-10\n"
    "02654235114,Diego Rocha,1995-07-19,diego@e.com,(41) 90000-0002,Vend,autonomo,2800,800.00,250,ativa,2022-11-30\n"
    "81618495950,Felipe Nunes,1988-09-08,felipe@e.com,(61) 90000-0003,Ana,formal,11000,10000.00,780,bloqueada,2019-06-18\n"
)

FAIXAS = (
    "score_min,score_max,limite_maximo,taxa_juros_mensal\n"
    "0,300,1000.00,0.0899\n"
    "301,600,5000.00,0.0699\n"
    "601,800,15000.00,0.0499\n"
    "801,1000,50000.00,0.0299\n"
)


@pytest.fixture
def repos(tmp_path):
    """Cria repositórios apontando para CSVs temporários."""
    clientes = tmp_path / "clientes.csv"
    faixas = tmp_path / "score_limite.csv"
    sol = tmp_path / "solicitacoes.csv"
    hist = tmp_path / "historico.csv"
    clientes.write_text(CLIENTES, encoding="utf-8")
    faixas.write_text(FAIXAS, encoding="utf-8")

    return SimpleNamespace(
        paths=SimpleNamespace(clientes=clientes, faixas=faixas, sol=sol, hist=hist),
        cliente=ClienteRepository(clientes),
        faixa=FaixaScoreRepository(faixas),
        solicitacao=SolicitacaoRepository(sol),
        historico=HistoricoScoreRepository(hist),
    )


@pytest.fixture
def services(repos, monkeypatch):
    """Container de serviços com repos temporários e RAG desligado (sem chamar embeddings)."""
    monkeypatch.setattr(knowledge_service, "get_retriever", lambda: None)
    svc = Services(
        auth=AuthService(repos.cliente),
        credito=CreditoService(repos.faixa, repos.solicitacao, repos.cliente),
        entrevista=EntrevistaService(repos.cliente, repos.historico),
        cambio=CambioService(),
        knowledge=KnowledgeService(),
    )
    set_services(svc)
    yield svc
    set_services(None)
