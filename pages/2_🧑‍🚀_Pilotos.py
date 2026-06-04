"""Página analítica de pilotos."""

from __future__ import annotations

from datetime import datetime
from typing import NamedTuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.constants import PAISES_TRADUCAO
from utils.db import (
    get_all_drivers,
    get_driver_career_evolution,
    get_driver_core_stats,
    get_driver_ranking_tables,
    get_driver_special_counts,
    get_driver_wins_by_constructor,
)
from utils.ui import (
    F1_RED,
    add_vertical_space,
    apply_common_chart_layout,
    plotly_chart,
    render_footer,
    render_header,
    setup_page,
    translate_column,
)


class EvolutionMetric(NamedTuple):
    title: str
    cumulative_column: str
    yearly_column: str
    label: str
    color: str


EVOLUTION_METRICS = [
    EvolutionMetric("Títulos Mundiais", "titles_cumulative", "titles_year", "Títulos", F1_RED),
    EvolutionMetric("Vitórias", "wins_cumulative", "wins_year", "Vitórias", "#FF7F0E"),
    EvolutionMetric("Pódios", "podiums_cumulative", "podiums_year", "Pódios", "#1F77B4"),
    EvolutionMetric("Poles", "poles_cumulative", "poles_year", "Poles", "#2CA02C"),
    EvolutionMetric("Voltas Mais Rápidas", "fastest_laps_cumulative", "fastest_laps_year", "Voltas Mais Rápidas", "#17BECF"),
    EvolutionMetric("Hat Tricks", "hat_tricks_cumulative", "hat_tricks_year", "Hat Tricks", "#9467BD"),
    EvolutionMetric("Grand Chelems", "grand_slems_cumulative", "grand_slems_year", "Grand Chelems", "#8C564B"),
]


@st.cache_data(show_spinner=False)
def load_drivers() -> pd.DataFrame:
    """Carrega e traduz a lista de pilotos."""
    return translate_column(get_all_drivers(), "nationality", PAISES_TRADUCAO)


@st.cache_data(show_spinner=False)
def load_driver_report(driver_id: int | str) -> dict[str, object]:
    """Carrega os dados detalhados de um piloto selecionado."""
    return {
        "stats": get_driver_core_stats(driver_id),
        "special_counts": get_driver_special_counts(driver_id),
        "wins_by_team": get_driver_wins_by_constructor(driver_id),
        "career_evolution": get_driver_career_evolution(driver_id),
    }


@st.cache_data(show_spinner=False)
def load_general_rankings() -> dict[str, pd.DataFrame]:
    return get_driver_ranking_tables()


def filter_drivers(drivers_df: pd.DataFrame) -> pd.DataFrame:
    """Renderiza campo de busca e filtra a lista de pilotos."""
    col_search, _ = st.columns([1, 2])
    with col_search:
        search_term = st.text_input("🔍 Pesquisar piloto (Ex: Senna, Hamilton):", "")

    if not search_term:
        return drivers_df
    return drivers_df[drivers_df["full_name"].str.contains(search_term, case=False, na=False)]


def to_int(value: object, default: int = 0) -> int:
    """Converte valores numéricos vindos do Pandas para int com fallback."""
    return default if pd.isna(value) else int(value)


def calculate_age(date_of_birth: object) -> str | int:
    """Calcula idade aproximada a partir do ano de nascimento."""
    if pd.isna(date_of_birth):
        return "N/A"
    dob = pd.to_datetime(date_of_birth, errors="coerce")
    if pd.isna(dob):
        return "N/A"
    return datetime.now().year - dob.year


def render_driver_bio_and_metrics(driver_name: str, driver_row: pd.Series, report: dict[str, object]) -> None:
    """Renderiza o cartão biográfico e os principais KPIs do piloto."""
    stats = report["stats"]
    special_counts = report["special_counts"]
    age = calculate_age(stats["date_of_birth"])
    permanent_number = to_int(stats["permanent_number"]) if pd.notna(stats["permanent_number"]) else "-"
    starts = to_int(stats["total_race_starts"])

    columns = st.columns([2, 1, 1, 1, 1, 1, 1, 1])
    with columns[0]:
        st.markdown(f"### {driver_name}")
        if pd.notna(stats["date_of_birth"]) and pd.notna(stats["permanent_number"]) and starts > 0:
            st.caption(f"🌍 {driver_row['nationality']} | 🎂 {age} anos | 🏎️ Nº {permanent_number}")
        else:
            birth_year = pd.to_datetime(stats["date_of_birth"], errors="coerce").year if pd.notna(stats["date_of_birth"]) else "N/A"
            st.caption(f"🌍 {driver_row['nationality']} | 🎂 {birth_year}")

    metrics = [
        ("Títulos Mundiais", stats["total_championship_wins"]),
        ("Vitórias", stats["total_race_wins"]),
        ("Pódios", stats["total_podiums"]),
        ("Poles", stats["total_pole_positions"]),
        ("Voltas Mais Rápidas", special_counts["fastest_count"]),
        ("Hat Tricks", special_counts["hat_count"]),
        ("Grand Chelems", special_counts["grand_count"]),
    ]
    for column, (label, value) in zip(columns[1:], metrics):
        column.metric(label, to_int(value))


def render_conversion_funnel(stats: pd.Series, driver_id: int | str) -> None:
    starts = to_int(stats["total_race_starts"])
    wins = to_int(stats["total_race_wins"])
    podiums = to_int(stats["total_podiums"])

    st.markdown("#### 🎯 Taxa de Conversão (Letalidade)")
    st.caption("De todas as corridas que largou, quantas viraram pódio e vitória?")
    if starts <= 0:
        st.info("Este piloto não possui largadas registradas.")
        return

    fig = go.Figure(
        go.Funnel(
            y=["Largadas", "Pódios", "Vitórias"],
            x=[starts, podiums, wins],
            textinfo="value+percent initial",
            textfont=dict(color=["white", "white", "black"]),
            marker={"color": ["#7A0000", F1_RED, "#FF6A6A"]},
        )
    )
    apply_common_chart_layout(fig, margin_top=20)
    plotly_chart(fig, key=f"funnel_{driver_id}")


def render_wins_by_team(wins_by_team: pd.DataFrame, driver_id: int | str) -> None:
    st.markdown("#### 🏭 Vitórias por Equipe")
    st.caption("A contribuição do piloto por construtora.")

    if wins_by_team.empty:
        st.info("Este piloto não possui vitórias registradas.")
        return

    fig = px.bar(
        wins_by_team,
        x="constructor",
        y="wins",
        labels={"constructor": "Equipe", "wins": "Vitórias"},
        color="wins",
        color_continuous_scale=["#FF6A6A", F1_RED, "#7A0000"],
    )
    apply_common_chart_layout(fig, margin_top=20, show_color_scale=False)
    fig.update_layout(showlegend=False)
    plotly_chart(fig, key=f"wins_by_team_{driver_id}")


def render_driver_radar(stats: pd.Series, driver_name: str, driver_id: int | str) -> None:
    starts = to_int(stats["total_race_starts"])
    wins = to_int(stats["total_race_wins"])
    podiums = to_int(stats["total_podiums"])
    poles = int(stats["total_pole_positions"] or 0)

    st.markdown("#### 🕸️ Perfil do Piloto (Radar)")
    st.caption("Comparativo percentual das métricas de sucesso.")
    if starts <= 0:
        st.info("Dados insuficientes para gerar o radar.")
        return

    win_rate = (wins / starts) * 100
    podium_rate = (podiums / starts) * 100
    pole_rate = (poles / starts) * 100

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=[win_rate, podium_rate, pole_rate, win_rate],
            theta=["Vitórias (%)", "Pódios (%)", "Poles (%)", "Vitórias (%)"],
            fill="toself",
            name=driver_name,
            line_color=F1_RED,
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(win_rate, podium_rate, pole_rate, 10) + 10])),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    plotly_chart(fig, key=f"radar_{driver_id}")


def render_performance_charts(driver_name: str, driver_id: int | str, report: dict[str, object]) -> None:
    """Renderiza os gráficos de profundidade analítica do piloto."""
    stats = report["stats"]
    columns = st.columns(3)
    with columns[0]:
        render_conversion_funnel(stats, driver_id)
    with columns[1]:
        render_wins_by_team(report["wins_by_team"], driver_id)
    with columns[2]:
        render_driver_radar(stats, driver_name, driver_id)


def render_evolution_line(plot_df: pd.DataFrame, metric: EvolutionMetric, driver_id: int | str) -> None:
    fig = px.line(
        plot_df,
        x="year",
        y=metric.cumulative_column,
        markers=True,
        labels={"year": "Ano", metric.cumulative_column: metric.label},
        custom_data=[plot_df[metric.yearly_column]],
    )
    fig.update_traces(
        line_color=metric.color,
        hovertemplate=(
            f"Ano: %{{x}}<br>{metric.label} (acumulado): %{{y}}"
            f"<br>{metric.label} no ano: %{{customdata[0]}}<extra></extra>"
        ),
    )
    apply_common_chart_layout(fig, margin_top=50)
    fig.update_layout(title=f"Evolução de {metric.title}", xaxis=dict(dtick=1))
    fig.update_yaxes(rangemode="tozero")
    plotly_chart(fig, key=f"line_{metric.cumulative_column}_{driver_id}")


def render_lollipop(plot_df: pd.DataFrame, metric: EvolutionMetric, driver_id: int | str) -> None:
    fig = go.Figure()
    years = plot_df["year"].tolist()
    values = plot_df[metric.yearly_column].tolist()
    for year, value in zip(years, values):
        fig.add_shape(type="line", x0=year, x1=year, y0=0, y1=value, line=dict(color=metric.color, width=2))
    fig.add_trace(
        go.Scatter(
            x=years,
            y=values,
            mode="markers",
            marker=dict(color=metric.color, size=10),
            hovertemplate=f"Ano: %{{x}}<br>{metric.label}: %{{y}}<extra></extra>",
        )
    )
    apply_common_chart_layout(fig, margin_top=40)
    fig.update_layout(title=f"{metric.title} por Ano")
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(rangemode="tozero")
    plotly_chart(fig, key=f"lollipop_{metric.yearly_column}_{driver_id}")


def render_career_evolution(driver_id: int | str, career_df: pd.DataFrame) -> None:
    st.subheader("📈 Evolução Anual de Carreira")

    if career_df.empty:
        st.info("Não há dados suficientes para montar os gráficos de evolução deste piloto.")
        return

    plot_df = career_df.copy()
    plot_df["year"] = pd.to_numeric(plot_df["year"], errors="coerce").astype(int)

    for metric in EVOLUTION_METRICS:
        left_col, right_col = st.columns([3, 2])
        with left_col:
            render_evolution_line(plot_df, metric, driver_id)
        with right_col:
            render_lollipop(plot_df, metric, driver_id)


def render_individual_tab(drivers_df: pd.DataFrame) -> None:
    filtered_drivers = filter_drivers(drivers_df)
    if filtered_drivers.empty:
        st.warning("Nenhum piloto encontrado com esse nome.")
        return

    driver_name = st.selectbox("Selecione um piloto para analisar:", filtered_drivers["full_name"])
    driver_row = filtered_drivers[filtered_drivers["full_name"] == driver_name].iloc[0]
    driver_id = driver_row["id"]
    report = load_driver_report(driver_id)

    render_driver_bio_and_metrics(driver_name, driver_row, report)
    st.divider()
    render_performance_charts(driver_name, driver_id, report)
    st.divider()
    render_career_evolution(driver_id, report["career_evolution"])


def render_general_table(title: str, df: pd.DataFrame) -> None:
    st.markdown(f"#### {title}")
    st.dataframe(df, width="stretch", hide_index=True)


def render_general_tab() -> None:
    st.subheader("📊 Estatísticas Gerais")
    ranking_tables = load_general_rankings()
    table_items = list(ranking_tables.items())

    for left_index in range(0, len(table_items), 2):
        columns = st.columns(2)
        for column, (title, df) in zip(columns, table_items[left_index : left_index + 2]):
            with column:
                render_general_table(title, df)


def main() -> None:
    setup_page("DataGrid F1 | Pilotos", "🧑‍🚀")
    render_header(
        "🧑‍🚀 Central Analítica do Piloto",
        "Raio-X completo da carreira: explore a conversão de resultados, histórico por equipe e o perfil de desempenho de cada piloto.",
    )

    drivers_df = load_drivers()
    tab_individual, tab_general = st.tabs(["Estatísticas Individuais", "Estatísticas Gerais"])
    with tab_individual:
        render_individual_tab(drivers_df)
    with tab_general:
        render_general_tab()

    render_footer()


if __name__ == "__main__":
    main()
