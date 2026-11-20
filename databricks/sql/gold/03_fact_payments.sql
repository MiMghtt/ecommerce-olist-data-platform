
-- ============================================================
-- OLIST DATA PLATFORM
-- GOLD LAYER - FACT PAYMENTS
-- Catalog: olist_dw
-- Schema: dw
--
-- Grain: one row per payment
-- Business key: order_id + payment_sequential
-- ============================================================

CREATE OR REPLACE TABLE olist_dw.dw.fact_payments AS

SELECT
    ROW_NUMBER() OVER (
        ORDER BY op.order_id, op.payment_sequential
    ) AS payment_sk,

    dc.customer_sk,

    CAST(
        DATE_FORMAT(o.order_purchase_timestamp, 'yyyyMMdd')
        AS INT
    ) AS date_key,

    op.order_id,
    op.payment_sequential,
    op.payment_type,
    op.payment_installments,
    op.payment_value,

    o.order_status,
    o.order_purchase_timestamp

FROM olist_dw.dw.order_payments op

INNER JOIN olist_dw.dw.orders o
    ON op.order_id = o.order_id

LEFT JOIN olist_dw.dw.dim_customer dc
    ON o.customer_id = dc.customer_id;
