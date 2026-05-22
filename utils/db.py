import sqlite3
from pathlib import Path
from contextlib import contextmanager
import pandas as pd

# Caminho absoluto para o f1db.db na raiz do projeto
DB_PATH = Path(__file__).parent.parent / "f1db.db"

class DBError(RuntimeError):
    pass

@contextmanager
def get_connection():
    """Gerencia a conexão com o banco de dados SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        yield conn
    except sqlite3.Error as exc:
        raise DBError(f"Erro ao acessar o banco de dados: {exc}") from exc
    finally:
        try:
            conn.close()
        except Exception:
            pass

def execute_query(query: str, params: tuple | None = None) -> pd.DataFrame:
    """Executa uma query no banco de dados e retorna um DataFrame Pandas."""
    if params:
        params = tuple(int(x) if pd.api.types.is_integer(x) else x for x in params)
        
    with get_connection() as conn:
        return pd.read_sql(query, conn, params=params)

import pandas as pd

# ==========================================
# 1. QUERIES GERAIS E FILTROS
# ==========================================

def get_seasons() -> list[int]:
    """Retorna uma lista com todos os anos de temporadas disponíveis."""
    query = "SELECT year FROM season ORDER BY year DESC"
    df = execute_query(query)
    return df["year"].tolist()

def get_races_by_season(year: int) -> pd.DataFrame:
    """Busca todas as corridas de uma temporada específica."""
    query = """
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
    """
    return execute_query(query, (year,))


# ==========================================
# 2. QUERIES DE PILOTOS (DRIVERS)
# ==========================================

def get_all_drivers() -> pd.DataFrame:
    """Retorna o diretório completo de pilotos e suas estatísticas base."""
    query = """
    SELECT 
        d.id,
        d.full_name,
        d.permanent_number,
        d.date_of_birth,
        c.name AS nationality,
        d.total_race_wins,
        d.total_podiums,
        d.total_championship_wins,
        d.total_pole_positions
    FROM driver d
    LEFT JOIN country c ON d.nationality_country_id = c.id
    ORDER BY d.total_race_wins DESC, d.last_name ASC
    """
    return execute_query(query)


# ==========================================
# 3. QUERIES DE CONSTRUTORAS (CONSTRUCTORS)
# ==========================================

def get_all_constructors() -> pd.DataFrame:
    """Retorna o histórico de todas as construtoras e equipes."""
    query = """
    SELECT 
        con.id,
        con.name,
        con.full_name,
        c.name AS country,
        con.total_race_wins,
        con.total_podiums,
        con.total_championship_wins
    FROM constructor con
    LEFT JOIN country c ON con.country_id = c.id
    ORDER BY con.total_race_wins DESC, con.name ASC
    """
    return execute_query(query)


# ==========================================
# 4. QUERIES DE CIRCUITOS E MAPAS (CIRCUITS)
# ==========================================

def get_all_circuits() -> pd.DataFrame:
    """Retorna todos os circuitos com dados de geolocalização para os mapas."""
    query = """
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
    return execute_query(query)


# ==========================================
# 5. QUERIES DE RESULTADOS DE CORRIDA
# ==========================================

def get_race_results(race_id: int) -> pd.DataFrame:
    """Retorna o resultado final detalhado de uma corrida específica."""
    query = """
    SELECT
        rr.position_text AS position,
        rr.grid_position_text AS grid,
        d.full_name AS driver_name,
        c.name AS constructor_name,
        rr.laps,
        rr.time,
        rr.reason_retired AS status,
        rr.points,
        rr.fastest_lap
    FROM race_result rr
    LEFT JOIN driver d ON rr.driver_id = d.id
    LEFT JOIN constructor c ON rr.constructor_id = c.id
    WHERE rr.race_id = ?
    ORDER BY rr.position_display_order
    """
    return execute_query(query, (race_id,))


# ==========================================
# 6. QUERIES DE CLASSIFICAÇÃO (STANDINGS)
# ==========================================

def get_driver_standings(year: int) -> pd.DataFrame:
    """Retorna a classificação final do Mundial de Pilotos de um ano."""
    query = """
    SELECT
        sds.position_text AS position,
        d.full_name AS driver_name,
        sds.points,
        sds.championship_won
    FROM season_driver_standing sds
    LEFT JOIN driver d ON sds.driver_id = d.id
    WHERE sds.year = ?
    ORDER BY sds.position_display_order
    """
    return execute_query(query, (year,))

def get_constructor_standings(year: int) -> pd.DataFrame:
    """Retorna a classificação final do Mundial de Construtores de um ano."""
    query = """
    SELECT
        scs.position_text AS position,
        c.name AS constructor_name,
        scs.points,
        scs.championship_won
    FROM season_constructor_standing scs
    LEFT JOIN constructor c ON scs.constructor_id = c.id
    WHERE scs.year = ?
    ORDER BY scs.position_display_order
    """
    return execute_query(query, (year,))