import stripe
import json
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

print("Fetching Stripe Charges")

try:
    charges = stripe.Charge.list(limit=5)

    print("Total Charges:", len(charges.data))

    charge_data = []

    for charge in charges.data:
        charge_data.append(charge)

    os.makedirs("data/raw/stripe/charges", exist_ok=True)

    with open("data/raw/stripe/charges/charges.json", "w") as file:
        json.dump(charge_data, file, indent=4)

    print("Charges saved successfully")

except Exception as e:
    print("Error:", e)