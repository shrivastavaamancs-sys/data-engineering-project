import pandas as pd
import psycopg2

INPUT_FILE = "data/processed/cleaned_data.csv"

DB_CONFIG = {
    "host": "localhost",
    "database": "ecommerce_etl_db",
    "user": "postgres",
    "password": "Anshul@789",
    "port": 5432
}


def load_data():

    print("Starting data loading...")

    df = pd.read_csv(
        INPUT_FILE,
        encoding="ISO-8859-1"
    )

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO online_retail (
            invoice_no,
            stock_code,
            description,
            quantity,
            invoice_date,
            unit_price,
            customer_id,
            country,
            total_amount
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for _, row in df.iterrows():
        cursor.execute(
            insert_query,
            (
                row["InvoiceNo"],
                row["StockCode"],
                row["Description"],
                row["Quantity"],
                row["InvoiceDate"],
                row["UnitPrice"],
                row["CustomerID"],
                row["Country"],
                row["TotalAmount"]
            )
        )

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Rows loaded: {len(df)}")
    print("Data successfully loaded into PostgreSQL.")


if __name__ == "__main__":
    load_data()