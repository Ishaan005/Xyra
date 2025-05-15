from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime


class InvoiceLineItemBase(BaseModel):
    """Base invoice line item schema"""
    description: str
    quantity: float = 1.0
    unit_price: float
    amount: float
    item_type: str  # subscription, usage, outcome
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    item_metadata: Optional[Dict[str, Any]] = None


class InvoiceLineItemCreate(InvoiceLineItemBase):
    """Schema for creating invoice line items"""
    pass


class InvoiceLineItemInDB(InvoiceLineItemBase):
    """Schema for invoice line items in DB"""
    id: int
    invoice_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Updated from orm_mode = True for Pydantic v2 compatibility


class InvoiceLineItem(InvoiceLineItemInDB):
    """Schema for invoice line item responses"""
    pass


class InvoiceBase(BaseModel):
    """Base invoice schema"""
    invoice_number: str
    due_date: datetime
    amount: float
    tax_amount: float = 0.0
    total_amount: float
    currency: str = "USD"
    status: str = "pending"
    notes: Optional[str] = None
    invoice_metadata: Optional[Dict[str, Any]] = None


class InvoiceCreate(BaseModel):
    """Schema for creating invoices"""
    organization_id: int
    due_date: datetime
    items: List[InvoiceLineItemCreate]
    notes: Optional[str] = None
    invoice_metadata: Optional[Dict[str, Any]] = None
    
    # Optional fields that can be auto-generated
    invoice_number: Optional[str] = None
    currency: str = "USD"


class InvoiceUpdate(BaseModel):
    """Schema for updating invoices"""
    status: Optional[str] = None
    payment_method: Optional[str] = None
    payment_date: Optional[datetime] = None
    notes: Optional[str] = None
    invoice_metadata: Optional[Dict[str, Any]] = None


class InvoicePayment(BaseModel):
    """Schema for invoice payment data"""
    payment_method: str
    payment_date: Optional[datetime] = None


class InvoiceInDB(InvoiceBase):
    """Schema for invoices in DB"""
    id: int
    organization_id: int
    issue_date: datetime
    payment_method: Optional[str] = None
    stripe_invoice_id: Optional[str] = None
    stripe_checkout_session_id: Optional[str] = None
    stripe_payment_link: Optional[str] = None
    payment_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Updated from orm_mode = True for Pydantic v2 compatibility


class Invoice(InvoiceInDB):
    """Schema for invoice responses"""
    pass


class InvoiceWithItems(Invoice):
    """Invoice schema with line items"""
    line_items: List[InvoiceLineItem] = []