"""Page 2 (EDA step 1): what is in the dataset and can we trust it?"""
import pandas as pd
import streamlit as st

from src import charts, profiling as p
from src.formatters import pct
from src.ui import kpi_row, note, page_header, section, show, table


def render(df):
    page_header("Data Profile", "Step 1 of the EDA: size, types, blanks, spread and outliers")
    st.caption("Profiles the full dataset (sidebar filters do not apply to this page).")

    num, cat = p.numeric_columns(df, include_flags=True), p.categorical_columns(df)
    missing = p.missing_summary(df)
    unexpected = missing[missing["Why"] == "Needs checking"]
    kpi_row([
        ("Rows", f"{len(df):,}", "one row per purchase order", "teal"),
        ("Columns", f"{df.shape[1]}", f"{len(num)} numeric, {len(cat)} text, incl. 3 derived", "teal"),
        ("Duplicate order IDs", f"{int(df['order_id'].duplicated().sum())}", "after cleaning on load", "green"),
        ("Unexpected blanks", f"{len(unexpected)}", "columns needing attention",
         "green" if unexpected.empty else "coral"),
    ])

    tab_schema, tab_missing, tab_stats, tab_out, tab_raw = st.tabs(
        ["Columns", "Missing values", "Summary statistics", "Outliers", "Raw rows"])

    with tab_schema:
        table(p.schema_table(df), height=520)

    with tab_missing:
        if missing.empty:
            note("No blank cells in this dataset.")
        else:
            left, right = st.columns([3, 2])
            with left:
                show(charts.missing_bar(missing))
            with right:
                table(missing.assign(**{"Missing %": missing["Missing %"].map(pct)}))
            note("Accepted orders have no rejection reason, so that blank is expected. "
                 "It is filled with 'Not rejected' on load and no other column has blanks.")

    with tab_stats:
        cols = st.multiselect("Columns", num, default=num[:10])
        if cols:
            stats = p.describe_numeric(df, cols)
            table(stats.round(3), column_config={"count": st.column_config.NumberColumn(format="%d")})
            note("Skew above +1 means a long right tail (a few very large orders). "
                 "Kurtosis above 3 means heavier tails than a normal curve.")
        else:
            st.info("Pick at least one column.")

    with tab_out:
        out_cols = [c for c in p.numeric_columns(df) if c in df.columns]
        out = p.outlier_table(df, out_cols)
        left, right = st.columns([3, 2])
        with left:
            show(charts.outlier_bar(out))
        with right:
            table(out.rename(columns={"low_fence": "Lower fence", "high_fence": "Upper fence",
                                      "outliers": "Outliers", "outlier_pct": "Share"})
                  .round(2), column_config={"Share": st.column_config.NumberColumn(format="percent")})
        note("Outliers here are values beyond 1.5 x IQR. Large order values and costs are real "
             "big purchases, not errors, so they are kept in every chart.", warn=True)

    with tab_raw:
        n = st.slider("Rows to preview", 5, 100, 20, step=5)
        sample = st.radio("Which rows", ["First rows", "Random sample"], horizontal=True)
        rows = df.head(n) if sample == "First rows" else df.sample(n, random_state=7)
        st.dataframe(rows, hide_index=True, width="stretch")
        st.download_button("Download cleaned dataset (CSV)", df.to_csv(index=False).encode(),
                           "cleaned_orders.csv", "text/csv")
