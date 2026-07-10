"""Estado de sessão da UI (Streamlit).

Guarda apenas o necessário para exibir o chat; o estado autoritativo do atendimento vive
no servidor (API), identificado por ``session_id``.
"""
from __future__ import annotations

import uuid

import streamlit as st


def _novo_id() -> str:
    return uuid.uuid4().hex


def init_session() -> None:
    st.session_state.setdefault("session_id", _novo_id())
    st.session_state.setdefault("historico", [])  # [{"role","content"}]
    st.session_state.setdefault("debug", {})
    st.session_state.setdefault("finished", False)


def reset_session() -> None:
    st.session_state.session_id = _novo_id()
    st.session_state.historico = []
    st.session_state.debug = {}
    st.session_state.finished = False
