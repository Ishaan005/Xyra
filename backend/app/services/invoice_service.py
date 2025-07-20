from typing import List, Optional
import logging
from datetime import datetime, timedelta, timezone
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.invoice import Invoice, InvoiceLineItem
from app.models.organization import Organization
from app.models.agent import Agent, AgentOutcome, AgentActivity
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


def get_invoice_by_stripe_session_id(db: Session, session_id: str) -> Optional[Invoice]:
    """
    Get invoice by Stripe Checkout Session ID
    """
    return db.query(Invoice).filter(Invoice.stripe_checkout_session_id == session_id).first()


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
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
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
    tax_amount = 0.0  # CTODO: Implement tax calculation logic if needed
    total_amount = amount + tax_amount
    
    # Create invoice
    invoice = Invoice(
        organization_id=invoice_in.organization_id,
        invoice_number=invoice_number,
        issue_date=datetime.now(timezone.utc),
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


def update_invoice(db: Session, invoice_id: int, invoice_in: InvoiceUpdate, extra_fields: Optional[dict] = None) -> Optional[Invoice]:
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
    if extra_fields:
        update_data.update(extra_fields)
    
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
    current_status = str(invoice.status)
    if current_status == "paid":
        raise ValueError("Cannot cancel a paid invoice")
    
    # Cancel invoice
    setattr(invoice, 'status', 'cancelled')
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
    current_status = str(invoice.status)
    if current_status == "cancelled":
        raise ValueError("Cannot mark a cancelled invoice as paid")
    
    if current_status == "paid":
        raise ValueError("Invoice is already marked as paid")
    
    # Update invoice using setattr to avoid SQLAlchemy typing issues
    setattr(invoice, 'status', 'paid')
    setattr(invoice, 'payment_method', payment_method)
    setattr(invoice, 'payment_date', payment_date or datetime.now(timezone.utc))
    
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
    due_date = datetime.now(timezone.utc) + timedelta(days=15)
    
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
        
        # Get actual values from SQLAlchemy objects
        agent_id = getattr(agent, 'id')
        billing_model_id = getattr(billing_model, 'id')
        agent_name = getattr(agent, 'name')
        
        if model_type == "agent":
            # Agent-based billing using dedicated config table
            if billing_model.agent_config:
                cfg = billing_model.agent_config
                base_fee = cfg.base_agent_fee
                
                # Add setup fee if this is the first billing cycle
                # Note: You might want to add logic to check if this is the first invoice
                item_amount = base_fee
                
                # Apply volume discount if enabled
                if cfg.volume_discount_enabled and cfg.volume_discount_threshold and cfg.volume_discount_percentage:
                    # For simplicity, assuming single agent. In practice, you'd check total agents.
                    if 1 >= cfg.volume_discount_threshold:
                        discount = item_amount * (cfg.volume_discount_percentage / 100.0)
                        item_amount -= discount
                
                if item_amount > 0:
                    invoice_items.append(
                        InvoiceLineItemCreate(
                            description=f"Agent subscription: {agent_name} - Monthly fee",
                            quantity=1,
                            unit_price=item_amount,
                            amount=item_amount,
                            item_type="subscription",
                            reference_id=agent_id,
                            reference_type="Agent",
                            item_metadata={"billing_model_id": billing_model_id, "billing_period": f"{year}-{month}"}
                        )
                    )
                    total_amount += item_amount
        
        elif model_type == "activity":
            # Activity-based billing using dedicated config table
            for cfg in billing_model.activity_config:
                if not cfg.is_active:
                    continue
                
                # Query activities in the date range
                activities_query = db.query(func.count(AgentActivity.id)).filter(
                    AgentActivity.agent_id == agent_id,
                    AgentActivity.timestamp >= start_date,
                    AgentActivity.timestamp <= end_date
                )
                
                if cfg.activity_type:
                    activities_query = activities_query.filter(AgentActivity.activity_type == cfg.activity_type)
                    
                activity_count = activities_query.scalar() or 0
                
                if activity_count > 0:
                    # Calculate cost using the same logic as the calculation service
                    activity_cost = 0.0
                    
                    # Add base agent fee
                    if cfg.base_agent_fee > 0:
                        activity_cost += cfg.base_agent_fee
                    
                    # Calculate unit-based cost with volume pricing
                    if cfg.volume_pricing_enabled and cfg.tier_1_threshold and cfg.tier_1_price:
                        # Apply tiered pricing
                        remaining_units = activity_count
                        unit_cost = 0.0
                        
                        # Tier 1
                        tier_1_units = min(remaining_units, cfg.tier_1_threshold)
                        unit_cost += tier_1_units * cfg.tier_1_price
                        remaining_units -= tier_1_units
                        
                        # Tier 2
                        if remaining_units > 0 and cfg.tier_2_threshold and cfg.tier_2_price:
                            tier_2_units = min(remaining_units, cfg.tier_2_threshold - cfg.tier_1_threshold)
                            unit_cost += tier_2_units * cfg.tier_2_price
                            remaining_units -= tier_2_units
                        
                        # Tier 3
                        if remaining_units > 0 and cfg.tier_3_price:
                            unit_cost += remaining_units * cfg.tier_3_price
                        
                        activity_cost += unit_cost
                    else:
                        # Simple per-unit pricing
                        activity_cost += cfg.price_per_unit * activity_count
                    
                    if activity_cost > 0:
                        invoice_items.append(
                            InvoiceLineItemCreate(
                                description=f"Agent usage: {agent_name} - {activity_count} {cfg.activity_type or 'activities'}",
                                quantity=activity_count,
                                unit_price=activity_cost / activity_count,
                                amount=activity_cost,
                                item_type="usage",
                                reference_id=agent_id,
                                reference_type="Agent",
                                item_metadata={"billing_model_id": billing_model_id, "billing_period": f"{year}-{month}"}
                            )
                        )
                        total_amount += activity_cost
        
        elif model_type == "outcome":
            # Outcome-based billing using dedicated config table
            for cfg in billing_model.outcome_config:
                if not cfg.is_active:
                    continue
                
                # Query outcomes in the date range
                outcomes_query = db.query(func.sum(AgentOutcome.value), func.count(AgentOutcome.id)).filter(
                    AgentOutcome.agent_id == agent_id,
                    AgentOutcome.timestamp >= start_date,
                    AgentOutcome.timestamp <= end_date
                )
                
                if cfg.outcome_type:
                    outcomes_query = outcomes_query.filter(AgentOutcome.outcome_type == cfg.outcome_type)
                    
                result = outcomes_query.first()
                outcome_value = (result[0] if result and result[0] is not None else 0.0)
                outcome_count = (result[1] if result and result[1] is not None else 0)
                
                # Skip if no outcomes or below minimum attribution value
                if outcome_value <= 0:
                    continue
                    
                if cfg.minimum_attribution_value and outcome_value < cfg.minimum_attribution_value:
                    continue
                
                # Calculate charges based on billing model configuration
                percentage_based_fee = 0.0
                fixed_fee = 0.0
                description_parts = []
                
                # 1. Calculate percentage-based fee
                if cfg.percentage and cfg.percentage > 0:
                    if cfg.tiered_pricing_enabled and cfg.tier_1_threshold and cfg.tier_1_percentage:
                        # Apply tiered percentage pricing
                        remaining_value = outcome_value
                        
                        # Tier 1
                        tier_1_value = min(remaining_value, cfg.tier_1_threshold)
                        percentage_based_fee += tier_1_value * (cfg.tier_1_percentage / 100.0)
                        remaining_value -= tier_1_value
                        
                        # Tier 2
                        if remaining_value > 0 and cfg.tier_2_threshold and cfg.tier_2_percentage:
                            tier_2_value = min(remaining_value, cfg.tier_2_threshold - cfg.tier_1_threshold)
                            percentage_based_fee += tier_2_value * (cfg.tier_2_percentage / 100.0)
                            remaining_value -= tier_2_value
                        
                        # Tier 3
                        if remaining_value > 0 and cfg.tier_3_percentage:
                            percentage_based_fee += remaining_value * (cfg.tier_3_percentage / 100.0)
                        
                        description_parts.append(f"Tiered percentage of ${outcome_value:.2f}")
                    else:
                        # Simple percentage-based pricing
                        percentage_based_fee = outcome_value * (cfg.percentage / 100.0)
                        description_parts.append(f"{cfg.percentage}% of ${outcome_value:.2f}")
                
                # 2. Calculate fixed charge fee
                if cfg.fixed_charge_per_outcome and cfg.fixed_charge_per_outcome > 0 and outcome_count > 0:
                    fixed_fee = cfg.fixed_charge_per_outcome * outcome_count
                    description_parts.append(f"${cfg.fixed_charge_per_outcome:.2f} × {outcome_count} outcomes")
                
                outcome_fee = percentage_based_fee + fixed_fee
                
                # Apply risk premium if configured
                if cfg.risk_premium_percentage and cfg.risk_premium_percentage > 0:
                    risk_adjustment = outcome_fee * (cfg.risk_premium_percentage / 100.0)
                    outcome_fee += risk_adjustment
                    description_parts.append(f"{cfg.risk_premium_percentage}% risk premium")
                
                # Apply success bonus if threshold is met
                if cfg.success_bonus_threshold and cfg.success_bonus_percentage and outcome_value >= cfg.success_bonus_threshold:
                    bonus = outcome_value * (cfg.success_bonus_percentage / 100.0)
                    outcome_fee += bonus
                    description_parts.append(f"{cfg.success_bonus_percentage}% success bonus")
                
                if outcome_fee > 0:
                    description = f"Agent outcomes: {agent_name} - {' + '.join(description_parts)}"
                    
                    # Determine appropriate quantity and unit price for display
                    if fixed_fee > 0 and percentage_based_fee == 0:
                        # Pure fixed charge model - show per outcome
                        quantity = outcome_count
                        unit_price = cfg.fixed_charge_per_outcome
                    else:
                        # Mixed or pure percentage model - show as total
                        quantity = 1
                        unit_price = outcome_fee
                    
                    invoice_items.append(
                        InvoiceLineItemCreate(
                            description=description,
                            quantity=quantity,
                            unit_price=unit_price,
                            amount=outcome_fee,
                            item_type="outcome",
                            reference_id=agent_id,
                            reference_type="Agent",
                            item_metadata={
                                "billing_model_id": billing_model_id, 
                                "billing_period": f"{year}-{month}",
                                "outcome_value": outcome_value,
                                "outcome_count": outcome_count,
                                "percentage_fee": percentage_based_fee,
                                "fixed_fee": fixed_fee,
                                "total_fee": outcome_fee,
                                "outcome_type": cfg.outcome_type
                            }
                        )
                    )
                    total_amount += outcome_fee
    
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
        invoice_metadata={"billing_period": f"{year}-{month}"}
    )
    
    # Create the invoice with items
    invoice = create_invoice(db, invoice_create)

    logger.info(f"Generated monthly invoice {invoice.invoice_number} for {organization.name} for {month}/{year}")
    return invoice