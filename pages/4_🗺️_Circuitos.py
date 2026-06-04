import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import execute_query, get_all_circuits, get_seasons, get_races_by_season
from utils.circuit_assets import get_available_circuit_layouts
from utils.constants import PAISES_TRADUCAO
from utils.ui import setup_sidebar, render_footer

IMAGE_VARIANTS = {
    "black": {"label": "Preto", "folder": "black"},
    "black-outline": {"label": "Preto com contorno", "folder": "black-outline"},
    "white": {"label": "Branco", "folder": "white"},
    "white-outline": {"label": "Branco com contorno", "folder": "white-outline"},
}

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="DataGrid F1 | Circuitos",
    page_icon="🗺️",
    layout="wide"
)

setup_sidebar()

st.title("🗺️ Geografia e Estatísticas de Pista")
st.markdown("Explore os palcos onde a história foi escrita. Veja a localização global das pistas e entenda a importância de largar na frente em cada traçado.")
st.divider()

# ==========================================
# 2. CARREGAMENTO DOS CIRCUITOS
# ==========================================
@st.cache_data(show_spinner=False)
def load_circuits():
    df = get_all_circuits()
    df["country"] = df["country"].map(PAISES_TRADUCAO).fillna(df["country"])
    return df

circuits_df = load_circuits()
map_df = circuits_df.dropna(subset=["latitude", "longitude"]).copy()

current_season = get_seasons()[0]
current_races = get_races_by_season(current_season)
current_circuit_names = current_races["circuit_name"].unique()
current_map_df = circuits_df[circuits_df["name"].isin(current_circuit_names)].dropna(subset=["latitude", "longitude"]).copy()

# ==========================================
# 3. FUNÇÕES AUXILIARES DE RENDERIZAÇÃO
# ==========================================
def render_map(df: pd.DataFrame, key: str):
    """Renderiza um mapa interativo com os circuitos."""
    fig_map = px.scatter_map(
        df, 
        lat="latitude", 
        lon="longitude", 
        hover_name="name", 
        hover_data={
            "place_name": True, 
            "country": True, 
            "total_races_held": True,
            "latitude": False, 
            "longitude": False
        },
        labels={
            "name": "Circuito",
            "place_name": "Local",
            "country": "País",
            "total_races_held": "Total de Corridas"
        },
        color_discrete_sequence=["#E10600"], # Cor vermelha F1
        zoom=1.2, 
        height=450
    )

    fig_map.update_layout(
        mapbox_style="carto-darkmatter",
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    st.plotly_chart(fig_map, width='stretch', key=key)

def render_circuit_analysis(selected_circuit_name: str, key_prefix: str):
    """Gera o painel de raio-X do circuito com informações e recordes históricos."""
    circuit_row = circuits_df[circuits_df["name"] == selected_circuit_name].iloc[0]
    circuit_id = circuit_row["id"]

    # Ficha técnica
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    col_kpi1.metric("Localização", f"{circuit_row['place_name']} ({circuit_row['country']})")
    col_kpi2.metric("Extensão", f"{circuit_row['length']} km" if pd.notna(circuit_row['length']) else "N/A")
    col_kpi3.metric("Curvas", int(circuit_row["turns"]) if pd.notna(circuit_row["turns"]) else "N/A")
    col_kpi4.metric("Total de Corridas", int(circuit_row["total_races_held"]) if pd.notna(circuit_row["total_races_held"]) else 0)

    st.markdown("<br>", unsafe_allow_html=True)

    # Reis da Pista & Importância do Grid
    col_kings, col_grid = st.columns([1, 2])

    with col_kings:
        st.markdown("#### 👑 Reis da Pista")
        st.caption("Quem dominou este traçado na história.")
        
        def get_circuit_record(cid, entity_type, metric_type):
            join_table = "driver e ON rr.driver_id = e.id" if entity_type == 'driver' else "constructor e ON rr.constructor_id = e.id"
            name_col = "e.last_name as name" if entity_type == 'driver' else "e.name as name"
            
            if metric_type == 'wins':
                cond = "rr.position_number = 1"
                label = "vitórias"
            elif metric_type == 'podiums':
                cond = "rr.position_number IN (1, 2, 3)"
                label = "pódios"
            else:
                cond = "rr.pole_position = 1"
                label = "poles"
                
            q = f"""
                SELECT {name_col}, COUNT(*) as total
                FROM race_result rr
                JOIN race r ON rr.race_id = r.id
                JOIN {join_table}
                WHERE r.circuit_id = ? AND {cond}
                GROUP BY e.id
                ORDER BY total DESC
                LIMIT 1
            """
            res = execute_query(q, (cid,))
            return f"{res.iloc[0]['name']} ({res.iloc[0]['total']} {label})" if not res.empty else "Dados indisponíveis"

        driver_wins_str = get_circuit_record(circuit_id, 'driver', 'wins')
        team_wins_str = get_circuit_record(circuit_id, 'constructor', 'wins')
        
        driver_podiums_str = get_circuit_record(circuit_id, 'driver', 'podiums')
        team_podiums_str = get_circuit_record(circuit_id, 'constructor', 'podiums')
        
        driver_poles_str = get_circuit_record(circuit_id, 'driver', 'poles')
        team_poles_str = get_circuit_record(circuit_id, 'constructor', 'poles')
        
        st.info(f"**🏆 Maior Vencedor**\n\n🏎️ **Piloto:** {driver_wins_str}\n\n🏭 **Equipe:** {team_wins_str}")
        st.success(f"**🍾 Mais Pódios**\n\n🏎️ **Piloto:** {driver_podiums_str}\n\n🏭 **Equipe:** {team_podiums_str}")
        st.warning(f"**⏱️ Mais Poles**\n\n🏎️ **Piloto:** {driver_poles_str}\n\n🏭 **Equipe:** {team_poles_str}")

    with col_grid:
        st.markdown("#### 🚦 A Importância da Classificação")
        st.caption("Relação entre a posição de largada e as vitórias conquistadas nesta pista.")
        
        q_grid = """
            SELECT rr.grid_position_number as grid_pos, COUNT(*) as wins
            FROM race_result rr
            JOIN race r ON rr.race_id = r.id
            WHERE r.circuit_id = ? AND rr.position_number = 1 AND rr.grid_position_number > 0
            GROUP BY rr.grid_position_number
            ORDER BY grid_pos ASC
        """
        grid_wins = execute_query(q_grid, (circuit_id,))
        
        if not grid_wins.empty:
            grid_wins["grid_pos"] = grid_wins["grid_pos"].astype(str)
            
            fig_grid = px.bar(
                grid_wins,
                x="grid_pos",
                y="wins",
                labels={"grid_pos": "Posição no Grid de Largada", "wins": "Total de Vitórias"},
                color="wins",
                color_continuous_scale=["#FF6A6A", "#E10600", "#7A0000"]
            )
            
            fig_grid.update_layout(
                xaxis_type='category', 
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_grid, width='stretch', key=f"fig_grid_{key_prefix}_{circuit_id}")
            
            pole_wins = grid_wins[grid_wins["grid_pos"] == "1"]["wins"].sum() if "1" in grid_wins["grid_pos"].values else 0
            total_wins = grid_wins["wins"].sum()
            
            if total_wins > 0:
                pole_percentage = (pole_wins / total_wins) * 100
                st.caption(f"🏁 **Insight:** Em **{pole_percentage:.1f}%** das vezes, quem largou na Pole Position (1º lugar) venceu a corrida neste circuito.")
        else:
            st.info("Não há dados históricos de grid de largada versus vitórias para este circuito.")

    st.divider()

    st.subheader("🖼️ Imagem do Circuito")

    col_preview_select, col_preview_image = st.columns([1, 2])

    with col_preview_select:
        selected_image_variant = st.selectbox(
            "Escolha o tipo de imagem do circuito:",
            options=list(IMAGE_VARIANTS.keys()),
            index=list(IMAGE_VARIANTS.keys()).index("white-outline"),
            format_func=lambda key: IMAGE_VARIANTS[key]["label"],
            key=f"circuit_image_variant_{key_prefix}_{circuit_id}",
        )

        available_layouts = get_available_circuit_layouts(circuit_row, selected_image_variant)

        if available_layouts:
            selected_layout_path = st.selectbox(
                "Escolha o traçado:",
                options=available_layouts,
                format_func=lambda path: f"Traçado {path.stem.rsplit('-', 1)[-1]}",
                key=f"circuit_layout_{key_prefix}_{circuit_id}_{selected_image_variant}",
            )
        else:
            selected_layout_path = None

    with col_preview_image:
        if selected_layout_path:
            st.image(
                str(selected_layout_path),
                caption=f"{selected_circuit_name} - {IMAGE_VARIANTS[selected_image_variant]['label']} - {selected_layout_path.stem.rsplit('-', 1)[-1]}",
                width=520,
            )
        else:
            st.info("Não foi encontrada imagem SVG para este circuito.")

# ==========================================
# 4. PAINEL EM ABAS
# ==========================================
tab_temporada, tab_global = st.tabs(["Visão da Temporada", "Visão Global"])

with tab_temporada:
    st.subheader(f"Visão da Temporada Atual: Circuitos de {current_season}")
    st.caption(f"Cada ponto representa um circuito no calendário da temporada {current_season}.")
    render_map(current_map_df, "map_season")
    
    st.divider()
    
    st.subheader("🔍 Raio-X do Traçado")
    selected_circuit_name_season = st.selectbox(
        "Selecione um circuito para analisar:", 
        current_map_df["name"],
        key="selectbox_season"
    )
    if selected_circuit_name_season:
        render_circuit_analysis(selected_circuit_name_season, "season")

with tab_global:
    st.subheader("Visão Global: Todos os Circuitos")
    st.caption("Cada ponto representa um circuito que já sediou ao menos um Grande Prêmio oficial.")
    render_map(map_df, "map_global")
    
    st.divider()
    
    st.subheader("🔍 Raio-X do Traçado")
    selected_circuit_name_global = st.selectbox(
        "Selecione um circuito para analisar:", 
        circuits_df["name"],
        key="selectbox_global"
    )
    if selected_circuit_name_global:
        render_circuit_analysis(selected_circuit_name_global, "global")

render_footer()