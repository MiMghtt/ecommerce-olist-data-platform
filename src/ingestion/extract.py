
from pathlib import Path
from zipfile import ZipFile
import logging

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_DIR = PROJECT_ROOT / "data" / "source"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

EXPECTED_FILES = {
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
}

logger = logging.getLogger(__name__)


def extract_dataset() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    zip_files = list(SOURCE_DIR.glob("*.zip"))

    if not zip_files:
        raise FileNotFoundError(
            f"Nenhum arquivo ZIP encontrado em {SOURCE_DIR}"
        )

    zip_path = zip_files[0]

    existing_files = {
        file.name for file in RAW_DIR.glob("*.csv")
    }

    if EXPECTED_FILES.issubset(existing_files):
        logger.info("Todos os arquivos RAW já existem.")
        return

    logger.info("Iniciando extração: %s", zip_path.name)

    with ZipFile(zip_path, "r") as archive:
        for member in archive.infolist():
            if Path(member.filename).name in EXPECTED_FILES:
                filename = Path(member.filename).name

                target = RAW_DIR / filename

                with archive.open(member) as source:
                    with target.open("wb") as destination:
                        destination.write(source.read())

    extracted_files = {
        file.name for file in RAW_DIR.glob("*.csv")
    }

    missing_files = EXPECTED_FILES - extracted_files

    if missing_files:
        raise RuntimeError(
            f"Arquivos não encontrados: {missing_files}"
        )

    logger.info("Extração concluída com sucesso.")
