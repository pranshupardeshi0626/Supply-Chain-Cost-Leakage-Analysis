# Supply Chain Cost Leakage Dashboard

An interactive **Streamlit** dashboard that analyses **100,000 FMCG purchase orders** (Apr 2021 - Mar 2024)
to find where a supply chain loses money and service quality, and what to do about it.

> **Business question:** Supply-chain cost is 3.15% of order value (₹486 Cr on ₹15,438 Cr of orders)
> and only 77% of orders arrive on time and in full. Which problems cost the most, and which fixes come first?

## Key findings

| # | Finding | Evidence |
|---|---|---|
| 1 | **Late deliveries** are the main OTIF problem | OTIF 77.4% = on-time 82.8% x in-full 93.5%; late orders run 7.4 days late on average |
| 2 | **Supplier reliability score predicts delays** | Low-score suppliers delay 29.3% of orders vs 9.5% for high-score; 14 of 50 suppliers have OTIF below 70% and handle 27% of orders |
| 3 | **East region lags** | OTIF 74.7% vs 80.4% in West (-5.6 pp) on the biggest-volume lane after South |
| 4 | **Air freight is costly, barely faster** | 5.7x Road's transport cost per order; on-time only +0.9 pp. Premium over Road-equivalent cost: **₹59.8 Cr** |
| 5 | **Overstock drives holding cost** | 31.6% of orders overstocked vs 18.1% stocked out; excess holding cost **₹45.9 Cr** (9.4% of total cost) |
| 6 | **Damaged in transit** is the top rejection reason | 34% of the 8.1% rejected orders; top two reasons = 55% |
| 7 | **Forecast error is not the culprit** | Correlation with stockout/overstock ~0.00; stock flags follow stock vs reorder point |
| 8 | **Problems are structural, not seasonal** | Monthly OTIF stays within 75.0-79.6% for 36 months |

All numbers are computed live by `src/insights.py` and verified by a regression test.

## Pages

| Page | What it shows |
|---|---|
| Overview | Cost and service KPIs, OTIF breakdown, cost split, monthly trends, category table |
| Key Findings | The 8 findings above, the three "leakage" estimates in rupees, an Air-to-Road what-if slider |
| Supplier Scorecard | OTIF / delay / rejection per supplier, adjustable at-risk threshold, CSV download |
| Cost Drivers | Transport mode, overstock vs stockout, rejection Pareto, region x category heatmap, cost correlations |
| Data Explorer | Free-form univariate, bivariate and multivariate EDA |
| SQL Lab | 7 business queries (window functions, CTEs) on in-memory SQLite, plus a safe custom query box |

## Project structure

```
app.py              entry point: page config, data loading, sidebar, routing
src/
  config.py         constants and thresholds
  data_loader.py    load -> validate schema -> clean
  metrics.py        KPI and leakage calculations (pure functions)
  insights.py       turns metrics into findings, evidence and caveats
  filters.py        sidebar filters
  charts.py         Plotly figure builders
  sql_layer.py      SQLite helper + read-only guard
  formatters.py     rupee / percent formatting
  ui.py, styles.py  reusable components and CSS
views/              one small file per page
sql/queries.sql     the SQL Lab queries
tests/              27 tests (hand-checked KPIs, SQL guard, every page renders)
INTERVIEW_GUIDE.md  how to explain this project
```

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Run tests: `pip install -r requirements-dev.txt && pytest`

## Definitions

- **OTIF** = delivered on time **and** in full.
- **Cost % of value** = (transport + holding cost) / order value.
- **Excess holding cost** = (avg holding cost of overstocked orders - avg of normal orders) x number of overstocked orders.
- **Air premium** = Air transport cost - Air order value x Road's transport-cost-to-value ratio.
- **Rejected order value** = value of orders affected, *not* a realised loss.

## Limitations (stated honestly)

- The dataset has **no revenue, margin or refund column**, so "loss" is analysed as *cost leakage* and
  *service failure*, not profit and loss.
- The data looks **synthetic** (very flat across years, seasons and categories). Real data would show more variation.
- Leakage figures are estimates with stated assumptions, not exact savings. Findings show association, not causation.

## Dataset

`data/fmcg_supply_chain_100k.csv`: 100,000 orders, 38 columns, 50 suppliers, 500 SKUs, 8 warehouses.
You can also upload your own CSV/Excel in the sidebar if it contains the required columns (see `src/config.py`).
