-- ============================================================
-- CUSTOMER DATA ETL PROJECT
-- SQL ANALYSIS
-- ============================================================


-- ============================================================
-- 1. TOTAL CUSTOMERS
-- ============================================================

SELECT
    COUNT(*) AS total_customers
FROM customers;


-- ============================================================
-- 2. TOTAL ORDERS
-- ============================================================

SELECT
    COUNT(*) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM orders;


-- ============================================================
-- 3. TOTAL REVENUE
-- ============================================================

SELECT
    SUM(quantity * price) AS total_revenue
FROM order_items;


-- ============================================================
-- 4. ORDERS BY COUNTRY
-- ============================================================

SELECT
    c.country,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY c.country
ORDER BY total_orders DESC;


-- ============================================================
-- 5. REVENUE BY COUNTRY
-- ============================================================

SELECT
    c.country,
    SUM(oi.quantity * oi.price) AS total_revenue
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN order_items oi
    ON o.order_id = oi.order_id
GROUP BY c.country
ORDER BY total_revenue DESC;


-- ============================================================
-- 6. TOP 10 PRODUCTS BY REVENUE
-- ============================================================

SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(oi.quantity * oi.price) AS revenue
FROM products p
JOIN order_items oi
    ON p.product_id = oi.product_id
GROUP BY
    p.product_id,
    p.product_name,
    p.category
ORDER BY revenue DESC
LIMIT 10;


-- ============================================================
-- 7. REVENUE BY CATEGORY
-- ============================================================

SELECT
    p.category,
    SUM(oi.quantity * oi.price) AS revenue
FROM products p
JOIN order_items oi
    ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY revenue DESC;


-- ============================================================
-- 8. MONTHLY REVENUE
-- ============================================================

SELECT
    DATE_TRUNC('month', o.order_date)::date AS month,
    SUM(oi.quantity * oi.price) AS revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month;


-- ============================================================
-- 9. TOP 10 CUSTOMERS BY SPENDING
-- ============================================================

SELECT
    c.customer_id,
    c.country,
    SUM(oi.quantity * oi.price) AS total_spending
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN order_items oi
    ON o.order_id = oi.order_id
GROUP BY
    c.customer_id,
    c.country
ORDER BY total_spending DESC
LIMIT 10;


-- ============================================================
-- 10. COUNTRY-WISE CUSTOMER RANKING
-- WINDOW FUNCTION
-- ============================================================

SELECT
    customer_id,
    country,
    total_spending,
    RANK() OVER (
        PARTITION BY country
        ORDER BY total_spending DESC
    ) AS country_rank
FROM (
    SELECT
        c.customer_id,
        c.country,
        SUM(oi.quantity * oi.price) AS total_spending
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
    JOIN order_items oi
        ON o.order_id = oi.order_id
    GROUP BY
        c.customer_id,
        c.country
) customer_sales
ORDER BY country, country_rank;


-- ============================================================
-- 11. AVERAGE ORDER VALUE
-- ============================================================

SELECT
    ROUND(
        SUM(oi.quantity * oi.price)
        / COUNT(DISTINCT o.order_id),
        2
    ) AS average_order_value
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id;


-- ============================================================
-- 12. TOP 10 ORDERS BY ORDER VALUE
-- ============================================================

SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    SUM(oi.quantity * oi.price) AS order_value
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
GROUP BY
    o.order_id,
    o.customer_id,
    o.order_date
ORDER BY order_value DESC
LIMIT 10;


-- ============================================================
-- DATA QUALITY CHECKS
-- ============================================================


-- ============================================================
-- 13. NULL CHECK - ORDERS
-- ============================================================

SELECT
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (
        WHERE order_id IS NULL
    ) AS null_order_id,
    COUNT(*) FILTER (
        WHERE customer_id IS NULL
    ) AS null_customer_id,
    COUNT(*) FILTER (
        WHERE order_date IS NULL
    ) AS null_order_date,
    COUNT(*) FILTER (
        WHERE status IS NULL
    ) AS null_status
FROM orders;


-- ============================================================
-- 14. DUPLICATE ORDERS
-- ============================================================

SELECT
    order_id,
    COUNT(*) AS duplicate_count
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;


-- ============================================================
-- 15. INVALID QUANTITY
-- ============================================================

SELECT
    COUNT(*) AS invalid_quantity
FROM order_items
WHERE quantity <= 0;


-- ============================================================
-- 16. INVALID PRICE
-- ============================================================

SELECT
    COUNT(*) AS invalid_price
FROM order_items
WHERE price < 0;


-- ============================================================
-- 17. INVALID CUSTOMER REFERENCES
-- ============================================================

SELECT
    COUNT(*) AS invalid_customer_references
FROM orders o
LEFT JOIN customers c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;


-- ============================================================
-- 18. INVALID ORDER / PRODUCT REFERENCES
-- ============================================================

SELECT
    COUNT(*) AS invalid_order_item_references
FROM order_items oi
LEFT JOIN orders o
    ON oi.order_id = o.order_id
LEFT JOIN products p
    ON oi.product_id = p.product_id
WHERE o.order_id IS NULL
   OR p.product_id IS NULL;