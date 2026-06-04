import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    expected_columns = [
        "total_championship_wins",
        "total_driver_championship_wins",
        "total_race_wins",
        "total_podiums",
        "total_pole_positions",
    ]
    for column in expected_columns:
        if column not in df.columns:
            df[column] = 0
    return df

constructors_df = load_constructors()

st.subheader("🌍 Ranking Histórico Global")
ranking_columns = [
    "name",
    "country",
    "total_championship_wins",
    "total_driver_championship_wins",
    "total_race_wins",
    "total_podiums",
    "total_pole_positions",
]
st.dataframe(
    constructors_df.reindex(columns=ranking_columns).head(50),
    width='stretch',
    hide_index=True,
    column_config={
        "name": "Construtora",
        "country": "País Sede",
        "total_championship_wins": st.column_config.NumberColumn("Títulos Mundiais", format="%d"),
        "total_driver_championship_wins": st.column_config.NumberColumn("Títulos de Pilotos", format="%d"),
        "total_race_wins": st.column_config.NumberColumn("Vitórias", format="%d"),
        "total_podiums": st.column_config.NumberColumn("Pódios", format="%d"),
        "total_pole_positions": st.column_config.NumberColumn("Poles", format="%d"),
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
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("País de Origem", team_row["country"])
m2.metric("Títulos Mundiais", int(team_row["total_championship_wins"]))
m3.metric("Títulos Piloto", int(team_row["total_driver_championship_wins"]))
m4.metric("Vitórias Totais", int(team_row["total_race_wins"]))
m5.metric("Pódios Totais", int(team_row["total_podiums"]))
m6.metric("Poles Totais", int(team_row["total_pole_positions"]))

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 4. PAINEL ANALÍTICO DA EQUIPE (Gráficos)
# ==========================================
st.markdown("### Painel de Desempenho e Histórico")

# Função auxiliar para gerar os gráficos de lollipop
def render_team_lollipop(df: pd.DataFrame, category_col: str, value_col: str, category_label: str, value_label: str, color: str, key: str):
    """Renderiza um gráfico do tipo lollipop para visualizar a distribuição de métricas por ano."""
    fig = go.Figure()
    categories = df[category_col].tolist()
    vals = df[value_col].tolist()
    for x, y in zip(categories, vals):
        fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color=color, width=2))
    fig.add_trace(go.Scatter(
        x=categories,
        y=vals,
        mode="markers",
        marker=dict(color=color, size=10),
        hovertemplate=f"{category_label}: %{{x}}<br>{value_label}: %{{y}}<extra></extra>"
    ))
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    if pd.api.types.is_numeric_dtype(df[category_col]):
        fig.update_xaxes(dtick=5)
    fig.update_yaxes(rangemode="tozero")
    st.plotly_chart(fig, width='stretch', key=key)


# Função auxiliar para gerar os gráficos de barra (Top 10)
def render_team_bar(df: pd.DataFrame, category_col: str, value_col: str, category_label: str, value_label: str, color_scale: list, key: str, orientation: str = 'v'):
    """Renderiza um gráfico de barras (horizontal ou vertical) padronizado."""
    if orientation == 'v':
        fig = px.bar(df, x=category_col, y=value_col, labels={category_col: category_label, value_col: value_label}, color=value_col, color_continuous_scale=color_scale)
    else:
        fig = px.bar(df, x=value_col, y=category_col, orientation='h', labels={category_col: category_label, value_col: value_label}, color=value_col, color_continuous_scale=color_scale)
        
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
    if orientation == 'v':
        fig.update_yaxes(rangemode="tozero")
    else:
        fig.update_xaxes(rangemode="tozero")
        fig.update_yaxes(autorange="reversed") # Mantém o maior valor no topo
        
    st.plotly_chart(fig, width='stretch', key=key)


# Função auxiliar para gerar os gráficos de evolução
def render_team_evolution(df: pd.DataFrame, x_col: str, y_col: str, y_label: str, color: str, key: str, custom_hover_col: str = None):
    """Renderiza um gráfico de linha interativo exibindo a evolução temporal de uma métrica da equipe."""
    if df.empty or df[y_col].max() == 0:
        st.info(f"Sem registros de {y_label.lower()} para esta equipe.")
        return

    if custom_hover_col:
        fig = px.line(
            df, x=x_col, y=y_col,
            markers=True,
            labels={x_col: "Ano", y_col: y_label},
            custom_data=[df[custom_hover_col]]
        )
        hovertemplate = f"Ano: %{{x}}<br>{y_label}: %{{y}}<br>Piloto: %{{customdata[0]}}<extra></extra>"
    else:
        fig = px.line(
            df, x=x_col, y=y_col,
            markers=True,
            labels={x_col: "Ano", y_col: y_label},
        )
        hovertemplate = f"Ano: %{{x}}<br>{y_label}: %{{y}}<extra></extra>"

    fig.update_traces(line_color=color, hovertemplate=hovertemplate)
    dtick_y = 1 if df[y_col].max() < 10 else None
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(dtick=5),
        yaxis=dict(dtick=dtick_y, rangemode="tozero")
    )
    st.plotly_chart(fig, width='stretch', key=key)

# Busca todos os dados de evolução da equipe (Vitórias, Poles, Pódios, Títulos)
query_evolution = """
    WITH team_years AS (
        SELECT DISTINCT r.year
        FROM race_result rr
        JOIN race r ON rr.race_id = r.id
        WHERE rr.constructor_id = ?
    ),
    team_titles AS (
        SELECT year, 1 AS title
        FROM season_constructor_standing
        WHERE constructor_id = ? AND championship_won = 1
    ),
    team_driver_titles AS (
        SELECT
            r.year,
            COUNT(DISTINCT sds.driver_id) AS driver_titles,
            MAX(d.full_name) AS driver_name
        FROM season_driver_standing sds
        JOIN race_result rr ON rr.driver_id = sds.driver_id
        JOIN race r ON rr.race_id = r.id AND r.year = sds.year
        JOIN driver d ON d.id = sds.driver_id
        WHERE rr.constructor_id = ? AND sds.championship_won = 1
        GROUP BY r.year
    ),
    team_wins AS (
        SELECT r.year, COUNT(*) AS wins
        FROM race_result rr
        JOIN race r ON rr.race_id = r.id
        WHERE rr.constructor_id = ? AND rr.position_number = 1
        GROUP BY r.year
    ),
    team_poles AS (
        SELECT r.year, COUNT(*) AS poles
        FROM race_result rr
        JOIN race r ON rr.race_id = r.id
        WHERE rr.constructor_id = ? AND rr.pole_position = 1
        GROUP BY r.year
    ),
    team_podiums AS (
        SELECT r.year, COUNT(*) AS podiums
        FROM race_result rr
        JOIN race r ON rr.race_id = r.id
        WHERE rr.constructor_id = ? AND rr.position_number IN (1, 2, 3)
        GROUP BY r.year
    )
    SELECT 
        ty.year, 
        COALESCE(tt.title, 0) AS titles,
        COALESCE(tdt.driver_titles, 0) AS driver_titles,
        COALESCE(tdt.driver_name, '') AS driver_name,
        COALESCE(tw.wins, 0) AS wins,
        COALESCE(tp.poles, 0) AS poles,
        COALESCE(tpod.podiums, 0) AS podiums
    FROM team_years ty
    LEFT JOIN team_titles tt ON ty.year = tt.year
    LEFT JOIN team_driver_titles tdt ON ty.year = tdt.year
    LEFT JOIN team_wins tw ON ty.year = tw.year
    LEFT JOIN team_poles tp ON ty.year = tp.year
    LEFT JOIN team_podiums tpod ON ty.year = tpod.year
    ORDER BY ty.year ASC
"""
evo_df = execute_query(query_evolution, (team_id, team_id, team_id, team_id, team_id, team_id))
if not evo_df.empty:
    evo_df["cum_titles"] = evo_df["titles"].cumsum()
    evo_df["cum_driver_titles"] = evo_df["driver_titles"].cumsum()
    evo_df["cum_wins"] = evo_df["wins"].cumsum()
    evo_df["cum_poles"] = evo_df["poles"].cumsum()
    evo_df["cum_podiums"] = evo_df["podiums"].cumsum()
    evo_df["hover_text"] = evo_df.apply(
        lambda row: f"<br>Piloto: {row['driver_name']}" if row["driver_titles"] > 0 and row["driver_name"] else "",
        axis=1,
    )

# --- 1. VITÓRIAS ---
r1_col1, r1_col2 = st.columns(2)
with r1_col1:
    st.markdown("#### 🥇 Top 10: Vitórias")
    st.caption("Pilotos que mais trouxeram o lugar mais alto do pódio para a equipe.")
    query_wins = """
        SELECT d.last_name as driver, COUNT(*) as value
        FROM race_result rr
        JOIN driver d ON rr.driver_id = d.id
        WHERE rr.constructor_id = ? AND rr.position_number = 1
        GROUP BY d.id
        ORDER BY value DESC
        LIMIT 10
    """
    wins_df = execute_query(query_wins, (team_id,))
    if not wins_df.empty:
        render_team_bar(wins_df, "driver", "value", "Piloto", "Vitórias", [[0, "#FF6A6A"], [0.5, "#E10600"], [1, "#7A0000"]], "chart_wins")
    else:
        st.info("Nenhuma vitória registrada para esta equipe.")

with r1_col2:
    st.markdown("#### 📈 Vitórias por Temporada")
    st.caption("Total de vitórias conquistadas em cada ano de participação.")
    wins_per_year_df = evo_df[evo_df["wins"] > 0].copy()
    if not wins_per_year_df.empty:
        render_team_lollipop(wins_per_year_df, "year", "wins", "Ano", "Vitórias", "#E10600", "evo_wins")
    else:
        st.info("Sem registros de vitórias para esta equipe.")

st.markdown("<br>", unsafe_allow_html=True)

# --- 2. POLES ---
r2_col1, r2_col2 = st.columns(2)
with r2_col1:
    st.markdown("#### ⏱️ Top 10: Pole Positions")
    st.caption("Pilotos que mais vezes largaram na primeira posição pela equipe.")
    query_poles = """
        SELECT d.last_name as driver, COUNT(*) as value
        FROM race_result rr
        JOIN driver d ON rr.driver_id = d.id
        WHERE rr.constructor_id = ? AND rr.pole_position = 1
        GROUP BY d.id
        ORDER BY value DESC
        LIMIT 10
    """
    poles_df = execute_query(query_poles, (team_id,))
    if not poles_df.empty:
        render_team_bar(poles_df, "driver", "value", "Piloto", "Poles", [[0, "#FFC285"], [0.5, "#FF7F0E"], [1, "#A34A00"]], "chart_poles")
    else:
        st.info("Nenhuma Pole Position registrada para esta equipe.")

with r2_col2:
    st.markdown("#### 📈 Poles por Temporada")
    st.caption("Total de poles conquistadas em cada ano de participação.")
    poles_per_year_df = evo_df[evo_df["poles"] > 0].copy()
    if not poles_per_year_df.empty:
        render_team_lollipop(poles_per_year_df, "year", "poles", "Ano", "Poles", "#FF7F0E", "evo_poles")
    else:
        st.info("Sem registros de poles para esta equipe.")

st.markdown("<br>", unsafe_allow_html=True)

# --- 3. PÓDIOS ---
r3_col1, r3_col2 = st.columns(2)
with r3_col1:
    st.markdown("#### 🍾 Top 10: Pódios")
    st.caption("Pilotos com maior presença no Top 3 vestindo as cores da escuderia.")
    query_podiums = """
        SELECT d.last_name as driver, COUNT(*) as value
        FROM race_result rr
        JOIN driver d ON rr.driver_id = d.id
        WHERE rr.constructor_id = ? AND rr.position_number IN (1, 2, 3)
        GROUP BY d.id
        ORDER BY value DESC
        LIMIT 10
    """
    podiums_df = execute_query(query_podiums, (team_id,))
    if not podiums_df.empty:
        render_team_bar(podiums_df, "driver", "value", "Piloto", "Pódios", [[0, "#85C2FF"], [0.5, "#1F77B4"], [1, "#0B4073"]], "chart_podiums")
    else:
        st.info("Nenhum pódio registrado para esta equipe.")

with r3_col2:
    st.markdown("#### 📈 Pódios por Temporada")
    st.caption("Total de pódios conquistados ao longo dos anos.")
    podiums_per_year_df = evo_df[evo_df["podiums"] > 0].copy()
    if not podiums_per_year_df.empty:
        render_team_lollipop(podiums_per_year_df, "year", "podiums", "Ano", "Pódios", "#1F77B4", "evo_podiums")
    else:
        st.info("Sem registros de pódios para esta equipe.")

st.markdown("<br>", unsafe_allow_html=True)

# --- 4. LARGADAS E ABANDONOS ---
r4_col1, r4_col2 = st.columns(2)
with r4_col1:
    st.markdown("#### 🏁 Top 10: Corridas Disputadas")
    st.caption("Pilotos mais fiéis em número de largadas oficiais pela equipe.")
    query_starts = """
        SELECT d.last_name as driver, COUNT(*) as value
        FROM race_result rr
        JOIN driver d ON rr.driver_id = d.id
        -- Conta apenas corridas em que o piloto efetivamente largou
        WHERE rr.constructor_id = ? AND rr.position_text NOT IN ('DNP', 'DNQ', 'DNPQ', 'DNS')
        GROUP BY d.id
        ORDER BY value DESC
        LIMIT 10
    """
    starts_df = execute_query(query_starts, (team_id,))
    if not starts_df.empty:
        render_team_bar(starts_df, "driver", "value", "Piloto", "Largadas", [[0, "#85E085"], [0.5, "#2CA02C"], [1, "#115911"]], "chart_starts")
    else:
        st.info("Nenhuma largada oficial registrada para esta equipe.")

with r4_col2:
    st.markdown("#### ⚠️ Top 10: Motivos de Abandono")
    st.caption("Principais falhas mecânicas ou incidentes que tiraram os carros da prova.")
    
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
        failures_df["reason"] = failures_df["reason"].map(STATUS_TRADUCAO).fillna(failures_df["reason"])
        render_team_bar(failures_df, "reason", "total", "Motivo", "Abandonos", [[0, "#85E0E0"], [0.5, "#17BECF"], [1, "#0A6B75"]], "chart_failures", orientation='h')
    else:
        st.success("Esta equipe tem um histórico impecável ou não há dados de abandono.")

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. TÍTULOS ---
r5_col1, r5_col2 = st.columns(2)
with r5_col1:
    st.markdown("#### 🏆 Evolução de Títulos Mundiais")
    st.caption("Acúmulo de campeonatos de construtores conquistados ao longo dos anos.")
    render_team_evolution(evo_df, "year", "cum_titles", "Títulos Acumulados", "#9467BD", "evo_titles")

with r5_col2:
    st.markdown("#### 🧑‍🚀 Evolução de Títulos de Pilotos")
    st.caption("Títulos mundiais de pilotos conquistados com os carros da equipe, acumulados ao longo dos anos.")
    render_team_evolution(evo_df, "year", "cum_driver_titles", "Títulos de Pilotos", "#9467BD", "evo_driver_titles", custom_hover_col="hover_text")

render_footer()