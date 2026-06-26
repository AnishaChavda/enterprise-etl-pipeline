import pandas as pd

df = pd.read_csv("data/transformed/customers.csv")

print(df.head())

print("\nDataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nRows Before:", len(df))

df = df.drop_duplicates()

print("Rows After:", len(df))

df["name"] = df["name"].astype(str).str.strip()

df["email"] = df["email"].astype(str).str.lower()

df["email"] = df["email"].fillna("unknown@email.com")

print("\nCleaned Data:")

print(df[["id", "name", "email"]])

output_file = "data/processed/customers_clean.csv"

df.to_csv(output_file, index=False)

print("\nCleaned file saved successfully")