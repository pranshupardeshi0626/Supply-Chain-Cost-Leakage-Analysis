"""Page 3: supplier scorecard."""
import streamlit as st

from src import charts, metrics as m
from src.config import DEFAULT_SUPPLIER_OTIF_FLOOR
from src.formatters import pct
from src.ui import banner, kpi_row, section


def render(df):
    banner("Supplier Scorecard", "Who delivers, who doesn't, and how much volume depends on them")
    floor = st.slider("Flag suppliers with OTIF below", 50, 95,
                      int(DEFAULT_SUPPLIER_OTIF_FLOOR * 100), format="%d%%") / 100
    sc = m.supplier_scorecard(df, floor)
    risky = sc[sc["at_risk"]]
    risky_orders = risky["orders"].sum() / sc["orders"].sum()

    kpi_row([
        ("Suppliers", f"{len(sc)}", None),
        ("At-risk suppliers", f"{len(risky)}", f"OTIF below {pct(floor, 0)}"),
        ("Share of orders from at-risk suppliers", pct(risky_orders), None),
    ])

    left, right = st.columns(2)
    left.plotly_chart(charts.supplier_scatter(sc), use_container_width=True)
    bands = m.reliability_bands(df)
    right.plotly_chart(charts.bar_by(bands, "reliability_band", "delay_rate",
                                     "Delay rate by reliability band", "Orders delayed", color="#e74c3c"),
                       use_container_width=True)

    section("Scorecard (worst OTIF first)")
    table = sc[["supplier_id", "region", "reliability", "orders", "otif", "delay_rate",
                "rejection_rate", "cost_pct", "at_risk"]].copy()
    for col in ["otif", "delay_rate", "rejection_rate"]:
        table[col] = (table[col] * 100).round(1)
    table["cost_pct"] = (table["cost_pct"] * 100).round(2)
    st.dataframe(table.rename(columns={
        "supplier_id": "Supplier", "region": "Region", "reliability": "Reliability score", "orders": "Orders",
        "otif": "OTIF %", "delay_rate": "Delayed %", "rejection_rate": "Rejected %",
        "cost_pct": "Cost % of value", "at_risk": "At risk"}), hide_index=True, use_container_width=True)
    st.download_button("Download scorecard (CSV)", sc.to_csv(index=False).encode(),
                       "supplier_scorecard.csv", "text/csv")
