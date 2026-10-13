import pandas as pd

from src.config import REQUIRED_COLUMNS
from src.data_loader import clean, load_default, validate_schema


def test_validate_schema_reports_missing_columns(small_df):
    assert validate_schema(small_df) == []
    assert validate_schema(small_df.drop(columns=["otif", "order_id"])) == ["order_id", "otif"]


def test_clean_fills_reason_adds_helpers_and_dedupes(small_df):
    raw = small_df.drop(columns=["year", "year_month", "cost_pct_of_value"])
    raw = pd.concat([raw, raw.iloc[[0]]])          # duplicate order A
    out = clean(raw)
    assert len(out) == 6
    assert (out.loc[out["order_id"] == "A", "rejection_reason"] == "Not rejected").all()
    assert {"year", "year_month", "cost_pct_of_value"} <= set(out.columns)
    assert out.loc[out["order_id"] == "A", "cost_pct_of_value"].iloc[0] == 500 / 10000


def test_clean_drops_unparseable_dates(small_df):
    raw = small_df.drop(columns=["year", "year_month", "cost_pct_of_value"]).copy()
    raw["order_date"] = raw["order_date"].astype(str)
    raw.loc[0, "order_date"] = "not-a-date"
    assert len(clean(raw)) == 5


def test_real_dataset_matches_known_numbers():
    """Golden test: these are the numbers quoted in the README."""
    df = load_default()
    assert len(df) == 100_000 and set(REQUIRED_COLUMNS) <= set(df.columns)
    assert df["order_id"].is_unique
    assert round(df["otif"].mean(), 4) == 0.7736
