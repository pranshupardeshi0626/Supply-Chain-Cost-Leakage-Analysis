import pytest

from src.filters import apply_filters
from src.formatters import inr, pct, pp
from src.insights import generate_insights
from src.sql_layer import build_connection, is_read_only, load_named_queries, run_query


def test_formatters():
    assert inr(598_292_687) == "₹59.8 Cr"
    assert inr(250_000) == "₹2.5 L"
    assert inr(950) == "₹950"
    assert pct(0.77355) == "77.4%"
    assert pp(-0.056) == "-5.6 pp"


def test_apply_filters(small_df):
    out = apply_filters(small_df, None, {"supplier_region": ["South"]})
    assert set(out["order_id"]) == {"C", "D", "E"}
    out = apply_filters(small_df, ("2023-02-01", "2023-02-28"), {"supplier_region": ["South", "North"]})
    assert set(out["order_id"]) == {"C", "D"}
    assert apply_filters(small_df, None, {"supplier_region": []}).empty


def test_sql_guard():
    assert is_read_only("SELECT 1;") and is_read_only("with a as (select 1) select * from a")
    for bad in ["DROP TABLE orders", "DELETE FROM orders", "select 1; drop table orders", "PRAGMA table_info(orders)"]:
        assert not is_read_only(bad)


def test_every_named_query_runs(small_df):
    conn = build_connection(small_df)
    queries = load_named_queries()
    assert len(queries) >= 7
    for name, sql in queries.items():
        assert not run_query(conn, sql).empty, name
    with pytest.raises(ValueError):
        run_query(conn, "DELETE FROM orders")


def test_sql_matches_pandas(small_df):
    conn = build_connection(small_df)
    sql_otif = run_query(conn, "SELECT AVG(otif) AS v FROM orders")["v"][0]
    assert sql_otif == pytest.approx(small_df["otif"].mean())


def test_insights_generate_with_evidence_and_caveats(small_df):
    insights = generate_insights(small_df)
    assert len(insights) >= 6
    assert all(i.title and i.finding and i.caveat for i in insights)
