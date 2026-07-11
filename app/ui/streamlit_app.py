"""Ponto de entrada da UI do Credibot (cliente HTTP da API).

Requer que `app/` esteja no PYTHONPATH (o Dockerfile e o README já cuidam disso).
"""
from __future__ import annotations

import streamlit as st

from ui.components.chat import AVATARES, render_history, render_welcome
from ui.components.sidebar import render_sidebar
from ui.service import APIError, enviar
from ui.state import init_session
from ui.styles import apply_styles, render_header

PLACEHOLDER_ATIVO = "Digite sua mensagem..."
PLACEHOLDER_ENCERRADO = "Atendimento encerrado. Clique em 'Novo atendimento'."

st.set_page_config(
    page_title="Credibot — Atendimento", layout="centered", initial_sidebar_state="expanded"
)


def _enviar_mensagem(prompt: str) -> None:
    st.session_state.historico.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=AVATARES["user"]):
        st.markdown(prompt)

    try:
        with st.spinner("Atendente digitando..."):
            resposta = enviar(st.session_state.session_id, prompt)
    except APIError as exc:
        st.error(f"Não consegui falar com o servidor de atendimento agora. ({exc})")
        return

    st.session_state.session_id = resposta.get("session_id", st.session_state.session_id)
    st.session_state.debug = resposta.get("debug", {})
    st.session_state.finished = bool(resposta.get("finished"))
    st.session_state.historico.append(
        {"role": "assistant", "content": resposta.get("reply", "")}
    )
    st.rerun()


def main() -> None:
    apply_styles()
    init_session()

    render_sidebar(st.session_state.debug, st.session_state.finished)
    render_header()
    render_welcome(st.session_state.historico, st.session_state.finished)
    render_history(st.session_state.historico)

    encerrado = st.session_state.finished
    prompt = st.chat_input(
        PLACEHOLDER_ENCERRADO if encerrado else PLACEHOLDER_ATIVO, disabled=encerrado
    )
    if prompt:
        _enviar_mensagem(prompt)


if __name__ == "__main__":
    main()
