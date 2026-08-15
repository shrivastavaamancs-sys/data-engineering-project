import pandas as pd

INPUT_FILE = "data/raw/online_retail_sample.csv"
OUTPUT_FILE = "data/processed/extracted_data.csv"

def extract_data():
    print("Starting data extraction...")

    df = pd.read_csv(
        INPUT_FILE,
        encoding="ISO-8859-1"
    )

    print(f"Rows extracted: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    return df


if __name__ == "__main__":
    df = extract_data()