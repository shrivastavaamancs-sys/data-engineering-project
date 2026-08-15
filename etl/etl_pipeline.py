import os
import time
import logging
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "extracted"
)

LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(LOG_DIR, exist_ok=True)

DB_CONFIG = {
    "host": "localhost",
    "database": "customer_etl_db",
    "user": "postgres",
    "password": "Anshul@789",
    "port": 5432
}


# ============================================================
# LOGGING
# ============================================================

LOG_FILE = os.path.join(LOG_DIR, "etl_pipeline.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# EXTRACT
# ============================================================

def extract_data():

    logger.info("=" * 50)
    logger.info("CUSTOMER DATA ETL PIPELINE STARTED")
    logger.info("=" * 50)

    logger.info("Reading CSV files...")

    customers = pd.read_csv(
        os.path.join(DATA_DIR, "customers.csv")
    )

    orders = pd.read_csv(
        os.path.join(DATA_DIR, "orders.csv")
    )

    order_items = pd.read_csv(
        os.path.join(DATA_DIR, "order_items.csv")
    )

    products = pd.read_csv(
        os.path.join(DATA_DIR, "products.csv")
    )

    logger.info(
        f"Customers extracted: {len(customers)}"
    )

    logger.info(
        f"Orders extracted: {len(orders)}"
    )

    logger.info(
        f"Order items extracted: {len(order_items)}"
    )

    logger.info(
        f"Products extracted: {len(products)}"
    )

    return customers, orders, order_items, products


# ============================================================
# TRANSFORMATION
# ============================================================

def transform_data(
    customers,
    orders,
    order_items,
    products
):

    logger.info("Starting transformation...")

    # Remove completely empty rows

    customers = customers.dropna(how="all")
    orders = orders.dropna(how="all")
    order_items = order_items.dropna(how="all")
    products = products.dropna(how="all")

    # Convert dates

    customers["signup_date"] = pd.to_datetime(
        customers["signup_date"],
        errors="coerce"
    )

    orders["order_date"] = pd.to_datetime(
        orders["order_date"],
        errors="coerce"
    )

    # Convert numeric columns

    customers["customer_id"] = pd.to_numeric(
        customers["customer_id"],
        errors="coerce"
    )

    orders["order_id"] = pd.to_numeric(
        orders["order_id"],
        errors="coerce"
    )

    orders["customer_id"] = pd.to_numeric(
        orders["customer_id"],
        errors="coerce"
    )

    order_items["order_id"] = pd.to_numeric(
        order_items["order_id"],
        errors="coerce"
    )

    order_items["product_id"] = pd.to_numeric(
        order_items["product_id"],
        errors="coerce"
    )

    order_items["quantity"] = pd.to_numeric(
        order_items["quantity"],
        errors="coerce"
    )

    order_items["price"] = pd.to_numeric(
        order_items["price"],
        errors="coerce"
    )

    products["product_id"] = pd.to_numeric(
        products["product_id"],
        errors="coerce"
    )

    # Remove duplicate records

    customers = customers.drop_duplicates(
        subset=["customer_id"]
    )

    orders = orders.drop_duplicates(
        subset=["order_id"]
    )

    products = products.drop_duplicates(
        subset=["product_id"]
    )

    order_items = order_items.drop_duplicates(
        subset=["order_id", "product_id"]
    )

    # Remove invalid primary keys

    customers = customers.dropna(
        subset=["customer_id"]
    )

    orders = orders.dropna(
        subset=["order_id", "customer_id"]
    )

    products = products.dropna(
        subset=["product_id"]
    )

    order_items = order_items.dropna(
        subset=[
            "order_id",
            "product_id",
            "quantity",
            "price"
        ]
    )

    # Convert IDs to integers

    customers["customer_id"] = customers[
        "customer_id"
    ].astype(int)

    orders["order_id"] = orders[
        "order_id"
    ].astype(int)

    orders["customer_id"] = orders[
        "customer_id"
    ].astype(int)

    products["product_id"] = products[
        "product_id"
    ].astype(int)

    order_items["order_id"] = order_items[
        "order_id"
    ].astype(int)

    order_items["product_id"] = order_items[
        "product_id"
    ].astype(int)

    order_items["quantity"] = order_items[
        "quantity"
    ].astype(int)

    logger.info("Transformation completed.")

    return (
        customers,
        orders,
        order_items,
        products
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_data(
    customers,
    orders,
    order_items,
    products
):

    logger.info("Starting data validation...")

    # Null checks

    logger.info(
        f"Customers rows: {len(customers)}"
    )

    logger.info(
        f"Orders rows: {len(orders)}"
    )

    logger.info(
        f"Order items rows: {len(order_items)}"
    )

    logger.info(
        f"Products rows: {len(products)}"
    )

    # Negative quantity

    negative_qty = (
        order_items["quantity"] < 0
    ).sum()

    if negative_qty > 0:

        logger.warning(
            f"Negative quantity rows: {negative_qty}"
        )

    # Negative price

    negative_price = (
        order_items["price"] < 0
    ).sum()

    if negative_price > 0:

        logger.warning(
            f"Negative price rows: {negative_price}"
        )

    # Foreign key validation

    invalid_customer_ids = (
        ~orders["customer_id"].isin(
            customers["customer_id"]
        )
    ).sum()

    if invalid_customer_ids > 0:

        logger.warning(
            f"Invalid customer references: "
            f"{invalid_customer_ids}"
        )

    invalid_order_ids = (
        ~order_items["order_id"].isin(
            orders["order_id"]
        )
    ).sum()

    if invalid_order_ids > 0:

        logger.warning(
            f"Invalid order references: "
            f"{invalid_order_ids}"
        )

    invalid_product_ids = (
        ~order_items["product_id"].isin(
            products["product_id"]
        )
    ).sum()

    if invalid_product_ids > 0:

        logger.warning(
            f"Invalid product references: "
            f"{invalid_product_ids}"
        )

    logger.info("Data validation completed.")


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    logger.info("Connecting to PostgreSQL...")

    connection = psycopg2.connect(
        **DB_CONFIG
    )

    logger.info(
        "PostgreSQL connection successful"
    )

    return connection


# ============================================================
# LOAD
# ============================================================

def load_data(
    customers,
    orders,
    order_items,
    products
):

    connection = get_connection()

    cursor = connection.cursor()

    try:

        logger.info("Clearing existing data...")

        cursor.execute(
            "TRUNCATE TABLE "
            "order_items, orders, products, customers "
            "CASCADE;"
        )

        # ----------------------------------------------------
        # Customers
        # ----------------------------------------------------

        customer_data = [
            (
                row.customer_id,
                row.country,
                row.signup_date
            )
            for row in customers.itertuples(
                index=False
            )
        ]

        execute_batch(
            cursor,
            """
            INSERT INTO customers
            (
                customer_id,
                country,
                signup_date
            )
            VALUES (%s, %s, %s)
            """,
            customer_data,
            page_size=1000
        )

        logger.info(
            f"Customers loaded: {len(customer_data)}"
        )

        # ----------------------------------------------------
        # Products
        # ----------------------------------------------------

        product_data = [
            (
                row.product_id,
                row.product_name,
                row.category
            )
            for row in products.itertuples(
                index=False
            )
        ]

        execute_batch(
            cursor,
            """
            INSERT INTO products
            (
                product_id,
                product_name,
                category
            )
            VALUES (%s, %s, %s)
            """,
            product_data,
            page_size=1000
        )

        logger.info(
            f"Products loaded: {len(product_data)}"
        )

        # ----------------------------------------------------
        # Orders
        # ----------------------------------------------------

        order_data = [
            (
                row.order_id,
                row.customer_id,
                row.order_date,
                row.status
            )
            for row in orders.itertuples(
                index=False
            )
        ]

        execute_batch(
            cursor,
            """
            INSERT INTO orders
            (
                order_id,
                customer_id,
                order_date,
                status
            )
            VALUES (%s, %s, %s, %s)
            """,
            order_data,
            page_size=1000
        )

        logger.info(
            f"Orders loaded: {len(order_data)}"
        )

        # ----------------------------------------------------
        # Order Items
        # ----------------------------------------------------

        item_data = [
            (
                row.order_id,
                row.product_id,
                row.quantity,
                row.price
            )
            for row in order_items.itertuples(
                index=False
            )
        ]

        execute_batch(
            cursor,
            """
            INSERT INTO order_items
            (
                order_id,
                product_id,
                quantity,
                price
            )
            VALUES (%s, %s, %s, %s)
            """,
            item_data,
            page_size=1000
        )

        logger.info(
            f"Order items loaded: {len(item_data)}"
        )

        connection.commit()

        logger.info(
            "All data loaded successfully."
        )

    except Exception as error:

        connection.rollback()

        logger.error(
            f"Load failed: {error}"
        )

        raise

    finally:

        cursor.close()
        connection.close()

        logger.info(
            "PostgreSQL connection closed"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    start_time = time.time()

    try:

        (
            customers,
            orders,
            order_items,
            products
        ) = extract_data()

        (
            customers,
            orders,
            order_items,
            products
        ) = transform_data(
            customers,
            orders,
            order_items,
            products
        )

        validate_data(
            customers,
            orders,
            order_items,
            products
        )

        load_data(
            customers,
            orders,
            order_items,
            products
        )

        execution_time = (
            time.time() - start_time
        )

        logger.info(
            f"ETL execution time: "
            f"{execution_time:.2f} seconds"
        )

        logger.info(
            "CUSTOMER DATA ETL PIPELINE "
            "COMPLETED SUCCESSFULLY"
        )

    except Exception as error:

        logger.exception(
            f"ETL PIPELINE FAILED: {error}"
        )

        print(
            f"ETL FAILED: {error}"
        )

        raise

    print(
        "ETL PIPELINE COMPLETED SUCCESSFULLY"
    )


if __name__ == "__main__":
    main()