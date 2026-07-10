"""Modelos de domínio (Pydantic v2)."""
from __future__ import annotations

from datetime import UTC, date, datetime

from pydantic import BaseModel, Field, field_validator

from src.domain.enums import StatusConta, StatusPedido, TipoEmprego


def _agora_utc() -> datetime:
    return datetime.now(UTC)


class Cliente(BaseModel):
    """Cliente do Banco Ágil (espelha uma linha de clientes.csv)."""

    cpf: str
    nome: str
    data_nascimento: date
    email: str = ""
    telefone: str = ""
    profissao: str = ""
    tipo_emprego: TipoEmprego = TipoEmprego.FORMAL
    renda_declarada: float = 0.0
    limite_atual: float = 0.0
    score: int = 0
    status_conta: StatusConta = StatusConta.ATIVA
    data_abertura: date | None = None

    @field_validator("score")
    @classmethod
    def _score_range(cls, v: int) -> int:
        return max(0, min(1000, v))

    @property
    def idade(self) -> int:
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )

    @property
    def primeiro_nome(self) -> str:
        return self.nome.split()[0] if self.nome else ""


class FaixaScore(BaseModel):
    """Faixa da política de crédito (score -> limite máximo)."""

    score_min: int
    score_max: int
    limite_maximo: float
    taxa_juros_mensal: float = 0.0

    def contem(self, score: int) -> bool:
        return self.score_min <= score <= self.score_max


class SolicitacaoAumento(BaseModel):
    """Pedido de aumento de limite (linha de solicitacoes_aumento_limite.csv)."""

    cpf_cliente: str
    data_hora_solicitacao: datetime = Field(default_factory=_agora_utc)
    limite_atual: float
    novo_limite_solicitado: float
    status_pedido: StatusPedido
    score_no_momento: int = 0
    motivo: str = ""


class RegistroScore(BaseModel):
    """Entrada do histórico de score (historico_score.csv)."""

    cpf_cliente: str
    data_hora: datetime = Field(default_factory=_agora_utc)
    score_anterior: int
    score_novo: int
    origem: str = "entrevista"


class DadosEntrevista(BaseModel):
    """Dados coletados na entrevista financeira."""

    renda_mensal: float
    tipo_emprego: TipoEmprego
    despesas_fixas: float
    num_dependentes: int = Field(ge=0)
    tem_dividas: bool


class Cotacao(BaseModel):
    """Resultado de uma cotação de câmbio."""

    moeda: str
    destino: str
    valor: float
    nome: str = ""
    atualizado_em: str = ""
