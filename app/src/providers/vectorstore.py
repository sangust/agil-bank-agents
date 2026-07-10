"""Provider do vector store do RAG: ChromaDB persistido em disco.

Chroma foi escolhido no lugar do FAISS por ser um banco vetorial de verdade (coleções
nomeadas, metadados, persistência gerenciada) mantendo-se embutido, sem servidor extra.
"""
from __future__ import annotations

from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever

from src.core.config import get_settings
from src.core.constants import CHROMA_COLLECTION, CHROMA_DIR
from src.core.logging import get_logger
from src.providers.embeddings import get_embeddings
from src.rag.loader import carregar_documentos, dividir_em_chunks

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_vectorstore() -> Chroma | None:
    """Coleção Chroma pronta para consulta, ou None se o RAG estiver indisponível.

    A coleção é criada e populada na primeira execução e reaproveitada depois.
    Falhas (sem chave de embeddings, rede) degradam para None em vez de quebrar.
    """
    embeddings = get_embeddings()
    if embeddings is None:
        return None

    try:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        store = Chroma(
            collection_name=CHROMA_COLLECTION,
            embedding_function=embeddings,
            persist_directory=str(CHROMA_DIR),
        )
        if store.get(limit=1)["ids"]:
            logger.info("Coleção Chroma '%s' já existente, reaproveitada.", CHROMA_COLLECTION)
            return store

        logger.info("Populando a coleção Chroma '%s'...", CHROMA_COLLECTION)
        chunks = dividir_em_chunks(carregar_documentos())
        if not chunks:
            return None
        store.add_documents(chunks)
        return store
    except Exception as exc:  # falha de embeddings/disco — degrada sem quebrar
        logger.error("Falha ao preparar o vector store Chroma: %s", exc)
        return None


def get_retriever() -> VectorStoreRetriever | None:
    """Retriever configurado com o top-k das settings, ou None se o RAG estiver off."""
    store = get_vectorstore()
    if store is None:
        return None
    return store.as_retriever(search_kwargs={"k": get_settings().rag_top_k})
