"""Estilos e cabeçalho da UI — tema claro corporativo (Credibot)."""
from __future__ import annotations

import streamlit as st

# Paleta
_NAVY = "#1e3a5f"
_NAVY_ESCURO = "#152b46"
_ACENTO = "#3b82f6"
_BORDA = "#e5e9f0"
_BORDA_SUAVE = "#eef1f6"
_TEXTO = "#1f2937"
_TEXTO_SUAVE = "#64748b"

# Marca (SVG inline, sem emoji): quadrado navy com um "C" aberto e um ponto de acento.
_LOGO = f"""
<svg width="44" height="44" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="44" height="44" rx="13" fill="{_NAVY}"/>
  <path d="M29 16.2a9 9 0 1 0 0 11.6" stroke="#ffffff" stroke-width="3.4"
        stroke-linecap="round"/>
  <circle cx="31.5" cy="22" r="2.9" fill="{_ACENTO}"/>
</svg>
"""

_CSS = f"""
<style>
  /* Fundo com leve profundidade (adeus branco chapado) */
  [data-testid="stAppViewContainer"] {{
    background: linear-gradient(180deg, #e7edf5 0%, #f4f7fb 45%, #f4f7fb 100%);
  }}
  #MainMenu, footer, header [data-testid="stToolbar"] {{ visibility: hidden; }}

  /* Conteúdo num card branco elevado */
  .main .block-container {{
    max-width: 800px; margin-top: 1.1rem;
    padding: 1.5rem 1.9rem 2.2rem;
    background: #ffffff; border: 1px solid {_BORDA}; border-radius: 18px;
    box-shadow: 0 8px 30px rgba(15,23,42,.07);
  }}

  /* Cabeçalho / marca */
  .cb-header {{
    display: flex; align-items: center; gap: 14px;
    padding-bottom: 16px; margin-bottom: 20px;
    border-bottom: 1px solid {_BORDA_SUAVE};
  }}
  .cb-header .cb-logo {{ flex: 0 0 auto; line-height: 0; }}
  .cb-header .cb-title {{
    font-size: 1.75rem; font-weight: 800; letter-spacing: -.025em;
    color: {_NAVY}; line-height: 1;
  }}
  .cb-header .cb-title span {{ color: {_ACENTO}; }}
  .cb-header .cb-sub {{ margin-top: 4px; font-size: .86rem; color: {_TEXTO_SUAVE}; }}
  .cb-header .cb-online {{
    margin-left: auto; font-size: .74rem; font-weight: 600; color: #15803d;
    display: inline-flex; align-items: center; gap: 6px;
  }}
  .cb-header .cb-online::before {{
    content: ""; width: 8px; height: 8px; border-radius: 50%; background: #22c55e;
  }}

  /* Bolhas de chat */
  [data-testid="stChatMessage"] {{
    background: #f8fafc; border: 1px solid {_BORDA_SUAVE}; border-radius: 14px;
    padding: 11px 15px; margin-bottom: 11px; color: {_TEXTO};
    box-shadow: 0 1px 2px rgba(15,23,42,.04);
  }}
  [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
    background: #eef4ff; border-color: #dbe6fb;
  }}
  [data-testid="stChatMessage"] p {{ color: {_TEXTO}; }}
  [data-testid="stChatMessage"] img {{
    border-radius: 50%; box-shadow: 0 0 0 3px #ffffff, 0 1px 3px rgba(15,23,42,.15);
  }}

  /* Caixa de input flutuante */
  [data-testid="stBottom"] {{ background: transparent; }}
  [data-testid="stBottom"] > div {{ background: transparent; }}
  [data-testid="stChatInput"] {{
    background: #ffffff; border: 1px solid {_BORDA}; border-radius: 14px;
    box-shadow: 0 4px 16px rgba(15,23,42,.08);
  }}
  [data-testid="stChatInput"] textarea {{ border-radius: 14px !important; }}

  /* Sidebar navy */
  [data-testid="stSidebar"] {{ background: {_NAVY}; border-right: none; }}
  [data-testid="stSidebar"] * {{ color: #e8eef5; }}
  [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
  [data-testid="stSidebar"] h3 {{ color: #ffffff; }}
  [data-testid="stSidebar"] [data-testid="stButton"] button {{
    background: #ffffff; color: {_NAVY}; border: none; font-weight: 700; border-radius: 9px;
  }}
  [data-testid="stSidebar"] [data-testid="stButton"] button:hover {{
    background: #e8eef5; color: {_NAVY_ESCURO};
  }}
  .cb-chip {{
    display: inline-block; padding: 3px 11px; border-radius: 999px;
    background: rgba(255,255,255,.14); color: #ffffff; font-weight: 600; font-size: .78rem;
  }}
  .cb-debug-card {{
    background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.14);
    border-radius: 10px; padding: 12px 14px; font-size: .84rem; line-height: 1.7;
  }}
</style>
"""


def apply_styles() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def render_header() -> None:
    st.markdown(
        f"""
        <div class="cb-header">
          <div class="cb-logo">{_LOGO}</div>
          <div>
            <div class="cb-title">Credi<span>bot</span></div>
            <div class="cb-sub">Assistente de crédito e câmbio</div>
          </div>
          <div class="cb-online">online</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
