import pytest
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert
from loading.models import Customer
from loading.snowflake_upsert import build_snowflake_merge_query, snowflake_upsert

def test_postgres_upsert_compilation():
    """
    Tests that the PostgreSQL dialect-specific insert statements compile
    correctly with the ON CONFLICT clause.
    """
    engine = create_engine("postgresql://")
    table = Customer.__table__
    
    stmt = insert(table).values([{
        "customer_id": "cus_1",
        "name": "Alice",
        "email": "alice@example.com",
        "source": "stripe",
        "created_date": "2026-06-01 00:00:00"
    }])
    
    # Check ON CONFLICT DO UPDATE compilation
    update_stmt = stmt.on_conflict_do_update(
        index_elements=["customer_id"],
        set_={"name": stmt.excluded.name}
    )
    
    compiled = str(update_stmt.compile(engine, dialect=postgresql.dialect()))
    assert "INSERT INTO customers" in compiled
    assert "ON CONFLICT (customer_id) DO UPDATE SET" in compiled

def test_snowflake_merge_query_builder():
    query = build_snowflake_merge_query(
        target_table="CUSTOMERS",
        staging_table="CUSTOMERS_TEMP_STAGE",
        columns=["customer_id", "name", "email"],
        pk_column="customer_id"
    )
    assert "MERGE INTO CUSTOMERS AS target" in query
    assert "USING CUSTOMERS_TEMP_STAGE AS source" in query
    assert "ON target.customer_id = source.customer_id" in query
    assert "target.name = source.name" in query
