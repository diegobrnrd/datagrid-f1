import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.db import execute_query, get_all_drivers, get_driver_career_evolution
from utils.constants import PAISES_TRADUCAO
from utils.ui import setup_sidebar, render_footer

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="DataGrid F1 | Pilotos",
    page_icon="🧑‍🚀",
    layout="wide",
)

setup_sidebar()

st.title("🧑‍🚀 Central Analítica do Piloto")
st.markdown("Raio-X completo da carreira: explore a conversão de resultados, histórico por equipe e o perfil de desempenho de cada piloto.")
st.divider()


# ==========================================
# 2. CARREGAMENTO BASE
# ==========================================
@st.cache_data(show_spinner=False)
def load_drivers_list():
    df = get_all_drivers()
    df["nationality"] = df["nationality"].map(PAISES_TRADUCAO).fillna(df["nationality"])
    return df


drivers_df = load_drivers_list()

tab_individual, tab_general = st.tabs(["Estatísticas Individuais", "Estatísticas Gerais"])


with tab_individual:
    col_busca, col_vazia = st.columns([1, 2])
    with col_busca:
        search_term = st.text_input("🔍 Pesquisar piloto (Ex: Senna, Hamilton):", "")

    if search_term:
        filtered_drivers = drivers_df[drivers_df["full_name"].str.contains(search_term, case=False, na=False)]
    else:
        filtered_drivers = drivers_df

    if filtered_drivers.empty:
        st.warning("Nenhum piloto encontrado com esse nome.")
    else:
        driver_selected_name = st.selectbox("Selecione um piloto para analisar:", filtered_drivers["full_name"])
        driver_row = filtered_drivers[filtered_drivers["full_name"] == driver_selected_name].iloc[0]
        driver_id = driver_row["id"]

        # ==========================================
        # 3. EXTRAÇÃO DE DADOS PROFUNDOS
        # ==========================================
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

        query_wins_by_team = """
            SELECT c.name AS constructor, COUNT(*) AS wins
            FROM race_result rr
            JOIN constructor c ON rr.constructor_id = c.id
            WHERE rr.driver_id = ? AND rr.position_number = 1
            GROUP BY c.name
            ORDER BY wins DESC
        """
        wins_by_team = execute_query(query_wins_by_team, (driver_id,))

        query_fastest = """
            SELECT COUNT(*) AS fastest_count
            FROM race_result
            WHERE driver_id = ? AND fastest_lap = 1
        """
        fastest_count = int(execute_query(query_fastest, (driver_id,)).iloc[0]["fastest_count"] or 0)

        query_hat = """
            SELECT COUNT(*) AS hat_count
            FROM race_result
            WHERE driver_id = ? AND pole_position = 1 AND fastest_lap = 1 AND position_number = 1
        """
        hat_count = int(execute_query(query_hat, (driver_id,)).iloc[0]["hat_count"] or 0)

        query_grand = """
            SELECT COUNT(*) AS grand_count
            FROM race_result
            WHERE driver_id = ? AND grand_slam = 1
        """
        grand_count = int(execute_query(query_grand, (driver_id,)).iloc[0]["grand_count"] or 0)

        career_evolution_df = get_driver_career_evolution(driver_id)

        # ==========================================
        # 4. CARTÃO BIOGRÁFICO E MÉTRICAS DE OURO
        # ==========================================
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

        with col_chart1:
            st.markdown("#### 🎯 Taxa de Conversão (Letalidade)")
            st.caption("De todas as corridas que largou, quantas viraram pódio e vitória?")
            if starts > 0:
                fig_funnel = go.Figure(go.Funnel(
                    y=["Largadas", "Pódios", "Vitórias"],
                    x=[starts, podiums, wins],
                    textinfo="value+percent initial",
                    textfont=dict(color=["white", "white", "black"]),
                    marker={"color": ["#7A0000", "#E10600", "#FF6A6A"]},
                ))
                fig_funnel.update_layout(margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_funnel, width="stretch", key=f"funnel_{driver_id}")
            else:
                st.info("Este piloto não possui largadas registradas.")

        with col_chart2:
            st.markdown("#### 🏭 Vitórias por Equipe")
            st.caption("A contribuição do piloto por construtora.")
            if not wins_by_team.empty:
                fig_bar = px.bar(
                    wins_by_team,
                    x="constructor",
                    y="wins",
                    labels={"constructor": "Equipe", "wins": "Vitórias"},
                    color="wins",
                    color_continuous_scale=["#FF6A6A","#E10600", "#7A0000"],
                )
                fig_bar.update_layout(showlegend=False, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
                st.plotly_chart(fig_bar, width="stretch", key=f"wins_by_team_{driver_id}")
            else:
                st.info("Este piloto não possui vitórias registradas.")

        with col_chart3:
            st.markdown("#### 🕸️ Perfil do Piloto (Radar)")
            st.caption("Comparativo percentual das métricas de sucesso.")
            if starts > 0:
                win_rate = (wins / starts) * 100
                podium_rate = (podiums / starts) * 100
                pole_rate = (poles / starts) * 100

                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=[win_rate, podium_rate, pole_rate, win_rate],
                    theta=["Vitórias (%)", "Pódios (%)", "Poles (%)", "Vitórias (%)"],
                    fill="toself",
                    name=driver_selected_name,
                    line_color="#E10600",
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, max(win_rate, podium_rate, pole_rate, 10) + 10])),
                    showlegend=False,
                    margin=dict(l=40, r=40, t=20, b=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_radar, width="stretch", key=f"radar_{driver_id}")
            else:
                st.info("Dados insuficientes para gerar o radar.")

        st.divider()

        # ==========================================
        # 6. EVOLUÇÃO ANUAL DA CARREIRA (GRÁFICOS)
        # ==========================================
        st.subheader("📈 Evolução Anual de Carreira")

        if career_evolution_df.empty:
            st.info("Não há dados suficientes para montar os gráficos de evolução deste piloto.")
        else:
            plot_df = career_evolution_df[[
                "year",
                "titles_year",
                "titles_cumulative",
                "wins_year",
                "wins_cumulative",
                "podiums_year",
                "podiums_cumulative",
                "poles_year",
                "poles_cumulative",
                "fastest_laps_year",
                "fastest_laps_cumulative",
                "hat_tricks_year",
                "hat_tricks_cumulative",
                "grand_slems_year",
                "grand_slems_cumulative",
            ]].copy()

            plot_df["year"] = pd.to_numeric(plot_df["year"], errors="coerce").astype(int)

            def render_evolution_chart(title: str, cum_col: str, year_col: str, y_label: str, color: str):
                """Renderiza gráfico de linha mostrando a evolução acumulada de uma métrica."""
                fig = px.line(
                    plot_df,
                    x="year",
                    y=cum_col,
                    markers=True,
                    labels={"year": "Ano", cum_col: y_label},
                    custom_data=[plot_df[year_col]],
                )
                hover_tmpl = f"Ano: %{{x}}<br>{y_label} (acumulado): %{{y}}<br>{y_label} no ano: %{{customdata[0]}}"
                fig.update_traces(line_color=color, hovertemplate=hover_tmpl)
                fig.update_layout(
                    title=title,
                    margin=dict(l=0, r=0, t=50, b=0),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(dtick=1),
                )
                fig.update_yaxes(rangemode="tozero")
                st.plotly_chart(fig, width="stretch", key=f"line_{cum_col}_{driver_id}")

            def render_lollipop(title: str, year_col: str, y_label: str, color: str):
                """Renderiza gráfico do tipo lollipop para exibir valores absolutos por ano."""
                fig = go.Figure()
                years = plot_df["year"].tolist()
                vals = plot_df[year_col].tolist()
                for x, y in zip(years, vals):
                    fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color=color, width=2))
                fig.add_trace(go.Scatter(
                    x=years,
                    y=vals,
                    mode="markers",
                    marker=dict(color=color, size=10),
                    hovertemplate=f"Ano: %{{x}}<br>{y_label}: %{{y}}",
                ))
                fig.update_layout(title=title, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                fig.update_xaxes(dtick=1)
                fig.update_yaxes(rangemode="tozero")
                st.plotly_chart(fig, width="stretch", key=f"lollipop_{year_col}_{driver_id}")

            cols = st.columns([3, 2])
            with cols[0]:
                render_evolution_chart("Evolução de Títulos Mundiais", "titles_cumulative", "titles_year", "Títulos", "#E10600")
            with cols[1]:
                render_lollipop("Títulos por Ano", "titles_year", "Títulos", "#E10600")

            cols = st.columns([3, 2])
            with cols[0]:
                render_evolution_chart("Evolução de Vitórias", "wins_cumulative", "wins_year", "Vitórias", "#FF7F0E")
            with cols[1]:
                render_lollipop("Vitórias por Ano", "wins_year", "Vitórias", "#FF7F0E")

            cols = st.columns([3, 2])
            with cols[0]:
                render_evolution_chart("Evolução de Pódios", "podiums_cumulative", "podiums_year", "Pódios", "#1F77B4")
            with cols[1]:
                render_lollipop("Pódios por Ano", "podiums_year", "Pódios", "#1F77B4")

            cols = st.columns([3, 2])
            with cols[0]:
                render_evolution_chart("Evolução de Poles", "poles_cumulative", "poles_year", "Poles", "#2CA02C")
            with cols[1]:
                render_lollipop("Poles por Ano", "poles_year", "Poles", "#2CA02C")

            cols = st.columns([3, 2])
            with cols[0]:
                render_evolution_chart("Evolução de Voltas Mais Rápidas", "fastest_laps_cumulative", "fastest_laps_year", "Voltas Mais Rápidas", "#17BECF")
            with cols[1]:
                render_lollipop("Voltas Mais Rápidas por Ano", "fastest_laps_year", "Voltas Mais Rápidas", "#17BECF")

            cols = st.columns([3, 2])
            with cols[0]:
                render_evolution_chart("Evolução de Hat Tricks", "hat_tricks_cumulative", "hat_tricks_year", "Hat Tricks", "#9467BD")
            with cols[1]:
                render_lollipop("Hat Tricks por Ano", "hat_tricks_year", "Hat Tricks", "#9467BD")

            cols = st.columns([3, 2])
            with cols[0]:
                render_evolution_chart("Evolução de Grand Chelems", "grand_slems_cumulative", "grand_slems_year", "Grand Chelems", "#8C564B")
            with cols[1]:
                render_lollipop("Grand Chelems por Ano", "grand_slems_year", "Grand Chelems", "#8C564B")


with tab_general:
    st.subheader("📊 Estatísticas Gerais")

    def build_general_table(query: str) -> pd.DataFrame:
        """Executa uma query e adiciona a coluna de Posição ao DataFrame."""
        df = execute_query(query)
        if df.empty:
            return df
        df = df.reset_index(drop=True)
        df.insert(0, "Posição", range(1, len(df) + 1))
        return df

    def render_general_table(title: str, df: pd.DataFrame):
        """Renderiza a tabela padronizada no Streamlit."""
        st.markdown(f"#### {title}")
        st.dataframe(df, width="stretch", hide_index=True)

    championships_df = build_general_table(
        """
        SELECT d.full_name AS Piloto, d.total_championship_wins AS Total
        FROM driver d
        WHERE d.total_championship_wins > 0
        ORDER BY d.total_championship_wins DESC, d.last_name ASC
        """
    )
    wins_df = build_general_table(
        """
        SELECT d.full_name AS Piloto, d.total_race_wins AS Total
        FROM driver d
        WHERE d.total_race_wins > 0
        ORDER BY d.total_race_wins DESC, d.last_name ASC
        """
    )
    podiums_df = build_general_table(
        """
        SELECT d.full_name AS Piloto, d.total_podiums AS Total
        FROM driver d
        WHERE d.total_podiums > 0
        ORDER BY d.total_podiums DESC, d.last_name ASC
        """
    )
    poles_df = build_general_table(
        """
        SELECT d.full_name AS Piloto, d.total_pole_positions AS Total
        FROM driver d
        WHERE d.total_pole_positions > 0
        ORDER BY d.total_pole_positions DESC, d.last_name ASC
        """
    )
    fastest_df = build_general_table(
        """
        SELECT d.full_name AS Piloto, COUNT(*) AS Total
        FROM race_result rr
        INNER JOIN driver d ON rr.driver_id = d.id
        WHERE rr.fastest_lap = 1
        GROUP BY rr.driver_id, d.full_name, d.last_name
        ORDER BY Total DESC, d.last_name ASC
        """
    )
    hats_df = build_general_table(
        """
        SELECT d.full_name AS Piloto, COUNT(*) AS Total
        FROM race_result rr
        INNER JOIN driver d ON rr.driver_id = d.id
        WHERE rr.pole_position = 1 AND rr.fastest_lap = 1 AND rr.position_number = 1
        GROUP BY rr.driver_id, d.full_name, d.last_name
        ORDER BY Total DESC, d.last_name ASC
        """
    )
    grand_df = build_general_table(
        """
        SELECT d.full_name AS Piloto, COUNT(*) AS Total
        FROM race_result rr
        INNER JOIN driver d ON rr.driver_id = d.id
        WHERE rr.grand_slam = 1
        GROUP BY rr.driver_id, d.full_name, d.last_name
        ORDER BY Total DESC, d.last_name ASC
        """
    )
    starts_df = build_general_table(
        """
        SELECT d.full_name AS Piloto, d.total_race_starts AS Total
        FROM driver d
        ORDER BY d.total_race_starts DESC, d.last_name ASC
        """
    )

    table_rows = [
        ("Campeonatos de Pilotos", championships_df),
        ("Vitórias", wins_df),
        ("Pódios", podiums_df),
        ("Poles", poles_df),
        ("Voltas Mais Rápidas", fastest_df),
        ("Hat Tricks", hats_df),
        ("Grand Chelems", grand_df),
        ("Largadas", starts_df),
    ]

    for left_index in range(0, len(table_rows), 2):
        left_title, left_df = table_rows[left_index]
        right_title, right_df = table_rows[left_index + 1]
        left_col, right_col = st.columns(2)
        with left_col:
            render_general_table(left_title, left_df)
        with right_col:
            render_general_table(right_title, right_df)


render_footer()