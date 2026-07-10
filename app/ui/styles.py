"""Estilos e cabeçalho da UI (repaginação visual)."""
from __future__ import annotations

import streamlit as st

_CSS = """
<style>
  /* Layout geral */
  .main .block-container { max-width: 820px; padding-top: 1.2rem; padding-bottom: 6rem; }
  #MainMenu, footer, header [data-testid="stToolbar"] { visibility: hidden; }

  /* Cabeçalho do banco */
  .ba-header {
    display: flex; align-items: center; gap: 14px;
    padding: 18px 22px; border-radius: 18px; margin-bottom: 18px;
    background: linear-gradient(135deg, #0f766e 0%, #10b981 100%);
    box-shadow: 0 8px 30px rgba(16,185,129,.25);
  }
  .ba-header .ba-logo {
    font-size: 30px; width: 52px; height: 52px; display: grid; place-items: center;
    background: rgba(255,255,255,.15); border-radius: 14px;
  }
  .ba-header .ba-title { font-size: 1.35rem; font-weight: 800; color: #fff; line-height: 1.1; }
  .ba-header .ba-sub { font-size: .82rem; color: rgba(255,255,255,.85); }
  .ba-badge {
    margin-left: auto; font-size: .72rem; font-weight: 700; color: #052e2b;
    background: #a7f3d0; padding: 5px 12px; border-radius: 999px;
  }

  /* Bolhas de chat */
  [data-testid="stChatMessage"] {
    background: #141B22; border: 1px solid #1f2a37; border-radius: 16px;
    padding: 10px 14px; margin-bottom: 8px;
  }
  [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #0f2e28; border-color: #14513f;
  }

  /* Caixa de input arredondada */
  [data-testid="stChatInput"] textarea { border-radius: 14px !important; }

  /* Sidebar */
  [data-testid="stSidebar"] { background: #0B0F14; border-right: 1px solid #1f2a37; }
  .ba-debug-card {
    background: #141B22; border: 1px solid #1f2a37; border-radius: 12px;
    padding: 12px 14px; font-size: .86rem;
  }
  .ba-chip {
    display: inline-block; padding: 2px 10px; border-radius: 999px;
    background: #10b98122; color: #34d399; font-weight: 700; font-size: .8rem;
  }
</style>
"""


def apply_styles() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def render_header() -> None:
    st.markdown(
        """
        <div class="ba-header">
          <div class="ba-logo">🏦</div>
          <div>
            <div class="ba-title">Banco Ágil</div>
            <div class="ba-sub">Atendimento inteligente • crédito, câmbio e mais</div>
          </div>
          <div class="ba-badge">● online</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
