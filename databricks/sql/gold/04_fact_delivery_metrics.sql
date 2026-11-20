
-- ============================================================
-- OLIST DATA PLATFORM
-- GOLD LAYER - FACT DELIVERY METRICS
-- Catalog: olist_dw
-- Schema: dw
--
-- Grain: one row per order
-- Business key: order_id
-- ============================================================

CREATE OR REPLACE TABLE olist_dw.dw.fact_delivery_metrics AS

SELECT
    ROW_NUMBER() OVER (
        ORDER BY o.order_id
    ) AS delivery_sk,

    dc.customer_sk,

    CAST(
        DATE_FORMAT(o.order_purchase_timestamp, 'yyyyMMdd')
        AS INT
    ) AS purchase_date_key,

    CAST(
        DATE_FORMAT(o.order_delivered_customer_date, 'yyyyMMdd')
        AS INT
    ) AS delivery_date_key,

    o.order_id,
    o.order_status,

    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,

    DATEDIFF(
        o.order_approved_at,
        o.order_purchase_timestamp
    ) AS days_to_approval,

    DATEDIFF(
        o.order_delivered_carrier_date,
        o.order_approved_at
    ) AS days_to_carrier,

    DATEDIFF(
        o.order_delivered_customer_date,
        o.order_delivered_carrier_date
    ) AS days_in_transit,

    DATEDIFF(
        o.order_delivered_customer_date,
        o.order_purchase_timestamp
    ) AS total_delivery_days,

    DATEDIFF(
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date
    ) AS delivery_delay_days,

    CASE
        WHEN o.order_status = 'canceled'
            THEN 'canceled'

        WHEN o.order_status = 'delivered'
             AND o.order_delivered_customer_date IS NULL
            THEN 'delivery_data_inconsistent'

        WHEN o.order_status = 'delivered'
             AND o.order_delivered_customer_date >
                 o.order_estimated_delivery_date
            THEN 'delivered_delayed'

        WHEN o.order_status = 'delivered'
             AND o.order_delivered_customer_date <=
                 o.order_estimated_delivery_date
            THEN 'delivered_on_time'

        ELSE 'not_delivered'
    END AS delivery_status

FROM olist_dw.dw.orders o

LEFT JOIN olist_dw.dw.dim_customer dc
    ON o.customer_id = dc.customer_id;
