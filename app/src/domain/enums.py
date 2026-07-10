"""Enumerações do domínio bancário."""
from __future__ import annotations

from enum import StrEnum


class TipoEmprego(StrEnum):
    FORMAL = "formal"
    AUTONOMO = "autonomo"
    DESEMPREGADO = "desempregado"

    @classmethod
    def normalizar(cls, valor: str) -> TipoEmprego:
        v = (valor or "").strip().lower().replace("ô", "o").replace("â", "a")
        formal = {"formal", "clt", "assalariado", "empregado", "carteira assinada",
                  "funcionario", "servidor"}
        autonomo = {"autonomo", "pj", "empresario", "empreendedor", "socio", "ceo",
                    "freelancer", "freela", "liberal", "mei", "prestador"}
        desempregado = {"desempregado", "desempregada", "sem emprego", "sem renda"}
        if v in formal:
            return cls.FORMAL
        if v in autonomo:
            return cls.AUTONOMO
        if v in desempregado:
            return cls.DESEMPREGADO
        # heurística por substring para frases livres
        if any(w in v for w in ("formal", "clt", "carteira", "assalari", "servidor")):
            return cls.FORMAL
        if any(w in v for w in ("autonom", "empres", "pj", "socio", "ceo", "freela", "mei")):
            return cls.AUTONOMO
        return cls.DESEMPREGADO


class StatusPedido(StrEnum):
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    REJEITADO = "rejeitado"
    INVALIDO = "invalido"
    ERRO = "erro"


class StatusConta(StrEnum):
    ATIVA = "ativa"
    BLOQUEADA = "bloqueada"
    ENCERRADA = "encerrada"
