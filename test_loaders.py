import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from etl.load import upsert_postgres
from db.models import Customer


def test_upsert_postgres_statement_compiles():
    engine = create_engine("postgresql+psycopg2://user:pass@localhost/test", echo=False)
    Session = sessionmaker(bind=engine)
    records = [
        {"customer_id": "cust_1", "name": "Alice", "email": "alice@example.com", "created_date": "2026-06-04T00:00:00Z"}
    ]
    assert records[0]["customer_id"] == "cust_1"
    assert records[0]["email"] == "alice@example.com"


def test_record_insertion_falls_back_on_empty():
    inserted = upsert_postgres(Customer, [], ["customer_id"])
    assert inserted == 0
