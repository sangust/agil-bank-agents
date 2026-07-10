"""Modelos de resultado retornados pelos serviços (Pydantic).

Substituem os antigos ``@dataclass``: validam os dados e são serializáveis.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from src.domain.enums import StatusPedido
from src.domain.models import Cliente, Cotacao, SolicitacaoAumento


class AuthResult(BaseModel):
    """Resultado de uma tentativa de autenticação."""

    ok: bool
    motivo: str
    mensagem: str
    cliente: Cliente | None = None


class ResumoLimite(BaseModel):
    """Fotografia do crédito do cliente (limite atual e teto da faixa)."""

    limite_atual: float
    score: int
    limite_maximo: float | None = None
    taxa_juros_mensal: float | None = None


class ResultadoAumento(BaseModel):
    """Resultado da avaliação de um pedido de aumento de limite."""

    status: StatusPedido
    mensagem: str
    limite_maximo: float | None = None
    taxa_juros_mensal: float | None = None
    solicitacao: SolicitacaoAumento | None = None
    cliente_atualizado: Cliente | None = None


class ResultadoEntrevista(BaseModel):
    """Resultado do recálculo de score após a entrevista financeira."""

    ok: bool
    mensagem: str
    novo_score: int | None = None
    cliente: Cliente | None = None


class ResultadoCotacao(BaseModel):
    """Resultado de uma consulta de câmbio."""

    ok: bool
    mensagem: str
    cotacao: Cotacao | None = None


class ResultadoConsulta(BaseModel):
    """Trechos recuperados da base de conhecimento (RAG)."""

    ok: bool
    trechos: list[str] = Field(default_factory=list)
    fontes: list[str] = Field(default_factory=list)

    @property
    def contexto(self) -> str:
        return "\n\n".join(self.trechos)
