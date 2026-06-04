"""Página de exploração de corridas e resultados."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.constants import DID_NOT_START_STATUSES, FINISHED_STATUS, STATUS_TRADUCAO
from utils.db import get_race_results, get_races_by_season, get_seasons
from utils.ui import add_vertical_space, apply_common_chart_layout, plotly_chart, render_footer, render_header, setup_page


@st.cache_data(show_spinner=False)
def load_seasons() -> list[int]:
    return get_seasons()


@st.cache_data(show_spinner=False)
def load_races(year: int) -> pd.DataFrame:
    races = get_races_by_season(year).copy()
    if not races.empty:
        races["date"] = pd.to_datetime(races["date"], errors="coerce").dt.strftime("%d/%m/%Y")
    return races


@st.cache_data(show_spinner=False)
def load_results(race_id: int) -> pd.DataFrame:
    return get_race_results(race_id)


def prepare_results(results: pd.DataFrame) -> pd.DataFrame:
    """Traduz e normaliza campos do resultado da corrida."""
    prepared = results.copy()
    prepared["status"] = prepared["status"].map(STATUS_TRADUCAO).fillna(prepared["status"])
    prepared["time"] = prepared["time"].fillna("---")
    prepared["status"] = prepared["status"].fillna(FINISHED_STATUS)
    prepared["laps"] = prepared["laps"].fillna(0).astype(int)
    prepared["points"] = prepared["points"].fillna(0).astype(float)
    return prepared


def select_race() -> tuple[pd.Series, int]:
    """Renderiza filtros em cascata e retorna a corrida selecionada."""
    seasons = load_seasons()
    col_season, col_race = st.columns([1, 3])

    with col_season:
        selected_season = st.selectbox("1. Selecione a Temporada:", seasons)

    races = load_races(selected_season)
    if races.empty:
        st.warning(f"Nenhuma corrida registrada para o ano de {selected_season}.")
        st.stop()

    with col_race:
        race_option = st.selectbox(
            "2. Selecione a Etapa (Grand Prix):",
            races.index,
            format_func=lambda idx: (
                f"Etapa {races.loc[idx, 'round']} - "
                f"{races.loc[idx, 'official_name']} ({races.loc[idx, 'date']})"
            ),
        )

    selected_race = races.loc[race_option]
    return selected_race, int(selected_race["id"])


def render_race_summary(selected_race: pd.Series) -> None:
    """Exibe o painel de resumo da corrida."""
    st.markdown(f"### 🏆 {selected_race['official_name']}")

    metrics = st.columns(4)
    metrics[0].metric("Data", selected_race["date"])
    metrics[1].metric("Circuito", selected_race["circuit_name"])
    metrics[2].metric("Localização", selected_race["location"])
    laps = int(selected_race["laps"]) if pd.notna(selected_race["laps"]) else "N/A"
    metrics[3].metric("Voltas Realizadas", laps)
    add_vertical_space()


def render_results_tab(results: pd.DataFrame) -> None:
    st.dataframe(
        results[["position", "driver_name", "constructor_name", "laps", "time", "points", "status"]],
        width="stretch",
        hide_index=True,
        column_config={
            "position": st.column_config.TextColumn("Posição", width="small"),
            "driver_name": "Piloto",
            "constructor_name": "Equipe",
            "laps": st.column_config.NumberColumn("Voltas", width="small"),
            "time": "Tempo / Gap",
            "points": st.column_config.NumberColumn("Pontos", format="%.1f"),
            "status": "Situação",
        },
    )


def render_grid_tab(results: pd.DataFrame) -> None:
    grid_df = results.copy()
    grid_df["grid_num"] = pd.to_numeric(grid_df["grid"], errors="coerce").fillna(999)
    grid_df = grid_df.sort_values("grid_num")

    st.dataframe(
        grid_df[["grid", "driver_name", "constructor_name"]],
        width="stretch",
        hide_index=True,
        column_config={
            "grid": st.column_config.TextColumn("Posição no Grid", width="small"),
            "driver_name": "Piloto",
            "constructor_name": "Equipe",
        },
    )


def classify_status(status_text: str) -> str:
    """Classifica a situação final em grupos usados no gráfico de confiabilidade."""
    if status_text == FINISHED_STATUS:
        return "Concluíram"
    if status_text in DID_NOT_START_STATUSES:
        return "Não Largaram"
    return "Abandonaram"


def render_race_highlights(results: pd.DataFrame) -> None:
    """Renderiza destaques esportivos da corrida."""
    st.subheader("Destaques")

    pole_row = results[results["pole_position"] == 1]
    fastest_row = results[results["fastest_lap"] == 1]
    winner_row = results.iloc[0]
    hat_trick_row = results[
        (results["pole_position"] == 1)
        & (results["fastest_lap"] == 1)
        & (results["position_number"] == 1)
    ]
    grand_chelem_row = results[results["grand_slam"] == 1]

    pole_name = pole_row.iloc[0]["driver_name"] if not pole_row.empty else "Desconhecido"
    fastest_name = fastest_row.iloc[0]["driver_name"] if not fastest_row.empty else "Desconhecido"

    st.success(f"**Pole Position:**\n\n🥇 {pole_name}")
    st.success(f"**Vencedor:**\n\n🏆 {winner_row['driver_name']}\n\n{winner_row['constructor_name']}")
    st.success(f"**Volta Mais Rápida:**\n\n⏱️ {fastest_name}")

    if not hat_trick_row.empty:
        st.success(f"**Hat Trick:**\n\n✨ {hat_trick_row.iloc[0]['driver_name']}\n\nPole + volta mais rápida + vitória")
    if not grand_chelem_row.empty:
        st.success(
            f"**Grand Chelem:**\n\n👑 {grand_chelem_row.iloc[0]['driver_name']}\n\n"
            "Pole + volta mais rápida + vitória + todas as voltas lideradas"
        )


def render_reliability_chart(results: pd.DataFrame) -> None:
    """Renderiza gráfico de confiabilidade e lista de abandonos."""
    st.subheader("⚙️ Taxa de Confiabilidade")
    st.caption("Proporção de pilotos que concluíram a prova versus abandonos e não largadas.")

    reliability_df = results.copy()
    reliability_df["is_finished"] = reliability_df["status"].apply(classify_status)
    reliability_counts = reliability_df["is_finished"].value_counts().reset_index()
    reliability_counts.columns = ["Status", "Quantidade"]

    fig = px.pie(
        reliability_counts,
        names="Status",
        values="Quantidade",
        hole=0.5,
        color="Status",
        color_discrete_map={
            "Concluíram": "#28a745",
            "Abandonaram": "#dc3545",
            "Não Largaram": "#6c757d",
        },
    )
    apply_common_chart_layout(fig, margin_top=30)
    plotly_chart(fig)

    abandonments = reliability_df[reliability_df["is_finished"] == "Abandonaram"]
    if not abandonments.empty:
        with st.expander("Ver motivos dos abandonos"):
            st.dataframe(
                abandonments[["driver_name", "constructor_name", "status"]],
                width="stretch",
                hide_index=True,
                column_config={
                    "driver_name": "Piloto",
                    "constructor_name": "Equipe",
                    "status": "Situação",
                },
            )


def render_insights_tab(results: pd.DataFrame) -> None:
    col_highlights, col_chart = st.columns([1, 2])
    with col_highlights:
        render_race_highlights(results)
    with col_chart:
        render_reliability_chart(results)


def main() -> None:
    setup_page("DataGrid F1 | Corridas", "🏁")
    render_header(
        "🏁 Explorador de Grandes Prêmios",
        "Mergulhe nos resultados oficiais, posições de largada e estatísticas de confiabilidade de qualquer corrida da história.",
    )

    selected_race, race_id = select_race()
    render_race_summary(selected_race)

    results = load_results(race_id)
    if results.empty:
        st.info("Os resultados detalhados desta corrida ainda não estão disponíveis no banco de dados.")
        st.stop()

    results = prepare_results(results)
    tab_results, tab_grid, tab_insights = st.tabs(["🏎️ Resultado Oficial", "🚦 Grid de Largada", "📊 Insights da Corrida"])
    with tab_results:
        render_results_tab(results)
    with tab_grid:
        render_grid_tab(results)
    with tab_insights:
        render_insights_tab(results)

    render_footer()


if __name__ == "__main__":
    main()
