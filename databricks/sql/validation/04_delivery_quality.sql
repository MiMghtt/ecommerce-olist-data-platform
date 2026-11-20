
-- ============================================================
-- OLIST DATA PLATFORM
-- DATA QUALITY - DELIVERY BUSINESS RULES
-- Catalog: olist_dw
-- Schema: dw
--
-- Purpose:
-- Validate delivery classifications and identify
-- business data inconsistencies.
-- ============================================================


-- ============================================================
-- 1. DELIVERY STATUS DISTRIBUTION
-- ============================================================

SELECT
    order_status,
    delivery_status,
    COUNT(*) AS total_orders,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM olist_dw.dw.fact_delivery_metrics
GROUP BY
    order_status,
    delivery_status
ORDER BY
    order_status,
    delivery_status;


-- ============================================================
-- 2. DELIVERED ORDERS WITHOUT DELIVERY DATE
-- Expected: 8 records based on current validation
-- ============================================================

SELECT
    order_id,
    order_status,
    order_delivered_customer_date,
    delivery_status
FROM olist_dw.dw.fact_delivery_metrics
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NULL;


-- ============================================================
-- 3. CANCELED ORDERS
-- All canceled orders must have delivery_status = 'canceled'
-- ============================================================

SELECT
    COUNT(*) AS canceled_orders,
    COUNT_IF(delivery_status <> 'canceled')
        AS incorrectly_classified_orders
FROM olist_dw.dw.fact_delivery_metrics
WHERE order_status = 'canceled';


-- ============================================================
-- 4. DELIVERY CLASSIFICATION CONSISTENCY
-- ============================================================

SELECT
    COUNT_IF(
        order_status = 'delivered'
        AND delivery_status NOT IN (
            'delivered_on_time',
            'delivered_delayed',
            'delivery_data_inconsistent'
        )
    ) AS invalid_delivered_classifications,

    COUNT_IF(
        order_status <> 'delivered'
        AND order_status <> 'canceled'
        AND delivery_status <> 'not_delivered'
    ) AS invalid_non_delivered_classifications

FROM olist_dw.dw.fact_delivery_metrics;


-- ============================================================
-- 5. ORDERS WITHOUT PAYMENT RECORD
-- ============================================================

SELECT
    o.order_id,
    o.order_status,
    o.order_purchase_timestamp
FROM olist_dw.dw.orders o
LEFT JOIN olist_dw.dw.fact_payments fp
    ON o.order_id = fp.order_id
WHERE fp.order_id IS NULL;


-- ============================================================
-- 6. SALES AND PAYMENT TOTALS
-- These metrics have different grains and business meanings.
-- Do not assume they should be equal.
-- ============================================================

SELECT
    'fact_sales' AS source_table,
    SUM(total_item_value) AS total_amount
FROM olist_dw.dw.fact_sales

UNION ALL

SELECT
    'fact_payments',
    SUM(payment_value)
FROM olist_dw.dw.fact_payments;
