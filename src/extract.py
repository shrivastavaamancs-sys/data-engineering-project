import pandas as pd

# Input file
input_file = "data/raw/archive/Amazon Sale Report.csv"

# Read CSV
df = pd.read_csv(
    input_file,
    encoding="utf-8",
    low_memory=False
)

print("=" * 60)
print("DATASET LOADED SUCCESSFULLY")
print("=" * 60)

print("\nRows:", len(df))
print("Columns:", len(df.columns))

print("\nColumn Names:")
for column in df.columns:
    print("-", column)

print("\nFirst 5 Records:")
print(df.head())

print("\nData Types:")
print(df.dtypes)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:", df.duplicated().sum())