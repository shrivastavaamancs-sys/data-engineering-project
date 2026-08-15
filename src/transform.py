import pandas as pd

# ============================================================
# 1. READ RAW DATA
# ============================================================

input_file = "data/raw/archive/Amazon Sale Report.csv"
output_file = "data/processed/amazon_sales_cleaned.csv"

df = pd.read_csv(
    input_file,
    encoding="utf-8",
    low_memory=False
)

print("=" * 60)
print("RAW DATA LOADED")
print("=" * 60)

print("Rows:", len(df))
print("Columns:", len(df.columns))


# ============================================================
# 2. REMOVE UNWANTED COLUMNS
# ============================================================

columns_to_drop = [
    "index",
    "Unnamed: 22"
]

df = df.drop(columns=columns_to_drop, errors="ignore")

# ============================================================
# 2.1 REMOVE DUPLICATE ROWS
# ============================================================

before = len(df)

df = df.drop_duplicates()

after = len(df)

print("Duplicate rows removed:", before - after)
# ============================================================
# 3. CLEAN COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace("-", "_", regex=False)
    .str.replace(" ", "_", regex=False)
)


# ============================================================
# 4. CONVERT DATE
# ============================================================

df["date"] = pd.to_datetime(
    df["date"],
    format="%m-%d-%y",
    errors="coerce"
)


# ============================================================
# 5. CLEAN TEXT COLUMNS
# ============================================================

text_columns = [
    "order_id",
    "status",
    "fulfilment",
    "sales_channel",
    "ship_service_level",
    "style",
    "sku",
    "category",
    "size",
    "asin",
    "courier_status",
    "currency",
    "ship_city",
    "ship_state",
    "ship_country",
    "promotion_ids",
    "fulfilled_by"
]

for column in text_columns:
    if column in df.columns:
        df[column] = df[column].astype("string").str.strip()


# ============================================================
# 6. HANDLE NUMERIC COLUMNS
# ============================================================

df["qty"] = pd.to_numeric(
    df["qty"],
    errors="coerce"
)

df["amount"] = pd.to_numeric(
    df["amount"],
    errors="coerce"
)

df["ship_postal_code"] = pd.to_numeric(
    df["ship_postal_code"],
    errors="coerce"
)


# ============================================================
# 7. HANDLE MISSING VALUES
# ============================================================

# These fields are optional/business-dependent,
# so we don't delete the rows.

df["promotion_ids"] = df["promotion_ids"].fillna("No Promotion")

df["fulfilled_by"] = df["fulfilled_by"].fillna("Unknown")

df["courier_status"] = df["courier_status"].fillna("Unknown")

df["currency"] = df["currency"].fillna("INR")


# ============================================================
# 8. DATA QUALITY CHECKS
# ============================================================

print("\n" + "=" * 60)
print("DATA QUALITY CHECKS")
print("=" * 60)

print("Duplicate rows:", df.duplicated().sum())

print("Invalid dates:", df["date"].isna().sum())

print("Missing Order IDs:", df["order_id"].isna().sum())

print("Missing Quantity:", df["qty"].isna().sum())

print("Missing Amount:", df["amount"].isna().sum())

print("\nOrders with missing Amount by Status:")
print(
    df[df["amount"].isna()]
    .groupby("status")
    .size()
    .sort_values(ascending=False)
)

print("\nOrders with missing Amount by Fulfilment:")
print(
    df[df["amount"].isna()]
    .groupby("fulfilment")
    .size()
    .sort_values(ascending=False)
)

print("Negative Quantity:", (df["qty"] < 0).sum())
print("\nOrders with missing Amount by Status:")
print(
    df[df["amount"].isna()]
    .groupby("status")
    .size()
    .sort_values(ascending=False)
)

print("\nOrders with missing Amount by Fulfilment:")
print(
    df[df["amount"].isna()]
    .groupby("fulfilment")
    .size()
    .sort_values(ascending=False)
)

print("Negative Amount:", (df["amount"] < 0).sum())


# ============================================================
# 9. REMOVE INVALID RECORDS
# ============================================================

df = df.dropna(
    subset=[
        "order_id",
        "date"
    ]
)

df = df[df["qty"].fillna(0) >= 0]

df = df[df["amount"].fillna(0) >= 0]


# ============================================================
# 10. CREATE REVENUE COLUMN
# ============================================================

df["revenue"] = (
    df["qty"] * df["amount"].fillna(0)
)


# ============================================================
# 11. SAVE PROCESSED DATA
# ============================================================

df.to_csv(
    output_file,
    index=False
)


# ============================================================
# 12. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("TRANSFORMATION COMPLETED")
print("=" * 60)

print("Final Rows:", len(df))
print("Final Columns:", len(df.columns))

print("\nFinal Columns:")
for column in df.columns:
    print("-", column)

print("\nProcessed file saved at:")
print(output_file)