import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import execute_query, get_all_circuits
from utils.constants import PAISES_TRADUCAO
from utils.ui import setup_sidebar, render_footer

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

# ==========================================
# 3. VISÃO ESPACIAL (Mapa Múndi)
# ==========================================
st.subheader("Visão Global: Todos os Circuitos")
st.caption("Cada ponto representa um circuito que já sediou ao menos um Grande Prêmio oficial.")

# Filtra apenas circuitos com latitude e longitude cadastradas
map_df = circuits_df.dropna(subset=["latitude", "longitude"]).copy()

# Criação do mapa interativo com Plotly
fig_map = px.scatter_map(
    map_df, 
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
    color_discrete_sequence=["#E10600"], # Cor vermelha F1
    zoom=1.2, 
    height=450
)

# Estilo de mapa escuro que não exige token do Mapbox
fig_map.update_layout(
    mapbox_style="carto-darkmatter",
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)

st.plotly_chart(fig_map, width='stretch')

st.divider()

# ==========================================
# 4. PAINEL DE ANÁLISE DA PISTA (Deep Dive)
# ==========================================
st.subheader("🔍 Raio-X do Traçado")

# Seleção do circuito
selected_circuit_name = st.selectbox(
    "Selecione um circuito para analisar:", 
    circuits_df["name"]
)

# Coleta os dados básicos do circuito selecionado
circuit_row = circuits_df[circuits_df["name"] == selected_circuit_name].iloc[0]
circuit_id = circuit_row["id"]

# Ficha técnica
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
col_kpi1.metric("Localização", f"{circuit_row['place_name']} ({circuit_row['country']})")
col_kpi2.metric("Extensão", f"{circuit_row['length']} km" if pd.notna(circuit_row['length']) else "N/A")
col_kpi3.metric("Curvas", int(circuit_row["turns"]) if pd.notna(circuit_row["turns"]) else "N/A")
col_kpi4.metric("Total de Corridas", int(circuit_row["total_races_held"]) if pd.notna(circuit_row["total_races_held"]) else 0)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 5. REIS DA PISTA & IMPORTÂNCIA DO GRID
# ==========================================
col_kings, col_grid = st.columns([1, 2])

with col_kings:
    st.markdown("#### 👑 Reis da Pista")
    st.caption("Quem dominou este traçado na história.")
    
    # Query: Piloto com mais vitórias neste circuito
    q_driver = """
        SELECT d.last_name as name, COUNT(*) as wins
        FROM race_result rr
        JOIN race r ON rr.race_id = r.id
        JOIN driver d ON rr.driver_id = d.id
        WHERE r.circuit_id = ? AND rr.position_number = 1
        GROUP BY d.id
        ORDER BY wins DESC
        LIMIT 1
    """
    best_driver = execute_query(q_driver, (circuit_id,))
    
    # Query: Equipe com mais vitórias neste circuito
    q_team = """
        SELECT c.name as name, COUNT(*) as wins
        FROM race_result rr
        JOIN race r ON rr.race_id = r.id
        JOIN constructor c ON rr.constructor_id = c.id
        WHERE r.circuit_id = ? AND rr.position_number = 1
        GROUP BY c.id
        ORDER BY wins DESC
        LIMIT 1
    """
    best_team = execute_query(q_team, (circuit_id,))
    
    # Formatação condicional (caso a pista seja nova e não tenha vitórias registradas)
    driver_str = f"{best_driver.iloc[0]['name']} ({best_driver.iloc[0]['wins']} vitórias)" if not best_driver.empty else "Dados indisponíveis"
    team_str = f"{best_team.iloc[0]['name']} ({best_team.iloc[0]['wins']} vitórias)" if not best_team.empty else "Dados indisponíveis"
    
    st.info(f"**Maior Vencedor (Piloto):**\n\n🏎️ {driver_str}")
    st.success(f"**Maior Vencedora (Equipe):**\n\n🏭 {team_str}")

with col_grid:
    st.markdown("#### A Importância da Classificação")
    st.caption("Relação entre a posição de largada e as vitórias conquistadas nesta pista.")
    
    # Query: Relaciona a posição de largada (grid) com vitórias
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
        # Converte para string para o Plotly tratar o eixo X como categoria e não pular números
        grid_wins["grid_pos"] = grid_wins["grid_pos"].astype(str)
        
        fig_grid = px.bar(
            grid_wins,
            x="grid_pos",
            y="wins",
            labels={"grid_pos": "Posição no Grid de Largada", "wins": "Total de Vitórias"},
            color_discrete_sequence=["#1f77b4"]
        )
        
        fig_grid.update_layout(
            xaxis_type='category', 
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_grid, width='stretch')
        
        # Gera o Insight de Porcentagem da Pole Position
        pole_wins = grid_wins[grid_wins["grid_pos"] == "1"]["wins"].sum() if "1" in grid_wins["grid_pos"].values else 0
        total_wins = grid_wins["wins"].sum()
        
        if total_wins > 0:
            pole_percentage = (pole_wins / total_wins) * 100
            st.caption(f"🏁 **Insight:** Em **{pole_percentage:.1f}%** das vezes, quem largou na Pole Position (1º lugar) venceu a corrida neste circuito.")
    else:
        st.info("Não há dados históricos de grid de largada versus vitórias para este circuito.")

render_footer()