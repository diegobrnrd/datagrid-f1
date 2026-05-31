import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.db import execute_query, get_all_drivers
from utils.constants import PAISES_TRADUCAO
from utils.ui import setup_sidebar, render_footer

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="DataGrid F1 | Pilotos",
    page_icon="🧑‍🚀",
    layout="wide"
)

setup_sidebar()

st.title("🧑‍🚀 Central Analítica do Piloto")
st.markdown("Raio-X completo da carreira: explore a conversão de resultados, histórico por equipe e o perfil de desempenho de cada piloto.")
st.divider()

# ==========================================
# 2. CARREGAMENTO E BUSCA (Sidebar/Top)
# ==========================================
@st.cache_data(show_spinner=False)
def load_drivers_list():
    df = get_all_drivers()
    df["nationality"] = df["nationality"].map(PAISES_TRADUCAO).fillna(df["nationality"])
    return df

drivers_df = load_drivers_list()

col_busca, col_vazia = st.columns([1, 2])
with col_busca:
    search_term = st.text_input("🔍 Pesquisar piloto (Ex: Senna, Hamilton):", "")

# Filtra o DataFrame com base na busca
if search_term:
    filtered_drivers = drivers_df[drivers_df["full_name"].str.contains(search_term, case=False, na=False)]
else:
    filtered_drivers = drivers_df

if filtered_drivers.empty:
    st.warning("Nenhum piloto encontrado com esse nome.")
    st.stop()

# Seleção do piloto
driver_selected_name = st.selectbox("Selecione um piloto para analisar:", filtered_drivers["full_name"])
driver_row = filtered_drivers[filtered_drivers["full_name"] == driver_selected_name].iloc[0]
driver_id = driver_row["id"]

# ==========================================
# 3. EXTRAÇÃO DE DADOS PROFUNDOS (Queries Específicas)
# ==========================================
# Busca estatísticas vitais do piloto selecionado
query_stats = """
    SELECT 
        total_race_starts,
        total_race_wins,
        total_podiums,
        total_pole_positions,
        total_championship_wins,
        date_of_birth,
        permanent_number
    FROM driver
    WHERE id = ?
"""
stats = execute_query(query_stats, (driver_id,)).iloc[0]

# Busca vitórias divididas por equipe (Construtora)
query_wins_by_team = """
    SELECT c.name as constructor, COUNT(*) as wins
    FROM race_result rr
    JOIN constructor c ON rr.constructor_id = c.id
    WHERE rr.driver_id = ? AND rr.position_number = 1
    GROUP BY c.name
    ORDER BY wins DESC
"""
wins_by_team = execute_query(query_wins_by_team, (driver_id,))

# --- INDICADORES ADICIONAIS DE CARREIRA ---
# Quantidade de voltas mais rápidas
query_fastest = """
    SELECT COUNT(*) AS fastest_count
    FROM race_result
    WHERE driver_id = ? AND fastest_lap = 1
"""
fastest_count = int(execute_query(query_fastest, (driver_id,)).iloc[0]["fastest_count"] or 0)

# Hat tricks (pole + fastest lap + vitória)
query_hat = """
    SELECT COUNT(*) AS hat_count
    FROM race_result
    WHERE driver_id = ? AND pole_position = 1 AND fastest_lap = 1 AND position_number = 1
"""
hat_count = int(execute_query(query_hat, (driver_id,)).iloc[0]["hat_count"] or 0)

# Grand chelems (campo `grand_slam` no banco)
query_grand = """
    SELECT COUNT(*) AS grand_count
    FROM race_result
    WHERE driver_id = ? AND grand_slam = 1
"""
grand_count = int(execute_query(query_grand, (driver_id,)).iloc[0]["grand_count"] or 0)

# ==========================================
# 4. CARTÃO BIOGRÁFICO E MÉTRICAS DE OURO
# ==========================================
# Cálculo de idade básico
idade = "N/A"
if pd.notna(stats["date_of_birth"]):
    dob = pd.to_datetime(stats["date_of_birth"])
    idade = datetime.now().year - dob.year


col_bio, col_m1, col_m2, col_m3, col_m4, col_m5, col_m6, col_m7 = st.columns([2, 1, 1, 1, 1, 1, 1, 1])

with col_bio:
    st.markdown(f"### {driver_selected_name}")
    num = int(stats["permanent_number"]) if pd.notna(stats["permanent_number"]) else "-"
    if pd.notna(stats["date_of_birth"]) and pd.notna(stats["permanent_number"]) and int(stats["total_race_starts"]) > 0:
        st.caption(f"🌍 {driver_row['nationality']} | 🎂 {idade} anos | 🏎️ Nº {num}")
    else:
        ano_nascimento = pd.to_datetime(stats["date_of_birth"]).year if pd.notna(stats["date_of_birth"]) else "N/A"
        st.caption(f"🌍 {driver_row['nationality']} | 🎂 {ano_nascimento}")

with col_m1: st.metric("Títulos Mundiais", int(stats["total_championship_wins"]))
with col_m2: st.metric("Vitórias", int(stats["total_race_wins"]))
with col_m3: st.metric("Pódios", int(stats["total_podiums"]))
with col_m4: st.metric("Poles", int(stats["total_pole_positions"]))
with col_m5: st.metric("Voltas Mais Rápidas", int(fastest_count))
with col_m6: st.metric("Hat Tricks", int(hat_count))
with col_m7: st.metric("Grand Chelems", int(grand_count))

st.divider()

# ==========================================
# 5. PROFUNDIDADE ANALÍTICA (Gráficos)
# ==========================================
starts = int(stats["total_race_starts"])
wins = int(stats["total_race_wins"])
podiums = int(stats["total_podiums"])
poles = int(stats["total_pole_positions"])

col_chart1, col_chart2, col_chart3 = st.columns(3)

# --- GRÁFICO 1: FUNIL DE CONVERSÃO ---
with col_chart1:
    st.markdown("#### Taxa de Conversão (Letalidade)")
    st.caption("De todas as corridas que largou, quantas viraram pódio e vitória?")
    
    if starts > 0:
        fig_funnel = go.Figure(go.Funnel(
            y=['Largadas', 'Pódios', 'Vitórias'],
            x=[starts, podiums, wins],
            textinfo="value+percent initial",
            marker={"color": ["#1f77b4", "#ff7f0e", "#E10600"]}
        ))
        fig_funnel.update_layout(margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_funnel, width='stretch')
    else:
        st.info("Este piloto não possui largadas registradas.")

# --- GRÁFICO 2: DESEMPENHO POR EQUIPE ---
with col_chart2:
    st.markdown("#### Vitórias por Equipe")
    st.caption("A contribuição do piloto por construtora.")
    
    if not wins_by_team.empty:
        fig_bar = px.bar(
            wins_by_team, 
            x="constructor", 
            y="wins",
            labels={"constructor": "Equipe", "wins": "Vitórias"},
            color="constructor",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_bar.update_layout(showlegend=False, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, width='stretch')
    else:
        st.info("Este piloto não possui vitórias registradas.")

# --- GRÁFICO 3: PERFIL DE DESEMPENHO (RADAR) ---
with col_chart3:
    st.markdown("#### Perfil do Piloto (Radar)")
    st.caption("Comparativo percentual das métricas de sucesso.")
    
    if starts > 0:
        win_rate = (wins / starts) * 100
        podium_rate = (podiums / starts) * 100
        pole_rate = (poles / starts) * 100
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[win_rate, podium_rate, pole_rate, win_rate], # Repete o primeiro valor para fechar o triângulo
            theta=['Vitórias (%)', 'Pódios (%)', 'Poles (%)', 'Vitórias (%)'],
            fill='toself',
            name=driver_selected_name,
            line_color='#E10600'
        ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max(win_rate, podium_rate, pole_rate, 10) + 10])),
            showlegend=False,
            margin=dict(l=40, r=40, t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_radar, width='stretch')
    else:
        st.info("Dados insuficientes para gerar o radar.")

render_footer()