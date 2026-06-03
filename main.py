from extraction.stripe_extractor import extract_stripe_data
from extraction.salesforce_extractor import extract_salesforce_data
from extraction.zendesk_extractor import extract_zendesk_data
from transformation.clean_data import clean_data
from loading.cdc_loader import load_stripe_customers_cdc, load_salesforce_orders_cdc, load_zendesk_tickets_cdc
from utils.alerting import send_slack_alert, send_email_alert
from config.database import init_db
import time

def run_pipeline():
    start_time = time.time()
    print("=======================================")
    print("Starting Enterprise ETL Pipeline...")
    print("=======================================")
    
    try:
        # Initialize Database schemas
        print("\n--- INITIALIZING DATABASE SCHEMAS ---")
        init_db()
        # Phase 1: Extraction
        print("\n--- PHASE 1: EXTRACTION ---")
        extract_stripe_data()
        extract_salesforce_data()
        extract_zendesk_data()
        
        time.sleep(1)
        
        # Phase 2: Transformation
        print("\n--- PHASE 2: TRANSFORMATION ---")
        clean_data()
        
        time.sleep(1)
        
        # Phase 3: Loading
        print("\n--- PHASE 3: LOADING ---")
        load_stripe_customers_cdc()
        load_salesforce_orders_cdc()
        load_zendesk_tickets_cdc()
        
        execution_time = time.time() - start_time
        print("\n=======================================")
        print("Pipeline Execution Completed Successfully!")
        print("=======================================")
        
        # Alert Success
        send_slack_alert("Enterprise ETL Pipeline", "SUCCESS", execution_time)
        
    except Exception as e:
        execution_time = time.time() - start_time
        print("\n=======================================")
        print("PIPELINE FAILED!")
        print("=======================================")
        
        # Alert Failure
        send_slack_alert("Enterprise ETL Pipeline", "FAILED", execution_time, error_summary=str(e))
        send_email_alert("Enterprise ETL Pipeline", "FAILED", execution_time, error_summary=str(e))
        raise e

if __name__ == "__main__":
    run_pipeline()
