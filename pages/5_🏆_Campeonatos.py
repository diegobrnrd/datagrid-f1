import streamlit as st
from utils.db import get_seasons, get_driver_standings, get_constructor_standings
from utils.ui import setup_sidebar, render_footer

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="DataGrid F1 | Campeonatos",
    page_icon="🏆",
    layout="wide"
)

setup_sidebar()

st.title("🏆 Tabelas de Classificação Final")
st.markdown("Reviva a história de cada temporada: veja quem dominou o Mundial de Pilotos e qual engenharia levou o troféu no Mundial de Construtores.")
st.divider()

# ==========================================
# 2. SELETOR DE TEMPORADA
# ==========================================
seasons = get_seasons()

# Cria colunas para centralizar o seletor
col_space_left, col_selector, col_space_right = st.columns([1, 2, 1])

with col_selector:
    selected_season = st.selectbox(
        "Selecione o ano da temporada para visualizar o campeonato:",
        seasons,
        index=0 # Por padrão, seleciona a temporada mais recente (primeira da lista)
    )

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 3. BUSCA DOS DADOS DE CLASSIFICAÇÃO
# ==========================================
# Busca os dados do campeonato de pilotos
driver_standings = get_driver_standings(selected_season)

# Busca os dados do campeonato de construtores
constructor_standings = get_constructor_standings(selected_season)

# ==========================================
# 4. COROAÇÃO (Destaque dos Campeões)
# ==========================================
if not driver_standings.empty:
    # O piloto campeão é aquele com championship_won = 1 (True) ou o líder de pontos (posição 1)
    champion_row = driver_standings[driver_standings["championship_won"] == 1]
    if champion_row.empty:
         champion_row = driver_standings.iloc[[0]] # Fallback para o líder caso a flag não esteja setada
    
    driver_champion_name = champion_row.iloc[0]["driver_name"]
    driver_champion_points = champion_row.iloc[0]["points"]
else:
    driver_champion_name = "N/A"
    driver_champion_points = 0

if not constructor_standings.empty:
     # Mesma lógica para a equipe campeã
    champion_team_row = constructor_standings[constructor_standings["championship_won"] == 1]
    if champion_team_row.empty:
         champion_team_row = constructor_standings.iloc[[0]]
         
    team_champion_name = champion_team_row.iloc[0]["constructor_name"]
    team_champion_points = champion_team_row.iloc[0]["points"]
else:
    team_champion_name = "N/A"
    team_champion_points = 0


# Exibe as caixas de coroação se houver dados
if not driver_standings.empty:
    col_champ1, col_champ2 = st.columns(2)
    
    with col_champ1:
        # use the champion row determined above (champion_row)
        if champion_row.iloc[0].get("championship_won") == 1:
            st.success(f"**Mundial de Pilotos ({selected_season})**\n\n🏆 Campeão: **{driver_champion_name}** ({driver_champion_points:.1f} pts)")
        else:
            st.info(f"**Mundial de Pilotos ({selected_season})**\n\n🏁 Líder: **{driver_champion_name}** ({driver_champion_points:.1f} pts)\n\n*Campeonato em andamento*")
        
    with col_champ2:
        if selected_season >= 1958 and not constructor_standings.empty:
            if champion_team_row.iloc[0].get("championship_won") == 1:
                st.success(f"**Mundial de Construtores ({selected_season})**\n\n🏭 Campeã: **{team_champion_name}** ({team_champion_points:.1f} pts)")
            else:
                st.info(f"**Mundial de Construtores ({selected_season})**\n\n🏁 Líder: **{team_champion_name}** ({team_champion_points:.1f} pts)\n\n*Campeonato em andamento*")
        elif selected_season < 1958:
            st.warning(f"**Mundial de Construtores ({selected_season})**\n\nO Mundial de Construtores ainda não havia sido criado (iniciou em 1958).")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 5. TABELAS DE CLASSIFICAÇÃO (TABS)
# ==========================================
tab_pilotos, tab_equipes = st.tabs(["👨‍🚀 Classificação de Pilotos", "🏭 Classificação de Construtores"])

with tab_pilotos:
    st.subheader(f"Mundial de Pilotos - Tabela Final de {selected_season}")
    
    if driver_standings.empty:
        st.info("Dados de classificação de pilotos não encontrados para esta temporada.")
    else:
        st.dataframe(
            driver_standings[["position", "driver_name", "points", "championship_won"]],
            width='stretch',
            hide_index=True,
            column_config={
                "position": st.column_config.TextColumn("Posição", width="small"),
                "driver_name": "Piloto",
                "points": st.column_config.NumberColumn("Pontuação Total", format="%.1f"),
                "championship_won": st.column_config.CheckboxColumn("Campeão Mundial 🏆"),
            },
        )

with tab_equipes:
    st.subheader(f"Mundial de Construtores - Tabela Final de {selected_season}")
    
    if selected_season < 1958:
         st.warning("Historicamente, o Campeonato Mundial de Construtores da FIA só foi introduzido em 1958. Portanto, não há classificação de equipes para este ano.")
    elif constructor_standings.empty:
        st.info("Dados de classificação de construtores não encontrados para esta temporada.")
    else:
        st.dataframe(
            constructor_standings[["position", "constructor_name", "points", "championship_won"]],
            width='stretch',
            hide_index=True,
            column_config={
                "position": st.column_config.TextColumn("Posição", width="small"),
                "constructor_name": "Construtora",
                "points": st.column_config.NumberColumn("Pontuação Total", format="%.1f"),
                "championship_won": st.column_config.CheckboxColumn("Campeã Mundial 🏆"),
            },
        )

render_footer()