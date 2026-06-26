import pytest
import os
from run_pipeline import run_pipeline
from loading.connection import get_db_session
from loading.models import Customer, Invoice, Payment, Subscription, Ticket, ETLRun

def test_full_pipeline_e2e():
    """
    Simulates a full end-to-end run: API -> Extraction -> Transformation -> Loading -> Reporting
    and checks if the database is populated.
    """
    # Run the pipeline with Snowflake dry-run enabled
    run_pipeline(dry_run_snowflake=True)

    # Query local SQLite database to verify data has been populated by the pipeline run
    with get_db_session() as session:
        # Check Customers
        customers = session.query(Customer).all()
        assert len(customers) > 0, "No customers populated by the pipeline."
        assert any(c.source == "stripe" for c in customers), "Stripe customers missing."
        assert any(c.source == "salesforce" for c in customers), "Salesforce accounts missing."

        # Check Invoices & Payments
        invoices = session.query(Invoice).all()
        assert len(invoices) > 0, "No invoices loaded."
        
        payments = session.query(Payment).all()
        assert len(payments) > 0, "No payments loaded."

        # Check Subscriptions
        subs = session.query(Subscription).all()
        assert len(subs) > 0, "No subscriptions loaded."

        # Check Support Tickets
        tickets = session.query(Ticket).all()
        assert len(tickets) > 0, "No support tickets loaded."

        # Check ETLRun
        runs = session.query(ETLRun).all()
        assert len(runs) > 0, "No run records written."
        assert runs[0].status == "SUCCESS", "Pipeline job run failed."
