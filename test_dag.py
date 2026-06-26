import pytest
import sys
import os

def test_dag_instantiation():
    """
    Tests that the DAG imports and instantiates task structures without errors.
    """
    # Add DAG folder path to sys.path so it can be imported as a standalone module
    dag_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../airflow/dags"))
    if dag_path not in sys.path:
        sys.path.append(dag_path)

    import daily_etl_pipeline as dag_mod
    
    assert dag_mod.dag is not None
    # Verify tasks are declared
    assert dag_mod.salesforce_task is not None
    assert dag_mod.zendesk_task is not None
    assert dag_mod.run_pipeline_task is not None
