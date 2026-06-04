"""Página analítica de construtoras."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.constants import PAISES_TRADUCAO, STATUS_TRADUCAO
from utils.db import (
    get_all_constructors,
    get_constructor_driver_metric,
    get_constructor_evolution,
    get_constructor_failure_reasons,
)
from utils.ui import (
    F1_RED,
    F1_RED_SCALE,
    add_vertical_space,
    apply_common_chart_layout,
    plotly_chart,
    render_footer,
    render_header,
    setup_page,
    translate_column,
)

RANKING_COLUMNS = [
    "name",
    "country",
    "total_championship_wins",
    "total_driver_championship_wins",
    "total_race_wins",
    "total_podiums",
    "total_pole_positions",
]

EXPECTED_NUMERIC_COLUMNS = [
    "total_championship_wins",
    "total_driver_championship_wins",
    "total_race_wins",
    "total_podiums",
    "total_pole_positions",
]


@st.cache_data(show_spinner=False)
def load_constructors() -> pd.DataFrame:
    """Carrega a lista de construtoras já traduzida."""
    constructors = translate_column(get_all_constructors(), "country", PAISES_TRADUCAO)
    for column in EXPECTED_NUMERIC_COLUMNS:
        if column not in constructors.columns:
            constructors[column] = 0
        constructors[column] = pd.to_numeric(constructors[column], errors="coerce").fillna(0).astype(int)
    return constructors


@st.cache_data(show_spinner=False)
def load_constructor_report(constructor_id: int | str) -> dict[str, pd.DataFrame]:
    """Carrega todos os dados do relatório de uma construtora."""
    return {
        "evolution": get_constructor_evolution(constructor_id),
        "wins": get_constructor_driver_metric(constructor_id, "wins"),
        "poles": get_constructor_driver_metric(constructor_id, "poles"),
        "podiums": get_constructor_driver_metric(constructor_id, "podiums"),
        "starts": get_constructor_driver_metric(constructor_id, "starts"),
        "failures": get_constructor_failure_reasons(constructor_id),
    }


def render_global_ranking(constructors_df: pd.DataFrame) -> None:
    st.subheader("🌍 Ranking Histórico Global")
    st.dataframe(
        constructors_df.reindex(columns=RANKING_COLUMNS).head(50),
        width="stretch",
        hide_index=True,
        column_config={
            "name": "Construtora",
            "country": "País Sede",
            "total_championship_wins": st.column_config.NumberColumn("Títulos Mundiais", format="%d"),
            "total_driver_championship_wins": st.column_config.NumberColumn("Títulos de Pilotos", format="%d"),
            "total_race_wins": st.column_config.NumberColumn("Vitórias", format="%d"),
            "total_podiums": st.column_config.NumberColumn("Pódios", format="%d"),
            "total_pole_positions": st.column_config.NumberColumn("Poles", format="%d"),
        },
    )


def render_team_metrics(team_row: pd.Series) -> None:
    metrics = st.columns(6)
    metrics[0].metric("País de Origem", team_row["country"])
    metrics[1].metric("Títulos Mundiais", int(team_row["total_championship_wins"]))
    metrics[2].metric("Títulos Piloto", int(team_row["total_driver_championship_wins"]))
    metrics[3].metric("Vitórias Totais", int(team_row["total_race_wins"]))
    metrics[4].metric("Pódios Totais", int(team_row["total_podiums"]))
    metrics[5].metric("Poles Totais", int(team_row["total_pole_positions"]))
    add_vertical_space()


def render_team_lollipop(
    df: pd.DataFrame,
    *,
    category_col: str,
    value_col: str,
    category_label: str,
    value_label: str,
    color: str,
    key: str,
) -> None:
    """Renderiza um gráfico lollipop padronizado."""
    fig = go.Figure()
    categories = df[category_col].tolist()
    values = df[value_col].tolist()
    for category, value in zip(categories, values):
        fig.add_shape(type="line", x0=category, x1=category, y0=0, y1=value, line=dict(color=color, width=2))
    fig.add_trace(
        go.Scatter(
            x=categories,
            y=values,
            mode="markers",
            marker=dict(color=color, size=10),
            hovertemplate=f"{category_label}: %{{x}}<br>{value_label}: %{{y}}<extra></extra>",
        )
    )
    apply_common_chart_layout(fig)
    if pd.api.types.is_numeric_dtype(df[category_col]):
        fig.update_xaxes(dtick=5)
    fig.update_yaxes(rangemode="tozero")
    plotly_chart(fig, key=key)


def render_team_bar(
    df: pd.DataFrame,
    *,
    category_col: str,
    value_col: str,
    category_label: str,
    value_label: str,
    color_scale: list,
    key: str,
    orientation: str = "v",
) -> None:
    """Renderiza gráfico de barras vertical ou horizontal."""
    if orientation == "v":
        fig = px.bar(
            df,
            x=category_col,
            y=value_col,
            labels={category_col: category_label, value_col: value_label},
            color=value_col,
            color_continuous_scale=color_scale,
        )
        fig.update_yaxes(rangemode="tozero")
    else:
        fig = px.bar(
            df,
            x=value_col,
            y=category_col,
            orientation="h",
            labels={category_col: category_label, value_col: value_label},
            color=value_col,
            color_continuous_scale=color_scale,
        )
        fig.update_xaxes(rangemode="tozero")
        fig.update_yaxes(autorange="reversed")

    apply_common_chart_layout(fig, show_color_scale=False)
    plotly_chart(fig, key=key)


def render_team_evolution(
    df: pd.DataFrame,
    *,
    x_col: str,
    y_col: str,
    y_label: str,
    color: str,
    key: str,
    custom_hover_col: str | None = None,
) -> None:
    """Renderiza gráfico de linha para evolução acumulada de uma equipe."""
    if df.empty or df[y_col].max() == 0:
        st.info(f"Sem registros de {y_label.lower()} para esta equipe.")
        return

    if custom_hover_col:
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            markers=True,
            labels={x_col: "Ano", y_col: y_label},
            custom_data=[df[custom_hover_col]],
        )
        hovertemplate = f"Ano: %{{x}}<br>{y_label}: %{{y}}<br>%{{customdata[0]}}<extra></extra>"
    else:
        fig = px.line(df, x=x_col, y=y_col, markers=True, labels={x_col: "Ano", y_col: y_label})
        hovertemplate = f"Ano: %{{x}}<br>{y_label}: %{{y}}<extra></extra>"

    fig.update_traces(line_color=color, hovertemplate=hovertemplate)
    apply_common_chart_layout(fig)
    fig.update_layout(xaxis=dict(dtick=5), yaxis=dict(dtick=1 if df[y_col].max() < 10 else None, rangemode="tozero"))
    plotly_chart(fig, key=key)


def render_metric_pair(
    title: str,
    caption: str,
    metric_df: pd.DataFrame,
    evolution_df: pd.DataFrame,
    *,
    metric_name: str,
    metric_label: str,
    yearly_column: str,
    color: str,
    color_scale: list,
    team_id: int | str,
) -> None:
    left_col, right_col = st.columns(2)
    with left_col:
        st.markdown(f"#### {title}")
        st.caption(caption)
        if metric_df.empty:
            st.info(f"Nenhum registro de {metric_label.lower()} para esta equipe.")
        else:
            render_team_bar(
                metric_df,
                category_col="driver",
                value_col="value",
                category_label="Piloto",
                value_label=metric_label,
                color_scale=color_scale,
                key=f"chart_{metric_name}_{team_id}",
            )

    with right_col:
        st.markdown(f"#### 📈 {metric_label} por Temporada")
        st.caption(f"Total de {_label_lower(metric_label)} conquistados em cada ano de participação.")
        filtered_evolution = evolution_df[evolution_df[yearly_column] > 0].copy() if not evolution_df.empty else evolution_df
        if filtered_evolution.empty:
            st.info(f"Sem registros de {metric_label.lower()} para esta equipe.")
        else:
            render_team_lollipop(
                filtered_evolution,
                category_col="year",
                value_col=yearly_column,
                category_label="Ano",
                value_label=metric_label,
                color=color,
                key=f"evo_{metric_name}_{team_id}",
            )


def _label_lower(label: str) -> str:
    """Normaliza labels para textos de legenda."""
    return label.lower()


def render_failures(failures_df: pd.DataFrame, team_id: int | str) -> None:
    st.markdown("#### ⚠️ Top 10: Motivos de Abandono")
    st.caption("Principais falhas mecânicas ou incidentes que tiraram os carros da prova.")

    if failures_df.empty:
        st.success("Esta equipe tem um histórico impecável ou não há dados de abandono.")
        return

    translated_failures = failures_df.copy()
    translated_failures["reason"] = translated_failures["reason"].map(STATUS_TRADUCAO).fillna(translated_failures["reason"])
    render_team_bar(
        translated_failures,
        category_col="reason",
        value_col="total",
        category_label="Motivo",
        value_label="Abandonos",
        color_scale=[[0, "#85E0E0"], [0.5, "#17BECF"], [1, "#0A6B75"]],
        key=f"chart_failures_{team_id}",
        orientation="h",
    )


def render_team_panel(team_id: int | str, report: dict[str, pd.DataFrame]) -> None:
    st.markdown("### Painel de Desempenho e Histórico")
    evolution_df = report["evolution"]

    render_metric_pair(
        "🥇 Top 10: Vitórias",
        "Pilotos que mais trouxeram o lugar mais alto do pódio para a equipe.",
        report["wins"],
        evolution_df,
        metric_name="wins",
        metric_label="Vitórias",
        yearly_column="wins",
        color=F1_RED,
        color_scale=F1_RED_SCALE,
        team_id=team_id,
    )
    add_vertical_space()

    render_metric_pair(
        "⏱️ Top 10: Pole Positions",
        "Pilotos que mais vezes largaram na primeira posição pela equipe.",
        report["poles"],
        evolution_df,
        metric_name="poles",
        metric_label="Poles",
        yearly_column="poles",
        color="#FF7F0E",
        color_scale=[[0, "#FFC285"], [0.5, "#FF7F0E"], [1, "#A34A00"]],
        team_id=team_id,
    )
    add_vertical_space()

    render_metric_pair(
        "🍾 Top 10: Pódios",
        "Pilotos com maior presença no Top 3 vestindo as cores da escuderia.",
        report["podiums"],
        evolution_df,
        metric_name="podiums",
        metric_label="Pódios",
        yearly_column="podiums",
        color="#1F77B4",
        color_scale=[[0, "#85C2FF"], [0.5, "#1F77B4"], [1, "#0B4073"]],
        team_id=team_id,
    )
    add_vertical_space()

    starts_col, failures_col = st.columns(2)
    with starts_col:
        st.markdown("#### 🏁 Top 10: Corridas Disputadas")
        st.caption("Pilotos mais fiéis em número de largadas oficiais pela equipe.")
        if report["starts"].empty:
            st.info("Nenhuma largada oficial registrada para esta equipe.")
        else:
            render_team_bar(
                report["starts"],
                category_col="driver",
                value_col="value",
                category_label="Piloto",
                value_label="Largadas",
                color_scale=[[0, "#85E085"], [0.5, "#2CA02C"], [1, "#115911"]],
                key=f"chart_starts_{team_id}",
            )
    with failures_col:
        render_failures(report["failures"], team_id)

    add_vertical_space()
    titles_col, driver_titles_col = st.columns(2)
    with titles_col:
        st.markdown("#### 🏆 Evolução de Títulos Mundiais")
        st.caption("Acúmulo de campeonatos de construtores conquistados ao longo dos anos.")
        render_team_evolution(
            evolution_df,
            x_col="year",
            y_col="cum_titles",
            y_label="Títulos Acumulados",
            color="#9467BD",
            key=f"evo_titles_{team_id}",
        )
    with driver_titles_col:
        st.markdown("#### 🧑‍🚀 Evolução de Títulos de Pilotos")
        st.caption("Títulos mundiais de pilotos conquistados com os carros da equipe, acumulados ao longo dos anos.")
        render_team_evolution(
            evolution_df,
            x_col="year",
            y_col="cum_driver_titles",
            y_label="Títulos de Pilotos",
            color="#9467BD",
            key=f"evo_driver_titles_{team_id}",
            custom_hover_col="hover_text",
        )


def render_deep_dive(constructors_df: pd.DataFrame) -> None:
    st.subheader("🔎 Análise Profunda por Equipe")
    selected_team = st.selectbox("Selecione uma equipe para gerar o relatório:", constructors_df["name"])
    team_row = constructors_df[constructors_df["name"] == selected_team].iloc[0]
    team_id = team_row["id"]

    render_team_metrics(team_row)
    report = load_constructor_report(team_id)
    render_team_panel(team_id, report)


def main() -> None:
    setup_page("DataGrid F1 | Construtoras", "🏭")
    render_header(
        "🏭 Domínio da Engenharia",
        "Descubra quais equipes dominaram a Fórmula 1, quais pilotos carregaram essas escuderias e qual a verdadeira taxa de confiabilidade de seus carros.",
    )

    constructors_df = load_constructors()
    render_global_ranking(constructors_df)
    st.divider()
    render_deep_dive(constructors_df)
    render_footer()


if __name__ == "__main__":
    main()
