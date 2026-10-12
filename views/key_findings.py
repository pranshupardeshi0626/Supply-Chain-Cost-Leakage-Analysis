"""Page 2: the story. Findings are generated from data, then sized in rupees."""
import streamlit as st

from src import metrics as m
from src.formatters import inr, pct
from src.insights import generate_insights
from src.ui import banner, insight_card, kpi_row, section


def render(df):
    banner("Key Findings & Recommendations", "What is going wrong, how big it is, and what to do")
    st.caption("Computed on the full dataset (sidebar filters do not apply to this page).")

    leak = m.leakage_estimates(df)
    section("Where the money leaks")
    kpi_row([
        ("Excess holding cost (overstock)", inr(leak["excess_holding"]),
         f"= {pct(leak['excess_holding'] / leak['total_cost'])} of total supply-chain cost"),
        ("Air freight premium", inr(leak["air_premium"]),
         f"= {pct(leak['air_premium'] / leak['total_cost'])} of total cost. Air cost above what Road would cost"),
        ("Rejected order value", inr(leak["rejected_value"]),
         "Value of orders affected. NOT realised loss: the dataset has no refund / write-off column"),
    ])
    st.caption("Excess holding and Air premium are cost estimates with stated assumptions; "
               "they overlap little but should not be treated as exact savings.")

    insights = generate_insights(df)
    section(f"{len(insights)} findings")
    for insight in insights:
        insight_card(insight)

    section("What-if: shift Air shipments to Road")
    share = st.slider("Share of Air shipments moved to Road", 0, 100, 25, step=5, format="%d%%") / 100
    result = m.air_shift_scenario(df, share)
    kpi_row([
        ("Estimated saving", inr(result["saving"]), None),
        ("As % of total supply-chain cost", pct(result["saving_pct_of_cost"]), None),
    ])
    st.caption("Assumes moved shipments cost what Road costs per rupee of order value and service level "
               "is unchanged. Air is only slightly faster in this data, but urgent orders may need it.")
