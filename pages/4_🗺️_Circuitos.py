"""Página de mapas e estatísticas de circuitos."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.circuit_assets import get_available_circuit_layouts
from utils.constants import PAISES_TRADUCAO
from utils.db import get_all_circuits, get_circuit_grid_wins, get_circuit_record, get_races_by_season, get_seasons
from utils.ui import F1_RED, add_vertical_space, apply_common_chart_layout, plotly_chart, render_footer, render_header, setup_page, translate_column

IMAGE_VARIANTS = {
    "black": {"label": "Preto", "folder": "black"},
    "black-outline": {"label": "Preto com contorno", "folder": "black-outline"},
    "white": {"label": "Branco", "folder": "white"},
    "white-outline": {"label": "Branco com contorno", "folder": "white-outline"},
}


@st.cache_data(show_spinner=False)
def load_circuits() -> pd.DataFrame:
    """Carrega circuitos com países traduzidos."""
    return translate_column(get_all_circuits(), "country", PAISES_TRADUCAO)


@st.cache_data(show_spinner=False)
def load_current_season_circuits(circuits_df: pd.DataFrame) -> tuple[int, pd.DataFrame]:
    """Retorna temporada mais recente e circuitos presentes nela."""
    current_season = get_seasons()[0]
    current_races = get_races_by_season(current_season)
    current_circuit_names = current_races["circuit_name"].unique()
    current_map_df = circuits_df[circuits_df["name"].isin(current_circuit_names)].dropna(subset=["latitude", "longitude"]).copy()
    return current_season, current_map_df


def render_map(df: pd.DataFrame, key: str) -> None:
    """Renderiza um mapa interativo com os circuitos."""
    if df.empty:
        st.info("Não há dados de latitude e longitude disponíveis para montar o mapa.")
        return

    fig = px.scatter_map(
        df,
        lat="latitude",
        lon="longitude",
        hover_name="name",
        hover_data={
            "place_name": True,
            "country": True,
            "total_races_held": True,
            "latitude": False,
            "longitude": False,
        },
        labels={
            "name": "Circuito",
            "place_name": "Local",
            "country": "País",
            "total_races_held": "Total de Corridas",
        },
        color_discrete_sequence=[F1_RED],
        zoom=1.2,
        height=450,
    )
    fig.update_layout(mapbox_style="carto-darkmatter", margin={"r": 0, "t": 0, "l": 0, "b": 0})
    plotly_chart(fig, key=key)


def format_record(record_df: pd.DataFrame) -> str:
    """Formata o retorno do recorde de circuito."""
    if record_df.empty:
        return "Dados indisponíveis"
    names = " / ".join(record_df["name"])
    total = int(record_df.iloc[0]["total"])
    label = record_df.iloc[0]["label"]
    return f"{names} ({total} {label})"


def render_circuit_facts(circuit_row: pd.Series) -> None:
    columns = st.columns(4)
    columns[0].metric("Localização", f"{circuit_row['place_name']} ({circuit_row['country']})")
    columns[1].metric("Extensão", f"{circuit_row['length']} km" if pd.notna(circuit_row["length"]) else "N/A")
    columns[2].metric("Curvas", int(circuit_row["turns"]) if pd.notna(circuit_row["turns"]) else "N/A")
    columns[3].metric("Total de Corridas", int(circuit_row["total_races_held"]) if pd.notna(circuit_row["total_races_held"]) else 0)
    add_vertical_space()


def render_track_kings(circuit_id: int | str) -> None:
    st.markdown("#### 👑 Reis da Pista")
    st.caption("Quem dominou este traçado na história.")

    driver_wins = format_record(get_circuit_record(circuit_id, "driver", "wins"))
    team_wins = format_record(get_circuit_record(circuit_id, "constructor", "wins"))
    driver_podiums = format_record(get_circuit_record(circuit_id, "driver", "podiums"))
    team_podiums = format_record(get_circuit_record(circuit_id, "constructor", "podiums"))
    driver_poles = format_record(get_circuit_record(circuit_id, "driver", "poles"))
    team_poles = format_record(get_circuit_record(circuit_id, "constructor", "poles"))

    st.info(f"**🏆 Maior Vencedor**\n\n🏎️ **Piloto:** {driver_wins}\n\n🏭 **Equipe:** {team_wins}")
    st.success(f"**🍾 Mais Pódios**\n\n🏎️ **Piloto:** {driver_podiums}\n\n🏭 **Equipe:** {team_podiums}")
    st.warning(f"**⏱️ Mais Poles**\n\n🏎️ **Piloto:** {driver_poles}\n\n🏭 **Equipe:** {team_poles}")


def render_grid_importance(circuit_id: int | str, key_prefix: str) -> None:
    st.markdown("#### 🚦 A Importância da Classificação")
    st.caption("Relação entre a posição de largada e as vitórias conquistadas nesta pista.")

    grid_wins = get_circuit_grid_wins(circuit_id)
    if grid_wins.empty:
        st.info("Não há dados históricos de grid de largada versus vitórias para este circuito.")
        return

    grid_wins = grid_wins.copy()
    grid_wins["grid_pos"] = grid_wins["grid_pos"].astype(str)
    fig = px.bar(
        grid_wins,
        x="grid_pos",
        y="wins",
        labels={"grid_pos": "Posição no Grid de Largada", "wins": "Total de Vitórias"},
        color="wins",
        color_continuous_scale=["#FF6A6A", F1_RED, "#7A0000"],
    )
    apply_common_chart_layout(fig, show_color_scale=False)
    fig.update_layout(xaxis_type="category")
    plotly_chart(fig, key=f"fig_grid_{key_prefix}_{circuit_id}")

    pole_wins = grid_wins[grid_wins["grid_pos"] == "1"]["wins"].sum() if "1" in grid_wins["grid_pos"].values else 0
    total_wins = grid_wins["wins"].sum()
    if total_wins > 0:
        pole_percentage = (pole_wins / total_wins) * 100
        st.caption(f"🏁 **Insight:** Em **{pole_percentage:.1f}%** das vezes, quem largou na Pole Position (1º lugar) venceu a corrida neste circuito.")


def render_circuit_image(circuit_row: pd.Series, selected_circuit_name: str, key_prefix: str) -> None:
    st.subheader("🖼️ Imagem do Circuito")
    col_select, col_image = st.columns([1, 2])
    circuit_id = circuit_row["id"]

    with col_select:
        selected_variant = st.selectbox(
            "Escolha o tipo de imagem do circuito:",
            options=list(IMAGE_VARIANTS.keys()),
            index=list(IMAGE_VARIANTS.keys()).index("white-outline"),
            format_func=lambda key: IMAGE_VARIANTS[key]["label"],
            key=f"circuit_image_variant_{key_prefix}_{circuit_id}",
        )
        available_layouts = get_available_circuit_layouts(circuit_row, selected_variant)
        selected_layout_path = None
        if available_layouts:
            selected_layout_path = st.selectbox(
                "Escolha o traçado:",
                options=available_layouts,
                format_func=lambda path: f"Traçado {path.stem.rsplit('-', 1)[-1]}",
                key=f"circuit_layout_{key_prefix}_{circuit_id}_{selected_variant}",
            )

    with col_image:
        if selected_layout_path:
            st.image(
                str(selected_layout_path),
                caption=(
                    f"{selected_circuit_name} - {IMAGE_VARIANTS[selected_variant]['label']} - "
                    f"{selected_layout_path.stem.rsplit('-', 1)[-1]}"
                ),
                width=520,
            )
        else:
            st.info("Não foi encontrada imagem SVG para este circuito.")


def render_circuit_analysis(circuits_df: pd.DataFrame, selected_circuit_name: str, key_prefix: str) -> None:
    """Gera o painel de raio-X do circuito."""
    circuit_row = circuits_df[circuits_df["name"] == selected_circuit_name].iloc[0]
    circuit_id = circuit_row["id"]

    render_circuit_facts(circuit_row)
    col_kings, col_grid = st.columns([1, 2])
    with col_kings:
        render_track_kings(circuit_id)
    with col_grid:
        render_grid_importance(circuit_id, key_prefix)

    st.divider()
    render_circuit_image(circuit_row, selected_circuit_name, key_prefix)


def render_season_tab(circuits_df: pd.DataFrame, current_season: int, current_map_df: pd.DataFrame) -> None:
    st.subheader(f"Visão da Temporada Atual: Circuitos de {current_season}")
    st.caption(f"Cada ponto representa um circuito no calendário da temporada {current_season}.")
    render_map(current_map_df, "map_season")
    st.divider()

    st.subheader("🔍 Raio-X do Traçado")
    if current_map_df.empty:
        st.info("Não há circuitos com coordenadas para a temporada atual.")
        return

    selected_circuit = st.selectbox("Selecione um circuito para analisar:", current_map_df["name"], key="selectbox_season")
    if selected_circuit:
        render_circuit_analysis(circuits_df, selected_circuit, "season")


def render_global_tab(circuits_df: pd.DataFrame, map_df: pd.DataFrame) -> None:
    st.subheader("Visão Global: Todos os Circuitos")
    st.caption("Cada ponto representa um circuito que já sediou ao menos um Grande Prêmio oficial.")
    render_map(map_df, "map_global")
    st.divider()

    st.subheader("🔍 Raio-X do Traçado")
    selected_circuit = st.selectbox("Selecione um circuito para analisar:", circuits_df["name"], key="selectbox_global")
    if selected_circuit:
        render_circuit_analysis(circuits_df, selected_circuit, "global")


def main() -> None:
    setup_page("DataGrid F1 | Circuitos", "🗺️")
    render_header(
        "🗺️ Geografia e Estatísticas de Pista",
        "Explore os palcos onde a história foi escrita. Veja a localização global das pistas e entenda a importância de largar na frente em cada traçado.",
    )

    circuits_df = load_circuits()
    map_df = circuits_df.dropna(subset=["latitude", "longitude"]).copy()
    current_season, current_map_df = load_current_season_circuits(circuits_df)

    tab_season, tab_global = st.tabs(["Visão da Temporada", "Visão Global"])
    with tab_season:
        render_season_tab(circuits_df, current_season, current_map_df)
    with tab_global:
        render_global_tab(circuits_df, map_df)

    render_footer()


if __name__ == "__main__":
    main()
