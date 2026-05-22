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