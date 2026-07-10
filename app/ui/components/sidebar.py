"""Barra lateral: identidade + painel de debug (estado vindo da API)."""
from __future__ import annotations

import streamlit as st

from ui.service import API_BASE_URL, health
from ui.state import reset_session

NOMES_AGENTES = {
    "triagem": "🤖 Triagem",
    "credito": "💳 Crédito",
    "entrevista": "🗣️ Entrevista de Crédito",
    "cambio": "💱 Câmbio",
}


def render_sidebar(debug: dict, finished: bool) -> None:
    with st.sidebar:
        st.header("🏦 Banco Ágil")
        st.caption("Atendimento com agentes de IA")
        st.button("🔄 Novo atendimento", on_click=reset_session, use_container_width=True)

        # status da API
        if health():
            st.markdown('<span class="ba-chip">API online</span>', unsafe_allow_html=True)
        else:
            st.warning(f"API indisponível em {API_BASE_URL}")

        st.divider()
        st.subheader("🔎 Debug (interno)")

        atual = debug.get("current_agent", "triagem")
        linhas = [
            f"**Agente ativo:** {NOMES_AGENTES.get(atual, atual)}",
            f"**Autenticado:** {'✅' if debug.get('authenticated') else '❌'}",
        ]
        if debug.get("cliente_nome"):
            linhas.append(f"**Cliente:** {debug['cliente_nome']}")
        if debug.get("limite") is not None:
            linhas.append(f"**Limite:** R$ {float(debug['limite']):,.2f}")
        if debug.get("score") is not None:
            linhas.append(f"**Score:** {debug['score']}")
        linhas.append(f"**Tentativas de auth:** {debug.get('auth_attempts', 0)}")
        if debug.get("pending_increase"):
            linhas.append(f"**Aumento pendente:** R$ {float(debug['pending_increase']):,.2f}")

        st.markdown(
            '<div class="ba-debug-card">' + "<br>".join(linhas) + "</div>",
            unsafe_allow_html=True,
        )
        if finished:
            st.success("Atendimento encerrado.")
