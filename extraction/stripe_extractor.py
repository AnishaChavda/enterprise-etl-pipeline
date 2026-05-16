import stripe
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv(dotenv_path=".env")

# Set Stripe API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

print("Stripe Extraction Started")


def fetch_customers(limit=10):
    """
    Fetch customers from Stripe API
    """

    try:
        customers = stripe.Customer.list(limit=limit)

        print(f"Customers fetched successfully: {len(customers.data)}")

        return customers.data

    except Exception as e:
        print("Error fetching customers:", e)
        return []


def save_customers_to_json(customers):
    """
    Save customer data into JSON file
    """

    try:
        customer_data = []

        for customer in customers:
            customer_data.append(customer.to_dict())

        # Generate timestamp filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        file_path = f"data/raw/stripe/customers_{timestamp}.json"

        with open(file_path, "w") as file:
            json.dump(customer_data, file, indent=4)

        print(f"Customer data saved successfully: {file_path}")

    except Exception as e:
        print("Error saving JSON:", e)


def main():
    """
    Main ETL extraction flow
    """

    customers = fetch_customers(limit=5)

    if customers:
        save_customers_to_json(customers)
    else:
        print("No customer data found")


# Run script
if __name__ == "__main__":
    main()