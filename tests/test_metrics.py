import pytest

from src import metrics as m


def test_headline_kpis(small_df):
    k = m.headline_kpis(small_df)
    assert k["orders"] == 6
    assert k["otif"] == pytest.approx(3 / 6)
    assert k["on_time"] == pytest.approx(5 / 6)
    assert k["in_full"] == pytest.approx(4 / 6)
    assert k["sc_cost"] == 1650 and k["order_value"] == 60000
    assert k["cost_pct"] == pytest.approx(0.0275)
    assert k["avg_delay_when_late"] == 5


def test_empty_selection_does_not_crash(small_df):
    k = m.headline_kpis(small_df.iloc[0:0])
    assert k["orders"] == 0 and k["otif"] == 0 and k["cost_pct"] == 0
    assert m.leakage_estimates(small_df.iloc[0:0])["excess_holding"] == 0


def test_kpis_by_region(small_df):
    r = m.kpis_by(small_df, "supplier_region").set_index("supplier_region")
    assert r.loc["North", "orders"] == 3 and r.loc["South", "orders"] == 3
    assert r.loc["North", "otif"] == pytest.approx(1 / 3)
    assert r.loc["South", "otif"] == pytest.approx(2 / 3)


def test_supplier_scorecard_flags_risk(small_df):
    sc = m.supplier_scorecard(small_df, otif_floor=0.5)
    assert list(sc["supplier_id"]) == ["S1", "S2"]          # worst OTIF first
    assert list(sc["at_risk"]) == [True, False]


def test_reliability_bands(small_df):
    b = m.reliability_bands(small_df).set_index("reliability_band")
    assert b.loc["Low (<=0.75)", "orders"] == 3
    assert b.loc["High (>0.85)", "orders"] == 3
    assert b.loc["Low (<=0.75)", "delay_rate"] == pytest.approx(1 / 3)


def test_rejection_breakdown(small_df):
    b = m.rejection_breakdown(small_df)
    assert len(b) == 1 and b.loc[0, "rejection_reason"] == "Expired" and b.loc[0, "cum_share"] == 1


def test_leakage_estimates(small_df):
    # overstock holding 150 vs normal avg (100+50+50+100+0)/5 = 60 -> extra 90 x 1 order
    assert m.excess_holding_cost(small_df) == pytest.approx(90)
    # Air: transport 800 on value 20000. Road rate = 400/40000 = 1% -> 800 - 200 = 600
    assert m.transport_premium(small_df) == pytest.approx(600)
    assert m.leakage_estimates(small_df)["rejected_value"] == 10000


def test_air_shift_scenario(small_df):
    s = m.air_shift_scenario(small_df, 0.5)
    assert s["saving"] == pytest.approx(300)
    assert s["saving_pct_of_cost"] == pytest.approx(300 / 1650)
    assert m.air_shift_scenario(small_df, 0)["saving"] == 0


def test_premium_is_zero_when_mode_missing(small_df):
    assert m.transport_premium(small_df[small_df["transport_mode"] == "Road"]) == 0


def test_monthly_trend_is_sorted(small_df):
    t = m.monthly_trend(small_df)
    assert list(t["orders"]) == [4, 2] and t["year_month"].is_monotonic_increasing
