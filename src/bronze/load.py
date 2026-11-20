
from pathlib import Path
import json
import logging

from spark.session import get_spark_session


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"

logger = logging.getLogger(__name__)


def load_bronze() -> None:
    spark = get_spark_session()

    BRONZE_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(RAW_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError("Nenhum CSV encontrado na RAW.")

    manifest = {}

    for file in csv_files:
        table_name = file.stem

        logger.info("Lendo arquivo: %s", file.name)

        df = (
            spark.read
            .option("header", "true")
            .option("encoding", "UTF-8")
            .option("inferSchema", "false")
            .csv(str(file))
        )

        output_dir = BRONZE_DIR / table_name
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{table_name}.parquet"

        (
            df.write
            .mode("overwrite")
            .parquet(str(output_file))
        )

        row_count = df.count()

        manifest[table_name] = {
            "source": file.name,
            "rows": row_count,
            "columns": len(df.columns),
            "output": str(output_file.relative_to(PROJECT_ROOT))
        }

        logger.info(
            "Tabela %s carregada: %s registros",
            table_name,
            row_count
        )

    manifest_file = BRONZE_DIR / "manifest.json"

    with manifest_file.open("w", encoding="utf-8") as file:
        json.dump(
            manifest,
            file,
            indent=4,
            ensure_ascii=False
        )

    logger.info("Carga Bronze finalizada.")
