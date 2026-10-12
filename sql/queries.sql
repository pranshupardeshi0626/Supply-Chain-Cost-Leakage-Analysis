-- Each query is named with "-- name:" so the SQL Lab page can load them.
-- Table: orders  (the cleaned dataset). Works on SQLite.

-- name: Headline KPIs
SELECT COUNT(*)                                   AS orders,
       ROUND(AVG(otif) * 100, 1)                  AS otif_pct,
       ROUND(AVG(on_time) * 100, 1)               AS on_time_pct,
       ROUND(AVG(in_full) * 100, 1)               AS in_full_pct,
       ROUND(SUM(total_sc_cost_inr) * 100.0 / SUM(order_value_inr), 2) AS cost_pct_of_value
FROM orders;

-- name: OTIF by supplier region
SELECT supplier_region,
       COUNT(*)                     AS orders,
       ROUND(AVG(otif) * 100, 1)    AS otif_pct,
       ROUND(AVG(on_time) * 100, 1) AS on_time_pct
FROM orders
GROUP BY supplier_region
ORDER BY otif_pct ASC;

-- name: Supplier ranking (window function)
SELECT supplier_id,
       supplier_region,
       COUNT(*)                  AS orders,
       ROUND(AVG(otif) * 100, 1) AS otif_pct,
       RANK() OVER (ORDER BY AVG(otif) ASC) AS worst_rank
FROM orders
GROUP BY supplier_id, supplier_region
ORDER BY worst_rank
LIMIT 10;

-- name: Air vs Road cost
SELECT transport_mode,
       COUNT(*)                                   AS orders,
       ROUND(AVG(transport_cost_inr), 0)          AS avg_transport_cost,
       ROUND(SUM(transport_cost_inr) * 100.0 / SUM(order_value_inr), 2) AS transport_pct_of_value,
       ROUND(AVG(on_time) * 100, 1)               AS on_time_pct
FROM orders
GROUP BY transport_mode
ORDER BY avg_transport_cost DESC;

-- name: Holding cost - overstock vs normal
SELECT CASE WHEN overstock_flag = 1 THEN 'Overstock' ELSE 'Normal' END AS stock_status,
       COUNT(*)                          AS orders,
       ROUND(AVG(holding_cost_inr), 0)   AS avg_holding_cost
FROM orders
GROUP BY overstock_flag;

-- name: Monthly OTIF with month-over-month change (LAG)
WITH monthly AS (
    SELECT strftime('%Y-%m', order_date) AS order_month,   -- NOT "month": the table already has a column of that name
           AVG(otif) * 100               AS otif_pct
    FROM orders
    GROUP BY order_month
)
SELECT order_month,
       ROUND(otif_pct, 1)                                   AS otif_pct,
       ROUND(otif_pct - LAG(otif_pct) OVER (ORDER BY order_month), 1) AS change_vs_prev_month
FROM monthly
ORDER BY order_month;

-- name: Rejection reasons with cumulative share (Pareto)
WITH reasons AS (
    SELECT rejection_reason, COUNT(*) AS orders
    FROM orders
    WHERE rejection_flag = 1
    GROUP BY rejection_reason
)
SELECT rejection_reason,
       orders,
       ROUND(orders * 100.0 / SUM(orders) OVER (), 1) AS share_pct,
       ROUND(SUM(orders) OVER (ORDER BY orders DESC) * 100.0 / SUM(orders) OVER (), 1) AS cumulative_pct
FROM reasons
ORDER BY orders DESC;
