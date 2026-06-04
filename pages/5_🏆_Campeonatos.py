"""Página de classificações e evolução dos campeonatos."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.db import (
    get_constructor_points_progression,
    get_constructor_standings,
    get_driver_points_progression,
    get_driver_standings,
    get_seasons,
)
from utils.ui import add_vertical_space, apply_common_chart_layout, plotly_chart, render_footer, render_header, setup_page


@st.cache_data(show_spinner=False)
def load_seasons() -> list[int]:
    return get_seasons()


@st.cache_data(show_spinner=False)
def load_championship_data(year: int) -> dict[str, pd.DataFrame]:
    """Carrega classificações e progressões de pontos da temporada."""
    return {
        "driver_standings": get_driver_standings(year),
        "constructor_standings": get_constructor_standings(year),
        "driver_progression": get_driver_points_progression(year),
        "constructor_progression": get_constructor_points_progression(year),
    }


def select_season(seasons: list[int]) -> int:
    """Renderiza o seletor centralizado de temporada."""
    _, col_selector, _ = st.columns([1, 2, 1])
    with col_selector:
        selected_season = st.selectbox(
            "Selecione o ano da temporada para visualizar o campeonato:",
            seasons,
            index=0,
        )
    add_vertical_space()
    return int(selected_season)


def get_champion_row(standings: pd.DataFrame) -> pd.DataFrame:
    """Retorna a linha do campeão; usa líder de pontos como fallback."""
    if standings.empty:
        return standings
    champion_row = standings[standings["championship_won"] == 1]
    return champion_row if not champion_row.empty else standings.iloc[[0]]


def render_crowning(selected_season: int, driver_standings: pd.DataFrame, constructor_standings: pd.DataFrame) -> None:
    """Renderiza os cards de campeão/líder da temporada."""
    if driver_standings.empty:
        return

    driver_champion = get_champion_row(driver_standings).iloc[0]
    columns = st.columns(2)

    with columns[0]:
        if driver_champion.get("championship_won") == 1:
            st.success(
                f"**Mundial de Pilotos ({selected_season})**\n\n"
                f"🏆 Campeão: **{driver_champion['driver_name']}** ({driver_champion['points']:.1f} pts)"
            )
        else:
            st.info(
                f"**Mundial de Pilotos ({selected_season})**\n\n"
                f"🏁 Líder: **{driver_champion['driver_name']}** ({driver_champion['points']:.1f} pts)\n\n"
                "*Campeonato em andamento*"
            )

    with columns[1]:
        if selected_season < 1958:
            st.warning(
                f"**Mundial de Construtores ({selected_season})**\n\n"
                "O Mundial de Construtores ainda não havia sido criado (iniciou em 1958)."
            )
            return
        if constructor_standings.empty:
            st.info(f"**Mundial de Construtores ({selected_season})**\n\nDados indisponíveis.")
            return

        constructor_champion = get_champion_row(constructor_standings).iloc[0]
        if constructor_champion.get("championship_won") == 1:
            st.success(
                f"**Mundial de Construtores ({selected_season})**\n\n"
                f"🏭 Campeã: **{constructor_champion['constructor_name']}** ({constructor_champion['points']:.1f} pts)"
            )
        else:
            st.info(
                f"**Mundial de Construtores ({selected_season})**\n\n"
                f"🏁 Líder: **{constructor_champion['constructor_name']}** ({constructor_champion['points']:.1f} pts)\n\n"
                "*Campeonato em andamento*"
            )

    add_vertical_space()


def render_driver_standings(selected_season: int, driver_standings: pd.DataFrame) -> None:
    st.subheader(f"Mundial de Pilotos - Tabela Final de {selected_season}")
    if driver_standings.empty:
        st.info("Dados de classificação de pilotos não encontrados para esta temporada.")
        return

    st.dataframe(
        driver_standings[["position", "driver_name", "points", "championship_won"]],
        width="stretch",
        hide_index=True,
        column_config={
            "position": st.column_config.TextColumn("Posição", width="small"),
            "driver_name": "Piloto",
            "points": st.column_config.NumberColumn("Pontuação Total", format="%.1f"),
            "championship_won": st.column_config.CheckboxColumn("Campeão Mundial 🏆"),
        },
    )


def render_constructor_standings(selected_season: int, constructor_standings: pd.DataFrame) -> None:
    st.subheader(f"Mundial de Construtores - Tabela Final de {selected_season}")
    if selected_season < 1958:
        st.warning("Historicamente, o Campeonato Mundial de Construtores da FIA só foi introduzido em 1958. Portanto, não há classificação de equipes para este ano.")
        return
    if constructor_standings.empty:
        st.info("Dados de classificação de construtores não encontrados para esta temporada.")
        return

    st.dataframe(
        constructor_standings[["position", "constructor_name", "points", "championship_won"]],
        width="stretch",
        hide_index=True,
        column_config={
            "position": st.column_config.TextColumn("Posição", width="small"),
            "constructor_name": "Construtora",
            "points": st.column_config.NumberColumn("Pontuação Total", format="%.1f"),
            "championship_won": st.column_config.CheckboxColumn("Campeã Mundial 🏆"),
        },
    )


def render_standings_tabs(selected_season: int, data: dict[str, pd.DataFrame]) -> None:
    tab_drivers, tab_teams = st.tabs(["👨‍🚀 Classificação de Pilotos", "🏭 Classificação de Construtores"])
    with tab_drivers:
        render_driver_standings(selected_season, data["driver_standings"])
    with tab_teams:
        render_constructor_standings(selected_season, data["constructor_standings"])


def render_progression_chart(
    progression_df: pd.DataFrame,
    *,
    entity_column: str,
    entity_label: str,
    color_sequence: list[str],
) -> None:
    """Renderiza gráfico de pontos acumulados corrida a corrida."""
    race_order = progression_df.sort_values("race_round")["race_label"].drop_duplicates().tolist()
    fig = px.line(
        progression_df,
        x="race_label",
        y="cumulative_points",
        color=entity_column,
        markers=True,
        custom_data=["race_name", "race_points"],
        labels={
            "race_label": "Corrida",
            "cumulative_points": "Pontos acumulados",
            entity_column: entity_label,
            "race_name": "Grande Prêmio",
        },
        hover_data={"race_name": True, "race_round": False, "cumulative_points": ":.1f"},
        category_orders={"race_label": race_order},
        color_discrete_sequence=color_sequence,
    )
    fig.update_traces(
        hovertemplate=(
            "Corrida: %{x}<br>"
            "Grande Prêmio: %{customdata[0]}<br>"
            "Pontos acumulados: %{y:.1f}<br>"
            "Pontos na corrida: %{customdata[1]:.1f}<extra></extra>"
        )
    )
    apply_common_chart_layout(fig, margin_top=20)
    fig.update_layout(legend_title_text=entity_label)
    plotly_chart(fig)


def render_points_progression(selected_season: int, data: dict[str, pd.DataFrame]) -> None:
    st.subheader("📈 Evolução da Pontuação na Temporada")
    st.caption("Cada linha mostra a pontuação acumulada corrida a corrida para os pilotos e as equipes que somaram pontos no ano selecionado.")

    driver_col, constructor_col = st.columns(2)
    with driver_col:
        st.markdown("#### 🏎️ Pilotos")
        driver_progression = data["driver_progression"]
        if driver_progression.empty:
            st.info("Não há pontos acumulados de pilotos para exibir nesta temporada.")
        else:
            render_progression_chart(
                driver_progression,
                entity_column="driver_name",
                entity_label="Pilotos",
                color_sequence=px.colors.qualitative.Dark24,
            )

    with constructor_col:
        st.markdown("#### 🏭 Construtoras")
        constructor_progression = data["constructor_progression"]
        if selected_season < 1958:
            st.warning("O Mundial de Construtores só existe a partir de 1958.")
        elif constructor_progression.empty:
            st.info("Não há pontos acumulados de construtoras para exibir nesta temporada.")
        else:
            render_progression_chart(
                constructor_progression,
                entity_column="constructor_name",
                entity_label="Construtoras",
                color_sequence=px.colors.qualitative.Set2,
            )


def main() -> None:
    setup_page("DataGrid F1 | Campeonatos", "🏆")
    render_header(
        "🏆 Tabelas de Classificação Final",
        "Reviva a história de cada temporada: veja quem dominou o Mundial de Pilotos e qual engenharia levou o troféu no Mundial de Construtores.",
    )

    selected_season = select_season(load_seasons())
    data = load_championship_data(selected_season)
    render_crowning(selected_season, data["driver_standings"], data["constructor_standings"])
    render_standings_tabs(selected_season, data)
    render_points_progression(selected_season, data)
    render_footer()


if __name__ == "__main__":
    main()
