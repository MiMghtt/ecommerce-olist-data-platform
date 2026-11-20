
-- ============================================================
-- OLIST DATA PLATFORM
-- GOLD LAYER - DIMENSION TABLES
-- Catalog: olist_dw
-- Schema: dw
-- ============================================================

USE CATALOG olist_dw;
USE SCHEMA dw;


-- ============================================================
-- 1. DIM_CUSTOMER
-- Grain: one row per customer_id
-- ============================================================

CREATE OR REPLACE TABLE olist_dw.dw.dim_customer AS
SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id) AS customer_sk,
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM olist_dw.dw.customers;


-- ============================================================
-- 2. DIM_PRODUCT
-- Grain: one row per product_id
-- ============================================================

CREATE OR REPLACE TABLE olist_dw.dw.dim_product AS
SELECT
    ROW_NUMBER() OVER (ORDER BY product_id) AS product_sk,
    product_id,
    product_category_name,
    product_category_name_english,
    product_name_lenght,
    product_description_lenght,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm
FROM olist_dw.dw.products;


-- ============================================================
-- 3. DIM_SELLER
-- Grain: one row per seller_id
-- ============================================================

CREATE OR REPLACE TABLE olist_dw.dw.dim_seller AS
SELECT
    ROW_NUMBER() OVER (ORDER BY seller_id) AS seller_sk,
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM olist_dw.dw.sellers;


-- ============================================================
-- 4. DIM_LOCATION
-- Grain: one row per ZIP code prefix
--
-- Coordinates: average latitude and longitude.
-- City/state: most frequent combination.
-- ============================================================

CREATE OR REPLACE TABLE olist_dw.dw.dim_location AS

WITH coordinates AS (
    SELECT
        geolocation_zip_code_prefix AS zip_code_prefix,
        AVG(geolocation_lat) AS latitude,
        AVG(geolocation_lng) AS longitude,
        COUNT(*) AS geolocation_count
    FROM olist_dw.dw.geolocation
    GROUP BY geolocation_zip_code_prefix
),

city_state_frequency AS (
    SELECT
        geolocation_zip_code_prefix AS zip_code_prefix,
        geolocation_city AS city,
        geolocation_state AS state,
        COUNT(*) AS frequency
    FROM olist_dw.dw.geolocation
    GROUP BY
        geolocation_zip_code_prefix,
        geolocation_city,
        geolocation_state
),

ranked_city_state AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY zip_code_prefix
            ORDER BY frequency DESC, city ASC, state ASC
        ) AS rn
    FROM city_state_frequency
)

SELECT
    ROW_NUMBER() OVER (ORDER BY c.zip_code_prefix) AS location_sk,
    c.zip_code_prefix,
    cs.city,
    cs.state,
    c.latitude,
    c.longitude,
    c.geolocation_count
FROM coordinates c
LEFT JOIN ranked_city_state cs
    ON c.zip_code_prefix = cs.zip_code_prefix
    AND cs.rn = 1;


-- ============================================================
-- 5. CUSTOMER LOCATION REFERENCE
-- ============================================================

ALTER TABLE olist_dw.dw.dim_customer
ADD COLUMNS (location_sk BIGINT);

MERGE INTO olist_dw.dw.dim_customer c
USING olist_dw.dw.dim_location l
ON c.customer_zip_code_prefix = l.zip_code_prefix
WHEN MATCHED THEN
    UPDATE SET c.location_sk = l.location_sk;


-- ============================================================
-- 6. SELLER LOCATION REFERENCE
-- ============================================================

ALTER TABLE olist_dw.dw.dim_seller
ADD COLUMNS (location_sk BIGINT);

MERGE INTO olist_dw.dw.dim_seller s
USING olist_dw.dw.dim_location l
ON s.seller_zip_code_prefix = l.zip_code_prefix
WHEN MATCHED THEN
    UPDATE SET s.location_sk = l.location_sk;


-- ============================================================
-- 7. DIM_DATE
-- Grain: one row per calendar date
-- ============================================================

CREATE OR REPLACE TABLE olist_dw.dw.dim_date AS

WITH date_bounds AS (
    SELECT
        LEAST(
            MIN(TO_DATE(order_purchase_timestamp)),
            MIN(TO_DATE(order_approved_at)),
            MIN(TO_DATE(order_delivered_carrier_date)),
            MIN(TO_DATE(order_delivered_customer_date)),
            MIN(TO_DATE(order_estimated_delivery_date))
        ) AS min_date,

        GREATEST(
            MAX(TO_DATE(order_purchase_timestamp)),
            MAX(TO_DATE(order_approved_at)),
            MAX(TO_DATE(order_delivered_carrier_date)),
            MAX(TO_DATE(order_delivered_customer_date)),
            MAX(TO_DATE(order_estimated_delivery_date))
        ) AS max_date

    FROM olist_dw.dw.orders
),

calendar AS (
    SELECT
        EXPLODE(
            SEQUENCE(min_date, max_date, INTERVAL 1 DAY)
        ) AS full_date
    FROM date_bounds
)

SELECT
    CAST(DATE_FORMAT(full_date, 'yyyyMMdd') AS INT) AS date_key,
    full_date,
    YEAR(full_date) AS year,
    QUARTER(full_date) AS quarter,
    MONTH(full_date) AS month,
    DATE_FORMAT(full_date, 'MMMM') AS month_name,
    WEEKOFYEAR(full_date) AS week_of_year,
    DAY(full_date) AS day,
    DAYOFWEEK(full_date) AS day_of_week,
    DATE_FORMAT(full_date, 'EEEE') AS day_name,

    CASE
        WHEN DAYOFWEEK(full_date) IN (1, 7) THEN TRUE
        ELSE FALSE
    END AS is_weekend,

    DATE_FORMAT(full_date, 'yyyy-MM') AS year_month

FROM calendar;
