"""
SQLAlchemy ORM models for the ETL data warehouse.
Includes support for soft deletes, timestamps, and audit trails.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Text,
    ForeignKey, Index, UniqueConstraint, CheckConstraint, Enum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from config.database import Base
import enum
import uuid

# Ensure we're using the same Base as database.py
from config.database import Base


class SoftDeleteMixin:
    """Mixin to add soft delete support to models."""
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)


class TimestampMixin:
    """Mixin to add timestamp tracking to models."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Customer(Base, TimestampMixin, SoftDeleteMixin):
    """Customer data model."""
    __tablename__ = "customers"
    
    customer_id = Column(String(50), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    company_name = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    street_address = Column(String(255), nullable=True)
    
    # Source tracking
    source_system = Column(String(50), nullable=False)  # e.g., 'salesforce', 'stripe'
    external_id = Column(String(255), nullable=True)
    
    # Relationships
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="customer", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="customer", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_customer_email", "email"),
        Index("idx_customer_source_external_id", "source_system", "external_id"),
        Index("idx_customer_created_at", "created_at"),
        UniqueConstraint("source_system", "external_id", name="uq_source_external_id"),
    )
    
    def __repr__(self):
        return f"<Customer {self.customer_id}: {self.first_name} {self.last_name}>"


class Order(Base, TimestampMixin, SoftDeleteMixin):
    """Order data model."""
    __tablename__ = "orders"
    
    order_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    
    order_date = Column(DateTime, nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(String(50), nullable=False, index=True)  # e.g., 'pending', 'completed', 'cancelled'
    
    # Shipping information
    shipping_address = Column(String(500), nullable=True)
    shipping_date = Column(DateTime, nullable=True)
    delivery_date = Column(DateTime, nullable=True)
    
    # Metadata
    source_system = Column(String(50), nullable=False)
    external_id = Column(String(255), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_order_customer_id", "customer_id"),
        Index("idx_order_date", "order_date"),
        Index("idx_order_status", "status"),
        Index("idx_order_source_external_id", "source_system", "external_id"),
    )
    
    def __repr__(self):
        return f"<Order {self.order_id}: {self.total_amount} {self.currency}>"


class OrderItem(Base, TimestampMixin):
    """Order item details."""
    __tablename__ = "order_items"
    
    item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(50), ForeignKey("orders.order_id"), nullable=False, index=True)
    
    product_id = Column(String(100), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, CheckConstraint("quantity > 0"), nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    
    __table_args__ = (
        Index("idx_order_item_order_id", "order_id"),
        Index("idx_order_item_product_id", "product_id"),
    )


class Payment(Base, TimestampMixin, SoftDeleteMixin):
    """Payment data model."""
    __tablename__ = "payments"
    
    payment_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    order_id = Column(String(50), ForeignKey("orders.order_id"), nullable=True, index=True)
    
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    payment_method = Column(String(50), nullable=False)  # e.g., 'credit_card', 'bank_transfer'
    status = Column(String(50), nullable=False, index=True)  # e.g., 'pending', 'completed', 'failed'
    
    payment_date = Column(DateTime, nullable=False, index=True)
    transaction_id = Column(String(255), unique=True, nullable=True)
    
    # Metadata
    source_system = Column(String(50), nullable=False)
    external_id = Column(String(255), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="payments")
    order = relationship("Order", back_populates="payments")
    
    __table_args__ = (
        Index("idx_payment_customer_id", "customer_id"),
        Index("idx_payment_order_id", "order_id"),
        Index("idx_payment_date", "payment_date"),
        Index("idx_payment_status", "status"),
        Index("idx_payment_source_external_id", "source_system", "external_id"),
    )
    
    def __repr__(self):
        return f"<Payment {self.payment_id}: {self.amount} {self.currency}>"


class SupportTicket(Base, TimestampMixin, SoftDeleteMixin):
    """Support ticket data model."""
    __tablename__ = "support_tickets"
    
    ticket_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), nullable=False, index=True)  # e.g., 'low', 'medium', 'high', 'critical'
    status = Column(String(50), nullable=False, index=True)  # e.g., 'open', 'in_progress', 'resolved', 'closed'
    
    assigned_to = Column(String(100), nullable=True)
    created_date = Column(DateTime, nullable=False, index=True)
    resolved_date = Column(DateTime, nullable=True)
    
    # Metadata
    source_system = Column(String(50), nullable=False)
    external_id = Column(String(255), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    # Relationships
    customer = relationship("Customer", foreign_keys=[customer_id])
    comments = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_ticket_customer_id", "customer_id"),
        Index("idx_ticket_status", "status"),
        Index("idx_ticket_priority", "priority"),
        Index("idx_ticket_created_date", "created_date"),
        Index("idx_ticket_source_external_id", "source_system", "external_id"),
    )


class TicketComment(Base, TimestampMixin):
    """Support ticket comments."""
    __tablename__ = "ticket_comments"
    
    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(50), ForeignKey("support_tickets.ticket_id"), nullable=False, index=True)
    
    comment_text = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)
    comment_date = Column(DateTime, nullable=False, index=True)
    
    # Relationships
    ticket = relationship("SupportTicket", back_populates="comments")


class AuditLog(Base, TimestampMixin):
    """Audit log for tracking data changes."""
    __tablename__ = "audit_logs"
    
    audit_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=True, index=True)
    
    table_name = Column(String(100), nullable=False, index=True)
    operation = Column(String(20), nullable=False)  # INSERT, UPDATE, DELETE
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    changed_by = Column(String(100), nullable=True)
    change_reason = Column(String(500), nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="audit_logs")
    
    __table_args__ = (
        Index("idx_audit_customer_id", "customer_id"),
        Index("idx_audit_table_name", "table_name"),
        Index("idx_audit_created_at", "created_at"),
    )


class ETLJobLog(Base, TimestampMixin):
    """ETL job execution logs."""
    __tablename__ = "etl_job_logs"
    
    job_log_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_name = Column(String(255), nullable=False, index=True)
    
    status = Column(String(20), nullable=False, index=True)  # RUNNING, SUCCESS, FAILED, SKIPPED
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    
    total_records_processed = Column(Integer, default=0)
    total_records_inserted = Column(Integer, default=0)
    total_records_updated = Column(Integer, default=0)
    total_records_failed = Column(Integer, default=0)
    
    error_message = Column(Text, nullable=True)
    error_traceback = Column(Text, nullable=True)
    
    execution_time_seconds = Column(Float, nullable=True)
    
    __table_args__ = (
        Index("idx_etl_job_name", "job_name"),
        Index("idx_etl_status", "status"),
        Index("idx_etl_start_time", "start_time"),
    )
    
    def __repr__(self):
        return f"<ETLJobLog {self.job_name}: {self.status}>"


class ETLMetadata(Base, TimestampMixin):
    """ETL metadata for incremental loading."""
    __tablename__ = "etl_metadata"
    
    metadata_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    source_system = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)  # e.g., 'customer', 'order', 'payment'
    
    last_successful_run = Column(DateTime, nullable=True)
    last_extraction_timestamp = Column(DateTime, nullable=True)
    last_extraction_id = Column(String(255), nullable=True)
    
    total_records_extracted = Column(Integer, default=0)
    total_records_loaded = Column(Integer, default=0)
    
    next_run_time = Column(DateTime, nullable=True)
    
    # Configuration
    incremental_enabled = Column(Boolean, default=True)
    incremental_field = Column(String(100), nullable=True)  # Field used for incremental extraction
    
    # Status tracking
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index("idx_etl_metadata_source_entity", "source_system", "entity_type"),
        Index("idx_etl_metadata_last_run", "last_successful_run"),
        UniqueConstraint("source_system", "entity_type", name="uq_source_entity"),
    )
    
    def __repr__(self):
        return f"<ETLMetadata {self.source_system}.{self.entity_type}>"
