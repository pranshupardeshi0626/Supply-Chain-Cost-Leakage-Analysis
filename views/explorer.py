"""Page 5: free-form EDA (univariate / bivariate / multivariate) on any column."""
import pandas as pd
import streamlit as st

from src import charts
from src.ui import banner

SAMPLE_ROWS = 5000   # scatter plots of 100K points are slow; a random sample shows the same shape


def _column_lists(df):
    num = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and c != "year"]
    cat = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])
           and not pd.api.types.is_datetime64_any_dtype(df[c]) and 1 < df[c].nunique() <= 30]
    return num, cat


def render(df):
    banner("Data Explorer", "Univariate, bivariate and multivariate analysis on any column")
    num, cat = _column_lists(df)
    tab1, tab2, tab3 = st.tabs(["Univariate", "Bivariate", "Multivariate"])

    with tab1:
        col = st.selectbox("Numeric column", num, key="uni")
        st.plotly_chart(charts.histogram(df, col), use_container_width=True)
        s = df[col]
        st.dataframe(pd.DataFrame({"mean": [s.mean()], "median": [s.median()], "std": [s.std()],
                                   "min": [s.min()], "max": [s.max()], "skew": [s.skew()],
                                   "kurtosis": [s.kurt()]}).round(3), hide_index=True)

    with tab2:
        sample = df.sample(min(SAMPLE_ROWS, len(df)), random_state=1)
        a, b = st.columns(2)
        x, y = a.selectbox("X (numeric)", num, index=0, key="bx"), b.selectbox("Y (numeric)", num, index=1, key="by")
        st.plotly_chart(charts.scatter(sample, x, y), use_container_width=True)
        st.caption(f"Scatter uses a random sample of {len(sample):,} rows. Correlation (all rows): "
                   f"{df[x].corr(df[y]):.3f}")
        a, b = st.columns(2)
        grp, val = a.selectbox("Group by", cat, key="gg"), b.selectbox("Numeric value", num, key="gv")
        st.plotly_chart(charts.box(df, grp, val), use_container_width=True)

    with tab3:
        chosen = st.multiselect("Columns for correlation heatmap", num,
                                default=[c for c in ["order_value_inr", "total_sc_cost_inr", "transport_cost_inr",
                                                     "holding_cost_inr", "supplier_delay_days", "otif"] if c in num])
        if len(chosen) >= 2:
            st.plotly_chart(charts.heatmap(df[chosen].corr().round(2), "Correlation matrix", fmt=".2f"),
                            use_container_width=True)
        else:
            st.info("Pick at least two columns.")
        a, b, c = st.columns(3)
        rows, cols_ = a.selectbox("Rows", cat, key="pr"), b.selectbox("Columns", cat, index=min(1, len(cat) - 1), key="pc")
        value = c.selectbox("Average of", num, key="pv")
        st.dataframe(df.pivot_table(index=rows, columns=cols_, values=value, aggfunc="mean").round(3))
