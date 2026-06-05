import pandas as pd
import os

# Load cleaned data
df = pd.read_csv("data/processed/customers_clean.csv")

# Convert Unix timestamp to readable date
df["created"] = pd.to_datetime(
    df["created"],
    unit="s"
)

# Rename columns
df.rename(
    columns={
        "id": "customer_id",
        "created": "created_date"
    },
    inplace=True
)

# Keep only useful columns
df = df[
    [
        "customer_id",
        "name",
        "email",
        "created_date"
    ]
]

# Create mapped folder if not exists
os.makedirs("data/mapped", exist_ok=True)

# Save mapped dataset
output_file = "data/mapped/customers_mapped.csv"

df.to_csv(output_file, index=False)

print("Customer schema mapping completed successfully")
print(f"Records Processed: {len(df)}")
print(f"Output File: {output_file}")

print("\nSample Data:")
print(df.head())