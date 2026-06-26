import pandas as pd

file_path = "data/raw/stripe/customers/customers_20260530_125057.json"

df = pd.read_json(file_path)

print(df[['id', 'name', 'email']])

output_path = "data/transformed/customers.csv"

df.to_csv(output_path, index=False)

print("CSV file created successfully")

print("\nShape:")
print(df.shape)