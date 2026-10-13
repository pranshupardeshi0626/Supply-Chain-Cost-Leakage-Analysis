import pandas as pd
import pytest

from src import profiling as p


def test_numeric_columns_skip_ids_and_flags(small_df):
    cols = p.numeric_columns(small_df)
    assert "order_value_inr" in cols
    assert not {"otif", "stockout_flag", "year"} & set(cols)
    assert "otif" in p.numeric_columns(small_df, include_flags=True)


def test_categorical_columns_have_few_levels(small_df):
    cats = p.categorical_columns(small_df)
    assert "supplier_region" in cats and "order_id" not in cats


def test_missing_summary_treats_not_rejected_as_expected(small_df):
    out = p.missing_summary(small_df)
    row = out[out["Column"] == "rejection_reason"].iloc[0]
    assert row["Missing"] == 5 and row["Missing %"] == pytest.approx(5 / 6)
    assert row["Why"].startswith("Expected")
    assert (out["Why"] != "Needs checking").all()


def test_iqr_outliers_flags_extreme_value():
    s = pd.Series([10, 11, 12, 11, 10, 12, 11, 500])
    res = p.iqr_outliers(s)
    assert res["outliers"] == 1 and res["outlier_pct"] == pytest.approx(1 / 8)


def test_top_correlations_lists_each_pair_once(small_df):
    cols = ["transport_cost_inr", "holding_cost_inr", "total_sc_cost_inr"]
    out = p.top_correlations(small_df, cols, n=10)
    assert len(out) == 3
    assert out["Correlation"].abs().is_monotonic_decreasing


def test_schema_and_category_summary(small_df):
    schema = p.schema_table(small_df)
    assert set(schema["Type"]) <= {"Number", "Text", "Date"} and len(schema) == small_df.shape[1]
    cs = p.category_summary(small_df, "supplier_region")
    assert cs["Orders"].sum() == 6 and cs["Share"].sum() == pytest.approx(1)
