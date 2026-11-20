
import pytest

from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    TimestampType,
    DoubleType,
    LongType
)

from spark.session import get_spark_session

from silver.transform import (
    convert_datatypes,
    remove_duplicates
)

from silver.quality import calculate_nulls


@pytest.fixture(scope="module")
def spark():
    session = get_spark_session()
    yield session
    session.stop()


def test_convert_datetime_and_count_invalid_values(spark):
    df = spark.createDataFrame(
        [
            ("2018-01-01 10:00:00",),
            ("data_invalida",),
            (None,)
        ],
        ["order_purchase_timestamp"]
    )

    report = {}

    result = convert_datatypes(
        df,
        "olist_orders_dataset",
        report
    )

    assert isinstance(
        result.schema["order_purchase_timestamp"].dataType,
        TimestampType
    )

    rows = result.collect()

    assert rows[1]["order_purchase_timestamp"] is None

    assert report["invalid_conversions"][
        "order_purchase_timestamp"
    ] == 1


def test_convert_numeric_and_count_invalid_values(spark):
    df = spark.createDataFrame(
        [
            ("100.50",),
            ("valor_invalido",),
            ("50.00",)
        ],
        ["price"]
    )

    report = {}

    result = convert_datatypes(
        df,
        "olist_order_items_dataset",
        report
    )

    assert isinstance(
        result.schema["price"].dataType,
        DoubleType
    )

    rows = result.collect()

    assert rows[0]["price"] == 100.50

    assert rows[1]["price"] is None

    assert report["invalid_conversions"]["price"] == 1


def test_convert_integer_and_count_invalid_values(spark):
    df = spark.createDataFrame(
        [
            ("1",),
            ("2.5",),
            ("invalido",),
            (None,)
        ],
        ["payment_sequential"]
    )

    report = {}

    result = convert_datatypes(
        df,
        "olist_order_payments_dataset",
        report
    )

    assert isinstance(
        result.schema["payment_sequential"].dataType,
        LongType
    )

    rows = result.collect()

    assert rows[0]["payment_sequential"] == 1

    assert rows[1]["payment_sequential"] is None

    assert rows[2]["payment_sequential"] is None

    assert report["invalid_conversions"][
        "payment_sequential"
    ] == 2


def test_remove_duplicates_and_preserve_incomplete_keys(spark):
    df = spark.createDataFrame(
        [
            ("A", "C1"),
            ("A", "C1"),
            (None, "C2"),
            (None, "C3")
        ],
        ["order_id", "customer_id"]
    )

    report = {}

    result = remove_duplicates(
        df,
        "olist_orders_dataset",
        report
    )

    assert result.count() == 3

    assert report["duplicates_removed"] == 1

    assert report["incomplete_key_records"] == 2

    assert (
        result.filter(F.col("order_id").isNull()).count()
        == 2
    )


def test_calculate_nulls(spark):
    df = spark.createDataFrame(
        [
            ("A", "C1", "delivered"),
            ("B", None, None),
            ("C", "C3", None)
        ],
        [
            "order_id",
            "customer_id",
            "order_status"
        ]
    )

    result = calculate_nulls(df)

    assert result == {
        "customer_id": 1,
        "order_status": 2
    }
