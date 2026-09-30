-- Runs against warehouse.sqlite created by retail.train.
-- Dates are ISO strings; this query is also easy to adapt to PostgreSQL.
SELECT sku, substr(date,1,7) AS month,
       SUM(units) AS demand, AVG(units) AS average_daily_demand,
       COUNT(*) AS observed_days
FROM daily_sales
GROUP BY sku, substr(date,1,7)
ORDER BY sku, month;
