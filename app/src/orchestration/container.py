"""Container de serviços (injeção de dependência leve).

Os handlers dos agentes acessam os serviços por ``get_services()``. Os testes injetam
implementações com repositórios temporários via ``set_services()``.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel, ConfigDict

from src.services.auth_service import AuthService
from src.services.cambio_service import CambioService
from src.services.credito_service import CreditoService
from src.services.entrevista_service import EntrevistaService
from src.services.knowledge_service import KnowledgeService


class Services(BaseModel):
    """Agrupa os serviços de negócio disponíveis para os agentes."""

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    auth: AuthService
    credito: CreditoService
    entrevista: EntrevistaService
    cambio: CambioService
    knowledge: KnowledgeService


_override: Services | None = None


@lru_cache(maxsize=1)
def _services_padrao() -> Services:
    return Services(
        auth=AuthService(),
        credito=CreditoService(),
        entrevista=EntrevistaService(),
        cambio=CambioService(),
        knowledge=KnowledgeService(),
    )


def get_services() -> Services:
    return _override or _services_padrao()


def set_services(services: Services | None) -> None:
    """Substitui o container (usado em testes). Passe None para restaurar o padrão."""
    global _override
    _override = services
