
from pyspark.sql import SparkSession


def get_spark_session() -> SparkSession:
    """
    Cria ou reutiliza uma sessão Spark local.
    """

    return (
        SparkSession.builder
        .master("local[*]")
        .appName("olist-data-engineering")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )
