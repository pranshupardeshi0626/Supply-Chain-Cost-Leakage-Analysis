"""Page 4 (EDA step 3): relationships between two or more variables."""
import pandas as pd
import streamlit as st

from src import charts, profiling as p
from src.ui import note, page_header, section, show, table

SAMPLE_ROWS = 5000   # scatter plots of 100K points are slow; a random sample shows the same shape
DEFAULT_CORR = ["order_value_inr", "ordered_qty", "unit_price_inr", "total_sc_cost_inr", "transport_cost_inr",
                "holding_cost_inr", "supplier_delay_days", "actual_lead_days", "forecast_error_pct"]


def _strength(r):
    r = abs(r)
    return "very weak" if r < 0.1 else "weak" if r < 0.3 else "moderate" if r < 0.6 else "strong"


def render(df):
    page_header("Bivariate and Multivariate Analysis", "Step 3 of the EDA: which variables move together")
    num, cat = p.numeric_columns(df), p.categorical_columns(df)
    tab1, tab2, tab3, tab4 = st.tabs(["Number vs number", "Group comparison", "Correlation matrix", "Pivot heatmap"])

    with tab1:
        sample = df.sample(min(SAMPLE_ROWS, len(df)), random_state=1)
        a, b, c = st.columns(3)
        x = a.selectbox("X axis", num, index=num.index("order_value_inr") if "order_value_inr" in num else 0)
        y = b.selectbox("Y axis", num, index=num.index("total_sc_cost_inr") if "total_sc_cost_inr" in num else 1)
        colour = c.selectbox("Colour by", ["None"] + cat)
        show(charts.scatter(sample, x, y, None if colour == "None" else colour))
        r = df[x].corr(df[y])
        note(f"Correlation across all {len(df):,} rows: <b>{r:+.3f}</b> ({_strength(r)}). "
             f"The chart shows a random sample of {len(sample):,} rows. Correlation is not causation.")

    with tab2:
        a, b = st.columns(2)
        grp = a.selectbox("Group by", cat, index=cat.index("transport_mode") if "transport_mode" in cat else 0)
        val = b.selectbox("Compare this number", num,
                          index=num.index("total_sc_cost_inr") if "total_sc_cost_inr" in num else 0)
        show(charts.box(df, grp, val))
        stats = (df.groupby(grp)[val].agg(["count", "mean", "median", "std"]).round(2)
                   .sort_values("median", ascending=False).reset_index())
        table(stats.rename(columns={"count": "Orders", "mean": "Mean", "median": "Median", "std": "Std dev"}))

    with tab3:
        default = [c for c in DEFAULT_CORR if c in num]
        chosen = st.multiselect("Columns", num, default=default)
        if len(chosen) >= 2:
            corr = df[chosen].corr().round(2)
            left, right = st.columns([3, 2])
            with left:
                show(charts.heatmap(corr, "Correlation matrix", fmt=".2f", diverging=True, height=480))
            with right:
                st.markdown("**Strongest pairs**")
                table(p.top_correlations(df, chosen, 8).round(3))
        else:
            st.info("Pick at least two columns.")

    with tab4:
        a, b, c, d = st.columns(4)
        rows = a.selectbox("Rows", cat, index=cat.index("supplier_region") if "supplier_region" in cat else 0)
        cols = b.selectbox("Columns", cat, index=cat.index("product_category") if "product_category" in cat else 0)
        value = c.selectbox("Value", num + ["otif", "on_time", "in_full", "rejection_flag"],
                            index=len(num))
        agg = d.selectbox("Aggregate", ["mean", "median", "sum"])
        if rows == cols:
            st.info("Choose two different columns.")
        else:
            pivot = df.pivot_table(index=rows, columns=cols, values=value, aggfunc=agg)
            fmt = ".1%" if value in {"otif", "on_time", "in_full", "rejection_flag"} and agg == "mean" else ",.0f"
            show(charts.heatmap(pivot, f"{agg.title()} of {value} by {rows} and {cols}", fmt=fmt, height=420))
