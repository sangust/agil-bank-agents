"""Aplicação FastAPI do Credibot (backend do atendimento)."""
from __future__ import annotations

from fastapi import FastAPI

from api.routes import chat, health

app = FastAPI(
    title="Credibot API",
    version="0.3.0",
    description="Atendimento bancário multi-agente (LangGraph + RAG) exposto por HTTP.",
)

app.include_router(health.router)
app.include_router(chat.router, prefix="/api")
