from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel

class Invoice(BaseModel):
    """
    Invoice model for tracking billing and payments
    """
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    
    # Invoice details
    invoice_number = Column(String, nullable=False, unique=True)
    issue_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    status = Column(String, default="pending")  # pending, paid, overdue, cancelled
    
    # Amount information
    amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    
    # Payment details
    payment_method = Column(String, nullable=True)
    stripe_invoice_id = Column(String, nullable=True)
    stripe_checkout_session_id = Column(String, nullable=True)
    stripe_payment_link = Column(String, nullable=True)
    payment_date = Column(DateTime, nullable=True)
    
    # Additional metadata
    notes = Column(String, nullable=True)
    invoice_metadata = Column(JSON, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="invoices")
    line_items = relationship("InvoiceLineItem", back_populates="invoice")
    
    def __str__(self) -> str:
        return f"Invoice(number={self.invoice_number}, amount={self.total_amount})"


class InvoiceLineItem(BaseModel):
    """
    Line items within an invoice
    """
    invoice_id = Column(Integer, ForeignKey("invoice.id"), nullable=False)
    
    # Item details
    description = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    
    # Item type and reference
    item_type = Column(String, nullable=False)  # subscription, usage, outcome
    reference_id = Column(Integer, nullable=True)  # ID of the referenced entity (agent, activity, etc.)
    reference_type = Column(String, nullable=True)  # Type of referenced entity (Agent, AgentActivity, etc.)
    
    # Metadata for reporting
    item_metadata = Column(JSON, nullable=True)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="line_items")
    
    def __str__(self) -> str:
        return f"InvoiceLineItem(description={self.description}, amount={self.amount})"