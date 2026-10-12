"""Single place for constants, so nothing is a "magic number" elsewhere."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "fmcg_supply_chain_100k.csv"
SQL_PATH = ROOT / "sql" / "queries.sql"

# Columns the dashboard needs. An uploaded file must contain all of them.
REQUIRED_COLUMNS = [
    "order_id", "order_date", "product_category", "supplier_id", "supplier_region",
    "supplier_reliability_score", "warehouse", "transport_mode",
    "ordered_qty", "stock_on_hand", "forecast_error_pct",
    "stockout_flag", "overstock_flag", "supplier_delayed", "supplier_delay_days",
    "transport_cost_inr", "holding_cost_inr", "total_sc_cost_inr", "order_value_inr",
    "rejection_flag", "rejection_reason", "on_time", "in_full", "otif",
]

CRORE = 1e7                      # 1 Crore = 10,000,000 INR
DEFAULT_SUPPLIER_OTIF_FLOOR = 0.70   # suppliers below this are flagged "at risk"
BASELINE_MODE = "Road"           # cheapest / most-used mode, used as the cost baseline
PREMIUM_MODE = "Air"             # mode we test for savings

# Reliability-score bands used in the supplier analysis
RELIABILITY_BINS = [0, 0.75, 0.85, 1.0]
RELIABILITY_LABELS = ["Low (<=0.75)", "Medium (0.75-0.85)", "High (>0.85)"]

# Colours
BLUE, NAVY, TEAL, RED, AMBER = "#2e86de", "#1b2a4a", "#1abc9c", "#e74c3c", "#f39c12"
