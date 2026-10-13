"""Page 3 (EDA step 2): one variable at a time."""
import streamlit as st

from src import charts, profiling as p
from src.formatters import compact, pct
from src.ui import kpi_row, note, page_header, section, show, table


def _skew_note(skew):
    if abs(skew) < 0.5:
        return "roughly symmetric"
    return ("right-skewed (a few very large values)" if skew > 0 else "left-skewed (a few very small values)")


def render(df):
    page_header("Univariate Analysis", "Step 2 of the EDA: the shape of each variable on its own")
    num, cat = p.numeric_columns(df), p.categorical_columns(df)

    section("Numeric variables", "Distribution, centre, spread and outliers")
    default = num.index("order_value_inr") if "order_value_inr" in num else 0
    col = st.selectbox("Choose a numeric column", num, index=default)
    s = df[col].dropna()
    out = p.iqr_outliers(s)
    kpi_row([
        ("Mean", compact(s.mean()), "", "teal"),
        ("Median", compact(s.median()), "", "teal"),
        ("Std deviation", compact(s.std()), f"range {compact(s.min())} to {compact(s.max())}", "amber"),
        ("Skew", f"{s.skew():+.2f}", _skew_note(s.skew()), "amber"),
        ("Outliers (IQR)", pct(out["outlier_pct"]), f"{out['outliers']:,} values", "coral"),
    ])
    show(charts.histogram(df, col))
    if s.mean() > s.median() * 1.1:
        note("Mean is well above the median: a small number of large values pull the average up. "
             "Use the median when describing a typical order.")

    section("Categorical variables", "How orders are spread across groups")
    ccol = st.selectbox("Choose a categorical column", cat,
                        index=cat.index("product_category") if "product_category" in cat else 0)
    summary = p.category_summary(df, ccol)
    left, right = st.columns([3, 2])
    with left:
        show(charts.category_counts(summary, ccol))
    with right:
        table(summary, column_config={"Orders": st.column_config.NumberColumn(format="%d"),
                                      "Share": st.column_config.ProgressColumn(
                                          "Share", format="percent", min_value=0,
                                          max_value=float(summary["Share"].max()))})
