import stripe
import json
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

print("Fetching Stripe Payments")

try:
    payments = stripe.PaymentIntent.list(limit=5)

    print("Total Payments:", len(payments.data))

    payment_data = []

    for payment in payments.data:
        payment_data.append(payment)

    os.makedirs("data/raw/stripe/payments", exist_ok=True)

    with open("data/raw/stripe/payments/payments.json", "w") as file:
        json.dump(payment_data, file, indent=4, default=str)

    print("Payments saved successfully")

except Exception as e:
    print("Error:", e)