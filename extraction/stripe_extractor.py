import stripe
import json
import os
import time
import logging

from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv(dotenv_path=".env")

# Stripe API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Configure logging
logging.basicConfig(
    filename="logs/stripe_extraction.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

print("Stripe Reliable Extraction Started")


def fetch_all_customers(limit=5, max_retries=3):

    all_customers = []

    starting_after = None

    while True:

        retries = 0

        while retries < max_retries:

            try:

                logging.info("Sending request to Stripe API")

                response = stripe.Customer.list(
                    limit=limit,
                    starting_after=starting_after
                )

                customers = response.data

                print(f"Fetched {len(customers)} customers")

                logging.info(f"Fetched {len(customers)} customers")

                # Store customers
                for customer in customers:
                    all_customers.append(customer.to_dict())

                # Pagination handling
                if response.has_more:

                    starting_after = customers[-1].id

                    print(f"Next page after: {starting_after}")

                    logging.info(f"Next page after: {starting_after}")

                else:
                    print("No more customers left")

                    logging.info("All customers fetched successfully")

                    return all_customers

                # Exit retry loop if successful
                break

            except stripe.error.RateLimitError as e:

                retries += 1

                print("Rate limit exceeded. Retrying...")

                logging.warning(f"Rate limit error: {e}")

                time.sleep(5)

            except stripe.error.APIConnectionError as e:

                retries += 1

                print("Network error. Retrying...")

                logging.warning(f"Connection error: {e}")

                time.sleep(5)

            except stripe.error.StripeError as e:

                print("Stripe API error:", e)

                logging.error(f"Stripe API error: {e}")

                return []

            except Exception as e:

                print("Unexpected error:", e)

                logging.error(f"Unexpected error: {e}")

                return []

    return all_customers


def save_customers(customers):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    file_path = f"data/raw/stripe/customers_{timestamp}.json"

    with open(file_path, "w") as file:
        json.dump(customers, file, indent=4)

    print(f"Customer data saved: {file_path}")

    logging.info(f"Customer data saved: {file_path}")


def main():

    customers = fetch_all_customers(limit=5)

    print(f"Total Customers Extracted: {len(customers)}")

    logging.info(f"Total Customers Extracted: {len(customers)}")

    save_customers(customers)


if __name__ == "__main__":
    main()