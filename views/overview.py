"""Page 1: the headline numbers a manager wants in the first 10 seconds."""
import streamlit as st

from src import charts, metrics as m
from src.formatters import inr, pct
from src.ui import hero, kpi_row, section, show, table


def render(df):
    k = m.headline_kpis(df)
    span = f"{df['order_date'].min():%b %Y} to {df['order_date'].max():%b %Y}"
    hero("Exploratory analysis of an FMCG supply chain",
         f"{inr(k['sc_cost'])} of supply-chain cost on {inr(k['order_value'])} of orders, "
         f"and only <span>{pct(k['otif'], 0)}</span> arrive on time and in full",
         f"{k['orders']:,} purchase orders, {span}. The pages on the left walk through the data "
         "step by step: profile it, look at each variable, then at the relationships that explain the leakage.",
         [(f"{k['orders']:,}", "orders analysed"), (pct(k["cost_pct"], 2), "cost as % of order value"),
          (pct(k["rejection_rate"]), "orders rejected"), (pct(k["overstock_rate"] + k["stockout_rate"], 0),
                                                         "orders with a stock imbalance")])

    section("Cost", "What the supply chain spends")
    kpi_row([
        ("Orders", f"{k['orders']:,}", "purchase orders in selection", "teal"),
        ("Order value", inr(k["order_value"]), "total value of purchase orders", "teal"),
        ("Supply-chain cost", inr(k["sc_cost"]), "transport + holding", "coral"),
        ("Cost % of order value", pct(k["cost_pct"], 2), "supply-chain cost / order value", "coral"),
    ])

    section("Service and inventory", "How well orders are delivered and stocked")
    kpi_row([
        ("OTIF", pct(k["otif"]), "on time AND in full", "green" if k["otif"] >= 0.9 else "amber"),
        ("Stockout rate", pct(k["stockout_rate"]), "stock below reorder point", "amber"),
        ("Overstock rate", pct(k["overstock_rate"]), "stock far above reorder point", "amber"),
        ("Rejection rate", pct(k["rejection_rate"]), "orders rejected on receipt", "coral"),
    ])

    section("Trend and delivery mix")
    trend = m.monthly_trend(df)
    left, right = st.columns([2, 1])
    with left:
        show(charts.line_trend(trend, "otif", "Monthly OTIF", "OTIF"))
    with right:
        show(charts.delivery_breakdown(k))

    left, right = st.columns([2, 1])
    with left:
        show(charts.line_trend(trend, "cost_pct", "Monthly cost as % of order value", "Cost %", color="#E4572E"))
    with right:
        show(charts.cost_split(k))

    section("By product category", "Sorted by cost as % of order value")
    cat = m.kpis_by(df, "product_category").sort_values("cost_pct", ascending=False)
    view = cat[["product_category", "orders", "otif", "cost_pct", "stockout_rate", "overstock_rate",
                "rejection_rate"]]
    table(view, column_config={
        "product_category": "Category",
        "orders": st.column_config.NumberColumn("Orders", format="%d"),
        "otif": st.column_config.ProgressColumn("OTIF", format="percent", min_value=0, max_value=1),
        "cost_pct": st.column_config.NumberColumn("Cost % of value", format="percent"),
        "stockout_rate": st.column_config.NumberColumn("Stockout", format="percent"),
        "overstock_rate": st.column_config.NumberColumn("Overstock", format="percent"),
        "rejection_rate": st.column_config.NumberColumn("Rejection", format="percent"),
    })
