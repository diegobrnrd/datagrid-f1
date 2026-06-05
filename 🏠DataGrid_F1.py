"""Página inicial do DataGrid F1."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.constants import PAISES_TRADUCAO
from utils.db import (
    get_constructor_count_by_season,
    get_dashboard_counts,
    get_grid_capacity_by_season,
    get_races_per_year,
    get_top_countries_by_constructors,
    get_top_countries_by_drivers,
    get_top_host_countries,
)
from utils.ui import (
    DARK_GRID,
    F1_RED,
    F1_RED_SCALE,
    add_vertical_space,
    apply_common_chart_layout,
    apply_metric_card_style,
    format_int_br,
    plotly_chart,
    render_footer,
    render_header,
    setup_page,
    translate_column,
)


@st.cache_data(show_spinner=False)
def load_dashboard_data() -> dict[str, object]:
    """Carrega todos os dados usados na visão global."""
    data = {
        "counts": get_dashboard_counts(),
        "races_per_year": get_races_per_year(),
        "host_countries": get_top_host_countries(),
        "grid_capacity": get_grid_capacity_by_season(),
        "team_count": get_constructor_count_by_season(),
        "driver_countries": get_top_countries_by_drivers(),
        "constructor_countries": get_top_countries_by_constructors(),
    }

    for key in ["host_countries", "driver_countries", "constructor_countries"]:
        data[key] = translate_column(data[key], "country", PAISES_TRADUCAO)

    return data


def render_global_kpis(counts: dict[str, int]) -> None:
    """Renderiza os quatro KPIs principais do projeto."""
    st.subheader("O Tamanho da História")
    columns = st.columns(4)
    kpis = [
        ("Pilotos Registrados", counts["drivers"]),
        ("Equipes Históricas", counts["constructors"]),
        ("Grandes Prêmios", counts["races"]),
        ("Circuitos Utilizados", counts["circuits"]),
    ]

    for column, (label, value) in zip(columns, kpis):
        column.metric(label, format_int_br(value))

    add_vertical_space()


def render_area_chart(
    df: pd.DataFrame,
    *,
    title: str,
    caption: str,
    x: str,
    y: str,
    y_label: str,
    empty_message: str,
) -> None:
    """Renderiza um gráfico de área padronizado."""
    st.markdown(f"#### {title}")
    st.caption(caption)

    if df.empty:
        st.info(empty_message)
        return

    fig = px.area(
        df,
        x=x,
        y=y,
        labels={x: "Temporada", y: y_label},
        color_discrete_sequence=[F1_RED],
    )
    fig.update_traces(
        line_color=F1_RED,
        hovertemplate=f"Temporada: %{{x}}<br>{y_label}: %{{y}}<extra></extra>",
    )
    apply_common_chart_layout(fig, height=320)
    fig.update_layout(
        xaxis=dict(dtick=5, showgrid=False),
        yaxis=dict(title=y_label, rangemode="tozero", showgrid=True, gridcolor=DARK_GRID),
    )
    plotly_chart(fig)


def render_horizontal_bar_chart(
    df: pd.DataFrame,
    *,
    title: str,
    caption: str,
    x: str,
    y: str,
    x_label: str,
    empty_message: str,
) -> None:
    """Renderiza gráfico horizontal de ranking."""
    st.markdown(f"#### {title}")
    st.caption(caption)

    if df.empty:
        st.info(empty_message)
        return

    fig = px.bar(
        df,
        x=x,
        y=y,
        orientation="h",
        labels={y: "País", x: x_label},
        color=x,
        color_continuous_scale=F1_RED_SCALE,
    )
    apply_common_chart_layout(fig, height=320, show_color_scale=False)
    fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor=DARK_GRID),
        yaxis=dict(showgrid=False, autorange="reversed"),
    )
    plotly_chart(fig)


def render_macro_view(data: dict[str, object]) -> None:
    """Renderiza a grade de gráficos do dashboard."""
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        render_area_chart(
            data["races_per_year"],
            title="📅 Evolução do Calendário de Corridas",
            caption="Evolução histórica da quantidade de Grandes Prêmios disputados a cada temporada.",
            x="year",
            y="total_races",
            y_label="Número de Corridas",
            empty_message="Não há dados suficientes para calcular a evolução do calendário.",
        )
    with chart_col2:
        render_horizontal_bar_chart(
            data["host_countries"],
            title="🌍 Top 10 Países-Sede de Corridas",
            caption="Ranking histórico dos países que mais sediaram Grandes Prêmios na F1.",
            x="total_races",
            y="country",
            x_label="Número de Corridas",
            empty_message="Não há dados suficientes para listar os países-sede.",
        )

    add_vertical_space()
    chart_row2_left, chart_row2_right = st.columns(2)
    with chart_row2_left:
        grid_capacity = data["grid_capacity"]
        grid_value_column = "grid_slots" if "grid_slots" in grid_capacity.columns else "avg_grid_slots"
        render_area_chart(
            grid_capacity,
            title="🚦 Evolução do Grid de Largada",
            caption="Variação da capacidade média/máxima de carros no grid ao longo das temporadas.",
            x="year",
            y=grid_value_column,
            y_label="Vagas no grid",
            empty_message="Não há dados suficientes para calcular a evolução do grid.",
        )
    with chart_row2_right:
        render_horizontal_bar_chart(
            data["driver_countries"],
            title="🌍 Top 10 Países de Origem de Pilotos",
            caption="Ranking dos países que mais revelaram pilotos para a Fórmula 1.",
            x="total_drivers",
            y="country",
            x_label="Pilotos",
            empty_message="Não há dados suficientes para listar os países de pilotos.",
        )

    add_vertical_space()
    chart_row3_left, chart_row3_right = st.columns(2)
    with chart_row3_left:
        render_area_chart(
            data["team_count"],
            title="🏭 Evolução de Construtoras Ativas",
            caption="Histórico da quantidade de equipes distintas participando a cada temporada.",
            x="year",
            y="total_teams",
            y_label="Equipes",
            empty_message="Não há dados suficientes para calcular a evolução das equipes.",
        )
    with chart_row3_right:
        render_horizontal_bar_chart(
            data["constructor_countries"],
            title="🌍 Top 10 Países de Origem de Construtoras",
            caption="Ranking dos países que mais fundaram equipes na Fórmula 1.",
            x="total_constructors",
            y="country",
            x_label="Equipes",
            empty_message="Não há dados suficientes para listar os países de equipes.",
        )


def render_navigation_guide() -> None:
    """Exibe o guia de navegação da aplicação."""
    st.divider()
    st.subheader("Explore o Banco de Dados")
    st.markdown("Utilize o menu lateral para navegar pelas seções da aplicação:")

    nav1, nav2, nav3 = st.columns(3)
    with nav1:
        st.info("**🏁 Corridas:** Mergulhe nos resultados oficiais, posições de largada, estatísticas de confiabilidade e destaques de qualquer evento histórico.")
        st.info("**🧑‍🚀 Pilotos:** Descubra o raio-x completo das lendas. Explore a evolução anual de carreira, taxas de conversão e rankings globais.")
    with nav2:
        st.success("**🏭 Construtoras:** Entenda o domínio da engenharia. Descubra quais equipes marcaram eras, seus pilotos pilares e históricos de abandonos.")
        st.success("**🗺️ Circuitos:** Explore mapas e imagens dos traçados. Descubra os reis de cada pista e a real importância da Pole Position.")
    with nav3:
        st.warning("**🏆 Campeonatos:** Reviva a história de cada temporada. Veja as classificações finais, os campeões e a evolução de pontos corrida a corrida.")

    st.caption("Dados fornecidos pelo projeto open-source F1DB.")


def main() -> None:
    setup_page(
        page_title="DataGrid F1 | Visão Global",
        page_icon="🏎️",
        initial_sidebar_state="expanded",
    )
    apply_metric_card_style()
    render_header(
        "🏎️ DataGrid F1",
        """
        Boas-vindas à plataforma analítica definitiva da Fórmula 1.
        Explore mais de sete décadas de dados históricos de engenharia, velocidade e estratégia, desde a primeira corrida em 1950 até os dias atuais.
        """,
    )

    dashboard_data = load_dashboard_data()
    render_global_kpis(dashboard_data["counts"])
    render_macro_view(dashboard_data)
    render_navigation_guide()
    render_footer()


if __name__ == "__main__":
    main()
