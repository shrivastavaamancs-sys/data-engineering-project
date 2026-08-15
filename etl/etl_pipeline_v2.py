import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
import time


# ==========================================
# 1. Project Paths
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "amazon_sales_cleaned.csv"


# ==========================================
# 2. PostgreSQL Configuration
# ==========================================

DB_CONFIG = {
    "host": "localhost",
    "database": "amazon_sales_db",
    "user": "postgres",
    "password": "Anshul@789",
    "port": 5432
}


# ==========================================
# 3. Start ETL
# ==========================================

start_time = time.time()

print("=" * 50)
print("AMAZON SALES ETL PIPELINE V2")
print("=" * 50)


# ==========================================
# 4. Extract
# ==========================================

print("\n[1/5] Reading CSV...")

df = pd.read_csv(INPUT_FILE)

print(f"Rows extracted: {len(df)}")
print(f"Columns extracted: {len(df.columns)}")


# ==========================================
# 5. Transform
# ==========================================

print("\n[2/5] Transforming data...")

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


# Date conversion
df["order_date"] = pd.to_datetime(
    df["order_date"],
    errors="coerce"
).dt.date


# Numeric conversion
df["qty"] = pd.to_numeric(
    df["qty"],
    errors="coerce"
)

df["amount"] = pd.to_numeric(
    df["amount"],
    errors="coerce"
)


# ==========================================
# 6. Data Validation
# ==========================================

print("\n[3/5] Validating data...")

before_cleaning = len(df)


# Remove invalid records
df.dropna(
    subset=[
        "order_id",
        "order_date"
    ],
    inplace=True
)


# Replace invalid numeric values
df["qty"] = df["qty"].fillna(0).astype(int)
df["amount"] = df["amount"].fillna(0)


# Remove duplicate order + SKU combinations
df.drop_duplicates(
    subset=[
        "order_id",
        "sku"
    ],
    inplace=True
)


after_cleaning = len(df)

print(f"Rows before cleaning: {before_cleaning}")
print(f"Rows after cleaning:  {after_cleaning}")
print(f"Rows removed:         {before_cleaning - after_cleaning}")


# ==========================================
# 7. PostgreSQL Connection
# ==========================================

print("\n[4/5] Connecting to PostgreSQL...")

conn = psycopg2.connect(**DB_CONFIG)

cursor = conn.cursor()


# ==========================================
# 8. Clear Existing Data
# ==========================================

cursor.execute(
    "TRUNCATE TABLE amazon_sales_etl;"
)

conn.commit()


# ==========================================
# 9. Batch Insert
# ==========================================

print("\n[5/5] Loading data into PostgreSQL...")


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
    df.itertuples(
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


# ==========================================
# 10. Close Connection
# ==========================================

cursor.close()
conn.close()


# ==========================================
# 11. Pipeline Summary
# ==========================================

end_time = time.time()

execution_time = end_time - start_time

print("\n" + "=" * 50)
print("ETL PIPELINE COMPLETED SUCCESSFULLY")
print("=" * 50)

print(f"Records loaded : {len(records)}")
print(f"Execution time : {execution_time:.2f} seconds")

print("=" * 50)