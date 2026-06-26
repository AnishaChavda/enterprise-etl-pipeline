import logging
from datetime import datetime

from db.postgres import init_postgres
from db.snowflake import initialize_snowflake
from etl.extract import (
    extract_salesforce_data,
    extract_stripe_charges,
    extract_stripe_customers,
    extract_stripe_payments,
    extract_zendesk_tickets,
)
from etl.load import (
    load_customers,
    merge_into_snowflake,
    record_etl_job,
    send_etl_alert,
)
from etl.transform import clean_customers, validate_customers, transform_support_tickets
from utils.notifications import send_slack_notification, send_email

LOGGER = logging.getLogger("etl.pipeline")
logging.basicConfig(level=logging.INFO)


def run_daily_etl():
    start_time = datetime.utcnow()
    job_name = "daily_etl_pipeline"
    try:
        init_postgres()
        initialize_snowflake()

        raw_customers = extract_stripe_customers()
        raw_charges = extract_stripe_charges()
        raw_payments = extract_stripe_payments()
        raw_salesforce = extract_salesforce_data()
        raw_tickets = extract_zendesk_tickets()

        cleaned_customers = clean_customers(raw_customers)
        validated_customers = validate_customers(cleaned_customers)

        processed_customer_count = load_customers(validated_customers)

        merge_into_snowflake("RAW.CUSTOMERS", validated_customers, ["customer_id"])

        record_etl_job(
            job_name=job_name,
            status="SUCCESS",
            start_time=start_time,
            end_time=datetime.utcnow(),
            processed=processed_customer_count,
        )

        success_message = (
            f"ETL job completed successfully. Customers loaded: {processed_customer_count}."
        )
        LOGGER.info(success_message)
        send_slack_notification(success_message)
        return True
    except Exception as exc:
        LOGGER.exception("ETL pipeline failed: %s", exc)
        record_etl_job(
            job_name=job_name,
            status="FAILED",
            start_time=start_time,
            end_time=datetime.utcnow(),
            processed=0,
            failed=1,
            error=str(exc),
        )
        send_etl_alert(
            subject="ETL Failure: daily_etl_pipeline",
            body=str(exc),
        )
        return False
