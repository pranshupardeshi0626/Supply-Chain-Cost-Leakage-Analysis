"""Single place for constants, so nothing is a "magic number" elsewhere."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "fmcg_supply_chain_100k.csv"

# Columns the dashboard needs. An uploaded file must contain all of them.
REQUIRED_COLUMNS = [
    "order_id", "order_date", "product_category", "supplier_id", "supplier_region",
    "supplier_reliability_score", "warehouse", "transport_mode",
    "ordered_qty", "stock_on_hand", "forecast_error_pct",
    "stockout_flag", "overstock_flag", "supplier_delayed", "supplier_delay_days",
    "transport_cost_inr", "holding_cost_inr", "total_sc_cost_inr", "order_value_inr",
    "rejection_flag", "rejection_reason", "on_time", "in_full", "otif",
]

CRORE = 1e7                          # 1 Crore = 10,000,000 INR
DEFAULT_SUPPLIER_OTIF_FLOOR = 0.70   # suppliers below this are flagged "at risk"
BASELINE_MODE = "Road"               # cheapest / most-used mode, used as the cost baseline
PREMIUM_MODE = "Air"                 # mode we test for savings

# Reliability-score bands used in the supplier analysis
RELIABILITY_BINS = [0, 0.75, 0.85, 1.0]
RELIABILITY_LABELS = ["Low (<=0.75)", "Medium (0.75-0.85)", "High (>0.85)"]

# Placeholder used for blank rejection_reason (accepted orders have no reason)
NOT_REJECTED = "Not rejected"

# Columns that are identifiers or flags: skipped from "numeric distribution" pickers
ID_LIKE = {"order_id", "sku_id", "supplier_id", "year", "month", "quarter"}
FLAG_COLUMNS = ["stockout_flag", "overstock_flag", "supplier_delayed", "rejection_flag",
                "on_time", "in_full", "otif"]

# Colour palette (one source of truth for CSS, Plotly and Python code)
INK = "#0F2437"       # sidebar / hero background
TEAL = "#0B7285"      # primary
AQUA = "#3CC4C4"      # highlight on dark
CORAL = "#E4572E"     # leakage, risk, bad
AMBER = "#EFA92D"     # inventory, caution
INDIGO = "#5C6BC0"    # secondary series
GREEN = "#2F9E73"     # good
SLATE = "#8493A6"     # neutral
# kept for backwards compatibility with older imports
BLUE, NAVY, RED = TEAL, INK, CORAL
