
-- ============================================================
-- OLIST DATA PLATFORM
-- DATA QUALITY - REFERENTIAL INTEGRITY
-- Catalog: olist_dw
-- Schema: dw
--
-- Purpose:
-- Validate relationships between fact and dimension tables.
-- A missing delivery date is allowed for orders not delivered.
-- ============================================================


-- ============================================================
-- 1. FACT SALES
-- Expected dimensions:
-- customer, product, seller and purchase date
-- ============================================================

SELECT
    'fact_sales' AS table_name,

    COUNT_IF(dc.customer_sk IS NULL) AS missing_customer,
    COUNT_IF(dp.product_sk IS NULL) AS missing_product,
    COUNT_IF(ds.seller_sk IS NULL) AS missing_seller,
    COUNT_IF(dd.date_key IS NULL) AS missing_purchase_date

FROM olist_dw.dw.fact_sales f

LEFT JOIN olist_dw.dw.dim_customer dc
    ON f.customer_sk = dc.customer_sk

LEFT JOIN olist_dw.dw.dim_product dp
    ON f.product_sk = dp.product_sk

LEFT JOIN olist_dw.dw.dim_seller ds
    ON f.seller_sk = ds.seller_sk

LEFT JOIN olist_dw.dw.dim_date dd
    ON f.date_key = dd.date_key;


-- ============================================================
-- 2. FACT PAYMENTS
-- Expected dimensions:
-- customer and purchase date
-- ============================================================

SELECT
    'fact_payments' AS table_name,

    COUNT_IF(dc.customer_sk IS NULL) AS missing_customer,
    COUNT_IF(dd.date_key IS NULL) AS missing_purchase_date

FROM olist_dw.dw.fact_payments f

LEFT JOIN olist_dw.dw.dim_customer dc
    ON f.customer_sk = dc.customer_sk

LEFT JOIN olist_dw.dw.dim_date dd
    ON f.date_key = dd.date_key;


-- ============================================================
-- 3. FACT DELIVERY METRICS
-- Expected dimensions:
-- customer, purchase date and delivery date
--
-- Delivery date is optional for orders not delivered.
-- ============================================================

SELECT
    'fact_delivery_metrics' AS table_name,

    COUNT_IF(dc.customer_sk IS NULL) AS missing_customer,
    COUNT_IF(purchase_date.date_key IS NULL)
        AS missing_purchase_date,

    COUNT_IF(
        f.delivery_date_key IS NOT NULL
        AND delivery_date.date_key IS NULL
    ) AS invalid_delivery_date

FROM olist_dw.dw.fact_delivery_metrics f

LEFT JOIN olist_dw.dw.dim_customer dc
    ON f.customer_sk = dc.customer_sk

LEFT JOIN olist_dw.dw.dim_date purchase_date
    ON f.purchase_date_key = purchase_date.date_key

LEFT JOIN olist_dw.dw.dim_date delivery_date
    ON f.delivery_date_key = delivery_date.date_key;
