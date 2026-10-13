"""Sidebar filters. `apply_filters` is pure (testable); `sidebar_filters` is the UI."""
import pandas as pd
import streamlit as st

FILTER_COLUMNS = {
    "Supplier region": "supplier_region",
    "Product category": "product_category",
    "Transport mode": "transport_mode",
    "Warehouse": "warehouse",
}


def apply_filters(df, date_range, selections: dict) -> pd.DataFrame:
    """selections maps column name -> list of allowed values."""
    mask = pd.Series(True, index=df.index)
    if date_range and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        mask &= df["order_date"].between(start, end)
    for col, allowed in selections.items():
        mask &= df[col].isin(allowed)
    return df[mask]


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.markdown('<div class="side-label">Filters</div>', unsafe_allow_html=True)
    min_d, max_d = df["order_date"].min().date(), df["order_date"].max().date()
    date_range = st.date_input("Order date", (min_d, max_d), min_value=min_d, max_value=max_d)

    selections = {}
    for label, col in FILTER_COLUMNS.items():
        options = sorted(df[col].dropna().unique())
        selections[col] = st.multiselect(label, options, default=options)

    # while the user is mid-selection of a date range, date_input returns 1 date: ignore it
    return apply_filters(df, date_range if len(date_range) == 2 else None, selections)
