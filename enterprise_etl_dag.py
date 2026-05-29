from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Ensure the root project directory is in the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extraction.stripe_extractor import extract_stripe_data
from extraction.salesforce_extractor import extract_salesforce_data
from transformation.clean_data import clean_data
from loading.db_loader import load_data

# Mock email alert callback
def on_failure_callback(context):
    print(f"!!! AIRFLOW ALERT !!! - Task {context.get('task_instance').task_id} failed. Sending alert email to data-team@enterprise.com...")

default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False, # Disabled real emails for this mock
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': on_failure_callback
}

dag = DAG(
    'enterprise_etl_pipeline',
    default_args=default_args,
    description='A DAG to execute the full enterprise ETL pipeline',
    schedule_interval=timedelta(days=1), # Runs daily
    catchup=False
)

task_extract_stripe = PythonOperator(
    task_id='extract_stripe_data',
    python_callable=extract_stripe_data,
    dag=dag,
)

task_extract_salesforce = PythonOperator(
    task_id='extract_salesforce_data',
    python_callable=extract_salesforce_data,
    dag=dag,
)

task_transform_data = PythonOperator(
    task_id='transform_and_clean_data',
    python_callable=clean_data,
    dag=dag,
)

task_load_data = PythonOperator(
    task_id='load_data_to_warehouse',
    python_callable=load_data,
    dag=dag,
)

# Set dependencies: Extract -> Transform -> Load
[task_extract_stripe, task_extract_salesforce] >> task_transform_data >> task_load_data
