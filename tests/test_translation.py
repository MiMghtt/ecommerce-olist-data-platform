
import pytest

import silver.transform as transform

from spark.session import get_spark_session
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType
)


@pytest.fixture(scope="module")
def spark():
    session = get_spark_session()
    yield session
    session.stop()


def test_product_category_translations(
    spark,
    tmp_path,
    monkeypatch
):

    # Criar estrutura temporária de arquivos.
    silver_dir = tmp_path / "silver"

    products_dir = silver_dir / "olist_products_dataset"
    translations_dir = (
        silver_dir / "product_category_name_translation"
    )

    products_dir.mkdir(parents=True)
    translations_dir.mkdir(parents=True)

    products_file = (
        products_dir / "olist_products_dataset.parquet"
    )

    translations_file = (
        translations_dir
        / "product_category_name_translation.parquet"
    )

    # Produtos para o teste.
    products_schema = StructType([
        StructField("product_id", StringType(), True),
        StructField("product_category_name", StringType(), True)
    ])

    products = spark.createDataFrame(
        [
            ("P1", "beleza_saude"),
            ("P2", "pc_gamer"),
            (
                "P3",
                "portateis_cozinha_e_preparadores_de_alimentos"
            ),
            ("P4", None)
        ],
        schema=products_schema
    )

    # Traduções originais.
    translations_schema = StructType([
        StructField("product_category_name", StringType(), True),
        StructField(
            "product_category_name_english",
            StringType(),
            True
        )
    ])

    translations = spark.createDataFrame(
        [
            ("beleza_saude", "health_beauty")
        ],
        schema=translations_schema
    )

    products.write.mode("overwrite").parquet(
        str(products_file)
    )

    translations.write.mode("overwrite").parquet(
        str(translations_file)
    )

    # Redirecionar a função para os diretórios temporários.
    monkeypatch.setattr(
        transform,
        "SILVER_DIR",
        silver_dir
    )

    # Capturar o relatório de qualidade sem gravar no projeto real.
    reports = {}

    def capture_quality_report(report, table_name):
        reports[table_name] = report

    monkeypatch.setattr(
        transform,
        "save_quality_report",
        capture_quality_report
    )

    # Executar a função real.
    transform.translate_product_categories()

    # Ler os produtos enriquecidos.
    result = spark.read.parquet(str(products_file))

    # Verificar tradução original.
    assert (
        result.filter(F.col("product_id") == "P1")
        .first()["product_category_name_english"]
        == "health_beauty"
    )

    # Verificar tradução complementar pc_gamer.
    assert (
        result.filter(F.col("product_id") == "P2")
        .first()["product_category_name_english"]
        == "pc_gamer"
    )

    # Verificar tradução complementar de cozinha.
    assert (
        result.filter(F.col("product_id") == "P3")
        .first()["product_category_name_english"]
        == "kitchen_and_food_preparers"
    )

    # Verificar preservação da categoria original.
    assert (
        result.filter(F.col("product_id") == "P1")
        .first()["product_category_name"]
        == "beleza_saude"
    )

    # Verificar preservação de categoria originalmente nula.
    product_p4 = result.filter(
        F.col("product_id") == "P4"
    ).first()

    assert product_p4["product_category_name"] is None

    assert (
        product_p4["product_category_name_english"]
        is None
    )

    # Verificar relatório de qualidade.
    report = reports["product_category_translation"]

    assert report["categories_without_translation"] == 0
    assert report["distinct_categories_without_translation"] == 0
    assert report["null_original_categories"] == 1
    assert report["manual_translations_added"] == 2
