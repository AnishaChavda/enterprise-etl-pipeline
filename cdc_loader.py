import os
import sys
import traceback
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text

# Adjust sys.path to ensure we can load our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.database import get_db_session, get_db_engine
from models.sqlalchemy_models import (
    Customer, Order, Payment, SupportTicket, AuditLog, ETLJobLog, ETLMetadata
)

class CDCLoader:
    """Handles incremental loading (CDC) and upsert logic into the warehouse."""

    def __init__(self, job_name: str, source_system: str, entity_type: str):
        self.job_name = job_name
        self.source_system = source_system.lower()
        self.entity_type = entity_type.lower()
        self.db_type = os.getenv("DATABASE_TYPE", "sqlite").lower()

    def get_last_run_timestamp(self, session: Session) -> datetime:
        """Fetch the last successful extraction/run timestamp for incremental extracts."""
        metadata = session.query(ETLMetadata).filter_by(
            source_system=self.source_system,
            entity_type=self.entity_type
        ).first()
        if metadata and metadata.last_successful_run:
            return metadata.last_successful_run
        # Return fallback far in past
        return datetime(2000, 1, 1)

    def update_etl_metadata(self, session: Session, records_processed: int, records_loaded: int):
        """Update last run metadata for incremental syncing."""
        metadata = session.query(ETLMetadata).filter_by(
            source_system=self.source_system,
            entity_type=self.entity_type
        ).first()

        now = datetime.utcnow()
        if not metadata:
            metadata = ETLMetadata(
                source_system=self.source_system,
                entity_type=self.entity_type,
                last_successful_run=now,
                last_extraction_timestamp=now,
                total_records_extracted=records_processed,
                total_records_loaded=records_loaded,
                is_active=True
            )
            session.add(metadata)
        else:
            metadata.last_successful_run = now
            metadata.last_extraction_timestamp = now
            metadata.total_records_extracted += records_processed
            metadata.total_records_loaded += records_loaded
            
    def log_job_start(self, session: Session) -> ETLJobLog:
        """Create a new job run log entry."""
        job_log = ETLJobLog(
            job_name=self.job_name,
            status="RUNNING",
            start_time=datetime.utcnow(),
            total_records_processed=0,
            total_records_inserted=0,
            total_records_updated=0,
            total_records_failed=0
        )
        session.add(job_log)
        session.commit()
        return job_log

    def log_job_end(self, session: Session, job_log: ETLJobLog, status: str, 
                    processed: int = 0, inserted: int = 0, updated: int = 0, 
                    failed: int = 0, error: str = None, traceback_str: str = None):
        """Finalize job execution run entry."""
        now = datetime.utcnow()
        job_log.status = status
        job_log.end_time = now
        job_log.total_records_processed = processed
        job_log.total_records_inserted = inserted
        job_log.total_records_updated = updated
        job_log.total_records_failed = failed
        job_log.error_message = error
        job_log.error_traceback = traceback_str
        job_log.execution_time_seconds = (now - job_log.start_time).total_seconds()
        
        session.add(job_log)
        session.commit()

    def upsert_records(self, model_class, records: list) -> tuple:
        """
        Generic robust row-by-row CDC upsert.
        Calculates column differences, writes AuditLogs, and saves to database.
        Returns: (inserted_count, updated_count)
        """
        session = get_db_session()
        job_log = self.log_job_start(session)
        
        inserted_count = 0
        updated_count = 0
        failed_count = 0
        
        pk_name = inspect(model_class).primary_key[0].name
        
        try:
            for raw_rec in records:
                # Clean Pandas float NaN/NaT values to None for clean database insertion
                rec = {k: (None if pd.isna(v) else v) for k, v in raw_rec.items()}
                try:
                    pk_value = rec.get(pk_name)
                    if not pk_value:
                        raise ValueError(f"Primary key '{pk_name}' missing in record.")
                    
                    # Fetch existing record
                    existing = session.query(model_class).filter(getattr(model_class, pk_name) == pk_value).first()
                    
                    if existing:
                        # Perform column comparison
                        old_values = {}
                        new_values = {}
                        changed = False
                        
                        for col in inspect(model_class).columns:
                            col_name = col.name
                            if col_name in rec:
                                current_val = getattr(existing, col_name)
                                input_val = rec[col_name]

                                # Normalize placeholder strings to None
                                if isinstance(input_val, str) and input_val.strip().upper() in ("N/A", ""):
                                    input_val = None

                                # Convert ISO datetime strings to datetime when column expects datetime
                                try:
                                    col_py_type = getattr(col.type, 'python_type', None)
                                except Exception:
                                    col_py_type = None

                                if isinstance(input_val, str) and col_py_type is datetime:
                                    try:
                                        input_val = datetime.fromisoformat(input_val)
                                    except Exception:
                                        # leave as string if parsing fails; SQLAlchemy will raise later
                                        pass

                                if current_val != input_val:
                                    old_values[col_name] = str(current_val) if current_val is not None else None
                                    new_values[col_name] = str(input_val) if input_val is not None else None
                                    setattr(existing, col_name, input_val)
                                    changed = True
                        
                        if changed:
                            # Log audit record
                            audit = AuditLog(
                                customer_id=rec.get("customer_id") if hasattr(model_class, "customer_id") else None,
                                table_name=model_class.__tablename__,
                                operation="UPDATE",
                                old_values=old_values,
                                new_values=new_values,
                                changed_by="etl_cdc_loader",
                                change_reason="Incremental sync update"
                            )
                            session.add(audit)
                            updated_count += 1
                    else:
                        # Insert brand new record
                        # Filter only valid columns matching table fields
                        valid_data = {}
                        for col in inspect(model_class).columns:
                            col_name = col.name
                            if col_name in rec:
                                val = rec[col_name]
                                if isinstance(val, str) and col.type.python_type == datetime:
                                    try:
                                        val = datetime.fromisoformat(val)
                                    except ValueError:
                                        pass
                                valid_data[col_name] = val
                        
                        new_rec = model_class(**valid_data)
                        session.add(new_rec)
                        
                        # Log audit record
                        audit = AuditLog(
                            customer_id=rec.get("customer_id") if hasattr(model_class, "customer_id") else None,
                            table_name=model_class.__tablename__,
                            operation="INSERT",
                            new_values={k: str(v) for k, v in valid_data.items() if v is not None},
                            changed_by="etl_cdc_loader",
                            change_reason="Incremental sync insert"
                        )
                        session.add(audit)
                        inserted_count += 1
                        
                except Exception as row_err:
                    failed_count += 1
                    print(f"Error processing row pk={rec.get(pk_name)}: {str(row_err)}")
            
            # Update last metadata run timestamp
            self.update_etl_metadata(session, len(records), inserted_count + updated_count)
            session.commit()
            
            self.log_job_end(
                session, job_log, "SUCCESS", 
                processed=len(records), 
                inserted=inserted_count, 
                updated=updated_count, 
                failed=failed_count
            )
            
        except Exception as e:
            session.rollback()
            error_msg = str(e)
            traceback_str = traceback.format_exc()
            self.log_job_end(
                session, job_log, "FAILED", 
                processed=len(records), 
                inserted=0, 
                updated=0, 
                failed=len(records),
                error=error_msg,
                traceback_str=traceback_str
            )
            raise e
        finally:
            session.close()
            
        return inserted_count, updated_count

# Convenience functions to run load for Salesforce, Stripe, Zendesk
def load_stripe_customers_cdc():
    csv_path = "data/processed/cleaned_stripe_users.csv"
    if not os.path.exists(csv_path):
        print(f"No cleaned Stripe data found at {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    records = []
    
    for _, row in df.iterrows():
        # Map cleaned_stripe_users schema to Customer ORM model fields
        name_parts = str(row["name"]).split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else "N/A"
        
        records.append({
            "customer_id": f"STRIPE-CUST-{row['user_id']}",
            "first_name": first_name,
            "last_name": last_name,
            "email": row["email"],
            "phone": row["phone"],
            "company_name": row["company_name"],
            "source_system": "stripe",
            "external_id": str(row["user_id"])
        })
        
    loader = CDCLoader("Stripe Customers Load", "stripe", "customer")
    inserted, updated = loader.upsert_records(Customer, records)
    print(f"Stripe CDC Load complete: {inserted} inserted, {updated} updated.")

def load_salesforce_orders_cdc():
    csv_path = "data/processed/cleaned_salesforce_posts.csv"
    if not os.path.exists(csv_path):
        print(f"No cleaned Salesforce data found at {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    records = []
    
    # Pre-populate customers if they don't exist to satisfy foreign key constraints
    # (Since Stripe user_id 1-10 are loaded as Stripe Customers, Salesforce user_id 1-10 can map directly!)
    session = get_db_session()
    for _, row in df.iterrows():
        cust_id = f"STRIPE-CUST-{row['user_id']}"
        customer = session.query(Customer).filter_by(customer_id=cust_id).first()
        if not customer:
            # Create a placeholder customer so FK doesn't fail
            customer = Customer(
                customer_id=cust_id,
                first_name="SF Placeholder",
                last_name=str(row["user_id"]),
                email=f"sf_placeholder_{row['user_id']}@example.com",
                source_system="salesforce",
                external_id=str(row["user_id"])
            )
            session.add(customer)
    session.commit()
    session.close()
    
    for _, row in df.iterrows():
        # Map Salesforce post/tickets to Order ORM model fields
        records.append({
            "order_id": f"SF-ORDER-{row['post_id']}",
            "customer_id": f"STRIPE-CUST-{row['user_id']}",
            "order_date": datetime.utcnow().isoformat(),
            "total_amount": 150.00,  # Mock pricing
            "currency": "USD",
            "status": "completed",
            "source_system": "salesforce",
            "external_id": str(row["post_id"])
        })
        
    loader = CDCLoader("Salesforce Orders Load", "salesforce", "order")
    inserted, updated = loader.upsert_records(Order, records)
    print(f"Salesforce CDC Load complete: {inserted} inserted, {updated} updated.")

def load_zendesk_tickets_cdc():
    csv_path = "data/processed/cleaned_zendesk_tickets.csv"
    if not os.path.exists(csv_path):
        print(f"No cleaned Zendesk data found at {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    records = []
    
    # Pre-populate customers if needed
    session = get_db_session()
    for _, row in df.iterrows():
        cust_id = f"STRIPE-CUST-{row['customer_id']}"
        customer = session.query(Customer).filter_by(customer_id=cust_id).first()
        if not customer:
            customer = Customer(
                customer_id=cust_id,
                first_name="ZDK Placeholder",
                last_name=str(row["customer_id"]),
                email=f"zdk_placeholder_{row['customer_id']}@example.com",
                source_system="zendesk",
                external_id=str(row["customer_id"])
            )
            session.add(customer)
    session.commit()
    session.close()
    
    for _, row in df.iterrows():
        records.append({
            "ticket_id": row["ticket_id"],
            "customer_id": f"STRIPE-CUST-{row['customer_id']}",
            "title": row["title"],
            "description": row["description"],
            "priority": row["priority"],
            "status": row["status"],
            "assigned_to": row["assigned_to"],
            "created_date": row["created_date"],
            "resolved_date": row["resolved_date"] if row["resolved_date"] != "N/A" else None,
            "source_system": "zendesk",
            "external_id": str(row["external_id"])
        })
        
    loader = CDCLoader("Zendesk Tickets Load", "zendesk", "ticket")
    inserted, updated = loader.upsert_records(SupportTicket, records)
    print(f"Zendesk CDC Load complete: {inserted} inserted, {updated} updated.")

if __name__ == "__main__":
    from config.database import init_db
    init_db()  # Setup tables first
    load_stripe_customers_cdc()
    load_salesforce_orders_cdc()
    load_zendesk_tickets_cdc()
