import stripe
import json
import os
import time
import logging

from datetime import datetime

from utils.stripe_client import *
from configs.config import (
    API_LIMIT,
    MAX_RETRIES,
    CUSTOMERS_PATH
)

logging.basicConfig(
    filename="logs/customer_extraction.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

print("Customer Extraction Started")


def fetch_all_customers():

    all_customers = []

    starting_after = None

    while True:

        retries = 0

        while retries < MAX_RETRIES:

            try:

                response = stripe.Customer.list(
                    limit=API_LIMIT,
                    starting_after=starting_after
                )

                customers = response.data

                print(f"Fetched {len(customers)} customers")

                for customer in customers:
                    all_customers.append(customer.to_dict())

                if response.has_more:

                    starting_after = customers[-1].id

                else:
                    return all_customers

                break

            except Exception as e:

                retries += 1

                logging.error(e)

    return all_customers


def save_customers(customers):

    os.makedirs(CUSTOMERS_PATH, exist_ok=True)

    file_path = f"{CUSTOMERS_PATH}/customers.json"

    with open(file_path, "w") as file:
        json.dump(customers, file, indent=4)

    print("Customers saved successfully")


if __name__ == "__main__":

    customers = fetch_all_customers()

    save_customers(customers)