
-- ============================================================
-- OLIST DATA PLATFORM
-- GOLD LAYER - FACT SALES
-- Catalog: olist_dw
-- Schema: dw
--
-- Grain: one row per order item
-- Business key: order_id + order_item_id
-- ============================================================

CREATE OR REPLACE TABLE olist_dw.dw.fact_sales AS

SELECT
    ROW_NUMBER() OVER (
        ORDER BY oi.order_id, oi.order_item_id
    ) AS sales_item_sk,

    dc.customer_sk,
    dp.product_sk,
    ds.seller_sk,

    CAST(
        DATE_FORMAT(o.order_purchase_timestamp, 'yyyyMMdd')
        AS INT
    ) AS date_key,

    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,

    o.order_status,
    o.order_purchase_timestamp,
    oi.shipping_limit_date,

    oi.price,
    oi.freight_value,

    oi.price + oi.freight_value AS total_item_value

FROM olist_dw.dw.order_items oi

INNER JOIN olist_dw.dw.orders o
    ON oi.order_id = o.order_id

LEFT JOIN olist_dw.dw.dim_customer dc
    ON o.customer_id = dc.customer_id

LEFT JOIN olist_dw.dw.dim_product dp
    ON oi.product_id = dp.product_id

LEFT JOIN olist_dw.dw.dim_seller ds
    ON oi.seller_id = ds.seller_id;
