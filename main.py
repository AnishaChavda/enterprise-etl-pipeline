from extraction.stripe_extractor import extract_stripe_data
from extraction.salesforce_extractor import extract_salesforce_data
from transformation.clean_data import clean_data
from loading.db_loader import load_data
import time

def send_slack_alert(error_message):
    print(f"\n[ALERT NOTIFICATION] Sending Slack alert to #data-engineering channel: {error_message}")

def run_pipeline():
    print("=======================================")
    print("Starting Enterprise ETL Pipeline...")
    print("=======================================")
    
    try:
        # Phase 1: Extraction
        print("\n--- PHASE 1: EXTRACTION ---")
        extract_stripe_data()
        extract_salesforce_data()
        
        time.sleep(1)
        
        # Phase 2: Transformation
        print("\n--- PHASE 2: TRANSFORMATION ---")
        clean_data()
        
        time.sleep(1)
        
        # Phase 3: Loading
        print("\n--- PHASE 3: LOADING ---")
        load_data()
        
        print("\n=======================================")
        print("Pipeline Execution Completed Successfully!")
        print("=======================================")
    except Exception as e:
        print("\n=======================================")
        print("PIPELINE FAILED!")
        print("=======================================")
        send_slack_alert(f"ETL Pipeline Failed unexpectedly. Error: {str(e)}")
        raise e

if __name__ == "__main__":
    run_pipeline()
