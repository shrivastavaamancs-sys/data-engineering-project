-- 1. Total Revenue
SELECT
    SUM(total_amount) AS total_revenue
FROM online_retail;


-- 2. Total Orders
SELECT
    COUNT(DISTINCT invoice_no) AS total_orders
FROM online_retail;


-- 3. Top 10 Products by Revenue
SELECT
    stock_code,
    description,
    SUM(total_amount) AS revenue
FROM online_retail
GROUP BY stock_code, description
ORDER BY revenue DESC
LIMIT 10;


-- 4. Top 10 Customers
SELECT
    customer_id,
    SUM(total_amount) AS total_spent
FROM online_retail
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 10;


-- 5. Country-wise Revenue
SELECT
    country,
    SUM(total_amount) AS total_sales
FROM online_retail
GROUP BY country
ORDER BY total_sales DESC;


-- 6. Monthly Revenue
SELECT
    DATE_TRUNC('month', invoice_date) AS month,
    SUM(total_amount) AS monthly_revenue
FROM online_retail
GROUP BY month
ORDER BY month;


-- 7. Average Order Value
SELECT
    SUM(total_amount) / COUNT(DISTINCT invoice_no) AS average_order_value
FROM online_retail;


-- 8. Customer Ranking
SELECT
    customer_id,
    SUM(total_amount) AS total_spent,
    RANK() OVER (
        ORDER BY SUM(total_amount) DESC
    ) AS customer_rank
FROM online_retail
GROUP BY customer_id;