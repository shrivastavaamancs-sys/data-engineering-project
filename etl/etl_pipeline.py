import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
import time
import logging
import sys


# ==========================================
# 1. Project Paths
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "amazon_sales_cleaned.csv"
)
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)

LOG_FILE = LOG_DIR / "etl_pipeline.log"


# ==========================================
# 2. Logging
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_FILE,
            encoding="utf-8"
        ),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


# ==========================================
# 3. PostgreSQL Configuration
# ==========================================

DB_CONFIG = {
    "host": "localhost",
    "database": "amazon_sales_db",
    "user": "postgres",
    "password": "Anshul@789",
    "port": 5432
}


# ==========================================
# 4. ETL Pipeline
# ==========================================

def run_etl():

    start_time = time.time()

    conn = None
    cursor = None

    logger.info("==========================================")
    logger.info("AMAZON SALES INCREMENTAL ETL V4 STARTED")
    logger.info("==========================================")


    try:

        # ======================================
        # EXTRACT
        # ======================================

        logger.info("Reading CSV file...")

        df = pd.read_csv(INPUT_FILE)

        logger.info(
            f"Rows extracted: {len(df)}"
        )


        # ======================================
        # TRANSFORM
        # ======================================

        logger.info("Starting transformation...")


        df = df[
            [
                "order_id",
                "date",
                "status",
                "fulfilment",
                "sales_channel",
                "sku",
                "category",
                "qty",
                "revenue"
            ]
        ].copy()


        df.rename(
            columns={
                "date": "order_date",
                "revenue": "amount"
            },
            inplace=True
        )


        df["order_date"] = pd.to_datetime(
            df["order_date"],
            errors="coerce"
        ).dt.date


        df["qty"] = pd.to_numeric(
            df["qty"],
            errors="coerce"
        )


        df["amount"] = pd.to_numeric(
            df["amount"],
            errors="coerce"
        )


        # ======================================
        # VALIDATION
        # ======================================

        logger.info("Starting data validation...")


        rows_before = len(df)


        df.dropna(
            subset=[
                "order_id",
                "order_date"
            ],
            inplace=True
        )


        df["qty"] = (
            df["qty"]
            .fillna(0)
            .astype(int)
        )


        df["amount"] = (
            df["amount"]
            .fillna(0)
        )


        df.drop_duplicates(
            subset=[
                "order_id",
                "sku"
            ],
            inplace=True
        )


        logger.info(
            f"Rows before cleaning: {rows_before}"
        )

        logger.info(
            f"Rows after cleaning: {len(df)}"
        )


        # ======================================
        # DATABASE CONNECTION
        # ======================================

        logger.info(
            "Connecting to PostgreSQL..."
        )


        conn = psycopg2.connect(
            **DB_CONFIG
        )

        cursor = conn.cursor()


        logger.info(
            "PostgreSQL connection successful"
        )


        # ======================================
        # GET EXISTING KEYS
        # ======================================

        logger.info(
            "Checking existing records..."
        )


        cursor.execute(
            """
            SELECT order_id, sku
            FROM amazon_sales_etl
            """
        )


        existing_keys = set(
            cursor.fetchall()
        )


        logger.info(
            f"Existing records in database: "
            f"{len(existing_keys)}"
        )


        # ======================================
        # FIND NEW RECORDS
        # ======================================

        df["record_key"] = list(
            zip(
                df["order_id"],
                df["sku"]
            )
        )


        new_df = df[
            ~df["record_key"].isin(
                existing_keys
            )
        ].copy()


        new_df.drop(
            columns=["record_key"],
            inplace=True
        )


        logger.info(
            f"New records detected: "
            f"{len(new_df)}"
        )


        # ======================================
        # INCREMENTAL LOAD
        # ======================================

        if len(new_df) > 0:

            logger.info(
                "Starting incremental batch load..."
            )


            insert_query = """
            INSERT INTO amazon_sales_etl
            (
                order_id,
                order_date,
                status,
                fulfilment,
                sales_channel,
                sku,
                category,
                qty,
                amount
            )
            VALUES %s
            """


            records = list(
                new_df.itertuples(
                    index=False,
                    name=None
                )
            )


            execute_values(
                cursor,
                insert_query,
                records,
                page_size=5000
            )


            conn.commit()


            logger.info(
                f"New records loaded: "
                f"{len(records)}"
            )

        else:

            logger.info(
                "No new records found."
            )


        # ======================================
        # SUMMARY
        # ======================================

        execution_time = (
            time.time() - start_time
        )


        logger.info(
            f"ETL execution time: "
            f"{execution_time:.2f} seconds"
        )


        logger.info(
            "INCREMENTAL ETL COMPLETED SUCCESSFULLY"
        )


    except Exception as e:

        logger.error(
            f"ETL PIPELINE FAILED: {e}",
            exc_info=True
        )


        if conn:
            conn.rollback()


        raise


    finally:

        if cursor:
            cursor.close()


        if conn:
            conn.close()


        logger.info(
            "PostgreSQL connection closed"
        )


# ==========================================
# Run ETL
# ==========================================

if __name__ == "__main__":

    run_etl()