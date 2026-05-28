import stripe
import json
import os
import logging
import time

from utils.stripe_client import *
from configs.config import (
    API_LIMIT,
    MAX_RETRIES,
    PAYMENTS_PATH
)

logging.basicConfig(
    filename="logs/payments_extraction.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

print("Payments Extraction Started")

start_time = time.time()

retries = 0

try:

    logging.info("Fetching payments from Stripe API")

    payments = stripe.PaymentIntent.list(limit=API_LIMIT)

    payment_data = []

    for payment in payments.data:
        payment_data.append(payment)

    os.makedirs(PAYMENTS_PATH, exist_ok=True)

    with open(f"{PAYMENTS_PATH}/payments.json", "w") as file:

        json.dump(payment_data, file, indent=4, default=str)

    logging.info("Payments saved successfully")

    print("Payments saved successfully")

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