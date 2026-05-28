import stripe
import json
import os

from utils.stripe_client import *
from configs.config import (
    API_LIMIT,
    PAYMENTS_PATH
)

print("Fetching Stripe Payments")

try:

    payments = stripe.PaymentIntent.list(limit=API_LIMIT)

    payment_data = []

    for payment in payments.data:
        payment_data.append(payment)

    os.makedirs(PAYMENTS_PATH, exist_ok=True)

    with open(f"{PAYMENTS_PATH}/payments.json", "w") as file:
        json.dump(payment_data, file, indent=4, default=str)

    print("Payments saved successfully")

except Exception as e:

    print("Error:", e)