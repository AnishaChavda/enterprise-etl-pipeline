import logging
from datetime import datetime
from typing import Any, Dict, List, Sequence

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError

from db.postgres import SessionLocal
from db.snowflake import get_snowflake_engine
from db.models import (
    AuditLog,
    Customer,
    ETLJobRun,
    RawCustomer,
    StagingCustomer,
)
from utils.notifications import send_slack_notification, send_email

LOGGER = logging.getLogger("etl.load")
logging.basicConfig(level=logging.INFO)


def upsert_postgres(model, records: List[Dict[str, Any]], conflict_columns: Sequence[str]):
    if not records:
        return 0

    session = SessionLocal()
    inserted = 0
    try:
        stmt = pg_insert(model).values(records)
        update_columns = {
            column.name: getattr(stmt.excluded, column.name)
            for column in model.__table__.columns
            if column.name not in ["id"]
        }
        stmt = stmt.on_conflict_do_update(index_elements=list(conflict_columns), set_=update_columns)
        result = session.execute(stmt)
        session.commit()
        inserted = result.rowcount or 0
        LOGGER.info("Upserted %s rows into %s", inserted, model.__tablename__)
    except SQLAlchemyError as exc:
        session.rollback()
        LOGGER.error("Postgres upsert failed for %s: %s", model.__tablename__, exc)
        raise
    finally:
        session.close()
    return inserted


def load_customers(records: List[Dict[str, Any]]):
    if not records:
        LOGGER.warning("No customer records to load")
        return 0

    raw_payloads = [
        {
            "customer_id": row["customer_id"],
            "payload": row,
            "source_created_at": row["created_date"],
        }
        for row in records
    ]

    upsert_postgres(RawCustomer, raw_payloads, ["customer_id"])
    upsert_postgres(StagingCustomer, records, ["customer_id"])
    inserted = upsert_postgres(Customer, records, ["customer_id"])
    return inserted


def record_etl_job(
    job_name: str,
    status: str,
    start_time: datetime,
    end_time: datetime,
    processed: int,
    failed: int = 0,
    retries: int = 0,
    error: str | None = None,
):
    session = SessionLocal()
    try:
        session.add(
            ETLJobRun(
                job_name=job_name,
                status=status,
                start_time=start_time,
                end_time=end_time,
                processed_records=processed,
                failed_records=failed,
                retry_count=retries,
                error_message=error,
            )
        )
        session.commit()
    except Exception as exc:
        session.rollback()
        LOGGER.error("Failed to record ETL job run: %s", exc)
    finally:
        session.close()


def merge_into_snowflake(table_name: str, records: List[Dict[str, Any]], key_fields: List[str]):
    if not records:
        return 0

    def quote_value(value):
        if value is None:
            return "NULL"
        return f"'{str(value).replace("'", "''")}'"

    engine = get_snowflake_engine()
    with engine.connect() as connection:
        columns = list(records[0].keys())
        staged_values = ", ".join(
            ["(" + ", ".join(quote_value(record[col]) for col in columns) + ")" for record in records]
        )
        columns_csv = ", ".join(columns)
        merge_condition = " AND ".join([f"target.{key} = source.{key}" for key in key_fields])
        update_set = ", ".join(
            [f"target.{c}=source.{c}" for c in columns if c not in key_fields]
        )
        merge_sql = f"""
            MERGE INTO {table_name} AS target
            USING (SELECT {columns_csv} FROM VALUES {staged_values}) AS source ({columns_csv})
            ON {merge_condition}
            WHEN MATCHED THEN UPDATE SET {update_set}
            WHEN NOT MATCHED THEN INSERT ({columns_csv}) VALUES ({columns_csv})
        """
        try:
            connection.execute(text(merge_sql))
            LOGGER.info("Snowflake merge completed for %s", table_name)
            return len(records)
        except Exception as exc:
            LOGGER.error("Snowflake merge failed: %s", exc)
            raise


def send_etl_alert(subject: str, body: str):
    send_slack_notification(subject + "\n" + body)
    send_email(subject, body, [])
