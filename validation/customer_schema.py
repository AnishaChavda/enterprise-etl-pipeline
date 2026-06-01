from pydantic import BaseModel, EmailStr
from typing import Optional


class Customer(BaseModel):

    customer_id: str

    name: Optional[str]

    email: EmailStr