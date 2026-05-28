import stripe
import json
import os
import logging
import time

from datetime import datetime

from utils.stripe_client import *
from configs.config import (
    API_LIMIT,
    MAX_RETRIES,
    PAYMENTS_PATH
)

# Logging Configuration
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

    # Create payments folder if not exists
    os.makedirs(PAYMENTS_PATH, exist_ok=True)

    # Timestamp filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    file_path = f"{PAYMENTS_PATH}/payments_{timestamp}.json"

    # Save JSON file
    with open(file_path, "w") as file:

        json.dump(payment_data, file, indent=4, default=str)

    logging.info(f"Payments saved successfully at {file_path}")

    print("Payments saved successfully")

except stripe.error.RateLimitError as e:

    retries += 1

    logging.warning(f"Rate limit error: {e}")

    print(f"Retry Attempt: {retries}")

except stripe.error.APIConnectionError as e:

    retries += 1

    logging.warning(f"API connection error: {e}")

    print(f"Retry Attempt: {retries}")

except stripe.error.AuthenticationError as e:

    logging.error(f"Authentication error: {e}")

    print("Authentication Failed")

except Exception as e:

    logging.error(f"Unexpected error: {e}")

    print("Unexpected Error")

end_time = time.time()

execution_time = end_time - start_time

logging.info(f"Execution Time: {execution_time} seconds")