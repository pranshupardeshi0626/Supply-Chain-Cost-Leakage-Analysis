"""Page 5: where cost builds up and which variables move it."""
import streamlit as st

from src import charts, metrics as m
from src.config import AMBER, AQUA, CORAL, TEAL
from src.ui import note, page_header, section, show


def render(df):
    page_header("Cost Drivers", "Transport, inventory and rejections: the three places cost builds up")

    section("Transport mode", "Which mode costs the most, and does it buy speed?")
    mode = m.kpis_by(df, "transport_mode").sort_values("cost_pct", ascending=False)
    left, right = st.columns(2)
    with left:
        show(charts.bar_by(mode, "transport_mode", "cost_pct", "Supply-chain cost as % of order value", "Cost %",
                           highlight="max"))
    with right:
        show(charts.bar_by(mode, "transport_mode", "on_time", "On-time rate by mode", "On-time", color=AQUA))

    section("Category and season", "Is cost concentrated anywhere?")
    left, right = st.columns(2)
    with left:
        show(charts.stacked_cost(m.kpis_by(df, "product_category"), "product_category",
                                 "Transport and holding cost by category"))
    with right:
        if "season" in df.columns:
            season = m.kpis_by(df, "season")
            show(charts.grouped_bars(season, "season", ["otif", "on_time"], "OTIF and on-time by season",
                                     ["OTIF", "On-time"], [TEAL, AQUA]))

    section("Inventory", "Overstock versus stockout")
    inv = m.kpis_by(df.assign(stock_status=df["overstock_flag"].map({1: "Overstock", 0: "Normal"})), "stock_status")
    inv["avg_holding_cost"] = inv["holding_cost"] / inv["orders"]
    region = m.kpis_by(df, "supplier_region")
    left, right = st.columns(2)
    with left:
        show(charts.bar_by(inv, "stock_status", "avg_holding_cost", "Average holding cost per order (INR)",
                           "INR", as_pct=False, color=AMBER, highlight="max"))
    with right:
        show(charts.grouped_bars(region, "supplier_region", ["overstock_rate", "stockout_rate"],
                                 "Overstock and stockout rate by region", ["Overstock", "Stockout"],
                                 [AMBER, CORAL]))

    section("Rejections", "Why orders are turned away")
    breakdown = m.rejection_breakdown(df)
    if breakdown.empty:
        st.info("No rejected orders in the current selection.")
    else:
        show(charts.pareto(breakdown))

    section("Where is OTIF weakest?", "Supplier region by product category")
    pivot = df.pivot_table(index="supplier_region", columns="product_category", values="otif", aggfunc="mean")
    show(charts.heatmap(pivot, "OTIF by region and category", height=380))

    section("What moves total cost?")
    show(charts.correlation_bar(m.cost_correlations(df)))
    note("Order value, quantity and price move cost the most. Forecast error has almost no link to cost. "
         "Correlation is not causation.")
