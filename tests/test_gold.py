
import pytest
from datetime import datetime

from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    TimestampType
)

import gold.delivery_metrics as delivery_metrics

from spark.session import get_spark_session


@pytest.fixture(scope="module")
def spark():
    session = get_spark_session()
    yield session
    session.stop()


@pytest.fixture
def gold_result(spark, tmp_path, monkeypatch):
    # Diretórios temporários para não alterar os dados reais do projeto.
    silver_dir = tmp_path / "silver"
    gold_dir = tmp_path / "gold"

    orders_dir = silver_dir / "olist_orders_dataset"
    orders_dir.mkdir(parents=True)

    # Massa de dados controlada para os testes.
    schema = StructType([
        StructField("order_id", StringType(), True),
        StructField("customer_id", StringType(), True),
        StructField("order_status", StringType(), True),
        StructField(
            "order_purchase_timestamp",
            TimestampType(),
            True
        ),
        StructField(
            "order_delivered_customer_date",
            TimestampType(),
            True
        ),
        StructField(
            "order_estimated_delivery_date",
            TimestampType(),
            True
        )
    ])

    orders = spark.createDataFrame(
        [
            (
                "order_on_time",
                "customer_1",
                "delivered",
                datetime(2018, 1, 1, 0, 0, 0),
                datetime(2018, 1, 3, 0, 0, 0),
                datetime(2018, 1, 4, 0, 0, 0)
            ),
            (
                "order_delayed",
                "customer_2",
                "delivered",
                datetime(2018, 1, 1),
                datetime(2018, 1, 5),
                datetime(2018, 1, 4)
            ),
            (
                "order_inconsistent",
                "customer_3",
                "delivered",
                datetime(2018, 1, 1),
                None,
                datetime(2018, 1, 4)
            ),
            (
                "order_not_delivered",
                "customer_4",
                "shipped",
                datetime(2018, 1, 1),
                None,
                datetime(2018, 1, 4)
            )
        ],
        schema=schema
    )

    input_file = (
        orders_dir / "olist_orders_dataset.parquet"
    )

    orders.write.mode("overwrite").parquet(str(input_file))

    # Redireciona os diretórios da função para os temporários.
    monkeypatch.setattr(
        delivery_metrics,
        "SILVER_DIR",
        silver_dir
    )

    monkeypatch.setattr(
        delivery_metrics,
        "GOLD_DIR",
        gold_dir
    )

    result = delivery_metrics.build_delivery_metrics()

    return result, gold_dir


def test_delivery_metrics_calculations(gold_result):
    df, _ = gold_result

    on_time = df.filter(
        F.col("order_id") == "order_on_time"
    ).first()

    delayed = df.filter(
        F.col("order_id") == "order_delayed"
    ).first()

    assert on_time["delivery_days"] == 2
    assert on_time["estimated_delivery_days"] == 3
    assert on_time["delivery_variance_days"] == -1
    assert on_time["delay_days"] == 0

    assert delayed["delivery_days"] == 4
    assert delayed["estimated_delivery_days"] == 3
    assert delayed["delivery_variance_days"] == 1
    assert delayed["delay_days"] == 1


def test_delivery_performance_classification(gold_result):
    df, _ = gold_result

    classifications = {
        row["order_id"]: row["delivery_performance"]
        for row in df.select(
            "order_id",
            "delivery_performance"
        ).collect()
    }

    assert classifications["order_on_time"] == "on_time_or_early"

    assert classifications["order_delayed"] == "delayed"

    assert (
        classifications["order_inconsistent"]
        == "inconsistent_delivery_data"
    )

    assert (
        classifications["order_not_delivered"]
        == "not_delivered"
    )


def test_inconsistent_delivered_order_keeps_metrics_null(gold_result):
    df, _ = gold_result

    order = df.filter(
        F.col("order_id") == "order_inconsistent"
    ).first()

    assert order["delivery_days"] is None
    assert order["delivery_variance_days"] is None
    assert order["delay_days"] is None
    assert order["is_delivered_on_time"] is None

    assert (
        order["delivery_performance"]
        == "inconsistent_delivery_data"
    )


def test_gold_parquet_is_persisted(gold_result, spark):
    df, gold_dir = gold_result

    output_file = (
        gold_dir
        / "fact_delivery_metrics"
        / "fact_delivery_metrics.parquet"
    )

    assert output_file.exists()

    saved_df = spark.read.parquet(str(output_file))

    assert saved_df.count() == df.count()

    assert (
        saved_df.select("order_id").distinct().count()
        == saved_df.count()
    )
