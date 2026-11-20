
from pathlib import Path
import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from spark.session import get_spark_session


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SILVER_DIR = PROJECT_ROOT / "data" / "silver"
GOLD_DIR = PROJECT_ROOT / "data" / "gold"

logger = logging.getLogger(__name__)


def build_delivery_metrics() -> DataFrame:

    spark = get_spark_session()

    orders_file = (
        SILVER_DIR
        / "olist_orders_dataset"
        / "olist_orders_dataset.parquet"
    )

    orders = spark.read.parquet(str(orders_file))

    # Selecionar somente os campos necessários.
    df = orders.select(
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    )

    # Prazo efetivo entre compra e entrega.
    df = df.withColumn(
        "delivery_days",
        (
            F.unix_micros("order_delivered_customer_date")
            - F.unix_micros("order_purchase_timestamp")
        ) / 86400000000.0
    )

    # Prazo estimado entre compra e entrega prevista.
    df = df.withColumn(
        "estimated_delivery_days",
        (
            F.unix_micros("order_estimated_delivery_date")
            - F.unix_micros("order_purchase_timestamp")
        ) / 86400000000.0
    )

    # Diferença entre entrega real e estimada.
    df = df.withColumn(
        "delivery_variance_days",
        (
            F.unix_micros("order_delivered_customer_date")
            - F.unix_micros("order_estimated_delivery_date")
        ) / 86400000000.0
    )

    # Considerar somente atrasos positivos.
    df = df.withColumn(
        "delay_days",
        F.when(
            F.col("delivery_variance_days").isNull(),
            F.lit(None).cast("double")
        ).otherwise(
            F.greatest(F.col("delivery_variance_days"), F.lit(0.0))
        )
    )

    # Indicador de entrega no prazo.
    delivered = (
        F.col("order_delivered_customer_date").isNotNull()
        & F.col("order_estimated_delivery_date").isNotNull()
    )

    df = df.withColumn(
        "is_delivered_on_time",
        F.when(
            delivered,
            F.col("order_delivered_customer_date")
            <= F.col("order_estimated_delivery_date")
        ).otherwise(
            F.lit(None).cast("boolean")
        )
    )

    # Classificação de entrega.
    df = df.withColumn(
        "delivery_performance",
        F.lit("not_delivered")
    )

    # Pedidos com status delivered, mas sem data efetiva.
    inconsistent_delivery = (
        (F.col("order_status") == "delivered")
        & F.col("order_delivered_customer_date").isNull()
    )

    df = df.withColumn(
        "delivery_performance",
        F.when(
            inconsistent_delivery,
            "inconsistent_delivery_data"
        ).otherwise(F.col("delivery_performance"))
    )

    df = df.withColumn(
        "delivery_performance",
        F.when(
            delivered & (F.col("delivery_variance_days") <= 0),
            "on_time_or_early"
        ).otherwise(F.col("delivery_performance"))
    )

    df = df.withColumn(
        "delivery_performance",
        F.when(
            delivered & (F.col("delivery_variance_days") > 0),
            "delayed"
        ).otherwise(F.col("delivery_performance"))
    )

    # Persistência.
    output_dir = GOLD_DIR / "fact_delivery_metrics"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = (
        output_dir / "fact_delivery_metrics.parquet"
    )

    df.write.mode("overwrite").parquet(str(output_file))

    logger.info(
        "Gold delivery metrics criada: %s registros",
        df.count()
    )

    return df
