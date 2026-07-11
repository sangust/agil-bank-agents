"""Constantes da aplicação — valores fixos, sem dependências de outros módulos.

Centraliza caminhos, limites, tabelas de pesos, dicionários de domínio e cabeçalhos de CSV
que antes estavam espalhados pelos módulos.
"""
from __future__ import annotations

from pathlib import Path
from typing import Final

# --- Caminhos ---------------------------------------------------------------
# app/src/core/constants.py -> core -> src -> app -> raiz do projeto
SRC_DIR: Final[Path] = Path(__file__).resolve().parents[1]
APP_DIR: Final[Path] = Path(__file__).resolve().parents[2]
BASE_DIR: Final[Path] = Path(__file__).resolve().parents[3]

# Dados e logs vivem dentro de app/ (artefatos da aplicação, não da raiz do repo).
DATA_DIR: Final[Path] = APP_DIR / "data"
LOGS_DIR: Final[Path] = APP_DIR / "logs"
INFRA_DIR: Final[Path] = BASE_DIR / "infra"
ENV_FILE: Final[Path] = INFRA_DIR / ".env"

DOCS_DIR: Final[Path] = SRC_DIR / "rag" / "documents"
CHROMA_DIR: Final[Path] = DATA_DIR / "chroma"
CHROMA_COLLECTION: Final[str] = "credibot_conhecimento"

CLIENTES_CSV: Final[Path] = DATA_DIR / "clientes.csv"
SCORE_LIMITE_CSV: Final[Path] = DATA_DIR / "score_limite.csv"
SOLICITACOES_CSV: Final[Path] = DATA_DIR / "solicitacoes_aumento_limite.csv"
HISTORICO_SCORE_CSV: Final[Path] = DATA_DIR / "historico_score.csv"
TARIFAS_CSV: Final[Path] = DATA_DIR / "tarifas.csv"

# --- Cabeçalhos de CSV ------------------------------------------------------
HEADER_SOLICITACOES: Final[list[str]] = [
    "cpf_cliente",
    "data_hora_solicitacao",
    "limite_atual",
    "novo_limite_solicitado",
    "status_pedido",
    "score_no_momento",
    "motivo",
]

HEADER_HISTORICO_SCORE: Final[list[str]] = [
    "cpf_cliente",
    "data_hora",
    "score_anterior",
    "score_novo",
    "origem",
]

# --- Orquestração e agentes -------------------------------------------------
AGENTE_PADRAO: Final[str] = "triagem"
AGENTES: Final[tuple[str, ...]] = ("triagem", "credito", "entrevista", "cambio")

MAX_ITERACOES_TURNO: Final[int] = 6
MAX_TENTATIVAS_AUTH: Final[int] = 3

# Prefixo que marca texto dirigido ao modelo (nunca deve chegar ao cliente).
MARCADOR_INTERNO: Final[str] = "[interno]"

MSG_INSTABILIDADE: Final[str] = (
    "Desculpe, estou com uma instabilidade técnica no momento. "
    "Pode tentar novamente em instantes?"
)
MSG_SEM_RESPOSTA: Final[str] = (
    "Desculpe, não consegui formular uma resposta agora. Pode repetir, por favor?"
)

# --- Score ------------------------------------------------------------------
SCORE_MINIMO: Final[int] = 0
SCORE_MAXIMO: Final[int] = 1000

PESO_RENDA: Final[int] = 30

# Chaves em texto: TipoEmprego é StrEnum, então o lookup funciona direto.
PESO_EMPREGO: Final[dict[str, int]] = {
    "formal": 300,
    "autonomo": 200,
    "desempregado": 0,
}
PESO_DEPENDENTES: Final[dict[int, int]] = {0: 100, 1: 80, 2: 60, 3: 30}
MAX_DEPENDENTES_TABELADO: Final[int] = 3  # 3 ou mais usam o mesmo peso
PESO_DIVIDAS: Final[dict[bool, int]] = {True: -100, False: 100}

# --- Datas ------------------------------------------------------------------
FORMATOS_DATA: Final[tuple[str, ...]] = ("%d/%m/%Y", "%d/%m/%y", "%Y/%m/%d")
FORMATOS_DATA_SEM_SEPARADOR: Final[tuple[str, ...]] = ("%d%m%Y", "%Y%m%d")
TAMANHO_DATA_SEM_SEPARADOR: Final[int] = 8
FORMATO_ISO: Final[str] = "%Y-%m-%d"

MESES: Final[dict[str, int]] = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "março": 3, "abril": 4, "maio": 5,
    "junho": 6, "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10,
    "novembro": 11, "dezembro": 12,
}

# --- CPF --------------------------------------------------------------------
TAMANHO_CPF: Final[int] = 11

# --- Câmbio -----------------------------------------------------------------
# Moeda padrão quando o cliente não especifica (dólar->real), conforme o desafio.
MOEDA_PADRAO: Final[str] = "USD"
MOEDA_DESTINO_PADRAO: Final[str] = "BRL"
TAMANHO_CODIGO_MOEDA: Final[int] = 3

# --- RAG --------------------------------------------------------------------
RAG_CHUNK_SIZE: Final[int] = 500
RAG_CHUNK_OVERLAP: Final[int] = 80

# --- HTTP -------------------------------------------------------------------
TIMEOUT_CAMBIO_S: Final[int] = 10
TIMEOUT_API_S: Final[int] = 90
TIMEOUT_HEALTH_S: Final[int] = 5
