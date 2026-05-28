import stripe
import json
import os

from utils.stripe_client import *
from configs.config import (
    API_LIMIT,
    CHARGES_PATH
)

print("Fetching Stripe Charges")

try:

    charges = stripe.Charge.list(limit=API_LIMIT)

    charge_data = []

    for charge in charges.data:
        charge_data.append(charge)

    os.makedirs(CHARGES_PATH, exist_ok=True)

    with open(f"{CHARGES_PATH}/charges.json", "w") as file:
        json.dump(charge_data, file, indent=4, default=str)

    print("Charges saved successfully")

except Exception as e:

    print("Error:", e)