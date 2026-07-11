"""Componente de chat: renderiza o histórico visível ao cliente."""
from __future__ import annotations

import streamlit as st

AVATARES = {"user": "🧑", "assistant": "🏦"}


def _texto_seguro(conteudo: str) -> str:
    """Escapa o cifrão: o Markdown do Streamlit trata `$...$` como LaTeX e comeria
    o "R$" dos valores em reais (ex.: exibia "R 15.000,00")."""
    return conteudo.replace("$", "\\$")


def render_history(historico: list[dict]) -> None:
    for msg in historico:
        with st.chat_message(msg["role"], avatar=AVATARES.get(msg["role"])):
            st.markdown(_texto_seguro(msg["content"]))


def render_welcome(historico: list[dict], finished: bool) -> None:
    if not historico and not finished:
        st.info(
            'Envie "Olá" para começar. O atendente vai pedir seu CPF e data de nascimento '
            "para autenticação."
        )
