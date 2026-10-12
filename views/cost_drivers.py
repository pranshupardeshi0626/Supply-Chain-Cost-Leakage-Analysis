"""Page 4: what drives cost and where service is weakest."""
import streamlit as st

from src import charts, metrics as m
from src.ui import banner, section


def render(df):
    banner("Cost Drivers", "Transport, inventory and rejections: the three places cost builds up")

    section("1. Transport mode")
    mode = m.kpis_by(df, "transport_mode").sort_values("cost_pct", ascending=False)
    left, right = st.columns(2)
    left.plotly_chart(charts.bar_by(mode, "transport_mode", "cost_pct", "Supply-chain cost % of order value",
                                    "Cost %"), use_container_width=True)
    right.plotly_chart(charts.bar_by(mode, "transport_mode", "on_time", "On-time rate by mode", "On-time",
                                     color="#1abc9c"), use_container_width=True)

    section("2. Inventory: overstock vs stockout")
    left, right = st.columns(2)
    inv = m.kpis_by(df.assign(stock_status=df["overstock_flag"].map({1: "Overstock", 0: "Normal"})),
                    "stock_status")
    inv["avg_holding_cost"] = inv["holding_cost"] / inv["orders"]
    left.plotly_chart(charts.bar_by(inv, "stock_status", "avg_holding_cost", "Average holding cost per order (INR)",
                                    "INR", as_pct=False, color="#f39c12"), use_container_width=True)
    region = m.kpis_by(df, "supplier_region")
    right.plotly_chart(charts.bar_by(region, "supplier_region", "overstock_rate", "Overstock rate by region",
                                     "Overstock"), use_container_width=True)

    section("3. Rejections")
    breakdown = m.rejection_breakdown(df)
    if breakdown.empty:
        st.info("No rejected orders in the current selection.")
    else:
        st.plotly_chart(charts.pareto(breakdown), use_container_width=True)

    section("4. Where is OTIF weakest? (region x category)")
    pivot = df.pivot_table(index="supplier_region", columns="product_category", values="otif", aggfunc="mean")
    st.plotly_chart(charts.heatmap(pivot, "OTIF by region and category"), use_container_width=True)

    section("5. What moves total cost?")
    st.plotly_chart(charts.correlation_bar(m.cost_correlations(df)), use_container_width=True)
    st.caption("Order value, quantity and price move cost the most. Forecast error has almost no link to cost. "
               "Correlation is not causation.")
