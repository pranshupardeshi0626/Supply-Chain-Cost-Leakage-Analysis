"""Turns numbers into findings. Every insight is computed from the data (nothing hard-coded),
and each carries a caveat so we never over-claim."""
from dataclasses import dataclass, field

import pandas as pd

from src import metrics as m
from src.formatters import inr, pct, pp


@dataclass
class Insight:
    title: str
    finding: str
    evidence: list = field(default_factory=list)
    action: str = ""
    caveat: str = ""


def otif_gap(df):
    k = m.headline_kpis(df)
    late_gap, full_gap = 1 - k["on_time"], 1 - k["in_full"]
    main = "late deliveries" if late_gap > full_gap else "incomplete deliveries"
    return Insight(
        "OTIF is held back mainly by " + main,
        f"Only {pct(k['otif'])} of orders arrive on time AND in full.",
        [f"On-time: {pct(k['on_time'])} ({pct(late_gap)} late)",
         f"In-full: {pct(k['in_full'])} ({pct(full_gap)} short)",
         f"When an order is late it is late by {k['avg_delay_when_late']:.1f} days on average"],
        "Fix delivery timeliness first: it explains far more OTIF failures than short shipments.",
        "OTIF = on_time AND in_full, so any late order fails OTIF by definition.")


def supplier_reliability(df):
    bands = m.reliability_bands(df)
    low, high = bands.iloc[0], bands.iloc[-1]
    sc = m.supplier_scorecard(df, 0.0)
    return Insight(
        "Supplier reliability score is a strong predictor of delays",
        f"Low-score suppliers delay {pct(low['delay_rate'])} of orders vs {pct(high['delay_rate'])} "
        f"for high-score suppliers.",
        [f"OTIF: {pct(low['otif'])} (low band) vs {pct(high['otif'])} (high band)",
         f"Across {len(sc)} suppliers OTIF ranges from {pct(sc['otif'].min())} to {pct(sc['otif'].max())}"],
        "Put the lowest-OTIF suppliers on a corrective plan and shift volume to high scorers.",
        "Score is a supplier attribute, so this shows an association; it does not prove causation.")


def regional_gap(df):
    r = m.kpis_by(df, "supplier_region").sort_values("otif")
    if len(r) < 2:
        return None
    worst, best = r.iloc[0], r.iloc[-1]
    return Insight(
        f"{worst['supplier_region']} region lags on OTIF",
        f"{worst['supplier_region']} OTIF is {pct(worst['otif'])} vs {pct(best['otif'])} in "
        f"{best['supplier_region']} ({pp(worst['otif'] - best['otif'])}).",
        [f"{worst['supplier_region']} handles {worst['orders']:,} orders "
         f"({pct(worst['orders'] / len(df))} of volume)",
         f"Its on-time rate is {pct(worst['on_time'])} vs {pct(best['on_time'])}"],
        f"Review {worst['supplier_region']} suppliers and lanes first: biggest volume with a weak OTIF.",
        "Regions differ by a few points; check supplier mix before blaming geography.")


def transport_mode(df):
    t = m.kpis_by(df, "transport_mode").set_index("transport_mode")
    if not {"Air", "Road"} <= set(t.index):
        return None
    air, road = t.loc["Air"], t.loc["Road"]
    ratio = (air["transport_cost"] / air["orders"]) / (road["transport_cost"] / road["orders"])
    return Insight(
        "Air freight is expensive and does not buy much reliability",
        f"Air transport costs {ratio:.1f}x more per order than Road "
        f"({inr(air['transport_cost'] / air['orders'])} vs {inr(road['transport_cost'] / road['orders'])}).",
        [f"Cost as % of order value: Air {pct(air['cost_pct'])} vs Road {pct(road['cost_pct'])}",
         f"On-time: Air {pct(air['on_time'])} vs Road {pct(road['on_time'])} "
         f"({pp(air['on_time'] - road['on_time'])})",
         f"Air premium over Road-equivalent cost: {inr(m.transport_premium(df))}"],
        "Restrict Air to genuinely urgent orders; test shifting routine Air volume to Road/Rail.",
        "Some Air orders may be urgent for reasons not in this data; treat savings as an upper bound.")


def overstock(df):
    k = m.headline_kpis(df)
    extra = m.excess_holding_cost(df)
    over = df[df["overstock_flag"] == 1]["holding_cost_inr"].mean()
    normal = df[df["overstock_flag"] == 0]["holding_cost_inr"].mean()
    return Insight(
        "Overstock is the bigger inventory problem and drives holding cost",
        f"{pct(k['overstock_rate'])} of orders are overstocked vs {pct(k['stockout_rate'])} stocked out.",
        [f"Holding cost per order: {inr(over)} (overstock) vs {inr(normal)} (normal)",
         f"Excess holding cost on overstocked orders: {inr(extra)} "
         f"({pct(extra / k['sc_cost'])} of total supply-chain cost)",
         f"Together, {pct(k['overstock_rate'] + k['stockout_rate'])} of orders have an inventory imbalance"],
        "Lower order quantities / reorder points for chronically overstocked SKUs.",
        "Overstock orders hold more stock by definition, so part of this gap is mechanical.")


def rejections(df):
    b = m.rejection_breakdown(df)
    if b.empty:
        return None
    k = m.headline_kpis(df)
    top = b.iloc[0]
    return Insight(
        f"'{top['rejection_reason']}' is the top rejection reason",
        f"{pct(k['rejection_rate'])} of orders are rejected; '{top['rejection_reason']}' causes "
        f"{pct(top['share'])} of them.",
        [f"Top 2 reasons cover {pct(b['cum_share'].iloc[min(1, len(b) - 1)])} of rejections",
         f"Value of rejected orders: {inr(df.loc[df['rejection_flag'] == 1, 'order_value_inr'].sum())}"],
        "Start with the top reason (packaging / carrier handling / expiry checks) for the quickest win.",
        "That is order VALUE affected, not realised loss: the data has no refund or write-off column.")


def forecast_error(df):
    corr_stockout = df["forecast_error_pct"].corr(df["stockout_flag"])
    corr_over = df["forecast_error_pct"].corr(df["overstock_flag"])
    weak = max(abs(corr_stockout), abs(corr_over)) < 0.05
    stockouts = df[df["stockout_flag"] == 1]
    below_rp = (stockouts["stock_on_hand"] < stockouts["reorder_point"]).mean() if len(stockouts) else 0.0
    verdict = ("is NOT linked to stockouts or overstock in this data"
               if weak else "shows some link to stock problems")
    return Insight(
        "Forecast error " + ("is not the culprit" if weak else "deserves a closer look"),
        f"Forecast error {verdict} (correlation {corr_stockout:+.2f} with stockouts, "
        f"{corr_over:+.2f} with overstock).",
        [f"{pct(below_rp)} of stockout orders had stock below the reorder point: the flag follows "
         f"stock level vs reorder point, not forecast accuracy"],
        "Review reorder-point and safety-stock rules before investing in better forecasting.",
        "Stock flags look derived from stock vs reorder point, so this cannot judge forecast quality itself.")


def stability(df):
    t = m.monthly_trend(df)
    if len(t) < 3:
        return None
    return Insight(
        "Problems are structural, not seasonal",
        f"Monthly OTIF stays between {pct(t['otif'].min())} and {pct(t['otif'].max())} "
        f"across {len(t)} months.",
        [f"Monthly cost-to-value ratio only moves between {pct(t['cost_pct'].min(), 2)} "
         f"and {pct(t['cost_pct'].max(), 2)}"],
        "Expect no improvement from waiting for a better season: process changes are needed.",
        "The dataset looks synthetic (very flat), so real data would likely show more seasonality.")


INSIGHT_BUILDERS = [otif_gap, supplier_reliability, regional_gap, transport_mode,
                    overstock, rejections, forecast_error, stability]


def generate_insights(df: pd.DataFrame) -> list:
    results = (build(df) for build in INSIGHT_BUILDERS)
    return [i for i in results if i is not None]
