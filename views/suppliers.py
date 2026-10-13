"""Page 6: supplier scorecard."""
import streamlit as st

from src import charts, metrics as m
from src.config import CORAL, DEFAULT_SUPPLIER_OTIF_FLOOR
from src.formatters import pct
from src.ui import kpi_row, page_header, section, show, table


def render(df):
    page_header("Supplier Analysis", "Who delivers, who does not, and how much volume depends on them")
    floor = st.slider("Flag suppliers with OTIF below", 50, 95, int(DEFAULT_SUPPLIER_OTIF_FLOOR * 100),
                      format="%d%%") / 100
    sc = m.supplier_scorecard(df, floor)
    risky = sc[sc["at_risk"]]
    risky_orders = risky["orders"].sum() / sc["orders"].sum()

    kpi_row([
        ("Suppliers", f"{len(sc)}", "in the current selection", "teal"),
        ("At-risk suppliers", f"{len(risky)}", f"OTIF below {pct(floor, 0)}", "coral", "bad" if len(risky) else ""),
        ("Orders from at-risk suppliers", pct(risky_orders), "share of all orders", "amber"),
        ("OTIF range", f"{pct(sc['otif'].min(), 0)} to {pct(sc['otif'].max(), 0)}", "worst to best supplier", "teal"),
    ])

    left, right = st.columns(2)
    with left:
        show(charts.supplier_scatter(sc))
    with right:
        bands = m.reliability_bands(df)
        show(charts.bar_by(bands, "reliability_band", "delay_rate", "Delay rate by reliability band",
                           "Orders delayed", color=CORAL))

    section("Scorecard", "Worst OTIF first")
    view = sc[["supplier_id", "region", "reliability", "orders", "otif", "delay_rate", "rejection_rate",
               "cost_pct", "at_risk"]]
    table(view, height=460, column_config={
        "supplier_id": "Supplier", "region": "Region",
        "reliability": st.column_config.NumberColumn("Reliability score", format="%.2f"),
        "orders": st.column_config.NumberColumn("Orders", format="%d"),
        "otif": st.column_config.ProgressColumn("OTIF", format="percent", min_value=0, max_value=1),
        "delay_rate": st.column_config.NumberColumn("Delayed", format="percent"),
        "rejection_rate": st.column_config.NumberColumn("Rejected", format="percent"),
        "cost_pct": st.column_config.NumberColumn("Cost % of value", format="percent"),
        "at_risk": st.column_config.CheckboxColumn("At risk")})
    st.download_button("Download scorecard (CSV)", sc.to_csv(index=False).encode(),
                       "supplier_scorecard.csv", "text/csv")
