import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import execute_query
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
    
    # Aplicando a tradução aos nomes dos países
    top_countries["country"] = top_countries["country"].map(PAISES_TRADUCAO).fillna(top_countries["country"])
    
    return total_drivers, total_constructors, total_races, total_circuits, races_per_year, top_countries

# Carrega os dados
kpi_drivers, kpi_constructors, kpi_races, kpi_circuits, df_races_year, df_top_countries = load_dashboard_metrics()

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
chart_col1, chart_col2 = st.columns([3, 2])

with chart_col1:
    st.markdown("#### Evolução do Calendário")
    st.caption("Quantidade de corridas disputadas por temporada.")
    
    fig_line = px.area(
        df_races_year, 
        x="year", 
        y="total_races",
        labels={"year": "Temporada", "total_races": "Número de Corridas"},
        color_discrete_sequence=["#E10600"] # Vermelho F1
    )
    fig_line.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#333'),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_line, width='stretch')

with chart_col2:
    st.markdown("#### Top 10 Países Sedes")
    st.caption("Locais que mais receberam Grandes Prêmios na história.")
    
    fig_bar = px.bar(
        df_top_countries, 
        x="country", 
        y="total_races",
        labels={"country": "País", "total_races": "Número de Corridas"},
            color="total_races",
            color_continuous_scale=[[0, "#FF6A6A"], [0.5, "#E10600"], [1, "#7A0000"]]
    )
    fig_bar.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#333'),
        plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False
    )
    st.plotly_chart(fig_bar, width='stretch')

st.divider()

# ==========================================
# 7. GUIA DE NAVEGAÇÃO (Onboarding do usuário)
# ==========================================
st.subheader("Explore o Banco de Dados")
st.markdown("Utilize o menu lateral para navegar pelas seções da aplicação:")

nav1, nav2, nav3 = st.columns(3)

with nav1:
    st.info("**🏁 Corridas:** Faça um drill-down detalhado nos resultados oficiais e posições de largada de qualquer evento histórico.")
    st.info("**🧑‍🚀 Pilotos:** Descubra o raio-x analítico das lendas do esporte, taxas de vitória e comparativos de carreira.")

with nav2:
    st.success("**🏭 Construtoras:** Entenda o domínio da engenharia. Quais equipes marcaram eras e quais pilotos foram seus pilares?")
    st.success("**🏆 Campeonatos:** A visão final da tabela. Quem ergueu os troféus de Piloto e Construtor no final de cada ano.")

with nav3:
    st.warning("**🗺️ Circuitos:** Mapas interativos e análises profundas sobre traçados. A pole position realmente importa em Mônaco?")

st.caption("Dados fornecidos pelo projeto open-source F1DB.")
render_footer()