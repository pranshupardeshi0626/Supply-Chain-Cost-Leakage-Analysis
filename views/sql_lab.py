"""Page 6: the same analysis in SQL (in-memory SQLite), plus a box for your own query."""
import streamlit as st

from src.sql_layer import build_connection, load_named_queries, run_query
from src.ui import banner, section


@st.cache_resource(show_spinner="Building in-memory SQL database...")
def _connection(_df, key):
    return build_connection(_df)


def render(df):
    banner("SQL Lab", "Business questions answered with SQL (SQLite, table name: orders)")
    st.caption("Runs on the full dataset. Only SELECT / WITH queries are allowed.")
    conn = _connection(df, f"{len(df)}-{df['order_id'].iloc[0]}-{df['order_id'].iloc[-1]}")
    queries = load_named_queries()

    section("Ready-made queries")
    name = st.selectbox("Choose a query", list(queries))
    st.code(queries[name], language="sql")
    st.dataframe(run_query(conn, queries[name]), hide_index=True, use_container_width=True)

    section("Write your own")
    sql = st.text_area("SQL", "SELECT product_category, COUNT(*) AS orders\nFROM orders\nGROUP BY product_category;",
                       height=130)
    if st.button("Run query"):
        try:
            st.dataframe(run_query(conn, sql), hide_index=True, use_container_width=True)
        except Exception as exc:  # show SQL mistakes to the user instead of crashing the app
            st.error(f"Query failed: {exc}")
