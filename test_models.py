import pytest

from db.models import Customer, ETLJobRun, Invoice, Payment, Subscription, SupportTicket


def test_customer_model_fields():
    assert Customer.__tablename__ == "customers"
    assert hasattr(Customer, "customer_id")
    assert hasattr(Customer, "email")
    assert hasattr(Customer, "created_date")


def test_warehouse_related_models():
    for model in [Invoice, Payment, Subscription, SupportTicket, ETLJobRun]:
        assert hasattr(model, "__tablename__")
        assert model.__tablename__ is not None


def test_customer_relationships():
    assert hasattr(Customer, "invoices")
    assert hasattr(Customer, "payments")
    assert hasattr(Customer, "subscriptions")
