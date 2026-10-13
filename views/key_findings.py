"""Page 7: the story. Findings are generated from data, then sized in rupees."""
import streamlit as st

from src import metrics as m
from src.formatters import inr, pct
from src.insights import generate_insights
from src.ui import insight_card, kpi_row, note, page_header, section


def render(df):
    page_header("Key Findings and Recommendations", "What the EDA shows is going wrong, how big it is, and what to do")
    st.caption("Computed on the full dataset (sidebar filters do not apply to this page).")

    leak = m.leakage_estimates(df)
    section("Where the money leaks")
    kpi_row([
        ("Excess holding cost", inr(leak["excess_holding"]),
         f"{pct(leak['excess_holding'] / leak['total_cost'])} of total cost, from overstock", "amber"),
        ("Air freight premium", inr(leak["air_premium"]),
         f"{pct(leak['air_premium'] / leak['total_cost'])} of total cost, above Road-equivalent", "coral"),
        ("Rejected order value", inr(leak["rejected_value"]), "value affected, not realised loss", "teal"),
    ])
    note("Excess holding and Air premium are estimates with stated assumptions. They overlap little "
         "but should not be treated as exact savings. The dataset has no refund or write-off column, "
         "so rejected value is exposure, not loss.", warn=True)

    insights = generate_insights(df)
    section(f"{len(insights)} findings")
    for n, insight in enumerate(insights, start=1):
        insight_card(insight, n)

    section("What-if: shift Air shipments to Road")
    share = st.slider("Share of Air shipments moved to Road", 0, 100, 25, step=5, format="%d%%") / 100
    result = m.air_shift_scenario(df, share)
    kpi_row([
        ("Estimated saving", inr(result["saving"]), "per the Air premium estimate", "green", "good"),
        ("As % of total supply-chain cost", pct(result["saving_pct_of_cost"]), "", "green", "good"),
    ])
    st.caption("Assumes moved shipments cost what Road costs per rupee of order value and service level "
               "is unchanged. Air is only slightly faster in this data, but urgent orders may need it.")
