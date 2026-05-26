import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import execute_query, get_all_constructors
from utils.constants import PAISES_TRADUCAO, STATUS_TRADUCAO
from utils.ui import setup_sidebar, render_footer

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="DataGrid F1 | Construtoras",
    page_icon="🏭",
    layout="wide"
)

setup_sidebar()

st.title("🏭 Domínio da Engenharia")
st.markdown("Descubra quais equipes dominaram a Fórmula 1, quais pilotos carregaram essas escuderias e qual a verdadeira taxa de confiabilidade de seus carros.")
st.divider()

# ==========================================
# 2. TABELA DE LIDERANÇA GLOBAL
# ==========================================
@st.cache_data(show_spinner=False)
def load_constructors():
    df = get_all_constructors()
    df["country"] = df["country"].map(PAISES_TRADUCAO).fillna(df["country"])
    return df

constructors_df = load_constructors()

st.subheader("Ranking Histórico Global")
st.dataframe(
    constructors_df[["name", "country", "total_championship_wins", "total_race_wins", "total_podiums"]].head(50),
    width='stretch',
    hide_index=True,
    column_config={
        "name": "Construtora",
        "country": "País Sede",
        "total_championship_wins": st.column_config.NumberColumn("Títulos Mundiais", format="%d"),
        "total_race_wins": st.column_config.NumberColumn("Vitórias", format="%d"),
        "total_podiums": st.column_config.NumberColumn("Pódios", format="%d"),
    }
)

st.divider()

# ==========================================
# 3. DEEP-DIVE POR EQUIPE (Seleção)
# ==========================================
st.subheader("🔎 Análise Profunda por Equipe")

# Seleção da equipe
team_selected = st.selectbox(
    "Selecione uma equipe para gerar o relatório:", 
    constructors_df["name"]
)

# Pega a linha da equipe selecionada e o ID
team_row = constructors_df[constructors_df["name"] == team_selected].iloc[0]
team_id = team_row["id"]

# Métricas Básicas
m1, m2, m3, m4 = st.columns(4)
m1.metric("País de Origem", team_row["country"])
m2.metric("Títulos Mundiais", int(team_row["total_championship_wins"]))
m3.metric("Vitórias Totais", int(team_row["total_race_wins"]))
m4.metric("Pódios Totais", int(team_row["total_podiums"]))

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 4. GRÁFICOS DE PESO E CONFIABILIDADE
# ==========================================
col_chart1, col_chart2 = st.columns(2)

# --- GRÁFICO 1: O PESO DOS PILOTOS ---
with col_chart1:
    st.markdown("#### O Peso dos Pilotos")
    st.caption("Quais pilotos trouxeram mais vitórias para esta equipe?")
    
    # Query para buscar os maiores vencedores pela equipe
    query_team_drivers = """
        SELECT d.last_name as driver, COUNT(*) as wins
        FROM race_result rr
        JOIN driver d ON rr.driver_id = d.id
        WHERE rr.constructor_id = ? AND rr.position_number = 1
        GROUP BY d.id
        ORDER BY wins DESC
        LIMIT 5
    """
    team_drivers_df = execute_query(query_team_drivers, (team_id,))
    
    if not team_drivers_df.empty:
        fig_drivers = px.bar(
            team_drivers_df,
            x="driver",
            y="wins",
            labels={"driver": "Piloto", "wins": "Vitórias pela Equipe"},
            color="driver",
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        fig_drivers.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_drivers, width='stretch')
    else:
        st.info("Nenhuma vitória registrada para detalhar pilotos.")

# --- GRÁFICO 2: TAXA DE CONFIABILIDADE E FALHAS ---
with col_chart2:
    st.markdown("#### Histórico de Abandonos (Top 10)")
    st.caption("Principais motivos pelos quais os carros desta equipe não terminaram corridas.")
    
    # Query para buscar motivos de abandono
    query_failures = """
        SELECT reason_retired as reason, COUNT(*) as total
        FROM race_result
        WHERE constructor_id = ? AND reason_retired IS NOT NULL
        GROUP BY reason_retired
        ORDER BY total DESC
        LIMIT 10
    """
    failures_df = execute_query(query_failures, (team_id,))
    
    if not failures_df.empty:
        # Traduz os motivos usando o dicionário
        failures_df["reason"] = failures_df["reason"].map(STATUS_TRADUCAO).fillna(failures_df["reason"])
        
        # Inverte a ordem para o gráfico de barras horizontais ficar com o maior no topo
        failures_df = failures_df.sort_values("total", ascending=True)
        
        fig_failures = px.bar(
            failures_df,
            x="total",
            y="reason",
            orientation='h',
            color="total",
            labels={"total": "Quantidade de Abandonos", "reason": "Motivo"},
            color_continuous_scale=["#FFE8CC", "#FFB347", "#FF7F0E", "#E67E22", "#D35400"]
        )
        fig_failures.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
        st.plotly_chart(fig_failures, width='stretch')
    else:
        st.success("Esta equipe tem um histórico impecável ou dados de abandono não registrados.")
    
render_footer()