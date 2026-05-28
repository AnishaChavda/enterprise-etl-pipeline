import stripe
import json
import os
import time
import logging

from utils.stripe_client import *
from configs.config import (
    API_LIMIT,
    MAX_RETRIES,
    CUSTOMERS_PATH
)

# Logging Configuration
logging.basicConfig(
    filename="logs/customer_extraction.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

print("Customer Extraction Started")


def fetch_all_customers():

    all_customers = []

    starting_after = None

    retries = 0

    start_time = time.time()

    while True:

        try:

            logging.info("Sending request to Stripe Customer API")

            response = stripe.Customer.list(
                limit=API_LIMIT,
                starting_after=starting_after
            )

            customers = response.data

            print(f"Fetched {len(customers)} customers")

            logging.info(f"Fetched {len(customers)} customers")

            for customer in customers:
                all_customers.append(customer.to_dict())

            if response.has_more:

                starting_after = customers[-1].id

                logging.info(f"Next page starts after {starting_after}")

            else:

                logging.info("All customers fetched successfully")

                break

        except stripe.error.RateLimitError as e:

            retries += 1

            logging.warning(f"Rate limit error: {e}")

            print(f"Retry Attempt: {retries}")

            time.sleep(5)

        except stripe.error.APIConnectionError as e:

            retries += 1

            logging.warning(f"API connection error: {e}")

            print(f"Retry Attempt: {retries}")

            time.sleep(5)

        except stripe.error.AuthenticationError as e:

            logging.error(f"Authentication Error: {e}")

            print("Authentication Failed")

            break

        except stripe.error.StripeError as e:

            logging.error(f"Stripe Error: {e}")

            print("Stripe API Error")

            break

        except Exception as e:

            logging.error(f"Unexpected Error: {e}")

            print("Unexpected Error")

            break

        if retries >= MAX_RETRIES:

            logging.error("Maximum retries reached")

            print("Maximum retries reached")

            break

    end_time = time.time()

    execution_time = end_time - start_time

    logging.info(f"Execution Time: {execution_time} seconds")

    return all_customers


def save_customers(customers):

    os.makedirs(CUSTOMERS_PATH, exist_ok=True)

    file_path = f"{CUSTOMERS_PATH}/customers.json"

    with open(file_path, "w") as file:

        json.dump(customers, file, indent=4)

    logging.info(f"Customer data saved at {file_path}")

    print("Customers saved successfully")


if __name__ == "__main__":

    customers = fetch_all_customers()

    save_customers(customers)