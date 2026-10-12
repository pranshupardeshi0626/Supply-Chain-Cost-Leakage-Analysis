"""Page 1: the headline numbers a manager wants in the first 10 seconds."""
import streamlit as st

from src import charts, metrics as m
from src.formatters import inr, pct
from src.ui import banner, kpi_row, section


def render(df):
    banner("Supply Chain Cost Leakage Dashboard",
           "Where a 100K-order FMCG supply chain loses money and service quality")
    k = m.headline_kpis(df)

    section("Cost")
    kpi_row([
        ("Orders", f"{k['orders']:,}", None),
        ("Order value", inr(k["order_value"]), "Total value of purchase orders"),
        ("Supply-chain cost", inr(k["sc_cost"]), "Transport + holding cost"),
        ("Cost % of order value", pct(k["cost_pct"], 2), "Supply-chain cost / order value"),
    ])

    section("Service & inventory")
    kpi_row([
        ("OTIF", pct(k["otif"]), "Orders delivered On Time AND In Full"),
        ("On-time", pct(k["on_time"]), None),
        ("Stockout rate", pct(k["stockout_rate"]), "Orders where stock fell below the reorder point"),
        ("Overstock rate", pct(k["overstock_rate"]), "Orders where stock is far above the reorder point"),
        ("Rejection rate", pct(k["rejection_rate"]), None),
    ])

    left, right = st.columns(2)
    left.plotly_chart(charts.otif_breakdown(k), use_container_width=True)
    right.plotly_chart(charts.cost_split(k), use_container_width=True)

    section("Trend over time")
    trend = m.monthly_trend(df)
    left, right = st.columns(2)
    left.plotly_chart(charts.line_trend(trend, "otif", "Monthly OTIF", "OTIF"), use_container_width=True)
    right.plotly_chart(charts.line_trend(trend, "cost_pct", "Monthly cost % of order value",
                                         "Cost %"), use_container_width=True)

    section("By product category")
    cat = m.kpis_by(df, "product_category").sort_values("cost_pct", ascending=False)
    table = cat[["product_category", "orders", "otif", "cost_pct", "stockout_rate",
                 "overstock_rate", "rejection_rate"]].copy()
    for col in ["otif", "cost_pct", "stockout_rate", "overstock_rate", "rejection_rate"]:
        table[col] = (table[col] * 100).round(2)
    st.dataframe(table.rename(columns={
        "product_category": "Category", "orders": "Orders", "otif": "OTIF %", "cost_pct": "Cost % of value",
        "stockout_rate": "Stockout %", "overstock_rate": "Overstock %", "rejection_rate": "Rejection %"}),
        hide_index=True, use_container_width=True)
