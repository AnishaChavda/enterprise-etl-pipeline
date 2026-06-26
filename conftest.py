import os
import sys
import pytest
from unittest.mock import MagicMock
from sqlalchemy import create_engine, event

# Set environment variables for testing BEFORE loading connection modules
os.environ["DATABASE_URL"] = "sqlite:///test_enterprise_etl.db"
os.environ["STRIPE_SECRET_KEY"] = "dummy"
os.environ["SALESFORCE_API_KEY"] = "dummy"
os.environ["ZENDESK_SUBDOMAIN"] = "dummy"

from loading.connection import Base, engine

# --- Mock Airflow for local testing on Python 3.14 ---
class MockTaskInstance:
    def __rshift__(self, other):
        return other
    def __rrshift__(self, other):
        return self

class MockTaskDecorator:
    def __call__(self, func):
        func.expand = MagicMock(return_value=MockTaskInstance())
        return func

mock_task = MockTaskDecorator()

class MockDAG:
    def __init__(self, *args, **kwargs):
        pass
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class MockPythonOperator:
    def __init__(self, *args, **kwargs):
        pass
    def __rshift__(self, other):
        return other
    def __rrshift__(self, other):
        return self

# Setup mock modules in sys.modules
airflow_mock = MagicMock()
airflow_mock.DAG = MockDAG

python_op_mock = MagicMock()
python_op_mock.PythonOperator = MockPythonOperator

decorators_mock = MagicMock()
decorators_mock.task = mock_task

sys.modules["airflow"] = airflow_mock
sys.modules["airflow.models"] = MagicMock()
sys.modules["airflow.operators"] = MagicMock()
sys.modules["airflow.operators.python"] = python_op_mock
sys.modules["airflow.decorators"] = decorators_mock

# Attach SQLite file databases to emulate schemas persistently during testing
@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("ATTACH DATABASE 'test_raw_data.db' AS raw_data")
    cursor.execute("ATTACH DATABASE 'test_staging.db' AS staging")
    cursor.execute("ATTACH DATABASE 'test_warehouse.db' AS warehouse")
    cursor.execute("ATTACH DATABASE 'test_audit.db' AS audit")
    cursor.execute("ATTACH DATABASE 'test_logs.db' AS logs")
    cursor.close()

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
    
    # Clean up all created test databases
    db_files = [
        "test_enterprise_etl.db",
        "test_raw_data.db",
        "test_staging.db",
        "test_warehouse.db",
        "test_audit.db",
        "test_logs.db"
    ]
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
            except Exception:
                pass
