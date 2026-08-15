-- =========================================================
-- Amazon Sales Data Engineering Project
-- SQL Analytics
-- =========================================================


-- =========================================================
-- 1. Monthly Revenue
-- =========================================================

SELECT
    DATE_TRUNC('month', order_date)::date AS month,
    COUNT(*) AS orders,
    SUM(qty) AS quantity,
    ROUND(SUM(amount), 2) AS revenue
FROM amazon_sales_etl
GROUP BY 1
ORDER BY 1;


-- =========================================================
-- 2. Category Performance
-- =========================================================

SELECT
    category,
    COUNT(*) AS orders,
    SUM(qty) AS quantity,
    ROUND(SUM(amount), 2) AS revenue
FROM amazon_sales_etl
GROUP BY category
ORDER BY revenue DESC;


-- =========================================================
-- 3. Fulfilment Performance
-- =========================================================

SELECT
    fulfilment,
    COUNT(*) AS orders,
    SUM(qty) AS quantity,
    ROUND(SUM(amount), 2) AS revenue
FROM amazon_sales_etl
GROUP BY fulfilment
ORDER BY revenue DESC;


-- =========================================================
-- 4. Top 10 SKU by Revenue
-- =========================================================

SELECT
    sku,
    category,
    SUM(qty) AS total_quantity,
    ROUND(SUM(amount), 2) AS revenue
FROM amazon_sales_etl
GROUP BY sku, category
ORDER BY revenue DESC
LIMIT 10;


-- =========================================================
-- 5. Monthly Revenue Ranking
-- CTE + RANK()
-- =========================================================

WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', order_date)::date AS month,
        SUM(amount) AS revenue
    FROM amazon_sales_etl
    GROUP BY 1
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    RANK() OVER (
        ORDER BY revenue DESC
    ) AS revenue_rank
FROM monthly_sales
ORDER BY revenue_rank;


-- =========================================================
-- 6. Month-over-Month Revenue Growth
-- CTE + LAG()
-- =========================================================

WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', order_date)::date AS month,
        SUM(amount) AS revenue
    FROM amazon_sales_etl
    GROUP BY 1
),
monthly_growth AS (
    SELECT
        month,
        revenue,
        LAG(revenue) OVER (
            ORDER BY month
        ) AS previous_month_revenue
    FROM monthly_sales
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(previous_month_revenue, 2) AS previous_month_revenue,
    ROUND(
        (
            (revenue - previous_month_revenue)
            / NULLIF(previous_month_revenue, 0)
        ) * 100,
        2
    ) AS growth_percentage
FROM monthly_growth
ORDER BY month;


-- =========================================================
-- 7. Top SKU per Category
-- CTE + ROW_NUMBER() + PARTITION BY
-- =========================================================

WITH sku_sales AS (
    SELECT
        category,
        sku,
        SUM(qty) AS total_quantity,
        SUM(amount) AS revenue
    FROM amazon_sales_etl
    GROUP BY category, sku
),
ranked_skus AS (
    SELECT
        category,
        sku,
        total_quantity,
        revenue,
        ROW_NUMBER() OVER (
            PARTITION BY category
            ORDER BY revenue DESC
        ) AS rn
    FROM sku_sales
)
SELECT
    category,
    sku,
    total_quantity,
    ROUND(revenue, 2) AS revenue
FROM ranked_skus
WHERE rn = 1
ORDER BY revenue DESC;


-- =========================================================
-- 8. Running / Cumulative Revenue
-- Window SUM()
-- =========================================================

SELECT
    order_date,
    ROUND(SUM(amount), 2) AS daily_revenue,
    ROUND(
        SUM(SUM(amount)) OVER (
            ORDER BY order_date
        ),
        2
    ) AS cumulative_revenue
FROM amazon_sales_etl
GROUP BY order_date
ORDER BY order_date;


-- =========================================================
-- 9. Next Month Revenue
-- CTE + LEAD()
-- =========================================================

WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', order_date)::date AS month,
        SUM(amount) AS revenue
    FROM amazon_sales_etl
    GROUP BY 1
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(
        LEAD(revenue) OVER (
            ORDER BY month
        ),
        2
    ) AS next_month_revenue
FROM monthly_sales
ORDER BY month;


-- =========================================================
-- 10. Top 3 SKU per Category
-- CTE + ROW_NUMBER() + PARTITION BY
-- =========================================================

WITH sku_sales AS (
    SELECT
        category,
        sku,
        SUM(qty) AS total_quantity,
        SUM(amount) AS revenue
    FROM amazon_sales_etl
    GROUP BY category, sku
),
ranked_skus AS (
    SELECT
        category,
        sku,
        total_quantity,
        revenue,
        ROW_NUMBER() OVER (
            PARTITION BY category
            ORDER BY revenue DESC
        ) AS rn
    FROM sku_sales
)
SELECT
    category,
    sku,
    total_quantity,
    ROUND(revenue, 2) AS revenue
FROM ranked_skus
WHERE rn <= 3
ORDER BY category, revenue DESC;