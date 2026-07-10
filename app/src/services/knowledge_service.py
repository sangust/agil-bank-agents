"""Serviço de conhecimento (RAG): responde dúvidas com base nas políticas do banco."""
from __future__ import annotations

from langchain_core.vectorstores import VectorStoreRetriever

from src.core.logging import get_logger
from src.domain.results import ResultadoConsulta
from src.providers.vectorstore import get_retriever

logger = get_logger(__name__)


class KnowledgeService:
    """Recupera trechos relevantes da base de conhecimento (Chroma).

    Degrada com segurança: sem chave de embeddings ou em falha de rede, ``consultar``
    devolve ``ok=False`` em vez de lançar exceção.
    """

    def __init__(self, retriever: VectorStoreRetriever | None = None) -> None:
        self._retriever = retriever if retriever is not None else get_retriever()

    def disponivel(self) -> bool:
        return self._retriever is not None

    def consultar(self, pergunta: str) -> ResultadoConsulta:
        if self._retriever is None:
            return ResultadoConsulta(ok=False)

        try:
            documentos = self._retriever.invoke(pergunta)
        except Exception as exc:  # falha de rede/embeddings em runtime
            logger.error("Falha na consulta ao RAG: %s", exc)
            return ResultadoConsulta(ok=False)

        return ResultadoConsulta(
            ok=True,
            trechos=[doc.page_content.strip() for doc in documentos],
            fontes=list(dict.fromkeys(doc.metadata.get("fonte", "?") for doc in documentos)),
        )
