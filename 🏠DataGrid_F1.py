import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import (
    execute_query,
    get_grid_capacity_by_season,
    get_constructor_count_by_season,
    get_top_countries_by_drivers,
    get_top_countries_by_constructors,
)
from utils.constants import PAISES_TRADUCAO
from utils.ui import setup_sidebar, render_footer

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA (Deve ser a 1ª linha)
# ==========================================
st.set_page_config(
    page_title="DataGrid F1 | Visão Global",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

setup_sidebar()

# ==========================================
# 2. ESTILIZAÇÃO CSS CUSTOMIZADA
# ==========================================
st.markdown("""
<style>
    /* Fundo escuro e bordas arredondadas para os cartões de KPIs */
    div[data-testid="metric-container"] {
        background-color: #1E1E24;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Destaca o valor do KPI com a cor vermelha clássica da F1 */
    div[data-testid="metric-container"] > div > div > div {
        color: #E10600 !important; 
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. EXTRAÇÃO DE DADOS OTIMIZADA (ETL)
# ==========================================
@st.cache_data(show_spinner=False)
def load_dashboard_metrics():
    """Executa queries agregadas focadas em performance para os KPIs."""
    
    # KPIs Globais
    total_drivers = execute_query("SELECT COUNT(id) as count FROM driver").iloc[0]['count']
    total_constructors = execute_query("SELECT COUNT(id) as count FROM constructor").iloc[0]['count']
    total_races = execute_query("SELECT COUNT(id) as count FROM race").iloc[0]['count']
    total_circuits = execute_query("SELECT COUNT(id) as count FROM circuit").iloc[0]['count']
    
    # Dados para o Gráfico de Evolução (Corridas por Ano)
    races_per_year = execute_query("""
        SELECT year, COUNT(id) as total_races 
        FROM race 
        GROUP BY year 
        ORDER BY year
    """)
    
    # Dados para o Gráfico de Países Sede (Top 10)
    top_countries = execute_query("""
        SELECT co.name as country, SUM(ci.total_races_held) as total_races 
        FROM circuit ci 
        LEFT JOIN country co ON ci.country_id = co.id 
        GROUP BY co.name 
        ORDER BY total_races DESC 
        LIMIT 10
    """)

    grid_capacity_by_season = get_grid_capacity_by_season()
    constructor_count_by_season = get_constructor_count_by_season()
    top_countries_by_drivers = get_top_countries_by_drivers()
    top_countries_by_constructors = get_top_countries_by_constructors()
    
    # Aplicando a tradução aos nomes dos países
    top_countries["country"] = top_countries["country"].map(PAISES_TRADUCAO).fillna(top_countries["country"])
    top_countries_by_drivers["country"] = top_countries_by_drivers["country"].map(PAISES_TRADUCAO).fillna(top_countries_by_drivers["country"])
    top_countries_by_constructors["country"] = top_countries_by_constructors["country"].map(PAISES_TRADUCAO).fillna(top_countries_by_constructors["country"])
    
    return (
        total_drivers,
        total_constructors,
        total_races,
        total_circuits,
        races_per_year,
        top_countries,
        grid_capacity_by_season,
        constructor_count_by_season,
        top_countries_by_drivers,
        top_countries_by_constructors,
    )

# Carrega os dados
kpi_drivers, kpi_constructors, kpi_races, kpi_circuits, df_races_year, df_top_countries, df_grid_capacity, df_team_count, df_top_driver_countries, df_top_team_countries = load_dashboard_metrics()

# ==========================================
# 4. HERO SECTION (Cabeçalho)
# ==========================================
st.title("🏎️ DataGrid F1")
st.markdown("""
Boas-vindas à plataforma analítica definitiva da Fórmula 1. 
Explore mais de sete décadas de dados históricos de engenharia, velocidade e estratégia, desde a primeira corrida em 1950 até os dias atuais.
""")
st.divider()

# ==========================================
# 5. KPIs GLOBAIS
# ==========================================
st.subheader("O Tamanho da História")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Pilotos Registrados", f"{kpi_drivers:,}".replace(",", "."))
col2.metric("Equipes Históricas", f"{kpi_constructors:,}".replace(",", "."))
col3.metric("Grandes Prêmios", f"{kpi_races:,}".replace(",", "."))
col4.metric("Circuitos Utilizados", f"{kpi_circuits:,}".replace(",", "."))

st.markdown("<br>", unsafe_allow_html=True) # Espaçamento vertical

# ==========================================
# 6. VISÃO MACRO (Gráficos Analíticos)
# ==========================================
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("#### 📅 Evolução do Calendário de Corridas")
    st.caption("Evolução histórica da quantidade de Grandes Prêmios disputados a cada temporada.")
    
    fig_line = px.area(
        df_races_year, 
        x="year", 
        y="total_races",
        labels={"year": "Temporada", "total_races": "Número de Corridas"},
        color_discrete_sequence=["#E10600"] # Vermelho F1
    )
    fig_line.update_layout(
        height=320,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#333'),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_line, width='stretch')

with chart_col2:
    st.markdown("#### 🌍 Top 10 Países-Sede de Corridas")
    st.caption("Ranking histórico dos países que mais sediaram Grandes Prêmios na F1.")
    
    fig_bar = px.bar(
        df_top_countries, 
        x="total_races",
        y="country",
        orientation="h",
        labels={"country": "País", "total_races": "Número de Corridas"},
            color="total_races",
            color_continuous_scale=[[0, "#FF6A6A"], [0.5, "#E10600"], [1, "#7A0000"]]
    )
    fig_bar.update_layout(
        height=320,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=True, gridcolor='#333'),
        yaxis=dict(showgrid=False, autorange="reversed"),
        plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False
    )
    st.plotly_chart(fig_bar, width='stretch')

st.markdown("<br>", unsafe_allow_html=True)

chart_row2_left, chart_row2_right = st.columns(2)

with chart_row2_left:
    st.markdown("#### 🚦 Evolução do Grid de Largada")
    st.caption("Variação da capacidade média/máxima de carros no grid ao longo das temporadas.")

    if df_grid_capacity.empty:
        st.info("Não há dados suficientes para calcular a evolução do grid.")
    else:
        grid_value_column = "grid_slots" if "grid_slots" in df_grid_capacity.columns else "avg_grid_slots"
        fig_grid = px.area(
            df_grid_capacity,
            x="year",
            y=grid_value_column,
            labels={"year": "Temporada", grid_value_column: "Vagas no grid"},
            color_discrete_sequence=["#E10600"],
        )
        fig_grid.update_traces(
            hovertemplate="Temporada: %{x}<br>Vagas no grid: %{y}<extra></extra>",
            line_color="#E10600",
        )
        fig_grid.update_layout(
            height=320,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(dtick=5),
            yaxis=dict(title="Vagas no grid", rangemode="tozero"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_grid, width='stretch')

with chart_row2_right:
    st.markdown("#### 🌍 Top 10 Países de Origem de Pilotos")
    st.caption("Ranking dos países que mais revelaram pilotos para a Fórmula 1.")

    if df_top_driver_countries.empty:
        st.info("Não há dados suficientes para listar os países de pilotos.")
    else:
        fig_driver_countries = px.bar(
            df_top_driver_countries,
            x="total_drivers",
            y="country",
            orientation="h",
            labels={"country": "País", "total_drivers": "Pilotos"},
            color="total_drivers",
            color_continuous_scale=[[0, "#FF6A6A"], [0.5, "#E10600"], [1, "#7A0000"]],
        )
        fig_driver_countries.update_layout(
            height=320,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=True, gridcolor='#333'),
            yaxis=dict(showgrid=False, autorange="reversed"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_driver_countries, width='stretch')

st.markdown("<br>", unsafe_allow_html=True)

chart_row3_left, chart_row3_right = st.columns(2)

with chart_row3_left:
    st.markdown("#### 🏭 Evolução de Construtoras Ativas")
    st.caption("Histórico da quantidade de equipes distintas participando a cada temporada.")

    if df_team_count.empty:
        st.info("Não há dados suficientes para calcular a evolução das equipes.")
    else:
        fig_team_count = px.area(
            df_team_count,
            x="year",
            y="total_teams",
            labels={"year": "Temporada", "total_teams": "Equipes"},
            color_discrete_sequence=["#E10600"],
        )
        fig_team_count.update_traces(
            hovertemplate="Temporada: %{x}<br>Equipes: %{y}<extra></extra>",
            line_color="#E10600",
        )
        fig_team_count.update_layout(
            height=320,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(dtick=5),
            yaxis=dict(title="Equipes", rangemode="tozero"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_team_count, width='stretch')

with chart_row3_right:
    st.markdown("#### 🌍 Top 10 Países de Origem de Construtoras")
    st.caption("Ranking dos países que mais fundaram equipes na Fórmula 1.")

    if df_top_team_countries.empty:
        st.info("Não há dados suficientes para listar os países de equipes.")
    else:
        fig_team_countries = px.bar(
            df_top_team_countries,
            x="total_constructors",
            y="country",
            orientation="h",
            labels={"country": "País", "total_constructors": "Equipes"},
            color="total_constructors",
            color_continuous_scale=[[0, "#FF6A6A"], [0.5, "#E10600"], [1, "#7A0000"]],
        )
        fig_team_countries.update_layout(
            height=320,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=True, gridcolor='#333'),
            yaxis=dict(showgrid=False, autorange="reversed"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_team_countries, width='stretch')

st.divider()

# ==========================================
# 7. GUIA DE NAVEGAÇÃO (Onboarding do usuário)
# ==========================================
st.subheader("Explore o Banco de Dados")
st.markdown("Utilize o menu lateral para navegar pelas seções da aplicação:")

nav1, nav2 = st.columns(2)

with nav1:
    st.info("**🏁 Corridas:** Mergulhe nos resultados oficiais, posições de largada, estatísticas de confiabilidade e destaques de qualquer evento histórico.")
    st.success("**🏭 Construtoras:** Entenda o domínio da engenharia. Descubra quais equipes marcaram eras, seus pilotos pilares e históricos de abandonos.")
    st.warning("**🏆 Campeonatos:** Reviva a história de cada temporada. Veja as classificações finais, os campeões e a evolução de pontos corrida a corrida.")

with nav2:
    st.info("**🧑‍🚀 Pilotos:** Descubra o raio-x completo das lendas. Explore a evolução anual de carreira, taxas de conversão e rankings globais.")
    st.success("**🗺️ Circuitos:** Explore mapas e imagens dos traçados. Descubra os reis de cada pista e a real importância da Pole Position.")

st.caption("Dados fornecidos pelo projeto open-source F1DB.")
render_footer()