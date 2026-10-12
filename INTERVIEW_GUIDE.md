# Interview Guide: Supply Chain Cost Leakage Dashboard

## 1. The 30-second pitch

"I analysed 100,000 FMCG purchase orders to find where a supply chain leaks money and service quality.
Supply-chain cost is 3.15% of order value, about ₹486 Cr, and only 77% of orders arrive on time and in full.
I built a Streamlit dashboard that sizes the problems in rupees: about ₹46 Cr of excess holding cost from
overstock and about ₹60 Cr of Air freight premium. It also ranks suppliers and recommends fixes. The code is split into
small tested modules, and I added a SQL layer that answers the same questions with window functions."

## 2. Explain the code in 2 minutes (the module map)

Say it as a pipeline: **load -> calculate -> explain -> show.**

| Step | File | One-sentence explanation |
|---|---|---|
| Load | `src/data_loader.py` | Reads the CSV, checks required columns exist, parses dates, removes duplicates, adds helper columns |
| Settings | `src/config.py` | Every threshold and column list in one place, so there are no magic numbers |
| Calculate | `src/metrics.py` | Pure functions: DataFrame in, numbers out. No Streamlit, so each is testable |
| Explain | `src/insights.py` | Each finding is a small function returning title, finding, evidence, action, caveat |
| Show | `src/charts.py`, `views/*.py` | Charts take prepared data and return a figure; each page is one short `render(df)` function |
| Glue | `app.py` | Loads data once (cached), draws the sidebar, applies filters, calls the selected page |
| SQL | `src/sql_layer.py`, `sql/queries.sql` | Copies the data into in-memory SQLite and runs read-only queries |
| Quality | `tests/` | 27 tests: hand-checked KPIs, SQL safety, a golden test on real data, every page renders |

**Why this structure?** "Separating calculation from display means I can test the numbers without launching the UI,
and I can explain any page by reading one short file."

Tip: open `src/metrics.py` and show `kpis_by(df, by)`. It is one `groupby().agg()` that powers region, mode,
category, supplier and month views. Reuse is the point.

## 3. Numbers to memorise

| Metric | Value |
|---|---|
| Orders / suppliers / SKUs / warehouses | 100,000 / 50 / 500 / 8 |
| Period | Apr 2021 - Mar 2024 |
| Order value / supply-chain cost | ₹15,438 Cr / ₹486 Cr (3.15%) |
| Cost split | Transport 51.7%, Holding 48.3% |
| OTIF / on-time / in-full | 77.4% / 82.8% / 93.5% |
| Late orders (avg delay) | 17.2% (7.4 days) |
| Stockout / overstock / imbalance total | 18.1% / 31.6% / 49.7% |
| Rejection rate | 8.1% (value ₹1,248 Cr) |
| Top rejection reason | Damaged in transit, 34% |
| Supplier OTIF range | 62.6% - 91.2%; 14 suppliers below 70% (27% of orders) |
| Delay rate: low vs high reliability score | 29.3% vs 9.5% |
| Region OTIF | West 80.4%, North 79.5%, Central 76.6%, South 76.3%, East 74.7% |
| Air vs Road | 5.7x transport cost per order; cost 6.2% vs 2.3% of value; on-time +0.9 pp |
| Excess holding cost | ₹45.9 Cr (9.4% of cost) |
| Air premium | ₹59.8 Cr (12.3% of cost); moving 25% of Air to Road saves about ₹15.0 Cr |

## 4. Likely questions and strong answers

**"Where is the loss? Is there a profit column?"**
No. The data has order value and supply-chain cost but no revenue or margin. So I framed it as *cost leakage*:
avoidable cost (excess holding, Air premium) plus *value at risk* (rejected orders). I say explicitly that rejected value
is not realised loss. Being clear about this is better than claiming a profit number I cannot support.

**"How did you calculate excess holding cost?"**
Overstocked orders carry ₹33,411 holding cost per order vs ₹18,888 for normal ones. The gap times 31,588 overstocked
orders is ₹45.9 Cr. Caveat: overstock means more stock, so part of the gap is mechanical. It is an estimate, not exact savings.

**"How did you calculate the Air premium?"**
Road's transport cost is a fixed share of order value. I apply that ratio to Air's order value and subtract it from
Air's actual transport cost. Caveat: some Air orders may be urgent, so ₹59.8 Cr is an upper bound.

**"Why is OTIF only 77% when in-full is 93%?"**
OTIF needs both. On-time is 82.8%, so lateness fails far more orders. Every late order fails OTIF by definition.
So the first fix is timeliness, not order completeness.

**"Does supplier reliability really matter?"**
Yes: delay rate goes 29.3% -> 18.9% -> 9.5% across low, medium and high bands. It does not affect rejection rate (about 8% in every band),
so reliability explains lateness, not quality. I avoided claiming it explains everything.

**"What did you find that surprised you?"**
Forecast error has no link to stockouts or overstock. Every stockout order has stock below the reorder point, so the flags follow
reorder rules, not forecasts. The recommendation is to review reorder points before investing in forecasting.

**"What are the weaknesses of your analysis?"**
The dataset looks synthetic (flat across seasons and years), has no profit data, and the findings are correlations.
I put caveats in the dashboard itself so nobody over-reads it.

**"Tell me about a bug you found."**
In my SQL monthly-trend query I aliased the date as `month`, but the table already has a `month` column. SQLite grouped by the
original column and silently returned wrong rows (months missing). I noticed the output skipped months, renamed the alias
to `order_month`, and added a test that checks every named query returns results and matches pandas.

**"How did you test it?"**
Unit tests on a 6-row dataset whose KPIs I computed by hand, a golden test pinning real-data OTIF at 77.36%,
SQL-vs-pandas agreement, a test that dangerous SQL is rejected, and Streamlit's `AppTest` to render every page.

**"How does the app stay fast on 100K rows?"**
`st.cache_data` loads and cleans the CSV once. Scatter plots use a 5,000-row random sample. The SQL connection is cached with
`st.cache_resource`.

**"Is the SQL box safe?"**
It only allows a single SELECT/WITH statement, and the SQLite connection is set to `query_only`. It is also an in-memory copy,
so the source data cannot be harmed.

**"Why Streamlit / SQLite?"**
Streamlit lets analysts ship an interactive tool in Python quickly. SQLite shows SQL skills with zero setup;
the queries port to Postgres or BigQuery with small changes (mainly `strftime`).

**"What would you do next?"**
Add revenue and margin data to size true profit impact, a statistical test or regression for supplier effects,
supplier-level cost-of-delay, and automated refresh from a database.

## 5. SQL talking points (`sql/queries.sql`)

- `RANK() OVER (ORDER BY AVG(otif))` ranks suppliers without a self-join.
- `LAG()` gives month-over-month OTIF change.
- `SUM() OVER ()` gives share of total; `SUM() OVER (ORDER BY ...)` gives the cumulative Pareto.
- A CTE (`WITH monthly AS ...`) keeps the monthly query readable.

## 6. Resume bullets (pick 3)

- Built an interactive Streamlit dashboard on **100K+ FMCG purchase orders** (Python, Pandas, Plotly, SQL) to diagnose supply-chain cost leakage and delivery performance.
- Quantified **~₹46 Cr excess holding cost** from overstock and **~₹60 Cr Air-freight premium** (about 22% of total supply-chain cost combined), and built a what-if tool to size savings from shifting Air volume to Road.
- Identified that **late deliveries drive OTIF failure** (OTIF 77.4%; on-time 82.8%) and that low-reliability suppliers delay **29% of orders vs 9.5%** for high scorers; built a supplier scorecard flagging 14 at-risk suppliers.
- Wrote **7 SQL queries** (window functions, CTEs) in SQLite and **27 automated tests**; refactored the app into small modules (metrics, insights, charts, views).
