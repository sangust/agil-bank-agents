"""Barra lateral: identidade + painel de debug (opcional, atrás de um toggle)."""
from __future__ import annotations

import streamlit as st

from ui.service import API_BASE_URL, health
from ui.state import reset_session
from ui.styles import LOGO_DARK

NOMES_AGENTES = {
    "triagem": "Triagem",
    "credito": "Crédito",
    "entrevista": "Entrevista de Crédito",
    "cambio": "Câmbio",
}

AVISO_DEBUG = (
    "Painel técnico interno: mostra o estado bruto do atendimento (agente ativo, "
    "autenticação, score). Serve para inspeção/demonstração — o cliente não veria isto."
)


def _row(rotulo: str, valor_html: str) -> str:
    return (
        f'<div class="cb-row"><span class="cb-k">{rotulo}</span>'
        f'<span class="cb-v">{valor_html}</span></div>'
    )


def _painel_debug(debug: dict) -> str:
    atual = debug.get("current_agent", "triagem")
    agente = NOMES_AGENTES.get(atual, atual)
    autenticado = bool(debug.get("authenticated"))

    linhas = [
        _row("Agente ativo", f'<span class="cb-pill agent">{agente}</span>'),
        _row(
            "Autenticado",
            '<span class="cb-pill on">Sim</span>' if autenticado
            else '<span class="cb-pill off">Não</span>',
        ),
    ]
    if debug.get("cliente_nome"):
        linhas.append(_row("Cliente", str(debug["cliente_nome"])))
    if debug.get("limite") is not None:
        linhas.append(_row("Limite", f'R$ {float(debug["limite"]):,.2f}'))
    if debug.get("score") is not None:
        linhas.append(_row("Score", str(debug["score"])))
    linhas.append(_row("Tentativas de auth", str(debug.get("auth_attempts", 0))))
    if debug.get("pending_increase"):
        linhas.append(_row("Aumento pendente", f'R$ {float(debug["pending_increase"]):,.2f}'))

    # Escapa "$" para o Markdown do Streamlit não interpretar "R$ ... R$" como LaTeX.
    return ('<div class="cb-panel">' + "".join(linhas) + "</div>").replace("$", "\\$")


def render_sidebar(debug: dict, finished: bool) -> None:
    with st.sidebar:
        st.markdown(
            f"""
            <div class="cb-brand">
              <div>{LOGO_DARK}</div>
              <div>
                <div class="cb-name">Credibot</div>
                <div class="cb-tag">Atendimento com agentes de IA</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Novo atendimento", on_click=reset_session, use_container_width=True)

        if health():
            st.markdown('<span class="cb-chip">API online</span>', unsafe_allow_html=True)
        else:
            st.warning(f"API indisponível em {API_BASE_URL}")

        st.divider()
        st.markdown('<div class="cb-eyebrow">Painel técnico</div>', unsafe_allow_html=True)
        if st.toggle("Mostrar debug interno", value=False):
            st.markdown(f'<div class="cb-note">{AVISO_DEBUG}</div>', unsafe_allow_html=True)
            st.markdown(_painel_debug(debug), unsafe_allow_html=True)

        if finished:
            st.success("Atendimento encerrado.")
