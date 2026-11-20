import logging

from ingestion.extract import extract_dataset
from bronze.load import load_bronze
from silver.transform import run_silver
from gold.delivery_metrics import build_delivery_metrics


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def main():

    logging.info("Iniciando pipeline Olist")

    # Etapa 1 - RAW
    extract_dataset()

    # Etapa 2 - BRONZE
    load_bronze()

    # Etapa 3 - SILVER
    run_silver()

    # Etapa 4 - GOLD
    logging.info("Iniciando camada Gold")

    df_gold = build_delivery_metrics()

    logging.info(
        "Camada Gold finalizada: %s registros",
        df_gold.count()
    )

    logging.info("Pipeline finalizado com sucesso!")


if __name__ == "__main__":
    main()