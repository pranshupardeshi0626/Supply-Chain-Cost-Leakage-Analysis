from src.filters import apply_filters
from src.formatters import compact, inr, pct, pp
from src.insights import generate_insights


def test_formatters():
    assert inr(598_292_687) == "₹59.8 Cr"
    assert inr(250_000) == "₹2.5 L"
    assert inr(950) == "₹950"
    assert inr(15_437_700_000) == "₹1,544 Cr"          # 1,000 Cr and above: no decimals
    assert compact(1_543_766.9) == "1.54M" and compact(12_345) == "12.3k" and compact(3.14159) == "3.14"
    assert pct(0.77355) == "77.4%"
    assert pp(-0.056) == "-5.6 pp"


def test_apply_filters(small_df):
    out = apply_filters(small_df, None, {"supplier_region": ["South"]})
    assert set(out["order_id"]) == {"C", "D", "E"}
    out = apply_filters(small_df, ("2023-02-01", "2023-02-28"), {"supplier_region": ["South", "North"]})
    assert set(out["order_id"]) == {"C", "D"}
    assert apply_filters(small_df, None, {"supplier_region": []}).empty


def test_insights_generate_with_evidence_and_caveats(small_df):
    insights = generate_insights(small_df)
    assert len(insights) >= 6
    assert all(i.title and i.finding and i.caveat for i in insights)
