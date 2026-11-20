
import json
from pathlib import Path

from pyspark.sql import functions as F


PROJECT_ROOT = Path(__file__).resolve().parents[2]

QUALITY_DIR = PROJECT_ROOT / "data" / "silver" / "quality_reports"


def save_quality_report(report: dict, table_name: str):
    QUALITY_DIR.mkdir(parents=True, exist_ok=True)

    output_file = QUALITY_DIR / f"{table_name}_quality.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )


def calculate_nulls(df):
    null_counts = (
        df.select([
            F.sum(
                F.when(F.col(column).isNull(), 1).otherwise(0)
            ).alias(column)
            for column in df.columns
        ])
        .first()
        .asDict()
    )

    return {
        column: int(count)
        for column, count in null_counts.items()
        if count is not None and count > 0
    }
