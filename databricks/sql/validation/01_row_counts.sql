
-- ============================================================
-- OLIST DATA PLATFORM
-- DATA QUALITY - ROW COUNT VALIDATION
-- Catalog: olist_dw
-- Schema: dw
--
-- Purpose:
-- Validate the number of records in Gold tables.
-- ============================================================

SELECT 'dim_customer' AS table_name,
       COUNT(*) AS total_records
FROM olist_dw.dw.dim_customer

UNION ALL

SELECT 'dim_product',
       COUNT(*)
FROM olist_dw.dw.dim_product

UNION ALL

SELECT 'dim_seller',
       COUNT(*)
FROM olist_dw.dw.dim_seller

UNION ALL

SELECT 'dim_location',
       COUNT(*)
FROM olist_dw.dw.dim_location

UNION ALL

SELECT 'dim_date',
       COUNT(*)
FROM olist_dw.dw.dim_date

UNION ALL

SELECT 'fact_sales',
       COUNT(*)
FROM olist_dw.dw.fact_sales

UNION ALL

SELECT 'fact_payments',
       COUNT(*)
FROM olist_dw.dw.fact_payments

UNION ALL

SELECT 'fact_delivery_metrics',
       COUNT(*)
FROM olist_dw.dw.fact_delivery_metrics

ORDER BY table_name;
