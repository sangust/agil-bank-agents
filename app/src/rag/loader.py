"""Carregamento e fatiamento dos documentos da base de conhecimento."""
from __future__ import annotations

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.constants import DOCS_DIR, RAG_CHUNK_OVERLAP, RAG_CHUNK_SIZE


def carregar_documentos() -> list[Document]:
    """Lê os markdown da base de conhecimento — um Document por arquivo."""
    return [
        Document(
            page_content=caminho.read_text(encoding="utf-8"),
            metadata={"fonte": caminho.stem},
        )
        for caminho in sorted(DOCS_DIR.glob("*.md"))
    ]


def dividir_em_chunks(documentos: list[Document]) -> list[Document]:
    """Quebra os documentos em trechos que casam melhor com a pergunta do cliente."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=RAG_CHUNK_SIZE, chunk_overlap=RAG_CHUNK_OVERLAP
    )
    return splitter.split_documents(documentos)
