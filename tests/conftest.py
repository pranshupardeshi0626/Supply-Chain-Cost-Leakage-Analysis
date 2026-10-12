import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import clean  # noqa: E402

BASE = dict(
    order_date="2023-01-10", product_category="Home Care", warehouse="WH-Delhi",
    ordered_qty=100, stock_on_hand=500, reorder_point=200, forecast_error_pct=0.1,
    unit_price_inr=100, actual_lead_days=10, stockout_flag=0, overstock_flag=0,
    supplier_delayed=0, supplier_delay_days=0, transport_cost_inr=100, holding_cost_inr=50,
    total_sc_cost_inr=150, order_value_inr=10000, rejection_flag=0, rejection_reason=None,
    on_time=1, in_full=1, otif=1, transport_mode="Road",
    supplier_id="S1", supplier_region="North", supplier_reliability_score=0.7,
)


@pytest.fixture
def small_df():
    """Six orders whose KPIs are easy to verify by hand (see tests/test_metrics.py)."""
    rows = [
        dict(order_id="A", transport_mode="Air", supplier_delayed=1, supplier_delay_days=5, on_time=0, otif=0,
             transport_cost_inr=400, holding_cost_inr=100, total_sc_cost_inr=500),
        dict(order_id="B", in_full=0, otif=0),
        dict(order_id="C", supplier_id="S2", supplier_region="South", supplier_reliability_score=0.9,
             overstock_flag=1, holding_cost_inr=150, total_sc_cost_inr=250, order_date="2023-02-10"),
        dict(order_id="D", supplier_id="S2", supplier_region="South", supplier_reliability_score=0.9,
             rejection_flag=1, rejection_reason="Expired", order_date="2023-02-11"),
        dict(order_id="E", supplier_id="S2", supplier_region="South", supplier_reliability_score=0.9,
             transport_mode="Air", in_full=0, otif=0, transport_cost_inr=400, holding_cost_inr=100,
             total_sc_cost_inr=500),
        dict(order_id="F", stockout_flag=1, holding_cost_inr=0, total_sc_cost_inr=100),
    ]
    return clean(pd.DataFrame([{**BASE, **r} for r in rows]))
