import pandas as pd

df = pd.read_csv(
    "data/validated/customers_validated.csv"
)

print("Validated Data Loaded")

print("\nTotal Records:")

print(len(df))

duplicate_count = df.duplicated(
    subset=["customer_id"]
).sum()

print(
    f"Duplicate Customer IDs: {duplicate_count}"
)
df = df.sort_values(
    by="created_date",
    ascending=False
)
df = df.reset_index(
    drop=True
)
print("\nFinal Dataset Preview:")

print(df.head())

output_file = (
    "data/final/customers_final.csv"
)

df.to_csv(
    output_file,
    index=False
)

print(
    "\nFinal Dataset Saved Successfully"
)
