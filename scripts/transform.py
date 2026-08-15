import pandas as pd

INPUT_FILE = "data/raw/online_retail_sample.csv"
OUTPUT_FILE = "data/processed/cleaned_data.csv"


def transform_data():

    print("Starting data transformation...")

    df = pd.read_csv(
        INPUT_FILE,
        encoding="ISO-8859-1"
    )

    print(f"Initial rows: {len(df)}")

    # Remove duplicate records
    df = df.drop_duplicates()

    # Remove rows with missing CustomerID
    df = df.dropna(subset=["CustomerID"])

    # Keep valid transactions
    df = df[df["Quantity"] > 0]
    df = df[df["UnitPrice"] > 0]

    # Convert date column
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    # Calculate total transaction amount
    df["TotalAmount"] = df["Quantity"] * df["UnitPrice"]

    # Convert CustomerID to integer
    df["CustomerID"] = df["CustomerID"].astype(int)

    # Save cleaned data
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Final rows: {len(df)}")
    print(f"Cleaned data saved to: {OUTPUT_FILE}")

    return df


if __name__ == "__main__":
    transform_data()