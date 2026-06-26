import pandas as pd
import os
import time

start_time = time.time()
print("Starting Customer Transformation Pipeline")

# --------------------------------------------------
# STEP 1 : Read Raw JSON
# --------------------------------------------------

json_file = "data/raw/stripe/customers/customers_20260530_125057.json"

df = pd.read_json(json_file)

print("Raw JSON Loaded")

# --------------------------------------------------
# STEP 2 : Cleaning
# --------------------------------------------------

# STEP 2 : Cleaning

if "id" in df.columns:
    df = df.drop_duplicates(subset=["id"])

print("Duplicate Removal Completed")

df["name"] = df["name"].astype(str).str.strip()

df["email"] = df["email"].fillna(
    "unknown@email.com"
)

df["email"] = df["email"].astype(str).str.lower()

print("Data Cleaning Completed")

# --------------------------------------------------
# STEP 3 : Schema Mapping
# --------------------------------------------------

df["created"] = pd.to_datetime(
    df["created"],
    unit="s"
)

df.rename(
    columns={
        "id": "customer_id",
        "created": "created_date"
    },
    inplace=True
)

df = df[
    [
        "customer_id",
        "name",
        "email",
        "created_date"
    ]
]

print("Schema Mapping Completed")

# --------------------------------------------------
# STEP 4 : Save Processed Dataset
# --------------------------------------------------

os.makedirs(
    "data/final",
    exist_ok=True
)

output_file = (
    "data/final/customers_final.csv"
)

df.to_csv(
    output_file,
    index=False
)

print("Pipeline Completed Successfully")

print(f"Total Records: {len(df)}")

print(f"Output File: {output_file}")
print(df.head())

end_time = time.time()

print(
    f"Execution Time: {end_time-start_time:.2f} seconds"
)