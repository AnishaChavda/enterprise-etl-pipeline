import pandas as pd

from customer_schema import Customer

df = pd.read_csv(
    "data/mapped/customers_mapped.csv"
)

validated_customers = []

for _, row in df.iterrows():

    try:

        customer = Customer(
            **row.to_dict()
        )

        validated_customers.append(
            customer.model_dump()
        )

    except Exception as e:

        print(
            f"Validation Failed: {e}"
        )

print(
    f"Valid Records: {len(validated_customers)}"
)

validated_df = pd.DataFrame(
    validated_customers
)

validated_df.to_csv(
    "data/validated/customers_validated.csv",
    index=False
)

print(
    "Validated data saved successfully"
)