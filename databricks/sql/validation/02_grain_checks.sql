
-- ============================================================
-- OLIST DATA PLATFORM
-- DATA QUALITY - GRAIN AND UNIQUENESS VALIDATION
-- Catalog: olist_dw
-- Schema: dw
--
-- Purpose:
-- Validate the business key uniqueness of fact tables.
--
-- Expected grain:
-- fact_sales: order_id + order_item_id
-- fact_payments: order_id + payment_sequential
-- fact_delivery_metrics: order_id
-- ============================================================


-- ============================================================
-- 1. FACT SALES
-- Expected: one row per order item
-- ============================================================

SELECT
    'fact_sales' AS table_name,
    COUNT(*) AS total_records,
    COUNT(DISTINCT CONCAT(order_id, '-', order_item_id))
        AS distinct_business_keys,
    COUNT(*) - COUNT(DISTINCT CONCAT(order_id, '-', order_item_id))
        AS duplicate_records
FROM olist_dw.dw.fact_sales;


-- ============================================================
-- 2. FACT PAYMENTS
-- Expected: one row per payment
-- ============================================================

SELECT
    'fact_payments' AS table_name,
    COUNT(*) AS total_records,
    COUNT(DISTINCT CONCAT(order_id, '-', payment_sequential))
        AS distinct_business_keys,
    COUNT(*) - COUNT(DISTINCT CONCAT(order_id, '-', payment_sequential))
        AS duplicate_records
FROM olist_dw.dw.fact_payments;


-- ============================================================
-- 3. FACT DELIVERY METRICS
-- Expected: one row per order
-- ============================================================

SELECT
    'fact_delivery_metrics' AS table_name,
    COUNT(*) AS total_records,
    COUNT(DISTINCT order_id) AS distinct_business_keys,
    COUNT(*) - COUNT(DISTINCT order_id) AS duplicate_records
FROM olist_dw.dw.fact_delivery_metrics;
