from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.invoice import Invoice, InvoiceLineItem
from app.models.organization import Organization
from app.models.agent import Agent, AgentCost, AgentOutcome, AgentActivity
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceLineItemCreate

# Configure logging
logger = logging.getLogger(__name__)


def get_invoice(db: Session, invoice_id: int) -> Optional[Invoice]:
    """
    Get invoice by ID
    """
    return db.query(Invoice).filter(Invoice.id == invoice_id).first()


def get_invoice_by_number(db: Session, invoice_number: str) -> Optional[Invoice]:
    """
    Get invoice by invoice number
    """
    return db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()


def get_invoices_by_organization(
    db: Session, org_id: int, skip: int = 0, limit: int = 100, status: Optional[str] = None
) -> List[Invoice]:
    """
    Get all invoices for an organization with optional status filter and pagination
    """
    query = db.query(Invoice).filter(Invoice.organization_id == org_id)
    
    if status:
        query = query.filter(Invoice.status == status)
    
    return query.order_by(Invoice.issue_date.desc()).offset(skip).limit(limit).all()


def generate_invoice_number() -> str:
    """
    Generate a unique invoice number with format: INV-YYYYMMDD-XXXX
    where XXXX is a unique identifier
    """
    today = datetime.utcnow().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[-4:].upper()
    return f"INV-{today}-{unique_id}"


def create_invoice(db: Session, invoice_in: InvoiceCreate) -> Invoice:
    """
    Create a new invoice for an organization
    """
    # Check if organization exists
    organization = db.query(Organization).filter(
        Organization.id == invoice_in.organization_id
    ).first()
    
    if not organization:
        raise ValueError(f"Organization with ID {invoice_in.organization_id} not found")
    
    # Generate invoice number if not provided
    invoice_number = invoice_in.invoice_number
    if not invoice_number:
        invoice_number = generate_invoice_number()
        
        # Ensure uniqueness
        while get_invoice_by_number(db, invoice_number):
            invoice_number = generate_invoice_number()
    else:
        # Check if invoice number already exists
        if get_invoice_by_number(db, invoice_number):
            raise ValueError(f"Invoice with number {invoice_number} already exists")
    
    # Calculate total amounts
    amount = sum(item.amount for item in invoice_in.items)
    tax_amount = 0.0  # Could be calculated based on tax rules
    total_amount = amount + tax_amount
    
    # Create invoice
    invoice = Invoice(
        organization_id=invoice_in.organization_id,
        invoice_number=invoice_number,
        issue_date=datetime.utcnow(),
        due_date=invoice_in.due_date,
        status="pending",
        amount=amount,
        tax_amount=tax_amount,
        total_amount=total_amount,
        currency=invoice_in.currency,
        notes=invoice_in.notes,
        invoice_metadata=invoice_in.invoice_metadata,
    )
    
    # Add invoice to database
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
    # Create line items
    for item in invoice_in.items:
        line_item = InvoiceLineItem(
            invoice_id=invoice.id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            amount=item.amount,
            item_type=item.item_type,
            reference_id=item.reference_id,
            reference_type=item.reference_type,
            item_metadata=item.item_metadata,
        )
        db.add(line_item)
    
    db.commit()
    db.refresh(invoice)
    
    logger.info(f"Created invoice {invoice.invoice_number} for organization {organization.name}")
    return invoice


def update_invoice(db: Session, invoice_id: int, invoice_in: InvoiceUpdate) -> Optional[Invoice]:
    """
    Update an invoice
    """
    invoice = get_invoice(db, invoice_id=invoice_id)
    if not invoice:
        logger.warning(f"Invoice update failed: Invoice not found with ID {invoice_id}")
        return None
    
    # Check if invoice can be updated
    if invoice.status in ["paid", "cancelled"]:
        raise ValueError(f"Cannot update invoice with status: {invoice.status}")
    
    # Update invoice properties - Using model_dump instead of dict for Pydantic v2
    update_data = invoice_in.model_dump(exclude_unset=True)
    
    # Update invoice attributes
    for field, value in update_data.items():
        if hasattr(invoice, field):
            setattr(invoice, field, value)
    
    # Commit changes to database
    db.commit()
    db.refresh(invoice)
    
    logger.info(f"Updated invoice: {invoice.invoice_number}")
    return invoice


def cancel_invoice(db: Session, invoice_id: int) -> Optional[Invoice]:
    """
    Cancel an invoice
    """
    invoice = get_invoice(db, invoice_id=invoice_id)
    if not invoice:
        logger.warning(f"Invoice cancellation failed: Invoice not found with ID {invoice_id}")
        return None
    
    # Check if invoice can be cancelled
    if invoice.status == "paid":
        raise ValueError("Cannot cancel a paid invoice")
    
    # Cancel invoice
    invoice.status = "cancelled"
    db.commit()
    db.refresh(invoice)
    
    logger.info(f"Cancelled invoice: {invoice.invoice_number}")
    return invoice


def mark_invoice_as_paid(db: Session, invoice_id: int, payment_method: str, payment_date: Optional[datetime] = None) -> Optional[Invoice]:
    """
    Mark an invoice as paid
    """
    invoice = get_invoice(db, invoice_id=invoice_id)
    if not invoice:
        logger.warning(f"Invoice payment update failed: Invoice not found with ID {invoice_id}")
        return None
    
    # Check if invoice can be marked as paid
    if invoice.status == "cancelled":
        raise ValueError("Cannot mark a cancelled invoice as paid")
    
    if invoice.status == "paid":
        raise ValueError("Invoice is already marked as paid")
    
    # Update invoice
    invoice.status = "paid"
    invoice.payment_method = payment_method
    invoice.payment_date = payment_date or datetime.utcnow()
    
    # Commit changes to database
    db.commit()
    db.refresh(invoice)
    
    logger.info(f"Marked invoice {invoice.invoice_number} as paid")
    return invoice


def get_invoice_with_items(db: Session, invoice_id: int) -> Optional[Invoice]:
    """
    Get invoice with line items
    """
    return db.query(Invoice).filter(Invoice.id == invoice_id).first()


def generate_monthly_invoice(db: Session, org_id: int, month: int, year: int) -> Invoice:
    """
    Generate a monthly invoice for an organization based on agent activities, costs, and outcomes
    """
    # Check if organization exists
    organization = db.query(Organization).filter(
        Organization.id == org_id
    ).first()
    
    if not organization:
        raise ValueError(f"Organization with ID {org_id} not found")
    
    # Calculate date range for the specified month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    # Set due date to 15 days from invoice generation
    due_date = datetime.utcnow() + timedelta(days=15)
    
    # Generate invoice number
    invoice_number = generate_invoice_number()
    while get_invoice_by_number(db, invoice_number):
        invoice_number = generate_invoice_number()
    
    # Get all agents for this organization
    agents = db.query(Agent).filter(Agent.organization_id == org_id).all()
    agent_ids = [agent.id for agent in agents]
    
    if not agent_ids:
        raise ValueError(f"No agents found for organization with ID {org_id}")
    
    # Prepare invoice items based on agent billing models
    invoice_items = []
    total_amount = 0.0
    
    for agent in agents:
        if not agent.billing_model:
            continue
        
        billing_model = agent.billing_model
        model_type = billing_model.model_type
        
        if model_type == "seat":
            # Seat-based billing
            price_per_seat = billing_model.config.get("price_per_seat", 0)
            billing_frequency = billing_model.config.get("billing_frequency", "monthly")
            
            # Check if this is the right billing cycle
            if billing_frequency == "monthly" or (billing_frequency == "quarterly" and month % 3 == 1):
                item_amount = price_per_seat
                invoice_items.append(
                    InvoiceLineItemCreate(
                        description=f"Agent access: {agent.name} - {billing_frequency} subscription",
                        quantity=1,
                        unit_price=item_amount,
                        amount=item_amount,
                        item_type="subscription",
                        reference_id=agent.id,
                        reference_type="Agent",
                        item_metadata={"billing_model_id": billing_model.id, "billing_period": f"{year}-{month}"}
                    )
                )
                total_amount += item_amount
        
        elif model_type == "activity":
            # Activity-based billing
            price_per_action = billing_model.config.get("price_per_action", 0)
            action_type = billing_model.config.get("action_type", None)
            
            # Query activities in the date range
            activities_query = db.query(func.count(AgentActivity.id)).filter(
                AgentActivity.agent_id == agent.id,
                AgentActivity.timestamp >= start_date,
                AgentActivity.timestamp <= end_date
            )
            
            if action_type:
                activities_query = activities_query.filter(AgentActivity.activity_type == action_type)
                
            activity_count = activities_query.scalar() or 0
            
            if activity_count > 0:
                item_amount = price_per_action * activity_count
                invoice_items.append(
                    InvoiceLineItemCreate(
                        description=f"Agent usage: {agent.name} - {activity_count} activities",
                        quantity=activity_count,
                        unit_price=price_per_action,
                        amount=item_amount,
                        item_type="usage",
                        reference_id=agent.id,
                        reference_type="Agent",
                        item_metadata={"billing_model_id": billing_model.id, "billing_period": f"{year}-{month}"}
                    )
                )
                total_amount += item_amount
        
        elif model_type == "outcome":
            # Outcome-based billing
            percentage = billing_model.config.get("percentage", 0) / 100.0  # Convert to decimal
            outcome_type = billing_model.config.get("outcome_type", None)
            
            # Query outcomes in the date range
            outcomes_query = db.query(func.sum(AgentOutcome.value)).filter(
                AgentOutcome.agent_id == agent.id,
                AgentOutcome.timestamp >= start_date,
                AgentOutcome.timestamp <= end_date
            )
            
            if outcome_type:
                outcomes_query = outcomes_query.filter(AgentOutcome.outcome_type == outcome_type)
                
            outcome_value = outcomes_query.scalar() or 0.0
            
            if outcome_value > 0:
                item_amount = outcome_value * percentage
                invoice_items.append(
                    InvoiceLineItemCreate(
                        description=f"Agent outcomes: {agent.name} - {percentage*100}% of {outcome_value}",
                        quantity=1,
                        unit_price=item_amount,
                        amount=item_amount,
                        item_type="outcome",
                        reference_id=agent.id,
                        reference_type="Agent",
                        item_metadata={"billing_model_id": billing_model.id, "billing_period": f"{year}-{month}"}
                    )
                )
                total_amount += item_amount
        
        elif model_type == "hybrid":
            # Hybrid billing model handles multiple billing types
            
            # Base fee component
            base_fee = billing_model.config.get("base_fee", 0)
            if base_fee > 0:
                invoice_items.append(
                    InvoiceLineItemCreate(
                        description=f"Agent base fee: {agent.name}",
                        quantity=1,
                        unit_price=base_fee,
                        amount=base_fee,
                        item_type="subscription",
                        reference_id=agent.id,
                        reference_type="Agent",
                        metadata={"billing_model_id": billing_model.id, "billing_period": f"{year}-{month}"}
                    )
                )
                total_amount += base_fee
            
            # Seat component
            seat_config = billing_model.config.get("seat_config", None)
            if seat_config:
                price_per_seat = seat_config.get("price_per_seat", 0)
                billing_frequency = seat_config.get("billing_frequency", "monthly")
                
                # Check if this is the right billing cycle
                if billing_frequency == "monthly" or (billing_frequency == "quarterly" and month % 3 == 1):
                    item_amount = price_per_seat
                    invoice_items.append(
                        InvoiceLineItemCreate(
                            description=f"Agent access: {agent.name} - {billing_frequency} subscription",
                            quantity=1,
                            unit_price=item_amount,
                            amount=item_amount,
                            item_type="subscription",
                            reference_id=agent.id,
                            reference_type="Agent",
                            item_metadata={"billing_model_id": billing_model.id, "billing_period": f"{year}-{month}"}
                        )
                    )
                    total_amount += item_amount
            
            # Activity components
            activity_configs = billing_model.config.get("activity_config", [])
            for activity_config in activity_configs:
                price_per_action = activity_config.get("price_per_action", 0)
                action_type = activity_config.get("action_type", None)
                
                if not action_type:
                    continue
                
                # Query activities in the date range
                activity_count = db.query(func.count(AgentActivity.id)).filter(
                    AgentActivity.agent_id == agent.id,
                    AgentActivity.activity_type == action_type,
                    AgentActivity.timestamp >= start_date,
                    AgentActivity.timestamp <= end_date
                ).scalar() or 0
                
                if activity_count > 0:
                    item_amount = price_per_action * activity_count
                    invoice_items.append(
                        InvoiceLineItemCreate(
                            description=f"Agent usage: {agent.name} - {activity_count} {action_type} activities",
                            quantity=activity_count,
                            unit_price=price_per_action,
                            amount=item_amount,
                            item_type="usage",
                            reference_id=agent.id,
                            reference_type="Agent",
                            item_metadata={"billing_model_id": billing_model.id, "billing_period": f"{year}-{month}"}
                        )
                    )
                    total_amount += item_amount
            
            # Outcome components
            outcome_configs = billing_model.config.get("outcome_config", [])
            for outcome_config in outcome_configs:
                percentage = outcome_config.get("percentage", 0) / 100.0  # Convert to decimal
                outcome_type = outcome_config.get("outcome_type", None)
                
                if not outcome_type:
                    continue
                
                # Query outcomes in the date range
                outcome_value = db.query(func.sum(AgentOutcome.value)).filter(
                    AgentOutcome.agent_id == agent.id,
                    AgentOutcome.outcome_type == outcome_type,
                    AgentOutcome.timestamp >= start_date,
                    AgentOutcome.timestamp <= end_date
                ).scalar() or 0.0
                
                if outcome_value > 0:
                    item_amount = outcome_value * percentage
                    invoice_items.append(
                        InvoiceLineItemCreate(
                            description=f"Agent outcomes: {agent.name} - {percentage*100}% of {outcome_value} {outcome_type}",
                            quantity=1,
                            unit_price=item_amount,
                            amount=item_amount,
                            item_type="outcome",
                            reference_id=agent.id,
                            reference_type="Agent",
                            metadata={"billing_model_id": billing_model.id, "billing_period": f"{year}-{month}"}
                        )
                    )
                    total_amount += item_amount
    
    # Check if there are any items to invoice
    if not invoice_items:
        raise ValueError(f"No billable items found for organization with ID {org_id} in {month}/{year}")
    
    # Create invoice
    invoice_create = InvoiceCreate(
        organization_id=org_id,
        invoice_number=invoice_number,
        due_date=due_date,
        items=invoice_items,
        currency="USD",
        notes=f"Monthly invoice for {start_date.strftime('%B %Y')}",
        metadata={"billing_period": f"{year}-{month}"}
    )
    
    # Create the invoice with items
    invoice = create_invoice(db, invoice_create)
    
    logger.info(f"Generated monthly invoice {invoice.invoice_number} for {organization.name} for {month}/{year}")
    return invoice