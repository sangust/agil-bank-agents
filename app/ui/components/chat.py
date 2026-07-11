"""Componente de chat: renderiza o histórico visível ao cliente."""
from __future__ import annotations

import base64

import streamlit as st


def _avatar_svg(inicial: str, fundo: str, cor: str) -> str:
    """Gera um avatar circular com uma inicial (sem emoji), como data URI."""
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='36' height='36' viewBox='0 0 36 36'>"
        f"<rect width='36' height='36' rx='18' fill='{fundo}'/>"
        "<text x='18' y='24' font-family='Helvetica,Arial,sans-serif' font-size='16' "
        f"font-weight='700' fill='{cor}' text-anchor='middle'>{inicial}</text></svg>"
    )
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


AVATARES = {
    "assistant": _avatar_svg("C", "#6366f1", "#ffffff"),
    "user": _avatar_svg("V", "#e6e7ec", "#3a3f4b"),
}


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
