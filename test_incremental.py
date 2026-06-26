import pytest
from datetime import datetime
from loading.incremental_loader import IncrementalLoader
from loading.connection import get_db_session
from loading.models import ETLRun, AuditLog, Customer

def test_incremental_loader_run_tracking():
    loader = IncrementalLoader(dry_run_snowflake=True)
    job_name = "test_job"

    # Start a run
    run_id = loader.create_run_record(job_name)
    assert run_id is not None

    with get_db_session() as session:
        run = session.query(ETLRun).filter(ETLRun.id == run_id).one()
        assert run.status == "RUNNING"
        assert run.job_name == job_name

    # End the run successfully
    loader.update_run_record(run_id, "SUCCESS", 42, "cursor_123")

    with get_db_session() as session:
        run = session.query(ETLRun).filter(ETLRun.id == run_id).one()
        assert run.status == "SUCCESS"
        assert run.records_processed == 42
        assert run.last_cursor_value == "cursor_123"

    # Get last cursor
    cursor = loader.get_last_successful_cursor(job_name)
    assert cursor == "cursor_123"

def test_incremental_loader_audit():
    loader = IncrementalLoader(dry_run_snowflake=True)
    run_id = loader.create_run_record("test_audit_job")
    
    loader.log_audit(run_id, "customers", "INSERT", ["cus_1", "cus_2"])

    with get_db_session() as session:
        audit = session.query(AuditLog).filter(AuditLog.etl_run_id == run_id).one()
        assert audit.table_name == "customers"
        assert audit.operation == "INSERT"
        assert "batch_count_2" in audit.record_id
