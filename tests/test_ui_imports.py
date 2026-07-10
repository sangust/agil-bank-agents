"""Regressão: garante que o pacote `ui` importa sem ModuleNotFoundError.

Pula localmente quando o Streamlit não está instalado; roda no CI (dep principal).
"""
import pytest

pytest.importorskip("streamlit")


def test_ui_package_importa():
    from ui import service, state, styles  # noqa: F401
    from ui.components import chat, sidebar  # noqa: F401

    assert hasattr(service, "enviar")
    assert hasattr(service, "health")
    assert hasattr(state, "init_session")
    assert hasattr(chat, "render_history")
    assert hasattr(sidebar, "render_sidebar")


def test_ui_entrypoint_importa():
    # Importar o entrypoint não deve falhar (define main(), não a executa).
    import ui.streamlit_app as app

    assert hasattr(app, "main")
