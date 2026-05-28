import stripe
import json
import os
import logging
import time

from utils.stripe_client import *
from configs.config import (
    API_LIMIT,
    MAX_RETRIES,
    CHARGES_PATH
)

logging.basicConfig(
    filename="logs/charges_extraction.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

print("Charges Extraction Started")

start_time = time.time()

retries = 0

try:

    logging.info("Fetching charges from Stripe API")

    charges = stripe.Charge.list(limit=API_LIMIT)

    charge_data = []

    for charge in charges.data:
        charge_data.append(charge)

    os.makedirs(CHARGES_PATH, exist_ok=True)

    with open(f"{CHARGES_PATH}/charges.json", "w") as file:

        json.dump(charge_data, file, indent=4, default=str)

    logging.info("Charges saved successfully")

    print("Charges saved successfully")

except stripe.error.RateLimitError as e:

    retries += 1

    logging.warning(f"Rate limit error: {e}")

except stripe.error.APIConnectionError as e:

    retries += 1

    logging.warning(f"API connection error: {e}")

except stripe.error.AuthenticationError as e:

    logging.error(f"Authentication error: {e}")

except Exception as e:

    logging.error(f"Unexpected error: {e}")

end_time = time.time()

logging.info(f"Execution Time: {end_time - start_time} seconds")