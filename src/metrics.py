"""All business calculations live here as small pure functions (DataFrame in, numbers out).

Definitions used across the project
-----------------------------------
OTIF            = on time AND in full (share of orders)
Cost % of value = total supply-chain cost / order value
Supply-chain cost = transport cost + holding cost
"""
import pandas as pd

from src.config import (BASELINE_MODE, PREMIUM_MODE, RELIABILITY_BINS,
                        RELIABILITY_LABELS)


def safe_div(a: float, b: float) -> float:
    return float(a) / float(b) if b else 0.0


# 1) Headline numbers -------------------------------------------------------
def headline_kpis(df: pd.DataFrame) -> dict:
    n = len(df)
    delayed = df[df["supplier_delayed"] == 1]
    return {
        "orders": n,
        "order_value": df["order_value_inr"].sum(),
        "sc_cost": df["total_sc_cost_inr"].sum(),
        "transport_cost": df["transport_cost_inr"].sum(),
        "holding_cost": df["holding_cost_inr"].sum(),
        "cost_pct": safe_div(df["total_sc_cost_inr"].sum(), df["order_value_inr"].sum()),
        "otif": df["otif"].mean() if n else 0.0,
        "on_time": df["on_time"].mean() if n else 0.0,
        "in_full": df["in_full"].mean() if n else 0.0,
        "stockout_rate": df["stockout_flag"].mean() if n else 0.0,
        "overstock_rate": df["overstock_flag"].mean() if n else 0.0,
        "rejection_rate": df["rejection_flag"].mean() if n else 0.0,
        "avg_delay_when_late": delayed["supplier_delay_days"].mean() if len(delayed) else 0.0,
    }


# 2) The same KPIs for any grouping (region, mode, supplier, month...) -------
def kpis_by(df: pd.DataFrame, by) -> pd.DataFrame:
    g = df.groupby(by).agg(
        orders=("order_id", "count"),
        otif=("otif", "mean"),
        on_time=("on_time", "mean"),
        in_full=("in_full", "mean"),
        delay_rate=("supplier_delayed", "mean"),
        stockout_rate=("stockout_flag", "mean"),
        overstock_rate=("overstock_flag", "mean"),
        rejection_rate=("rejection_flag", "mean"),
        sc_cost=("total_sc_cost_inr", "sum"),
        transport_cost=("transport_cost_inr", "sum"),
        holding_cost=("holding_cost_inr", "sum"),
        order_value=("order_value_inr", "sum"),
    )
    g["cost_pct"] = g["sc_cost"] / g["order_value"]
    g["avg_cost_per_order"] = g["sc_cost"] / g["orders"]
    return g.reset_index()


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    return kpis_by(df, "year_month").sort_values("year_month")


# 3) Suppliers --------------------------------------------------------------
def supplier_scorecard(df: pd.DataFrame, otif_floor: float) -> pd.DataFrame:
    sc = kpis_by(df, "supplier_id")
    info = df.groupby("supplier_id").agg(
        region=("supplier_region", "first"),
        reliability=("supplier_reliability_score", "mean"),
    ).reset_index()
    sc = sc.merge(info, on="supplier_id")
    sc["at_risk"] = sc["otif"] < otif_floor
    return sc.sort_values("otif").reset_index(drop=True)


def reliability_bands(df: pd.DataFrame) -> pd.DataFrame:
    """Do suppliers with a higher reliability score really deliver on time?"""
    band = pd.cut(df["supplier_reliability_score"], RELIABILITY_BINS, labels=RELIABILITY_LABELS)
    g = df.groupby(band, observed=True).agg(
        orders=("order_id", "count"),
        delay_rate=("supplier_delayed", "mean"),
        otif=("otif", "mean"),
        rejection_rate=("rejection_flag", "mean"),
    )
    return g.reset_index(names="reliability_band")


# 4) Rejections -------------------------------------------------------------
def rejection_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Pareto table: rejection reasons sorted by count with cumulative share."""
    rej = df[df["rejection_flag"] == 1]
    out = (rej.groupby("rejection_reason")
              .agg(orders=("order_id", "count"), order_value=("order_value_inr", "sum"))
              .sort_values("orders", ascending=False).reset_index())
    total = out["orders"].sum()
    out["share"] = out["orders"] / total if total else 0.0
    out["cum_share"] = out["share"].cumsum()
    return out


# 5) Money that can be saved ("cost leakage") ----------------------------------
def excess_holding_cost(df: pd.DataFrame) -> float:
    """Extra holding cost carried by overstocked orders vs. normal orders."""
    over, normal = df[df["overstock_flag"] == 1], df[df["overstock_flag"] == 0]
    if over.empty or normal.empty:
        return 0.0
    extra_per_order = over["holding_cost_inr"].mean() - normal["holding_cost_inr"].mean()
    return max(extra_per_order, 0.0) * len(over)


def transport_premium(df: pd.DataFrame, premium=PREMIUM_MODE, baseline=BASELINE_MODE) -> float:
    """What Air shipments cost ABOVE what they would cost at Road's cost-to-value ratio."""
    prem, base = df[df["transport_mode"] == premium], df[df["transport_mode"] == baseline]
    if prem.empty or base.empty:
        return 0.0
    base_rate = safe_div(base["transport_cost_inr"].sum(), base["order_value_inr"].sum())
    return max(prem["transport_cost_inr"].sum() - prem["order_value_inr"].sum() * base_rate, 0.0)


def air_shift_scenario(df: pd.DataFrame, shift_share: float) -> dict:
    """What-if: move `shift_share` (0-1) of Air shipments to Road."""
    saving = transport_premium(df) * shift_share
    total = df["total_sc_cost_inr"].sum()
    return {"saving": saving, "saving_pct_of_cost": safe_div(saving, total)}


def leakage_estimates(df: pd.DataFrame) -> dict:
    rejected_value = df.loc[df["rejection_flag"] == 1, "order_value_inr"].sum()
    return {
        "excess_holding": excess_holding_cost(df),
        "air_premium": transport_premium(df),
        "rejected_value": rejected_value,
        "total_cost": df["total_sc_cost_inr"].sum(),
    }


# 6) Cost drivers -----------------------------------------------------------
DRIVER_COLUMNS = ["order_value_inr", "ordered_qty", "stock_on_hand", "unit_price_inr",
                  "actual_lead_days", "supplier_delay_days", "forecast_error_pct"]


def cost_correlations(df: pd.DataFrame) -> pd.Series:
    """Correlation of each possible driver with total supply-chain cost."""
    cols = [c for c in DRIVER_COLUMNS if c in df.columns]
    return df[cols].corrwith(df["total_sc_cost_inr"]).sort_values(ascending=False)
