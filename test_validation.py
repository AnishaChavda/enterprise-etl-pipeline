import pytest
from validation.models import CustomerValidation, InvoiceValidation
from validation.validator import validate_records

def test_customer_validation():
    # Valid customer
    valid_data = [
        {
            "customer_id": "cus_123",
            "name": "Jane Doe",
            "email": "JANE.DOE@EXAMPLE.COM",
            "source": "stripe",
            "created_date": "2026-06-01T00:00:00"
        }
    ]
    validated = validate_records(valid_data, CustomerValidation, "customers")
    assert len(validated) == 1
    assert validated[0]["customer_id"] == "cus_123"
    # Email should be standardized to lower case
    assert validated[0]["email"] == "jane.doe@example.com"

def test_customer_validation_invalid():
    # Invalid customer email
    invalid_data = [
        {
            "customer_id": "cus_123",
            "name": "Jane Doe",
            "email": "invalid_email_no_at",
            "source": "stripe",
            "created_date": "2026-06-01T00:00:00"
        }
    ]
    validated = validate_records(invalid_data, CustomerValidation, "customers")
    assert len(validated) == 0
