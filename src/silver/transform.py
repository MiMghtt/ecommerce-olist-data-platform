
from pathlib import Path
import logging

from pyspark.sql import Window
from pyspark.sql import functions as F

from spark.session import get_spark_session
from silver.quality import (
    save_quality_report,
    calculate_nulls
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"
SILVER_DIR = PROJECT_ROOT / "data" / "silver"

logger = logging.getLogger(__name__)


# Regras de unicidade
UNIQUE_KEYS = {
    "olist_customers_dataset": ["customer_id"],
    "olist_orders_dataset": ["order_id"],
    "olist_order_items_dataset": [
        "order_id",
        "order_item_id"
    ],
    "olist_order_payments_dataset": [
        "order_id",
        "payment_sequential"
    ],
    "olist_order_reviews_dataset": [
        "review_id",
        "order_id"
    ],
    "olist_products_dataset": ["product_id"],
    "olist_sellers_dataset": ["seller_id"],
    "product_category_name_translation": [
        "product_category_name"
    ]
}


# Colunas de data
DATETIME_COLUMNS = {
    "olist_orders_dataset": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ],
    "olist_order_items_dataset": [
        "shipping_limit_date"
    ],
    "olist_order_reviews_dataset": [
        "review_creation_date",
        "review_answer_timestamp"
    ]
}


# Colunas numéricas
NUMERIC_COLUMNS = {
    "olist_order_items_dataset": [
        "price",
        "freight_value"
    ],
    "olist_order_payments_dataset": [
        "payment_value"
    ],
    "olist_products_dataset": [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ],
    "olist_geolocation_dataset": [
        "geolocation_lat",
        "geolocation_lng"
    ]
}


# Colunas inteiras
INTEGER_COLUMNS = {
    "olist_order_payments_dataset": [
        "payment_sequential",
        "payment_installments"
    ],
    "olist_order_reviews_dataset": [
        "review_score"
    ]
}


def _count_conditions(df, conditions):
    """
    Calcula a quantidade de registros que atendem
    a cada condição, em uma única agregação Spark.
    """
    if not conditions:
        return {}

    aggregations = [
        F.sum(
            F.when(condition, 1).otherwise(0)
        ).alias(name)
        for name, condition in conditions.items()
    ]

    result = df.agg(*aggregations).first().asDict()

    return {
        name: int(count or 0)
        for name, count in result.items()
    }



def convert_datatypes(df, table_name, report):
    invalid_values = {}

    # Conversão de datas
    for column in DATETIME_COLUMNS.get(table_name, []):
        if column in df.columns:
            original = F.col(column)
            converted = F.try_to_timestamp(original)

            invalid = (
                original.isNotNull()
                & converted.isNull()
            )

            invalid_values[column] = (
                df.filter(invalid).count()
            )

            df = df.withColumn(column, converted)

    # Conversão de números
    for column in NUMERIC_COLUMNS.get(table_name, []):
        if column in df.columns:
            original = F.col(column)
            converted = F.expr(
                f"try_cast(`{column}` AS DOUBLE)"
            )

            invalid = (
                original.isNotNull()
                & converted.isNull()
            )

            invalid_values[column] = (
                df.filter(invalid).count()
            )

            df = df.withColumn(column, converted)

    # Conversão de inteiros
    for column in INTEGER_COLUMNS.get(table_name, []):
        if column in df.columns:
            original = F.col(column)

            converted = F.expr(
                f"try_cast(`{column}` AS DOUBLE)"
            )

            invalid = (
                original.isNotNull()
                & (
                    converted.isNull()
                    | (converted % 1 != 0)
                )
            )

            invalid_values[column] = (
                df.filter(invalid).count()
            )

            df = df.withColumn(
                column,
                F.when(
                    converted.isNotNull()
                    & (converted % 1 == 0),
                    converted.cast("long")
                ).otherwise(
                    F.lit(None).cast("long")
                )
            )

    report["invalid_conversions"] = invalid_values

    return df


def remove_duplicates(df, table_name, report):
    keys = UNIQUE_KEYS.get(table_name)

    if not keys:
        report["duplicates_removed"] = 0
        return df

    # Não remover registros cuja chave está incompleta.
    # Eles serão contabilizados como problemas de qualidade.
    complete_key = F.lit(True)

    for column in keys:
        complete_key = complete_key & F.col(column).isNotNull()

    valid_records = df.filter(complete_key)
    incomplete_records = df.filter(~complete_key)

    # Ordenação determinística para selecionar um registro
    # por chave. Não representa necessariamente a ordem
    # original do CSV.
    ordering_columns = [
        F.col(column).asc_nulls_first()
        for column in df.columns
        if column not in keys
    ]

    if not ordering_columns:
        ordering_columns = [F.lit(1)]

    window = (
        Window
        .partitionBy(*keys)
        .orderBy(*ordering_columns)
    )

    valid_records = (
        valid_records
        .withColumn(
            "_duplicate_row",
            F.row_number().over(window)
        )
    )

    duplicate_count = valid_records.filter(
        F.col("_duplicate_row") > 1
    ).count()

    valid_records = (
        valid_records
        .filter(F.col("_duplicate_row") == 1)
        .drop("_duplicate_row")
    )

    df = valid_records.unionByName(incomplete_records)

    report["duplicates_removed"] = duplicate_count
    report["incomplete_key_records"] = incomplete_records.count()

    return df


def transform_table(table_name):
    spark = get_spark_session()

    input_file = (
        BRONZE_DIR
        / table_name
        / f"{table_name}.parquet"
    )

    if not input_file.exists():
        raise FileNotFoundError(input_file)

    logger.info("Transformando tabela: %s", table_name)

    df = spark.read.parquet(str(input_file))

    records_before = df.count()

    report = {
        "table": table_name,
        "records_before": records_before,
        "nulls_before": calculate_nulls(df)
    }

    # Conversão de tipos
    df = convert_datatypes(
        df,
        table_name,
        report
    )

    # Remoção de duplicidades
    df = remove_duplicates(
        df,
        table_name,
        report
    )

    report["records_after"] = df.count()
    report["nulls_after"] = calculate_nulls(df)

    # Persistência
    output_dir = SILVER_DIR / table_name
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{table_name}.parquet"

    (
        df.write
        .mode("overwrite")
        .parquet(str(output_file))
    )

    save_quality_report(report, table_name)

    logger.info(
        "%s finalizada: %s registros",
        table_name,
        report["records_after"]
    )

    return df


def translate_product_categories():
    spark = get_spark_session()

    products_file = (
        SILVER_DIR
        / "olist_products_dataset"
        / "olist_products_dataset.parquet"
    )

    translation_file = (
        SILVER_DIR
        / "product_category_name_translation"
        / "product_category_name_translation.parquet"
    )

    products = spark.read.parquet(str(products_file))
    translations = spark.read.parquet(str(translation_file))

    # Evitar duplicação da coluna em reexecuções.
    if "product_category_name_english" in products.columns:
        products = products.drop("product_category_name_english")

    # Traduções complementares
    manual_translations = spark.createDataFrame([
        (
            "pc_gamer",
            "pc_gamer"
        ),
        (
            "portateis_cozinha_e_preparadores_de_alimentos",
            "kitchen_and_food_preparers"
        )
    ], [
        "product_category_name",
        "product_category_name_english"
    ])

    # Combinar traduções originais e complementares
    translations = translations.unionByName(manual_translations)

    # Garantir uma tradução por categoria
    translations = translations.dropDuplicates([
        "product_category_name"
    ])

    # Preservar a categoria original
    products = products.join(
        translations,
        on="product_category_name",
        how="left"
    )

    # Identificar categorias sem tradução
    missing_translation = (
        F.col("product_category_name").isNotNull()
        & F.col("product_category_name_english").isNull()
    )

    report = {
        "table": "products",
        "categories_without_translation": products.filter(
            missing_translation
        ).count(),
        "distinct_categories_without_translation": (
            products
            .filter(missing_translation)
            .select("product_category_name")
            .distinct()
            .count()
        ),
        "null_original_categories": products.filter(
            F.col("product_category_name").isNull()
        ).count(),
        "manual_translations_added": 2
    }

    save_quality_report(
        report,
        "product_category_translation"
    )

    (
        products.write
        .mode("overwrite")
        .parquet(str(products_file))
    )

    logger.info(
        "Categorias sem tradução: %s",
        report["distinct_categories_without_translation"]
    )


def run_silver():
    tables = [
        "olist_customers_dataset",
        "olist_orders_dataset",
        "olist_order_items_dataset",
        "olist_order_payments_dataset",
        "olist_order_reviews_dataset",
        "olist_products_dataset",
        "olist_sellers_dataset",
        "olist_geolocation_dataset",
        "product_category_name_translation"
    ]

    for table in tables:
        transform_table(table)

    translate_product_categories()

    logger.info("Camada Silver finalizada com sucesso.")
