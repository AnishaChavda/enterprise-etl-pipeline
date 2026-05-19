import stripe
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv(dotenv_path=".env")

# Set Stripe API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

print("Stripe Pagination Extraction Started")


def fetch_all_customers(limit=5):
    """
    Fetch all customers using Stripe pagination
    """

    all_customers = []

    starting_after = None

    while True:

        # API request
        response = stripe.Customer.list(
            limit=limit,
            starting_after=starting_after
        )

        customers = response.data

        print("=" * 50)
        print(f"Fetched {len(customers)} customers")
        print("=" * 50)

        # Add customers to master list
        for customer in customers:
            all_customers.append(customer.to_dict())

        # Check pagination
        if response.has_more:

            # Get last customer ID
            starting_after = customers[-1].id

            print(f"Fetching next page after: {starting_after}")

        else:
            print("No more customers left")
            break

    return all_customers


def save_customers(customers):
    """
    Save customers into JSON file
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    file_path = f"data/raw/stripe/customers_{timestamp}.json"

    with open(file_path, "w") as file:
        json.dump(customers, file, indent=4)

    print(f"Customer data saved: {file_path}")


def main():

    customers = fetch_all_customers(limit=5)

    print(f"Total Customers Extracted: {len(customers)}")

    save_customers(customers)


if __name__ == "__main__":
    main()