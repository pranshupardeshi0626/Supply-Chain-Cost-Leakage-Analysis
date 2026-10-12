"""Run SQL on the dataset using an in-memory SQLite database (no server needed)."""
import re
import sqlite3

import pandas as pd

from src.config import SQL_PATH


def build_connection(df: pd.DataFrame) -> sqlite3.Connection:
    """Copy the DataFrame into an in-memory SQLite table called `orders`."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    out = df.copy()
    for col in out.select_dtypes(include="datetime").columns:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    out.to_sql("orders", conn, index=False)
    conn.execute("PRAGMA query_only = ON")  # block INSERT/UPDATE/DELETE from here on
    return conn


def load_named_queries(path=SQL_PATH) -> dict:
    """Parse sql/queries.sql into {name: sql}."""
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"^-- name:\s*(.+)$", text, flags=re.MULTILINE)
    return {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts), 2)}


def is_read_only(sql: str) -> bool:
    """Only plain SELECT / WITH queries and a single statement are allowed."""
    cleaned = sql.strip().rstrip(";").strip()
    return bool(re.match(r"(?is)^(select|with)\b", cleaned)) and ";" not in cleaned


def run_query(conn: sqlite3.Connection, sql: str) -> pd.DataFrame:
    if not is_read_only(sql):
        raise ValueError("Only a single SELECT / WITH query is allowed.")
    return pd.read_sql_query(sql, conn)
