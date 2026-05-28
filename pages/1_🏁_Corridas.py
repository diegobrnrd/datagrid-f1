import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import get_seasons, get_races_by_season, get_race_results
from utils.constants import STATUS_TRADUCAO
from utils.ui import setup_sidebar, render_footer

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="DataGrid F1 | Corridas",
    page_icon="🏁",
    layout="wide"
)

setup_sidebar()

st.title("🏁 Explorador de Grandes Prêmios")
st.markdown("Mergulhe nos resultados oficiais, posições de largada e estatísticas de confiabilidade de qualquer corrida da história.")
st.divider()

# ==========================================
# 2. FILTROS EM CASCATA (Header)
# ==========================================
# Primeiro pegamos as temporadas para o primeiro filtro
seasons = get_seasons()

col_filtro1, col_filtro2 = st.columns([1, 3])

with col_filtro1:
    selected_season = st.selectbox("1. Selecione a Temporada:", seasons)

# Busca as corridas do ano selecionado
races = get_races_by_season(selected_season)

if races.empty:
    st.warning(f"Nenhuma corrida registrada para o ano de {selected_season}.")
    st.stop() # Interrompe a execução da página aqui

# Formata a data para padrão brasileiro
races["date"] = pd.to_datetime(races["date"]).dt.strftime("%d/%m/%Y")

with col_filtro2:
    # Cria as opções do selectbox baseadas no DataFrame de corridas
    race_option = st.selectbox(
        "2. Selecione a Etapa (Grand Prix):",
        races.index,
        format_func=lambda x: f"Etapa {races.loc[x, 'round']} - {races.loc[x, 'official_name']} ({races.loc[x, 'date']})"
    )

selected_race = races.loc[race_option]
race_id = int(selected_race["id"])

# ==========================================
# 3. PAINEL DO EVENTO (Resumo)
# ==========================================
st.markdown(f"### 🏆 {selected_race['official_name']}")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Data", selected_race["date"])
m2.metric("Circuito", selected_race["circuit_name"])
m3.metric("Localização", selected_race["location"])
m4.metric("Voltas Realizadas", int(selected_race["laps"]) if pd.notna(selected_race["laps"]) else "N/A")

st.markdown("<br>", unsafe_allow_html=True)

# Busca os resultados da corrida selecionada
results = get_race_results(race_id)

if results.empty:
    st.info("Os resultados detalhados desta corrida ainda não estão disponíveis no banco de dados.")
    st.stop()

# ==========================================
# 4. PREPARAÇÃO DOS DADOS (ETL Local)
# ==========================================
# Traduz os motivos de abandono (status)
results["status"] = results["status"].map(STATUS_TRADUCAO).fillna(results["status"])

# Trata nulos para exibição limpa
results["time"] = results["time"].fillna("---")
results["status"] = results["status"].fillna("Concluiu a prova")
results["laps"] = results["laps"].fillna(0).astype(int)
results["points"] = results["points"].fillna(0).astype(float)

# ==========================================
# 5. NAVEGAÇÃO POR ABAS (Tabs)
# ==========================================
tab_resultados, tab_grid, tab_insights = st.tabs([
    "🏎️ Resultado Oficial", 
    "🚦 Grid de Largada", 
    "📊 Insights da Corrida"
])

# --- ABA 1: RESULTADO OFICIAL ---
with tab_resultados:
    st.dataframe(
        results[["position", "driver_name", "constructor_name", "laps", "time", "points", "status"]],
        width='stretch',
        hide_index=True,
        column_config={
            "position": st.column_config.TextColumn("Posição", width="small"),
            "driver_name": "Piloto",
            "constructor_name": "Equipe",
            "laps": st.column_config.NumberColumn("Voltas", width="small"),
            "time": "Tempo / Gap",
            "points": st.column_config.NumberColumn("Pontos", format="%.1f"),
            "status": "Situação"
        }
    )

# --- ABA 2: GRID DE LARGADA ---
with tab_grid:
    # Para ordenar o grid corretamente, precisamos converter textos como 'PL' (Pit Lane) para números altos temporariamente
    grid_df = results.copy()
    grid_df["grid_num"] = pd.to_numeric(grid_df["grid"], errors='coerce').fillna(999)
    grid_df = grid_df.sort_values("grid_num")
    
    st.dataframe(
        grid_df[["grid", "driver_name", "constructor_name"]],
        width='stretch',
        hide_index=True,
        column_config={
            "grid": st.column_config.TextColumn("Posição no Grid", width="small"),
            "driver_name": "Piloto",
            "constructor_name": "Equipe"
        }
    )

# --- ABA 3: INSIGHTS DA CORRIDA ---
with tab_insights:
    col_destaques, col_grafico = st.columns([1, 2])
    
    with col_destaques:
        st.subheader("Destaques")

        if results.empty:
            st.info("Não há destaques disponíveis para esta corrida.")
        else:
            pole_row = results[results["pole_position"] == 1]
            pole_name = pole_row.iloc[0]["driver_name"] if not pole_row.empty else "Desconhecido"

            fastest_row = results[results["fastest_lap"] == 1]
            fastest_name = fastest_row.iloc[0]["driver_name"] if not fastest_row.empty else "Desconhecido"

            winner_row = results.iloc[0]
            winner_name = winner_row["driver_name"]
            winner_team = winner_row["constructor_name"]

            hat_trick_row = results[(results["pole_position"] == 1) & (results["fastest_lap"] == 1) & (results["position_number"] == 1)]
            hat_trick_name = hat_trick_row.iloc[0]["driver_name"] if not hat_trick_row.empty else None

            grand_chelem_row = results[results["grand_slam"] == 1]
            grand_chelem_name = grand_chelem_row.iloc[0]["driver_name"] if not grand_chelem_row.empty else None

            st.success(f"**Pole Position:**\n\n🥇 {pole_name}")
            st.success(f"**Vencedor:**\n\n🏆 {winner_name}\n\n{winner_team}")
            st.success(f"**Volta Mais Rápida:**\n\n⏱️ {fastest_name}")

            if hat_trick_name:
                st.success(f"**Hat Trick:**\n\n✨ {hat_trick_name}\n\nPole + volta mais rápida + vitória")

            if grand_chelem_name:
                st.success(f"**Grand Chelem:**\n\n👑 {grand_chelem_name}\n\nPole + volta mais rápida + vitória + todas as voltas lideradas")

    with col_grafico:
        st.subheader("Taxa de Confiabilidade (Terminaram vs Abandonos)")
        
        # Lógica de confiabilidade baseada na coluna `status`
        # Se for "Concluiu a prova" (que definimos no ETL), ele terminou. Caso contrário, abandonou.
        results["is_finished"] = results["status"].apply(lambda x: "Concluíram" if x == "Concluiu a prova" else "Abandonaram")
        reliability_counts = results["is_finished"].value_counts().reset_index()
        reliability_counts.columns = ["Status", "Quantidade"]
        
        # Gráfico de Rosca
        fig_pie = px.pie(
            reliability_counts,
            names="Status",
            values="Quantidade",
            hole=0.5,
            color="Status",
            color_discrete_map={"Concluíram": "#28a745", "Abandonaram": "#dc3545"}
        )
        fig_pie.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        
        st.plotly_chart(fig_pie, width='stretch')
        
        # Lista os motivos de abandono se houverem
        abandonos = results[results["is_finished"] == "Abandonaram"]
        if not abandonos.empty:
            with st.expander("Ver motivos dos abandonos"):
                st.dataframe(
                    abandonos[["driver_name", "constructor_name", "status"]],
                    width='stretch',
                    hide_index=True
                    ,column_config={
                        "driver_name": "Piloto",
                        "constructor_name": "Equipe",
                        "status": "Situação"
                    }
                )

render_footer()