from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.services import invoice_service, organization_service

router = APIRouter()


@router.get("/", response_model=List[schemas.Invoice])
def read_invoices(
    org_id: int = Query(..., description="Organization ID to filter invoices"),
    status: Optional[str] = Query(None, description="Filter by invoice status"),
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve invoices for an organization.
    
    Users can only access invoices for their own organization unless they are superusers.
    """
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access invoices for this organization",
        )
    
    # Check if organization exists
    organization = organization_service.get_organization(db, org_id=org_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    # Get invoices for the organization
    invoices = invoice_service.get_invoices_by_organization(
        db, org_id=org_id, skip=skip, limit=limit, status=status
    )
    
    return invoices


@router.post("/", response_model=schemas.Invoice)
def create_invoice(
    *,
    db: Session = Depends(deps.get_db),
    invoice_in: schemas.InvoiceCreate,
    current_user: schemas.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Create new invoice for an organization.
    
    Only superusers can create invoices.
    """
    # Create invoice
    try:
        invoice = invoice_service.create_invoice(db, invoice_in=invoice_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return invoice


@router.get("/{invoice_id}", response_model=schemas.InvoiceWithItems)
def read_invoice(
    invoice_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific invoice by ID.
    
    Users can only access invoices for their own organization unless they are superusers.
    """
    # Get invoice
    invoice = invoice_service.get_invoice_with_items(db, invoice_id=invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != invoice.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this invoice",
        )
    
    return invoice


@router.put("/{invoice_id}", response_model=schemas.Invoice)
def update_invoice(
    *,
    db: Session = Depends(deps.get_db),
    invoice_id: int,
    invoice_in: schemas.InvoiceUpdate,
    current_user: schemas.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Update an invoice.
    
    Only superusers can update invoices.
    Cannot update invoices with status 'paid' or 'cancelled'.
    """
    # Get invoice
    invoice = invoice_service.get_invoice(db, invoice_id=invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    
    # Update invoice
    try:
        updated_invoice = invoice_service.update_invoice(db, invoice_id=invoice_id, invoice_in=invoice_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return updated_invoice


@router.post("/{invoice_id}/cancel", response_model=schemas.Invoice)
def cancel_invoice(
    *,
    db: Session = Depends(deps.get_db),
    invoice_id: int,
    current_user: schemas.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Cancel an invoice.
    
    Only superusers can cancel invoices.
    Cannot cancel invoices with status 'paid'.
    """
    # Get invoice
    invoice = invoice_service.get_invoice(db, invoice_id=invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    
    # Cancel invoice
    try:
        invoice = invoice_service.cancel_invoice(db, invoice_id=invoice_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return invoice


@router.post("/{invoice_id}/pay", response_model=schemas.Invoice)
def mark_invoice_as_paid(
    *,
    db: Session = Depends(deps.get_db),
    invoice_id: int,
    payment_data: schemas.invoice.InvoicePayment,
    current_user: schemas.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Mark an invoice as paid.
    
    Only superusers can mark invoices as paid.
    Cannot mark invoices with status 'cancelled' as paid.
    """
    # Get invoice
    invoice = invoice_service.get_invoice(db, invoice_id=invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    
    # Mark invoice as paid
    try:
        invoice = invoice_service.mark_invoice_as_paid(
            db, 
            invoice_id=invoice_id, 
            payment_method=payment_data.payment_method,
            payment_date=payment_data.payment_date
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return invoice


@router.post("/generate/monthly", response_model=schemas.InvoiceWithItems)
def generate_monthly_invoice(
    *,
    db: Session = Depends(deps.get_db),
    org_id: int = Query(..., description="Organization ID to generate invoice for"),
    year: int = Query(..., description="Year for the invoice"),
    month: int = Query(..., description="Month for the invoice (1-12)"),
    current_user: schemas.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Generate a monthly invoice for an organization based on agent activities, costs, and outcomes.
    
    Only superusers can generate invoices.
    """
    # Validate month
    if month < 1 or month > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Month must be between 1 and 12",
        )
    
    # Check if organization exists
    organization = organization_service.get_organization(db, org_id=org_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    # Generate invoice
    try:
        invoice = invoice_service.generate_monthly_invoice(db, org_id=org_id, month=month, year=year)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return invoice