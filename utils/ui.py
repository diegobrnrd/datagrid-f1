"""Componentes visuais e helpers de apresentação do DataGrid F1."""

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

F1_RED = "#E10600"
F1_DARK_RED = "#7A0000"
F1_LIGHT_RED = "#FF6A6A"
TRANSPARENT = "rgba(0,0,0,0)"
DARK_GRID = "#333"
F1_RED_SCALE = [[0, F1_LIGHT_RED], [0.5, F1_RED], [1, F1_DARK_RED]]

_METRIC_CARD_CSS = """
<style>
    div[data-testid="metric-container"] {
        background-color: #1E1E24;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    div[data-testid="metric-container"] > div > div > div {
        color: #E10600 !important;
    }
</style>
"""


def setup_page(
    page_title: str,
    page_icon: str,
    *,
    layout: str = "wide",
    initial_sidebar_state: str | None = None,
) -> None:
    """Configura página e sidebar mantendo `set_page_config` como primeiro comando Streamlit."""
    config: dict[str, Any] = {
        "page_title": page_title,
        "page_icon": page_icon,
        "layout": layout,
    }
    if initial_sidebar_state:
        config["initial_sidebar_state"] = initial_sidebar_state

    st.set_page_config(**config)
    setup_sidebar()


def setup_sidebar() -> None:
    """Configura os elementos visuais da barra lateral."""
    st.logo("https://upload.wikimedia.org/wikipedia/commons/3/33/F1.svg")
    with st.sidebar:
        st.caption("Powered by [F1DB](https://github.com/f1db/f1db) • CC BY 4.0")


def apply_metric_card_style() -> None:
    """Aplica o estilo dos cards de métricas usados no dashboard inicial."""
    st.markdown(_METRIC_CARD_CSS, unsafe_allow_html=True)


def render_header(title: str, description: str) -> None:
    """Renderiza título, descrição e divisor da página."""
    st.title(title)
    st.markdown(description)
    st.divider()


def render_footer() -> None:
    """Renderiza o rodapé centralizado com crédito do projeto."""
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align:center; color: #666; font-size: 0.9rem;'>
            <p>🏎️ <b>DataGrid F1 Explorer</b></p>
            <p>Desenvolvido por
                <a href="https://github.com/diegobrnrd" target="_blank" style="color: #E10600; text-decoration: none;">
                    <b>Diego Bernardo</b>
                </a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def add_vertical_space(lines: int = 1) -> None:
    """Adiciona espaçamento vertical simples sem espalhar HTML nas páginas."""
    st.markdown("<br>" * max(lines, 1), unsafe_allow_html=True)


def format_int_br(value: int | float | str | None) -> str:
    """Formata números inteiros usando ponto como separador de milhar."""
    if pd.isna(value):
        return "0"
    return f"{int(value):,}".replace(",", ".")


def translate_column(df: pd.DataFrame, column: str, translations: Mapping[str, str]) -> pd.DataFrame:
    """Traduz uma coluna de texto preservando valores sem tradução cadastrada."""
    translated_df = df.copy()
    if column in translated_df.columns:
        translated_df[column] = translated_df[column].map(translations).fillna(translated_df[column])
    return translated_df


def apply_common_chart_layout(
    fig: go.Figure,
    *,
    height: int | None = None,
    margin_top: int = 10,
    show_color_scale: bool | None = None,
) -> go.Figure:
    """Aplica layout padrão transparente usado nos gráficos do app."""
    layout: dict[str, Any] = {
        "margin": dict(l=0, r=0, t=margin_top, b=0),
        "paper_bgcolor": TRANSPARENT,
        "plot_bgcolor": TRANSPARENT,
    }
    if height is not None:
        layout["height"] = height
    if show_color_scale is not None:
        layout["coloraxis_showscale"] = show_color_scale

    fig.update_layout(**layout)
    return fig


def plotly_chart(fig: go.Figure, *, key: str | None = None) -> None:
    """Renderiza gráfico em largura total com uma chamada única."""
    st.plotly_chart(fig, width="stretch", key=key)
