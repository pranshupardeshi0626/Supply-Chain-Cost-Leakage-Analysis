"""Load -> validate -> clean. No Streamlit here, so it is easy to unit-test."""
import pandas as pd

from src.config import DATA_PATH, NOT_REJECTED, REQUIRED_COLUMNS


def validate_schema(df: pd.DataFrame) -> list:
    """Return the list of required columns that are missing (empty list = OK)."""
    return [c for c in REQUIRED_COLUMNS if c not in df.columns]


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Parse dates, fill expected blanks and add the helper columns the app uses."""
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df = df.dropna(subset=["order_date"])
    df = df.drop_duplicates(subset="order_id")

    # rejection_reason is blank for accepted orders: that is expected, not missing data
    df["rejection_reason"] = df["rejection_reason"].fillna(NOT_REJECTED)

    df["year"] = df["order_date"].dt.year
    df["year_month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    df["cost_pct_of_value"] = df["total_sc_cost_inr"] / df["order_value_inr"]
    return df.reset_index(drop=True)


def load_csv(source) -> pd.DataFrame:
    """Read a CSV path or file-like object and return the cleaned frame."""
    return clean(pd.read_csv(source))


def load_excel(source) -> pd.DataFrame:
    return clean(pd.read_excel(source))


def load_default() -> pd.DataFrame:
    return load_csv(DATA_PATH)
