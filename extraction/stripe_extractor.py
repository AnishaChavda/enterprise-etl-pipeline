import stripe
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Set Stripe API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

print("Stripe Extraction Started")

try:
    # Fetch customers
    customers = stripe.Customer.list(limit=5)

    print("Customers fetched successfully")
    print("Total Customers:", len(customers.data))
    print("Has More:", customers.has_more)

    customer_data = []

    for customer in customers.data:
        customer_data.append(customer.to_dict())

    # Save JSON data
    with open("data/raw/stripe/customers.json", "w") as file:
        json.dump(customer_data, file, indent=4)

    print("Customer data saved successfully")

except Exception as e:
    print("Error:", e)