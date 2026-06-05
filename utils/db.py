"""Camada de acesso ao banco SQLite do DataGrid F1.

Este módulo centraliza as consultas SQL usadas pelas páginas Streamlit. A ideia é deixar
as páginas focadas em seleção de filtros e renderização, enquanto as regras de extração e
agregação ficam aqui.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "f1db.db"

ALLOWED_COUNT_TABLES = {"driver", "constructor", "race", "circuit"}


class DBError(RuntimeError):
    """Erro de acesso ou execução de consulta no banco de dados."""


@contextmanager
def get_connection():
    """Abre e fecha uma conexão SQLite com segurança."""
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        yield conn
    except sqlite3.Error as exc:
        raise DBError(f"Erro ao acessar o banco de dados: {exc}") from exc
    finally:
        if conn is not None:
            conn.close()


def _to_python_scalar(value: Any) -> Any:
    """Converte escalares NumPy/Pandas para tipos nativos aceitos pelo sqlite3."""
    return value.item() if hasattr(value, "item") else value


def _normalize_params(params: Any | None) -> tuple[Any, ...] | None:
    if params is None:
        return None
    if isinstance(params, tuple):
        values = params
    elif isinstance(params, Iterable) and not isinstance(params, (str, bytes)):
        values = tuple(params)
    else:
        values = (params,)
    return tuple(_to_python_scalar(value) for value in values)


def execute_query(query: str, params: Any | None = None) -> pd.DataFrame:
    """Executa uma consulta SQL parametrizada e retorna um DataFrame."""
    with get_connection() as conn:
        return pd.read_sql(query, conn, params=_normalize_params(params))


def count_rows(table_name: str) -> int:
    """Conta linhas de uma tabela permitida."""
    if table_name not in ALLOWED_COUNT_TABLES:
        raise ValueError(f"Tabela não permitida para contagem: {table_name}")

    df = execute_query(f"SELECT COUNT(id) AS total FROM {table_name}")
    return int(df.iloc[0]["total"] or 0)


# -----------------------------------------------------------------------------
# Dashboard inicial
# -----------------------------------------------------------------------------


def get_dashboard_counts() -> dict[str, int]:
    """Retorna os KPIs globais usados no dashboard inicial."""
    return {
        "drivers": count_rows("driver"),
        "constructors": count_rows("constructor"),
        "races": count_rows("race"),
        "circuits": count_rows("circuit"),
    }


def get_races_per_year() -> pd.DataFrame:
    """Retorna a quantidade de corridas por temporada."""
    return execute_query(
        """
        SELECT year, COUNT(id) AS total_races
        FROM race
        GROUP BY year
        ORDER BY year
        """
    )


def get_top_host_countries(limit: int = 10) -> pd.DataFrame:
    """Retorna os países que mais sediaram corridas."""
    return execute_query(
        """
        SELECT co.name AS country, SUM(ci.total_races_held) AS total_races
        FROM circuit ci
        LEFT JOIN country co ON ci.country_id = co.id
        WHERE co.name IS NOT NULL
        GROUP BY co.name
        ORDER BY total_races DESC, co.name ASC
        LIMIT ?
        """,
        (limit,),
    )


def get_grid_capacity_by_season() -> pd.DataFrame:
    """Retorna a quantidade média de vagas no grid por temporada."""
    return execute_query(
        """
        WITH race_grid AS (
            SELECT
                r.year,
                rr.race_id,
                COUNT(*) AS grid_slots
            FROM race_result rr
            INNER JOIN race r ON rr.race_id = r.id
            WHERE rr.grid_position_text IS NOT NULL
              AND rr.grid_position_text != ''
            GROUP BY r.year, rr.race_id
        )
        SELECT
            year,
            ROUND(AVG(grid_slots)) AS avg_grid_slots
        FROM race_grid
        GROUP BY year
        ORDER BY year
        """
    )


def get_constructor_count_by_season() -> pd.DataFrame:
    """Retorna a quantidade de equipes distintas por temporada."""
    return execute_query(
        """
        SELECT
            r.year,
            COUNT(DISTINCT rr.constructor_id) AS total_teams
        FROM race_result rr
        INNER JOIN race r ON rr.race_id = r.id
        WHERE rr.constructor_id IS NOT NULL
        GROUP BY r.year
        ORDER BY r.year
        """
    )


def get_top_countries_by_drivers(limit: int = 10) -> pd.DataFrame:
    """Retorna os países com mais pilotos na história da F1."""
    return execute_query(
        """
        SELECT
            c.name AS country,
            COUNT(DISTINCT d.id) AS total_drivers
        FROM driver d
        LEFT JOIN country c ON d.nationality_country_id = c.id
        WHERE c.name IS NOT NULL
        GROUP BY c.name
        ORDER BY total_drivers DESC, c.name ASC
        LIMIT ?
        """,
        (limit,),
    )


def get_top_countries_by_constructors(limit: int = 10) -> pd.DataFrame:
    """Retorna os países com mais equipes na história da F1."""
    return execute_query(
        """
        SELECT
            c.name AS country,
            COUNT(DISTINCT con.id) AS total_constructors
        FROM constructor con
        LEFT JOIN country c ON con.country_id = c.id
        WHERE c.name IS NOT NULL
        GROUP BY c.name
        ORDER BY total_constructors DESC, c.name ASC
        LIMIT ?
        """,
        (limit,),
    )


# -----------------------------------------------------------------------------
# Filtros e corridas
# -----------------------------------------------------------------------------


def get_seasons() -> list[int]:
    """Retorna as temporadas disponíveis, da mais recente para a mais antiga."""
    df = execute_query("SELECT year FROM season ORDER BY year DESC")
    return df["year"].tolist()


def get_races_by_season(year: int) -> pd.DataFrame:
    """Busca todas as corridas de uma temporada específica."""
    return execute_query(
        """
        SELECT
            r.id,
            r.round,
            r.date,
            r.official_name,
            r.laps,
            r.distance,
            c.name AS circuit_name,
            c.place_name AS location
        FROM race r
        LEFT JOIN circuit c ON r.circuit_id = c.id
        WHERE r.year = ?
        ORDER BY r.round
        """,
        (year,),
    )


def get_race_results(race_id: int) -> pd.DataFrame:
    """Retorna o resultado final detalhado de uma corrida específica."""
    return execute_query(
        """
        SELECT
            rr.position_text AS position,
            rr.position_number AS position_number,
            rr.grid_position_text AS grid,
            rr.grid_position_number,
            d.full_name AS driver_name,
            c.name AS constructor_name,
            rr.laps,
            rr.time,
            COALESCE(
                rr.reason_retired,
                CASE
                    WHEN rr.position_text IN ('DNF', 'DNP', 'DNPQ', 'DNQ', 'DNS', 'DSQ', 'EX', 'NC')
                    THEN rr.position_text
                    ELSE NULL
                END
            ) AS status,
            rr.points,
            rr.pole_position,
            rr.fastest_lap,
            rr.grand_slam
        FROM race_result rr
        LEFT JOIN driver d ON rr.driver_id = d.id
        LEFT JOIN constructor c ON rr.constructor_id = c.id
        WHERE rr.race_id = ?
        ORDER BY rr.position_display_order
        """,
        (race_id,),
    )


# -----------------------------------------------------------------------------
# Pilotos
# -----------------------------------------------------------------------------


def get_all_drivers() -> pd.DataFrame:
    """Retorna o diretório completo de pilotos e suas estatísticas base."""
    return execute_query(
        """
        SELECT
            d.id,
            d.full_name,
            d.permanent_number,
            d.date_of_birth,
            c.name AS nationality,
            d.total_race_starts,
            d.total_race_wins,
            d.total_podiums,
            d.total_championship_wins,
            d.total_pole_positions
        FROM driver d
        LEFT JOIN country c ON d.nationality_country_id = c.id
        ORDER BY d.total_race_wins DESC, d.last_name ASC
        """
    )


def get_driver_core_stats(driver_id: int | str) -> pd.Series:
    """Retorna as estatísticas principais de um piloto."""
    df = execute_query(
        """
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
        """,
        (driver_id,),
    )
    if df.empty:
        raise DBError(f"Piloto não encontrado: {driver_id}")
    return df.iloc[0]


def get_driver_wins_by_constructor(driver_id: int | str) -> pd.DataFrame:
    """Retorna as vitórias de um piloto agrupadas por construtora."""
    return execute_query(
        """
        SELECT c.name AS constructor, COUNT(*) AS wins
        FROM race_result rr
        INNER JOIN constructor c ON rr.constructor_id = c.id
        WHERE rr.driver_id = ? AND rr.position_number = 1
        GROUP BY c.name
        ORDER BY wins DESC, c.name ASC
        """,
        (driver_id,),
    )


def get_driver_special_counts(driver_id: int | str) -> pd.Series:
    """Retorna contagens de voltas rápidas, hat tricks e grand chelems."""
    df = execute_query(
        """
        SELECT
            SUM(CASE WHEN fastest_lap = 1 THEN 1 ELSE 0 END) AS fastest_count,
            SUM(CASE WHEN pole_position = 1 AND fastest_lap = 1 AND position_number = 1 THEN 1 ELSE 0 END) AS hat_count,
            SUM(CASE WHEN grand_slam = 1 THEN 1 ELSE 0 END) AS grand_count
        FROM race_result
        WHERE driver_id = ?
        """,
        (driver_id,),
    )
    return df.fillna(0).iloc[0]


def _ranking_table(query: str) -> pd.DataFrame:
    df = execute_query(query)
    if df.empty:
        return df
    ranked_df = df.reset_index(drop=True)
    ranked_df.insert(0, "Posição", range(1, len(ranked_df) + 1))
    return ranked_df


def get_driver_ranking_tables() -> dict[str, pd.DataFrame]:
    """Retorna rankings gerais de pilotos exibidos na aba de estatísticas gerais."""
    ranking_queries = {
        "Campeonatos de Pilotos": """
            SELECT d.full_name AS Piloto, d.total_championship_wins AS Total
            FROM driver d
            WHERE d.total_championship_wins > 0
            ORDER BY d.total_championship_wins DESC, d.last_name ASC
        """,
        "Vitórias": """
            SELECT d.full_name AS Piloto, d.total_race_wins AS Total
            FROM driver d
            WHERE d.total_race_wins > 0
            ORDER BY d.total_race_wins DESC, d.last_name ASC
        """,
        "Pódios": """
            SELECT d.full_name AS Piloto, d.total_podiums AS Total
            FROM driver d
            WHERE d.total_podiums > 0
            ORDER BY d.total_podiums DESC, d.last_name ASC
        """,
        "Poles": """
            SELECT d.full_name AS Piloto, d.total_pole_positions AS Total
            FROM driver d
            WHERE d.total_pole_positions > 0
            ORDER BY d.total_pole_positions DESC, d.last_name ASC
        """,
        "Voltas Mais Rápidas": """
            SELECT d.full_name AS Piloto, COUNT(*) AS Total
            FROM race_result rr
            INNER JOIN driver d ON rr.driver_id = d.id
            WHERE rr.fastest_lap = 1
            GROUP BY rr.driver_id, d.full_name, d.last_name
            ORDER BY Total DESC, d.last_name ASC
        """,
        "Hat Tricks": """
            SELECT d.full_name AS Piloto, COUNT(*) AS Total
            FROM race_result rr
            INNER JOIN driver d ON rr.driver_id = d.id
            WHERE rr.pole_position = 1 AND rr.fastest_lap = 1 AND rr.position_number = 1
            GROUP BY rr.driver_id, d.full_name, d.last_name
            ORDER BY Total DESC, d.last_name ASC
        """,
        "Grand Chelems": """
            SELECT d.full_name AS Piloto, COUNT(*) AS Total
            FROM race_result rr
            INNER JOIN driver d ON rr.driver_id = d.id
            WHERE rr.grand_slam = 1
            GROUP BY rr.driver_id, d.full_name, d.last_name
            ORDER BY Total DESC, d.last_name ASC
        """,
        "Largadas": """
            SELECT d.full_name AS Piloto, d.total_race_starts AS Total
            FROM driver d
            ORDER BY d.total_race_starts DESC, d.last_name ASC
        """,
    }
    return {title: _ranking_table(query) for title, query in ranking_queries.items()}


def get_driver_career_evolution(driver_id: int | str) -> pd.DataFrame:
    """Retorna a evolução anual acumulada dos principais marcos de carreira de um piloto."""
    df = execute_query(
        """
        WITH years AS (
            SELECT DISTINCT r.year
            FROM race_result rr
            INNER JOIN race r ON rr.race_id = r.id
            WHERE rr.driver_id = ?

            UNION

            SELECT DISTINCT sds.year
            FROM season_driver_standing sds
            WHERE sds.driver_id = ?
        ),
        titles AS (
            SELECT sds.year, COUNT(*) AS titles_year
            FROM season_driver_standing sds
            WHERE sds.driver_id = ? AND sds.championship_won = 1
            GROUP BY sds.year
        ),
        wins AS (
            SELECT r.year, COUNT(*) AS wins_year
            FROM race_result rr
            INNER JOIN race r ON rr.race_id = r.id
            WHERE rr.driver_id = ? AND rr.position_number = 1
            GROUP BY r.year
        ),
        podiums AS (
            SELECT r.year, COUNT(*) AS podiums_year
            FROM race_result rr
            INNER JOIN race r ON rr.race_id = r.id
            WHERE rr.driver_id = ? AND rr.position_number IN (1, 2, 3)
            GROUP BY r.year
        ),
        poles AS (
            SELECT r.year, COUNT(*) AS poles_year
            FROM race_result rr
            INNER JOIN race r ON rr.race_id = r.id
            WHERE rr.driver_id = ? AND rr.pole_position = 1
            GROUP BY r.year
        ),
        fastest_laps AS (
            SELECT r.year, COUNT(*) AS fastest_laps_year
            FROM race_result rr
            INNER JOIN race r ON rr.race_id = r.id
            WHERE rr.driver_id = ? AND rr.fastest_lap = 1
            GROUP BY r.year
        ),
        hat_tricks AS (
            SELECT r.year, COUNT(*) AS hat_tricks_year
            FROM race_result rr
            INNER JOIN race r ON rr.race_id = r.id
            WHERE rr.driver_id = ?
              AND rr.position_number = 1
              AND rr.pole_position = 1
              AND rr.fastest_lap = 1
            GROUP BY r.year
        ),
        grand_slems AS (
            SELECT r.year, COUNT(*) AS grand_slems_year
            FROM race_result rr
            INNER JOIN race r ON rr.race_id = r.id
            WHERE rr.driver_id = ? AND rr.grand_slam = 1
            GROUP BY r.year
        )
        SELECT
            y.year,
            COALESCE(t.titles_year, 0) AS titles_year,
            COALESCE(w.wins_year, 0) AS wins_year,
            COALESCE(pod.podiums_year, 0) AS podiums_year,
            COALESCE(pol.poles_year, 0) AS poles_year,
            COALESCE(fl.fastest_laps_year, 0) AS fastest_laps_year,
            COALESCE(ht.hat_tricks_year, 0) AS hat_tricks_year,
            COALESCE(gs.grand_slems_year, 0) AS grand_slems_year
        FROM years y
        LEFT JOIN titles t ON y.year = t.year
        LEFT JOIN wins w ON y.year = w.year
        LEFT JOIN podiums pod ON y.year = pod.year
        LEFT JOIN poles pol ON y.year = pol.year
        LEFT JOIN fastest_laps fl ON y.year = fl.year
        LEFT JOIN hat_tricks ht ON y.year = ht.year
        LEFT JOIN grand_slems gs ON y.year = gs.year
        ORDER BY y.year
        """,
        (driver_id,) * 9,
    )

    if df.empty:
        return df

    metric_columns = [
        "titles_year",
        "wins_year",
        "podiums_year",
        "poles_year",
        "fastest_laps_year",
        "hat_tricks_year",
        "grand_slems_year",
    ]
    for column in metric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).astype(int)
        df[column.replace("_year", "_cumulative")] = df[column].cumsum().astype(int)

    return df

# -----------------------------------------------------------------------------
# Construtoras
# -----------------------------------------------------------------------------


def get_all_constructors() -> pd.DataFrame:
    """Retorna o histórico de todas as construtoras e equipes."""
    return execute_query(
        """
        SELECT
            con.id,
            con.name,
            con.full_name,
            c.name AS country,
            COALESCE(driver_titles.total_driver_championship_wins, 0) AS total_driver_championship_wins,
            con.total_race_wins,
            con.total_podiums,
            con.total_championship_wins,
            COALESCE(poles.total_pole_positions, 0) AS total_pole_positions
        FROM constructor con
        LEFT JOIN country c ON con.country_id = c.id
        LEFT JOIN (
            SELECT
                rr.constructor_id,
                COUNT(DISTINCT sds.year) AS total_driver_championship_wins
            FROM race_result rr
            INNER JOIN race r ON rr.race_id = r.id
            INNER JOIN season_driver_standing sds
                ON rr.driver_id = sds.driver_id
               AND r.year = sds.year
               AND sds.championship_won = 1
            GROUP BY rr.constructor_id
        ) AS driver_titles ON driver_titles.constructor_id = con.id
        LEFT JOIN (
            SELECT constructor_id, COUNT(*) AS total_pole_positions
            FROM race_result
            WHERE pole_position = 1
            GROUP BY constructor_id
        ) AS poles ON poles.constructor_id = con.id
        ORDER BY con.total_race_wins DESC, con.name ASC
        """
    )


def get_constructor_evolution(constructor_id: int | str) -> pd.DataFrame:
    """Retorna evolução anual de títulos, vitórias, poles e pódios de uma equipe."""
    df = execute_query(
        """
        WITH team_years AS (
            SELECT DISTINCT r.year
            FROM race_result rr
            INNER JOIN race r ON rr.race_id = r.id
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
            INNER JOIN race_result rr ON rr.driver_id = sds.driver_id
            INNER JOIN race r ON rr.race_id = r.id AND r.year = sds.year
            INNER JOIN driver d ON d.id = sds.driver_id
            WHERE rr.constructor_id = ? AND sds.championship_won = 1
            GROUP BY r.year
        ),
        team_wins AS (
            SELECT r.year, COUNT(*) AS wins
            FROM race_result rr
            INNER JOIN race r ON rr.race_id = r.id
            WHERE rr.constructor_id = ? AND rr.position_number = 1
            GROUP BY r.year
        ),
        team_poles AS (
            SELECT r.year, COUNT(*) AS poles
            FROM race_result rr
            INNER JOIN race r ON rr.race_id = r.id
            WHERE rr.constructor_id = ? AND rr.pole_position = 1
            GROUP BY r.year
        ),
        team_podiums AS (
            SELECT r.year, COUNT(*) AS podiums
            FROM race_result rr
            INNER JOIN race r ON rr.race_id = r.id
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
        """,
        (constructor_id,) * 6,
    )

    if df.empty:
        return df

    for column in ["titles", "driver_titles", "wins", "poles", "podiums"]:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).astype(int)

    df["cum_titles"] = df["titles"].cumsum()
    df["cum_driver_titles"] = df["driver_titles"].cumsum()
    df["cum_wins"] = df["wins"].cumsum()
    df["cum_poles"] = df["poles"].cumsum()
    df["cum_podiums"] = df["podiums"].cumsum()
    df["hover_text"] = df.apply(
        lambda row: f"Piloto: {row['driver_name']}" if row["driver_titles"] > 0 and row["driver_name"] else "",
        axis=1,
    )
    return df


_CONSTRUCTOR_DRIVER_METRICS = {
    "wins": "rr.position_number = 1",
    "poles": "rr.pole_position = 1",
    "podiums": "rr.position_number IN (1, 2, 3)",
    "starts": "rr.position_text NOT IN ('DNP', 'DNQ', 'DNPQ', 'DNS')",
}


def get_constructor_driver_metric(
    constructor_id: int | str,
    metric: str,
    *,
    limit: int = 10,
) -> pd.DataFrame:
    """Retorna Top N pilotos de uma equipe para a métrica solicitada."""
    if metric not in _CONSTRUCTOR_DRIVER_METRICS:
        raise ValueError(f"Métrica de construtora inválida: {metric}")

    condition = _CONSTRUCTOR_DRIVER_METRICS[metric]
    return execute_query(
        f"""
        SELECT d.last_name AS driver, COUNT(*) AS value
        FROM race_result rr
        INNER JOIN driver d ON rr.driver_id = d.id
        WHERE rr.constructor_id = ? AND {condition}
        GROUP BY d.id, d.last_name
        ORDER BY value DESC, d.last_name ASC
        LIMIT ?
        """,
        (constructor_id, limit),
    )


def get_constructor_failure_reasons(constructor_id: int | str, *, limit: int = 10) -> pd.DataFrame:
    """Retorna os principais motivos de abandono de uma construtora."""
    return execute_query(
        """
        SELECT reason_retired AS reason, COUNT(*) AS total
        FROM race_result
        WHERE constructor_id = ? AND reason_retired IS NOT NULL
        GROUP BY reason_retired
        ORDER BY total DESC, reason_retired ASC
        LIMIT ?
        """,
        (constructor_id, limit),
    )


# -----------------------------------------------------------------------------
# Circuitos
# -----------------------------------------------------------------------------


def get_all_circuits() -> pd.DataFrame:
    """Retorna todos os circuitos com dados de geolocalização para os mapas."""
    return execute_query(
        """
        SELECT
            ci.id,
            ci.name,
            ci.place_name,
            co.name AS country,
            ci.latitude,
            ci.longitude,
            ci.length,
            ci.turns,
            ci.total_races_held
        FROM circuit ci
        LEFT JOIN country co ON ci.country_id = co.id
        ORDER BY ci.name
        """
    )


_CIRCUIT_ENTITY_SQL = {
    "driver": {
        "join": "driver e ON rr.driver_id = e.id",
        "name": "e.last_name AS name",
    },
    "constructor": {
        "join": "constructor e ON rr.constructor_id = e.id",
        "name": "e.name AS name",
    },
}

_CIRCUIT_METRIC_SQL = {
    "wins": {"condition": "rr.position_number = 1", "label": "vitórias"},
    "podiums": {"condition": "rr.position_number IN (1, 2, 3)", "label": "pódios"},
    "poles": {"condition": "rr.pole_position = 1", "label": "poles"},
}


def get_circuit_record(circuit_id: int | str, entity_type: str, metric_type: str) -> pd.DataFrame:
    """Retorna o maior vencedor/maior pontuador de uma métrica em um circuito."""
    if entity_type not in _CIRCUIT_ENTITY_SQL:
        raise ValueError(f"Tipo de entidade inválido: {entity_type}")
    if metric_type not in _CIRCUIT_METRIC_SQL:
        raise ValueError(f"Tipo de métrica inválido: {metric_type}")

    entity = _CIRCUIT_ENTITY_SQL[entity_type]
    metric = _CIRCUIT_METRIC_SQL[metric_type]
    df = execute_query(
        f"""
        SELECT {entity['name']}, COUNT(*) AS total
        FROM race_result rr
        INNER JOIN race r ON rr.race_id = r.id
        INNER JOIN {entity['join']}
        WHERE r.circuit_id = ? AND {metric['condition']}
        GROUP BY e.id
        ORDER BY total DESC, name ASC
        LIMIT 1
        """,
        (circuit_id,),
    )
    if not df.empty:
        df["label"] = metric["label"]
    return df


def get_circuit_grid_wins(circuit_id: int | str) -> pd.DataFrame:
    """Retorna vitórias por posição de largada em um circuito."""
    return execute_query(
        """
        SELECT rr.grid_position_number AS grid_pos, COUNT(*) AS wins
        FROM race_result rr
        INNER JOIN race r ON rr.race_id = r.id
        WHERE r.circuit_id = ?
          AND rr.position_number = 1
          AND rr.grid_position_number > 0
        GROUP BY rr.grid_position_number
        ORDER BY grid_pos ASC
        """,
        (circuit_id,),
    )


# -----------------------------------------------------------------------------
# Campeonatos
# -----------------------------------------------------------------------------


def get_driver_standings(year: int) -> pd.DataFrame:
    """Retorna a classificação final do Mundial de Pilotos de um ano."""
    return execute_query(
        """
        SELECT
            sds.position_text AS position,
            d.full_name AS driver_name,
                REPLACE(
                    (
                        SELECT GROUP_CONCAT(DISTINCT c.name)
                        FROM race_result rr
                        INNER JOIN race r ON rr.race_id = r.id
                        INNER JOIN constructor c ON rr.constructor_id = c.id
                        WHERE r.year = sds.year AND rr.driver_id = sds.driver_id
                    ), ',', ' / '
                ) AS constructor_name,
            sds.points,
            sds.championship_won
        FROM season_driver_standing sds
        LEFT JOIN driver d ON sds.driver_id = d.id
        WHERE sds.year = ?
        ORDER BY sds.position_display_order
        """,
        (year,),
    )


def get_constructor_standings(year: int) -> pd.DataFrame:
    """Retorna a classificação final do Mundial de Construtores de um ano."""
    return execute_query(
        """
        SELECT
            scs.position_text AS position,
            c.name AS constructor_name,
            scs.points,
            scs.championship_won
        FROM season_constructor_standing scs
        LEFT JOIN constructor c ON scs.constructor_id = c.id
        WHERE scs.year = ?
        ORDER BY scs.position_display_order
        """,
        (year,),
    )


def _build_points_progression(df: pd.DataFrame, entity_column: str) -> pd.DataFrame:
    """Consolida pontos por corrida em uma série acumulada por participante."""
    if df.empty:
        return df

    progression_df = df.copy()
    progression_df["race_round"] = pd.to_numeric(progression_df["race_round"], errors="coerce").fillna(0).astype(int)
    progression_df["race_points"] = pd.to_numeric(progression_df["race_points"], errors="coerce").fillna(0.0)

    race_labels = (
        progression_df[["race_round", "race_name"]]
        .drop_duplicates(subset=["race_round"])
        .sort_values("race_round")
        .set_index("race_round")
    )

    pivot_df = progression_df.pivot_table(
        index="race_round",
        columns=entity_column,
        values="race_points",
        aggfunc="sum",
        fill_value=0,
    ).sort_index()

    cumulative_df = pivot_df.cumsum().reset_index()
    cumulative_df = cumulative_df.melt(
        id_vars="race_round",
        var_name=entity_column,
        value_name="cumulative_points",
    )
    cumulative_df = cumulative_df.merge(race_labels, left_on="race_round", right_index=True, how="left")
    cumulative_df = cumulative_df.merge(
        progression_df[["race_round", entity_column, "race_points"]],
        on=["race_round", entity_column],
        how="left",
    )
    cumulative_df["race_label"] = cumulative_df["race_round"].apply(lambda round_number: f"Corrida {round_number}")

    return cumulative_df


def get_driver_points_progression(year: int) -> pd.DataFrame:
    """Retorna a evolução acumulada de pontos dos pilotos ao longo da temporada."""
    df = execute_query(
        """
        SELECT
            r.round AS race_round,
            r.official_name AS race_name,
            d.full_name AS driver_name,
            SUM(COALESCE(rr.points, 0)) AS race_points
        FROM race_result rr
        INNER JOIN race r ON rr.race_id = r.id
        INNER JOIN driver d ON rr.driver_id = d.id
        WHERE r.year = ?
        GROUP BY r.round, r.official_name, rr.driver_id, d.full_name
        HAVING SUM(COALESCE(rr.points, 0)) > 0
        ORDER BY r.round, d.full_name
        """,
        (year,),
    )
    return _build_points_progression(df, "driver_name")


def get_constructor_points_progression(year: int) -> pd.DataFrame:
    """Retorna a evolução acumulada de pontos das equipes ao longo da temporada."""
    df = execute_query(
        """
        SELECT
            r.round AS race_round,
            r.official_name AS race_name,
            c.name AS constructor_name,
            SUM(COALESCE(rr.points, 0)) AS race_points
        FROM race_result rr
        INNER JOIN race r ON rr.race_id = r.id
        INNER JOIN constructor c ON rr.constructor_id = c.id
        WHERE r.year = ?
        GROUP BY r.round, r.official_name, rr.constructor_id, c.name
        HAVING SUM(COALESCE(rr.points, 0)) > 0
        ORDER BY r.round, c.name
        """,
        (year,),
    )
    return _build_points_progression(df, "constructor_name")
