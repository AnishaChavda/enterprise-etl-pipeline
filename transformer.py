import logging
from datetime import datetime

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def parse_datetime(val):
    if not val:
        return None
    if isinstance(val, (int, float)):
        return datetime.utcfromtimestamp(val)
    if isinstance(val, datetime):
        return val
    try:
        # Try parsing standard ISO formats
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except ValueError:
        try:
            return datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                return datetime.strptime(val, "%Y-%m-%d")
            except ValueError as e:
                logging.error(f"Cannot parse datetime value: {val}. Error: {e}")
                raise e

def transform_stripe_customers(raw_list):
    transformed = []
    for item in raw_list:
        transformed.append({
            "customer_id": item.get("id"),
            "name": item.get("name"),
            "email": item.get("email"),
            "source": "stripe",
            "created_date": parse_datetime(item.get("created"))
        })
    return transformed

def transform_stripe_charges(raw_list):
    transformed_invoices = []
    transformed_payments = []

    for item in raw_list:
        created_dt = parse_datetime(item.get("created"))
        amount_usd = float(item.get("amount", 0)) / 100.0
        
        # We can map Stripe charges to both invoices and payments to populate both schemas
        transformed_invoices.append({
            "invoice_id": f"inv_{item.get('id')}",
            "customer_id": item.get("customer"),
            "amount": amount_usd,
            "currency": item.get("currency"),
            "status": item.get("status"),
            "due_date": None,
            "created_date": created_dt
        })

        transformed_payments.append({
            "payment_id": item.get("id"),
            "customer_id": item.get("customer"),
            "invoice_id": f"inv_{item.get('id')}",
            "amount": amount_usd,
            "currency": item.get("currency"),
            "status": item.get("status"),
            "payment_method": item.get("payment_method_details", {}).get("type") if isinstance(item.get("payment_method_details"), dict) else item.get("payment_method"),
            "created_date": created_dt
        })

    return transformed_invoices, transformed_payments

def transform_stripe_subscriptions(raw_list):
    transformed = []
    for item in raw_list:
        transformed.append({
            "subscription_id": item.get("id"),
            "customer_id": item.get("customer"),
            "status": item.get("status"),
            "current_period_start": parse_datetime(item.get("current_period_start")),
            "current_period_end": parse_datetime(item.get("current_period_end")),
            "cancel_at_period_end": bool(item.get("cancel_at_period_end", False)),
            "created_date": parse_datetime(item.get("created"))
        })
    return transformed

def transform_sf_accounts(raw_list):
    transformed = []
    for item in raw_list:
        transformed.append({
            "customer_id": item.get("Id"),
            "name": item.get("Name"),
            "email": item.get("BillingEmail__c"),
            "source": "salesforce",
            "created_date": parse_datetime(item.get("CreatedDate"))
        })
    return transformed

def transform_sf_opportunities(raw_list):
    transformed_invoices = []
    for item in raw_list:
        created_dt = parse_datetime(item.get("CreatedDate"))
        transformed_invoices.append({
            "invoice_id": item.get("Id"),
            "customer_id": item.get("AccountId"),
            "amount": float(item.get("Amount", 0.0) or 0.0),
            "currency": item.get("CurrencyIsoCode", "USD"),
            "status": item.get("StageName"),
            "due_date": parse_datetime(item.get("CloseDate")),
            "created_date": created_dt
        })
    return transformed_invoices

def transform_zd_tickets(raw_list):
    transformed = []
    for item in raw_list:
        transformed.append({
            "ticket_id": str(item.get("id")),
            "customer_id": str(item.get("requester_id")) if item.get("requester_id") else None,
            "subject": item.get("subject"),
            "status": item.get("status"),
            "priority": item.get("priority") or "normal",
            "created_date": parse_datetime(item.get("created_at"))
        })
    return transformed
