import pandas as pd
import psycopg2
from pathlib import Path


# ==============================
# 1. File Paths
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "amazon_sales_cleaned.csv"


# ==============================
# 2. PostgreSQL Configuration
# ==============================

DB_CONFIG = {
    "host": "localhost",
    "database": "amazon_sales_db",
    "user": "postgres",
    "password": "YOUR_POSTGRES_PASSWORD",
    "port": 5432
}


# ==============================
# 3. Read CSV
# ==============================

print("Reading CSV file...")

df = pd.read_csv(INPUT_FILE)

print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")


# ==============================
# 4. Select Required Columns
# ==============================

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
]


# ==============================
# 5. Rename Columns
# ==============================

df.rename(
    columns={
        "date": "order_date",
        "revenue": "amount"
    },
    inplace=True
)


# ==============================
# 6. Data Type Conversion
# ==============================

df["order_date"] = pd.to_datetime(
    df["order_date"],
    errors="coerce"
).dt.date

df["qty"] = pd.to_numeric(
    df["qty"],
    errors="coerce"
).fillna(0).astype(int)

df["amount"] = pd.to_numeric(
    df["amount"],
    errors="coerce"
).fillna(0)


# ==============================
# 7. Remove Invalid Records
# ==============================

df.dropna(
    subset=[
        "order_id",
        "order_date"
    ],
    inplace=True
)


# ==============================
# 8. Remove Duplicate Orders
# ==============================

df.drop_duplicates(
    subset=["order_id", "sku"],
    inplace=True
)


print(f"Rows after cleaning: {len(df)}")


# ==============================
# 9. Connect to PostgreSQL
# ==============================

print("Connecting to PostgreSQL...")

conn = psycopg2.connect(**DB_CONFIG)

cursor = conn.cursor()


# ==============================
# 10. Clear Existing ETL Data
# ==============================

cursor.execute(
    "TRUNCATE TABLE amazon_sales_etl;"
)

conn.commit()


# ==============================
# 11. Insert Data
# ==============================

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
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


print("Loading data into PostgreSQL...")


for row in df.itertuples(index=False, name=None):

    cursor.execute(
        insert_query,
        row
    )


# ==============================
# 12. Commit Transaction
# ==============================

conn.commit()


print("ETL completed successfully!")


# ==============================
# 13. Close Connection
# ==============================

cursor.close()
conn.close()

print("PostgreSQL connection closed.")