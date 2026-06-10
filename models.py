from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator

class CustomerValidation(BaseModel):
    customer_id: str = Field(..., min_length=1)
    name: Optional[str] = None
    email: EmailStr
    source: str = Field(..., min_length=1)
    created_date: datetime

    @field_validator("email", mode="before")
    @classmethod
    def clean_email(cls, v):
        if not v or str(v).strip() == "":
            return "unknown@email.com"
        return str(v).strip().lower()

class InvoiceValidation(BaseModel):
    invoice_id: str = Field(..., min_length=1)
    customer_id: str = Field(..., min_length=1)
    amount: float = Field(..., ge=0.0)
    currency: str = Field(..., min_length=2, max_length=10)
    status: str = Field(..., min_length=1)
    due_date: Optional[datetime] = None
    created_date: datetime

class PaymentValidation(BaseModel):
    payment_id: str = Field(..., min_length=1)
    customer_id: str = Field(..., min_length=1)
    invoice_id: Optional[str] = None
    amount: float = Field(..., ge=0.0)
    currency: str = Field(..., min_length=2, max_length=10)
    status: str = Field(..., min_length=1)
    payment_method: Optional[str] = None
    created_date: datetime

class SubscriptionValidation(BaseModel):
    subscription_id: str = Field(..., min_length=1)
    customer_id: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1)
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    created_date: datetime

class TicketValidation(BaseModel):
    ticket_id: str = Field(..., min_length=1)
    customer_id: Optional[str] = None
    subject: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1)
    priority: str = Field(..., min_length=1)
    created_date: datetime
