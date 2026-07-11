"""Estilos e cabeçalho da UI — tema Grafite + Índigo (Credibot).

Seletores baseados nos data-testid reais do Streamlit 1.59. Paleta em tokens no topo.
"""
from __future__ import annotations

import streamlit as st

# --- Tokens de design (Grafite + Índigo) ------------------------------------
_DARK = "#16181f"        # sidebar / base escura (grafite)
_DARK_2 = "#1c2030"      # topo do gradiente da sidebar
_INK = "#1b1e27"         # texto principal (grafite)
_MUTED = "#6b7280"       # texto secundário
_ACCENT = "#6366f1"      # índigo (acento único)
_ACCENT_DEEP = "#4f46e5"
_ACCENT_SOFT = "#a5b4fc" # índigo claro (sobre fundo escuro)
_BORDER = "#e6e7ec"      # borda neutra grafite
_SURFACE = "#ffffff"     # card de conteúdo
_GOOD = "#22c55e"        # semântico (autenticado / online)
_WARN = "#f59e0b"        # semântico (aviso)
_BAD = "#ef6a4d"         # semântico (não autenticado)


def _logo(size: int) -> str:
    """Marca: badge índigo com barras ascendentes (score subindo) e ponto de topo."""
    return f"""
<svg width="{size}" height="{size}" viewBox="0 0 44 44" fill="none"
     xmlns="http://www.w3.org/2000/svg">
  <rect width="44" height="44" rx="13" fill="{_ACCENT}"/>
  <rect x="11" y="26" width="5.5" height="7" rx="2.6" fill="#ffffff" opacity="0.85"/>
  <rect x="19.25" y="20" width="5.5" height="13" rx="2.6" fill="#ffffff" opacity="0.92"/>
  <rect x="27.5" y="13" width="5.5" height="20" rx="2.6" fill="#ffffff"/>
  <circle cx="30.25" cy="10.2" r="2.5" fill="{_ACCENT_SOFT}"/>
</svg>
"""


LOGO_LIGHT = _logo(42)   # header (sobre card branco)
LOGO_DARK = _logo(34)    # sidebar (sobre grafite) — mesma marca, índigo contrasta nos dois

_CSS = f"""
<style>
  /* Fundo com leve profundidade (grafite frio); header do Streamlit transparente */
  [data-testid="stAppViewContainer"] {{
    background: radial-gradient(1100px 560px at 72% -8%, #edeef3 0%, #f3f4f8 42%, #f4f5f8 100%);
  }}
  [data-testid="stHeader"] {{ background: transparent; }}
  /* Esconde só o supérfluo — NUNCA o toolbar inteiro (ele hospeda o controle da sidebar) */
  #MainMenu, [data-testid="stMainMenu"], [data-testid="stAppDeployButton"],
  [data-testid="stStatusWidget"], [data-testid="stDecoration"] {{ display: none; }}

  /* Conteúdo num card branco elevado */
  [data-testid="stMainBlockContainer"] {{
    max-width: 820px; padding: 1.7rem 2rem 2.4rem; margin-top: 1.4rem;
    background: {_SURFACE}; border: 1px solid {_BORDER}; border-radius: 20px;
    box-shadow: 0 1px 0 rgba(255,255,255,.6) inset, 0 14px 40px rgba(20, 22, 31, .10);
  }}

  /* Cabeçalho / marca */
  .cb-header {{
    display: flex; align-items: center; gap: 14px;
    padding-bottom: 16px; margin-bottom: 20px; border-bottom: 1px solid {_BORDER};
  }}
  .cb-header .cb-logo {{ flex: 0 0 auto; line-height: 0; }}
  .cb-header .cb-title {{
    font-size: 1.72rem; font-weight: 800; letter-spacing: -.03em; color: {_INK}; line-height: 1;
  }}
  .cb-header .cb-title span {{ color: {_ACCENT}; }}
  .cb-header .cb-sub {{ margin-top: 4px; font-size: .85rem; color: {_MUTED}; }}
  .cb-header .cb-online {{
    margin-left: auto; font-size: .72rem; font-weight: 600; color: #15803d;
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(34,197,94,.12); padding: 4px 11px; border-radius: 999px;
  }}
  .cb-header .cb-online::before {{
    content: ""; width: 8px; height: 8px; border-radius: 50%; background: {_GOOD};
  }}

  /* Bolhas de chat */
  [data-testid="stChatMessage"] {{
    background: #f7f8fb; border: 1px solid {_BORDER}; border-radius: 14px;
    padding: 12px 16px; margin-bottom: 12px; color: {_INK};
    box-shadow: 0 1px 2px rgba(20, 22, 31, .04);
  }}
  [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
    background: #eef0fe; border-color: #dcdefb;
  }}
  [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li {{ color: {_INK}; }}
  [data-testid="stChatMessage"] img {{
    border-radius: 50%; box-shadow: 0 0 0 3px {_SURFACE}, 0 1px 3px rgba(20, 22, 31, .18);
  }}

  /* Aviso de boas-vindas (st.info) discreto, em índigo */
  [data-testid="stMain"] [data-testid="stAlertContainer"] {{
    background: #eef0fe; border: 1px solid #dcdefb; color: {_INK}; border-radius: 12px;
  }}

  /* Caixa de input flutuante */
  [data-testid="stBottom"], [data-testid="stBottom"] > div {{ background: transparent; }}
  [data-testid="stChatInput"] {{
    background: {_SURFACE}; border: 1px solid {_BORDER}; border-radius: 14px;
    box-shadow: 0 6px 20px rgba(20, 22, 31, .10);
  }}
  [data-testid="stChatInput"] textarea {{ border-radius: 14px !important; color: {_INK}; }}
  [data-testid="stChatInput"] textarea::placeholder {{ color: {_MUTED}; }}

  /* ---------------- Sidebar (grafite) ---------------- */
  [data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {_DARK_2} 0%, {_DARK} 100%);
    color: #d7dae3; border-right: none;
  }}
  [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{ padding-top: .6rem; }}
  [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,.09); margin: 1.1rem 0; }}

  /* Botão de RECOLHER a sidebar (setinha visível sobre o grafite) */
  [data-testid="stSidebarHeader"] {{ padding-top: .4rem; }}
  [data-testid="stSidebarCollapseButton"] button {{ background: transparent; }}
  [data-testid="stSidebarCollapseButton"] button svg,
  [data-testid="stSidebarCollapseButton"] button * {{
    color: #cbd0dc !important; fill: #cbd0dc !important;
  }}
  [data-testid="stSidebarCollapseButton"] button:hover {{ background: rgba(255,255,255,.10); }}

  /* Botão de REABRIR quando recolhida: fixo no canto, sempre visível e por cima de tudo */
  [data-testid="stExpandSidebarButton"] {{
    position: fixed !important; top: 12px; left: 12px; z-index: 1000;
    display: block !important; visibility: visible !important; opacity: 1 !important;
  }}
  [data-testid="stExpandSidebarButton"] button {{
    background: #ffffff; border: 1px solid {_BORDER}; border-radius: 10px;
    box-shadow: 0 4px 14px rgba(20,22,31,.16); width: 40px; height: 40px;
  }}
  [data-testid="stExpandSidebarButton"] button svg,
  [data-testid="stExpandSidebarButton"] button * {{
    color: {_ACCENT} !important; fill: {_ACCENT} !important;
  }}
  [data-testid="stExpandSidebarButton"] button:hover {{ background: #eef0fe; }}

  /* Marca da sidebar */
  .cb-brand {{ display: flex; align-items: center; gap: 11px; margin-bottom: 4px; }}
  .cb-brand .cb-name {{
    font-size: 1.18rem; font-weight: 800; color: #fff; letter-spacing: -.02em;
  }}
  .cb-brand .cb-tag {{ font-size: .74rem; color: #8b90a4; margin-top: 1px; }}

  /* Eyebrow de seção */
  .cb-eyebrow {{
    font-size: .68rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase;
    color: #7c839a; margin: 2px 0 10px;
  }}

  /* Botão da sidebar */
  [data-testid="stSidebar"] [data-testid="stButton"] button {{
    background: #ffffff; border: none; border-radius: 10px; font-weight: 700;
    box-shadow: 0 2px 10px rgba(0,0,0,.22); transition: transform .12s ease, background .15s ease;
  }}
  [data-testid="stSidebar"] [data-testid="stButton"] button,
  [data-testid="stSidebar"] [data-testid="stButton"] button * {{ color: {_INK} !important; }}
  [data-testid="stSidebar"] [data-testid="stButton"] button:hover {{ background: #eef0fe; }}
  [data-testid="stSidebar"] [data-testid="stButton"] button:active {{ transform: translateY(1px); }}

  /* Toggle do debug */
  [data-testid="stSidebar"] [data-testid="stCheckbox"] label p {{
    color: #d7dae3; font-size: .9rem;
  }}

  /* Pílula de status da API */
  .cb-chip {{
    display: inline-flex; align-items: center; gap: 6px; margin-top: 4px;
    padding: 4px 11px; border-radius: 999px; font-weight: 600; font-size: .78rem;
    background: rgba(34,197,94,.16); color: #bbf7d0;
  }}
  .cb-chip::before {{
    content: ""; width: 7px; height: 7px; border-radius: 50%; background: {_GOOD};
  }}

  /* Aviso ao abrir o debug */
  .cb-note {{
    background: rgba(245,158,11,.12); border: 1px solid rgba(245,158,11,.30);
    color: #f2c877; border-radius: 10px; padding: 9px 12px; font-size: .78rem;
    line-height: 1.45; margin-bottom: 10px;
  }}

  /* Painel de debug */
  .cb-panel {{
    display: flex; flex-direction: column; gap: 9px;
    background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.11);
    border-radius: 12px; padding: 13px 15px; font-size: .84rem;
  }}
  .cb-panel .cb-row {{
    display: flex; justify-content: space-between; align-items: center; gap: 10px;
  }}
  .cb-panel .cb-k {{ color: #8b90a4; }}
  .cb-panel .cb-v {{ color: #fff; font-weight: 600; text-align: right; }}
  .cb-pill {{ padding: 2px 9px; border-radius: 999px; font-size: .74rem; font-weight: 700; }}
  .cb-pill.on {{ background: rgba(34,197,94,.20); color: #86efac; }}
  .cb-pill.off {{ background: rgba(239,106,77,.20); color: #fca88f; }}
  .cb-pill.agent {{ background: rgba(99,102,241,.28); color: #c7cbff; }}
</style>
"""


def apply_styles() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def render_header() -> None:
    st.markdown(
        f"""
        <div class="cb-header">
          <div class="cb-logo">{LOGO_LIGHT}</div>
          <div>
            <div class="cb-title">Credi<span>bot</span></div>
            <div class="cb-sub">Assistente de crédito e câmbio</div>
          </div>
          <div class="cb-online">online</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
