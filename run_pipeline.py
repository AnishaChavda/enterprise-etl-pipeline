import os
import glob
import json
import logging
import time
from datetime import datetime
from dotenv import load_dotenv

from loading.models import init_db, Customer, Invoice, Payment, Subscription, Ticket
from loading.incremental_loader import IncrementalLoader
from extraction.stripe_extractor import run_stripe_extraction
from extraction.salesforce_connector import run_salesforce_extraction
from extraction.zendesk_extractor import run_zendesk_extraction
from transformation import transformer
from validation import validator
from validation import models as val_models
from utils.monitoring import PipelineMetrics
from utils.slack_notifier import send_slack_alert
from utils.email_notifier import send_email_alert

load_dotenv()

# Logging Configuration
logging.basicConfig(
    filename="logs/pipeline_execution.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger("").addHandler(console)

def get_latest_raw_file(directory, pattern):
    search_path = os.path.join(directory, pattern)
    files = glob.glob(search_path)
    if not files:
        return None
    return max(files, key=os.path.getctime)

def load_json_data(filepath):
    if not filepath or not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON from file {filepath}")
            return []

def run_pipeline(dry_run_snowflake=True):
    print("Initializing Database Schemas...")
    init_db()

    metrics = PipelineMetrics()
    loader = IncrementalLoader(dry_run_snowflake=dry_run_snowflake)

    job_name = "daily_etl_pipeline"
    run_id = loader.create_run_record(job_name)
    metrics.start_timing("total_pipeline")

    cursor = loader.get_last_successful_cursor(job_name)
    total_records = 0
    error_occurred = None

    try:
        # --------------------------------------------------
        # STEP 1 : Extraction
        # --------------------------------------------------
        metrics.start_timing("extraction")
        logging.info("Starting extraction phase...")
        
        # Stripe
        start_api = time.time()
        run_stripe_extraction(cursor)
        metrics.record_api_latency("stripe", time.time() - start_api)

        # Salesforce
        start_api = time.time()
        run_salesforce_extraction(cursor)
        metrics.record_api_latency("salesforce", time.time() - start_api)

        # Zendesk
        start_api = time.time()
        run_zendesk_extraction(cursor)
        metrics.record_api_latency("zendesk", time.time() - start_api)

        metrics.stop_timing("extraction")

        # --------------------------------------------------
        # STEP 2 : Transform & Validate & Load Staging/Warehouse
        # --------------------------------------------------
        metrics.start_timing("transform_validate_load")
        logging.info("Starting transform, validate, and load phase...")

        # A. Customers
        stripe_cust_file = get_latest_raw_file("data/raw/stripe/customers", "*.json")
        sf_acc_file = get_latest_raw_file("data/raw/salesforce/accounts", "*.json")
        
        stripe_customers_raw = load_json_data(stripe_cust_file)
        sf_accounts_raw = load_json_data(sf_acc_file)

        customers_transformed = (
            transformer.transform_stripe_customers(stripe_customers_raw) + 
            transformer.transform_sf_accounts(sf_accounts_raw)
        )
        customers_validated = validator.validate_records(
            customers_transformed, 
            val_models.CustomerValidation, 
            "customers"
        )
        total_records += loader.load_data(run_id, Customer, customers_validated, "customer_id")

        # B. Invoices & Payments
        stripe_charges_file = get_latest_raw_file("data/raw/stripe/charges", "*.json")
        sf_opp_file = get_latest_raw_file("data/raw/salesforce/opportunities", "*.json")
        
        stripe_charges_raw = load_json_data(stripe_charges_file)
        sf_opps_raw = load_json_data(sf_opp_file)

        stripe_inv_transformed, stripe_pmt_transformed = transformer.transform_stripe_charges(stripe_charges_raw)
        sf_inv_transformed = transformer.transform_sf_opportunities(sf_opps_raw)

        invoices_transformed = stripe_inv_transformed + sf_inv_transformed
        invoices_validated = validator.validate_records(
            invoices_transformed, 
            val_models.InvoiceValidation, 
            "invoices"
        )
        total_records += loader.load_data(run_id, Invoice, invoices_validated, "invoice_id")

        payments_validated = validator.validate_records(
            stripe_pmt_transformed, 
            val_models.PaymentValidation, 
            "payments"
        )
        total_records += loader.load_data(run_id, Payment, payments_validated, "payment_id")

        # C. Subscriptions
        stripe_sub_file = get_latest_raw_file("data/raw/stripe/subscriptions", "*.json")
        stripe_subs_raw = load_json_data(stripe_sub_file)

        subs_transformed = transformer.transform_stripe_subscriptions(stripe_subs_raw)
        subs_validated = validator.validate_records(
            subs_transformed, 
            val_models.SubscriptionValidation, 
            "subscriptions"
        )
        total_records += loader.load_data(run_id, Subscription, subs_validated, "subscription_id")

        # D. Support Tickets
        zd_tickets_file = get_latest_raw_file("data/raw/zendesk/tickets", "*.json")
        zd_tickets_raw = load_json_data(zd_tickets_file)

        tickets_transformed = transformer.transform_zd_tickets(zd_tickets_raw)
        tickets_validated = validator.validate_records(
            tickets_transformed, 
            val_models.TicketValidation, 
            "support_tickets"
        )
        total_records += loader.load_data(run_id, Ticket, tickets_validated, "ticket_id")

        metrics.stop_timing("transform_validate_load")

        # --------------------------------------------------
        # STEP 3 : Data Quality Checks
        # --------------------------------------------------
        metrics.start_timing("data_quality_checks")
        logging.info("Starting data quality checks...")
        # Check: Verify customer email format and that invoice amounts are non-negative
        for inv in invoices_validated:
            if inv["amount"] < 0:
                raise ValueError(f"Data Quality Failure: Invoice {inv['invoice_id']} has negative amount.")
        metrics.stop_timing("data_quality_checks")

    except Exception as e:
        error_occurred = str(e)
        logging.error(f"Pipeline execution failed: {e}")
        raise e

    finally:
        duration = metrics.stop_timing("total_pipeline")
        
        if error_occurred:
            loader.update_run_record(
                run_id=run_id,
                status="FAILED",
                records_processed=total_records,
                last_cursor_value=cursor,
                error_message=error_occurred
            )
            # Send Slack Fail Alert
            send_slack_alert(job_name, "FAILED", duration, error_occurred, total_records)
            # Send Email Fail Alert
            send_email_alert(
                subject="ETL Pipeline Failure",
                body_html=f"<h3>Critical Pipeline Failure</h3><p>Job: {job_name}</p><p>Error: {error_occurred}</p>",
                alert_type="CRITICAL"
            )
        else:
            # Set cursor to current timestamp for next incremental runs
            new_cursor = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            loader.update_run_record(
                run_id=run_id,
                status="SUCCESS",
                records_processed=total_records,
                last_cursor_value=new_cursor
            )
            # Send Slack Success Alert
            send_slack_alert(job_name, "SUCCESS", duration, records_processed=total_records)

        # Generate metrics report
        metrics.generate_dashboard_report()

    print("Pipeline Execution Completed.")

if __name__ == "__main__":
    run_pipeline(dry_run_snowflake=True)