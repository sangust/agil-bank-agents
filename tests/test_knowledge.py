"""Testes do serviço de conhecimento (RAG) com degradação graciosa."""
from langchain_core.documents import Document

from src.services import knowledge_service
from src.services.knowledge_service import KnowledgeService

_DOC = Document(page_content="O Pix é gratuito e ilimitado.", metadata={"fonte": "tarifas"})


class _RetrieverFalso:
    def invoke(self, _pergunta):
        return [_DOC]


class _RetrieverQuebrado:
    def invoke(self, _pergunta):
        raise RuntimeError("timeout")


def test_rag_indisponivel_degrada(monkeypatch):
    monkeypatch.setattr(knowledge_service, "get_retriever", lambda: None)
    servico = KnowledgeService()
    assert servico.disponivel() is False

    resultado = servico.consultar("qual a tarifa do pix?")
    assert resultado.ok is False
    assert resultado.trechos == []
    assert resultado.contexto == ""


def test_rag_retorna_trechos():
    resultado = KnowledgeService(retriever=_RetrieverFalso()).consultar("tarifa do pix?")
    assert resultado.ok is True
    assert "Pix" in resultado.contexto
    assert resultado.fontes == ["tarifas"]


def test_rag_erro_no_retriever_degrada():
    resultado = KnowledgeService(retriever=_RetrieverQuebrado()).consultar("x")
    assert resultado.ok is False
