import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, ValidationError

LOGGER = logging.getLogger("etl.transform")
logging.basicConfig(level=logging.INFO)


class CustomerPayload(BaseModel):
    customer_id: str
    name: Optional[str]
    email: EmailStr
    created_date: datetime


def clean_customers(raw_customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cleaned = []
    for customer in raw_customers:
        payload = {
            "customer_id": customer.get("id"),
            "name": customer.get("name") or customer.get("metadata", {}).get("name"),
            "email": (customer.get("email") or "unknown@example.com").strip().lower(),
            "created_date": datetime.utcfromtimestamp(customer.get("created", 0)) if customer.get("created") is not None else None,
        }
        cleaned.append(payload)
    LOGGER.info("Cleaned %s customer records", len(cleaned))
    return cleaned


def validate_customers(customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    validated = []
    for record in customers:
        try:
            validated_record = CustomerPayload(**record).model_dump()
            validated.append(validated_record)
        except ValidationError as exc:
            LOGGER.warning("Customer validation failed: %s", exc)
    LOGGER.info("Validated %s customer records", len(validated))
    return validated


def transform_support_tickets(raw_tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    transformed = []
    for ticket in raw_tickets:
        transformed.append(
            {
                "ticket_id": str(ticket.get("id")),
                "customer_id": str(ticket.get("requester_id", "")),
                "subject": ticket.get("subject", "unknown"),
                "status": ticket.get("status", "unknown"),
                "priority": ticket.get("priority"),
                "created_date": ticket.get("created_at"),
                "closed_date": ticket.get("updated_at"),
            }
        )
    LOGGER.info("Transformed %s Zendesk tickets", len(transformed))
    return transformed
