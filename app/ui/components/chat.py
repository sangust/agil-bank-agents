"""Componente de chat: renderiza o histórico visível ao cliente."""
from __future__ import annotations

import streamlit as st

AVATARES = {"user": "🧑", "assistant": "🏦"}


def render_history(historico: list[dict]) -> None:
    for msg in historico:
        with st.chat_message(msg["role"], avatar=AVATARES.get(msg["role"])):
            st.markdown(msg["content"])


def render_welcome(historico: list[dict], finished: bool) -> None:
    if not historico and not finished:
        st.info(
            'Envie "Olá" para começar. O atendente vai pedir seu CPF e data de nascimento '
            "para autenticação."
        )
