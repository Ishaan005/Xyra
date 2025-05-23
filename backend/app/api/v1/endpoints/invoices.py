from typing import Any, List, Optional, Dict
from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.core.config import settings
from app.services import invoice_service, organization_service, stripe_service, pdf_service, email_service
from app.api.v1 import stripe_webhook

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

router.include_router(stripe_webhook.router, prefix="")

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

    # Generate Stripe payment link
    try:
        stripe_result = stripe_service.create_checkout_session(
            amount=invoice.total_amount,
            currency=invoice.currency,
            invoice_number=invoice.invoice_number,
            description=invoice.notes or f"Invoice {invoice.invoice_number}",
            success_url=f"{settings.FRONTEND_BASE_URL}/dashboard/invoices/{invoice.id}?payment_status=success",
            cancel_url=f"{settings.FRONTEND_BASE_URL}/dashboard/invoices/{invoice.id}?payment_status=cancelled",
        )
        if stripe_result:
            invoice = invoice_service.update_invoice(
                db,
                invoice_id=invoice.id,
                invoice_in=schemas.InvoiceUpdate(),
                extra_fields={
                    "stripe_checkout_session_id": stripe_result["session_id"],
                    "stripe_payment_link": stripe_result["payment_link"]
                }
            )
    except Exception:
        pass  # Optionally log Stripe errors

    # Generate PDF invoice automatically
    import tempfile
    pdf_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            pdf_service.generate_invoice_pdf(invoice, db.query(organization_service.Organization).filter_by(id=invoice.organization_id).first(), invoice.line_items, tmpfile.name)
            pdf_path = tmpfile.name
            # TODO: store the path or upload to cloud storage here
    except Exception:
        pass  # TODO: Handle PDF generation errors
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
    
    # Add PDF and Stripe payment link URLs to the response
    pdf_url = f"/api/v1/invoices/{invoice_id}/pdf"
    payment_link = invoice.stripe_payment_link
    invoice_dict = invoice.__dict__.copy()
    invoice_dict["pdf_url"] = pdf_url
    invoice_dict["stripe_payment_link"] = payment_link
    return invoice_dict


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


@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
):
    """
    Download a PDF version of the invoice.
    """
    invoice = invoice_service.get_invoice_with_items(db, invoice_id=invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != invoice.organization_id):
        raise HTTPException(status_code=403, detail="Not enough permissions to access this invoice")
    organization = db.query(organization_service.Organization).filter_by(id=invoice.organization_id).first()
    output_path = f"/tmp/invoice_{invoice.invoice_number}.pdf"
    pdf_service.generate_invoice_pdf(invoice, organization, invoice.line_items, output_path)
    from fastapi.responses import FileResponse
    return FileResponse(output_path, filename=f"invoice_{invoice.invoice_number}.pdf", media_type="application/pdf")


@router.post("/send-email", response_model=schemas.Invoice)
def send_invoice_email(
    *,
    db: Session = Depends(deps.get_db),
    email_data: schemas.InvoiceEmailRequest,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Send an invoice to a recipient via email.
    
    Users can only send invoices for their own organization unless they are superusers.
    """
    # Check if either invoice_id or invoice_number is provided
    if email_data.invoice_id is None and email_data.invoice_number is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either invoice_id or invoice_number must be provided",
        )
    
    # Get the invoice based on the provided identifier
    invoice = None
    if email_data.invoice_id:
        invoice = invoice_service.get_invoice_with_items(db, invoice_id=email_data.invoice_id)
    else:
        invoice = invoice_service.get_invoice_by_number(db, invoice_number=email_data.invoice_number)
        if invoice:
            # Get full invoice with items
            invoice = invoice_service.get_invoice_with_items(db, invoice_id=invoice.id)
    
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
    
    # Get the organization
    organization = db.query(organization_service.Organization).filter_by(id=invoice.organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
      # Send the email with our email service
    from app.services import email_service
    success, error_msg = email_service.send_invoice_email(
        invoice_id=invoice.id,
        recipient_email=email_data.recipient_email,
        organization=organization,
        invoice=invoice,
        line_items=invoice.line_items,
        payment_link=email_data.payment_link or invoice.stripe_payment_link,
        include_pdf=email_data.include_pdf,
        custom_message=email_data.message
    )
    
    if not success:
        error_detail = "Failed to send email"
        if error_msg:
            error_detail = f"Failed to send email: {error_msg}"
            
        if "not configured" in error_msg:
            # This is a configuration error
            logger.error(f"Email configuration error: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Email service is not properly configured. Please contact the administrator.",
            )
        else:
            # This is a general error during email sending
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail,
            )
    
    # Update invoice metadata to record that it was sent
    invoice_metadata = invoice.invoice_metadata or {}
    email_history = invoice_metadata.get("email_history", [])
    email_history.append({
        "sent_at": datetime.utcnow().isoformat(),
        "recipient": email_data.recipient_email,
        "sent_by": current_user.email,
        "included_pdf": email_data.include_pdf,
        "included_payment_link": bool(email_data.payment_link or invoice.stripe_payment_link)
    })
    invoice_metadata["email_history"] = email_history
    
    # Update the invoice
    invoice = invoice_service.update_invoice(
        db,
        invoice_id=invoice.id,
        invoice_in=schemas.InvoiceUpdate(invoice_metadata=invoice_metadata)
    )
    
    return invoice


@router.post("/send-bulk-email", response_model=Dict[str, Any])
def send_bulk_invoice_email(
    *,
    db: Session = Depends(deps.get_db),
    email_data: schemas.BulkInvoiceEmailRequest,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Send an invoice to multiple recipients via email.
    
    Users can only send invoices for their own organization unless they are superusers.
    This endpoint is more efficient for sending the same invoice to multiple recipients.
    """
    from datetime import datetime
    import uuid
    
    # Check if either invoice_id or invoice_number is provided
    if email_data.invoice_id is None and email_data.invoice_number is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either invoice_id or invoice_number must be provided",
        )
    
    # Get the invoice based on the provided identifier
    invoice = None
    if email_data.invoice_id:
        invoice = invoice_service.get_invoice_with_items(db, invoice_id=email_data.invoice_id)
    else:
        invoice = invoice_service.get_invoice_by_number(db, invoice_number=email_data.invoice_number)
        if invoice:
            # Get full invoice with items
            invoice = invoice_service.get_invoice_with_items(db, invoice_id=invoice.id)
    
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
    
    # Get the organization
    organization = db.query(organization_service.Organization).filter_by(id=invoice.organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    # Validate recipient emails (max allowed recipients)
    max_recipients = 100  # Set a reasonable limit
    if len(email_data.recipient_emails) > max_recipients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many recipients. Maximum allowed is {max_recipients}."
        )
    
    # Send the emails with our email service
    from app.services import email_service
    background_tasks = BackgroundTasks()
    
    # Prepare HTML and text templates
    html_template = email_service.get_invoice_email_html_template()
    text_template = email_service.get_invoice_email_text_template()
    
    # Prepare payment info
    payment_link = email_data.payment_link or invoice.stripe_payment_link
    payment_info = ""
    if payment_link:
        payment_info = email_service.get_payment_button_html(payment_link)
    
    # Prepare custom message
    custom_message_html = email_service.get_custom_message_html(email_data.message)
    
    # Prepare PDF message
    pdf_message = "A PDF copy of this invoice is attached to this email for your records." if email_data.include_pdf else "If you need a PDF copy of this invoice, please contact us."
    
    # Prepare template variables dictionary
    invoice_vars = {
        "invoice_number": invoice.invoice_number,
        "organization_name": organization.name,
        "issue_date": invoice.issue_date.strftime('%Y-%m-%d'),
        "due_date": invoice.due_date.strftime('%Y-%m-%d'),
        "currency": invoice.currency,
        "total_amount": f"{invoice.total_amount:.2f}",
        "custom_message_html": custom_message_html,
        "payment_info": payment_info,
        "pdf_message": pdf_message,
        "payment_link": payment_link
    }
    
    # Prepare attachments if needed
    attachments = None
    if email_data.include_pdf:
        import tempfile
        import os
        
        # Generate PDF once and reuse for all recipients
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            pdf_service.generate_invoice_pdf(invoice, organization, invoice.line_items, tmpfile.name)
            with open(tmpfile.name, 'rb') as f:
                pdf_data = f.read()
                attachments = {
                    recipient: [(f"Invoice_{invoice.invoice_number}.pdf", pdf_data)]
                    for recipient in email_data.recipient_emails
                }
            # Clean up temp file
            os.unlink(tmpfile.name)
    
    # Fill templates with variables
    html_content = html_template.format(**invoice_vars)
    plain_text = text_template.format(**invoice_vars)
    
    # Personalize for each recipient if requested
    template_vars = {}
    if email_data.personalize_content and email_data.recipient_variables:
        template_vars = email_data.recipient_variables
    
    # Execute bulk send
    bulk_send_results = email_service.send_bulk_emails(
        recipients=email_data.recipient_emails,
        subject=f"Invoice {invoice.invoice_number} from {organization.name}",
        body_html_template=html_content,
        body_text_template=plain_text,
        template_vars=template_vars,
        cc=email_data.cc,
        bcc=email_data.bcc,
        reply_to=email_data.reply_to or organization.contact_email,
        attachments=attachments,
        track_opens=True,
        track_clicks=True,
        priority="high",
        add_dkim_signature=True,
        metadata={"invoice_id": invoice.id, "invoice_number": invoice.invoice_number}
    )
    
    # Update invoice metadata
    invoice_metadata = invoice.invoice_metadata or {}
    email_history = invoice_metadata.get("email_history", [])
    
    bulk_email_id = str(uuid.uuid4())
    email_history.append({
        "bulk_email_id": bulk_email_id,
        "sent_at": datetime.utcnow().isoformat(),
        "recipients_count": len(email_data.recipient_emails),
        "successful_count": sum(1 for result in bulk_send_results.values() if result.get('success')),
        "sent_by": current_user.email,
        "included_pdf": email_data.include_pdf,
        "included_payment_link": bool(payment_link)
    })
    
    invoice_metadata["email_history"] = email_history
    
    # Update the invoice
    invoice = invoice_service.update_invoice(
        db,
        invoice_id=invoice.id,
        invoice_in=schemas.InvoiceUpdate(invoice_metadata=invoice_metadata)
    )
    
    # Prepare the response with bulk send results and invoice info
    response = {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "bulk_email_id": bulk_email_id,
        "recipients_count": len(email_data.recipient_emails),
        "successful_count": sum(1 for result in bulk_send_results.values() if result.get('success')),
        "failed_count": sum(1 for result in bulk_send_results.values() if not result.get('success')),
        "email_details": bulk_send_results
    }
    
    return response


@router.get("/{invoice_id}/email-status", response_model=Dict[str, Any])
def get_invoice_email_status(
    *,
    db: Session = Depends(deps.get_db),
    invoice_id: int,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get the email status for a specific invoice.
    
    Retrieves the email delivery status, opens, clicks, and other tracking information
    for emails sent for this invoice.
    """
    # Get the invoice
    invoice = invoice_service.get_invoice(db, invoice_id=invoice_id)
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
    
    # Extract email history from invoice metadata
    invoice_metadata = invoice.invoice_metadata or {}
    email_history = invoice_metadata.get("email_history", [])
    
    # Get email tracking IDs from history if available
    email_tracking_ids = []
    for history_item in email_history:
        if "email_id" in history_item:
            email_tracking_ids.append(history_item["email_id"])
    
    # Get status updates from email service
    from app.services import email_service
    email_statuses = {}
    
    for email_id in email_tracking_ids:
        status = email_service.get_email_status(email_id)
        if status:
            email_statuses[email_id] = status
    
    # Prepare response
    response = {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "email_history": email_history,
        "email_statuses": email_statuses,
        "total_emails_sent": len(email_history),
        "total_opens": sum(1 for status in email_statuses.values() if status.get("status") == email_service.EmailStatus.OPENED),
        "total_clicks": sum(1 for status in email_statuses.values() if status.get("status") == email_service.EmailStatus.CLICKED),
        "total_delivered": sum(1 for status in email_statuses.values() if status.get("status") == email_service.EmailStatus.DELIVERED),
        "total_failed": sum(1 for status in email_statuses.values() if status.get("status") == email_service.EmailStatus.FAILED)
    }
    
    return response